#!/usr/bin/env python

from gnuradio import gr, usrp, blks2, rds
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import stdgui2, fftsink2, scopesink2
from optparse import OptionParser
from usrpm import usrp_dbid
import math, sys, wx

class rds_tx_block(stdgui2.std_top_block):
	def __init__(self, frame, panel, vbox, argv):
		stdgui2.std_top_block.__init__ (self, frame, panel, vbox, argv)

		parser = OptionParser (option_class=eng_option)
		parser.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
						help="select USRP Tx side A or B")
		parser.add_option("-f", "--freq", type="eng_float", default=107.2e6,
						help="set Tx frequency to FREQ [required]", metavar="FREQ")
		parser.add_option("--wavfile", type="string", default=None,
						help="open .wav audio file FILE")
		parser.add_option("--xml", type="string", default="rds_data.xml",
						help="open .xml RDS data FILE")
		(options, args) = parser.parse_args()
		if len(args) != 0:
			parser.print_help()
			sys.exit(1)

		usrp_interp = 500
		self.u = usrp.sink_c (0, usrp_interp)
		print "USRP Serial: ", self.u.serial_number()
		usrp_rate = self.u.dac_rate() / usrp_interp		# 256 kS/s

		# determine the daughterboard subdevice we're using
		if options.tx_subdev_spec is None:
			options.tx_subdev_spec = usrp.pick_tx_subdevice(self.u)
		self.u.set_mux(usrp.determine_tx_mux_value(self.u, options.tx_subdev_spec))
		self.subdev = usrp.selected_subdev(self.u, options.tx_subdev_spec)
		print "Using d'board", self.subdev.side_and_name()

		# set max Tx gain, tune frequency and enable transmitter
		gain = self.subdev.gain_range()[1]
		self.subdev.set_gain(gain)
		print "Gain set to", gain
		if self.u.tune(self.subdev.which(), self.subdev, options.freq):
			print "Tuned to", options.freq/1e6, "MHz"
		else:
			sys.exit(1)
		self.subdev.set_enable(True)

		# open wav file containing floats in the [-1, 1] range, repeat
		if options.wavfile is None:
			print "Please provide a wavfile to transmit! Exiting\n"
			sys.exit(1)
		self.src = gr.wavfile_source(options.wavfile, True)
		nchans = self.src.channels()
		sample_rate = self.src.sample_rate()
		bits_per_sample = self.src.bits_per_sample()
		print nchans, "channels,", sample_rate, "samples/sec,", \
			bits_per_sample, "bits/sample"

		# resample to usrp rate
		self.resample_left = blks2.rational_resampler_fff(usrp_rate, sample_rate)
		self.resample_right = blks2.rational_resampler_fff(usrp_rate, sample_rate)
		self.connect ((self.src, 0), self.resample_left)
		self.connect ((self.src, 1), self.resample_right)

		# create L+R (mono) and L-R (stereo)
		self.audio_lpr = gr.add_ff()
		self.audio_lmr = gr.sub_ff()
		self.connect (self.resample_left, (self.audio_lpr, 0))
		self.connect (self.resample_left, (self.audio_lmr, 0))
		self.connect (self.resample_right, (self.audio_lpr, 1))
		self.connect (self.resample_right, (self.audio_lmr, 1))

		# low-pass filter for L+R
		audio_lpr_taps = gr.firdes.low_pass(
			1,				# gain
			usrp_rate,		# sampling rate
			15e3,			# passband cutoff
			1e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.audio_lpr_filter = gr.fir_filter_fff (1, audio_lpr_taps)
		self.connect (self.audio_lpr, self.audio_lpr_filter)

		# create pilot tone at 19 kHz
		self.pilot = gr.sig_source_f(
			usrp_rate,			# sampling rate
			gr.GR_SIN_WAVE,		# waveform
			19e3,				# frequency
			5e-2)				# amplitude

		# upconvert L-R to 38 kHz and band-pass
		self.mix_stereo = gr.multiply_ff()
		audio_lmr_taps = gr.firdes.band_pass(
			2e2,			# gain
			usrp_rate,		# sampling rate
			38e3-15e3,		# low cutoff
			38e3+15e3,		# high cutoff
			1e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.audio_lmr_filter = gr.fir_filter_fff (1, audio_lmr_taps)
		self.connect (self.audio_lmr, (self.mix_stereo, 0))
		self.connect (self.pilot, (self.mix_stereo, 1))
		self.connect (self.pilot, (self.mix_stereo, 2))
		self.connect (self.mix_stereo, self.audio_lmr_filter)

		# create NRZ diff-encoded RDS bitstream
		# enforce the 1187.5bps rate
		# mix with 57kHz carrier (equivalent to BPSK)
		self.rds_enc = rds.data_encoder('rds_data.xml')
		self.diff_enc = gr.diff_encoder_bb(2)
		self.manchester1 = gr.map_bb([1,2])
		self.manchester2 = gr.unpack_k_bits_bb(2)
		self.nrz = gr.map_bb([-1,1])
		self.c2f = gr.char_to_float()
		self.rate_enforcer = rds.rate_enforcer(usrp_rate)
		self.bpsk_mod = gr.multiply_ff()
		self.connect (self.rds_enc, self.diff_enc, self.manchester1, \
			self.manchester2, self.nrz, self.c2f)
		self.connect (self.c2f, (self.rate_enforcer, 0))
		self.connect (self.pilot, (self.rate_enforcer, 1))
		self.connect (self.rate_enforcer, (self.bpsk_mod, 0))
		self.connect (self.pilot, (self.bpsk_mod, 1))
		self.connect (self.pilot, (self.bpsk_mod, 2))
		self.connect (self.pilot, (self.bpsk_mod, 3))

		# RDS band-pass filter
		rds_filter_taps = gr.firdes.band_pass(
			50,				# gain
			usrp_rate,		# sampling rate
			57e3-3e3,		# low cutoff
			57e3+3e3,		# high cutoff
			1e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.rds_filter = gr.fir_filter_fff (1, rds_filter_taps)
		self.connect (self.bpsk_mod, self.rds_filter)

		# mix L+R, pilot, L-R and RDS
		self.mixer = gr.add_ff()
		self.connect (self.audio_lpr_filter, (self.mixer, 0))
		self.connect (self.pilot, (self.mixer, 1))
		self.connect (self.audio_lmr_filter, (self.mixer, 2))
		self.connect (self.rds_filter, (self.mixer, 3))

		# fm modulation, gain & TX
		max_dev = 75e3
		k = 2*math.pi*max_dev/usrp_rate		# modulator sensitivity
		self.modulator = gr.frequency_modulator_fc (k)
		self.gain = gr.multiply_const_cc (1e4)
		self.connect (self.mixer, self.modulator, self.gain, self.u)

		# plot an FFT to verify we are sending what we want
		if 1:
			self.fft = fftsink2.fft_sink_f(panel, title="Pre FM modulation",
				fft_size=512*4, sample_rate=usrp_rate, y_per_div=20, ref_level=-20)
			self.connect (self.mixer, self.fft)
			vbox.Add (self.fft.win, 1, wx.EXPAND)
		if 0:
			self.scope = scopesink2.scope_sink_f(panel, title="RDS encoder output",
				sample_rate=usrp_rate)
			self.connect (self.rds_enc, self.scope)
			vbox.Add (self.scope.win, 1, wx.EXPAND)

if __name__ == '__main__':
	app = stdgui2.stdapp(rds_tx_block, "RDS Tx")
	app.MainLoop ()
