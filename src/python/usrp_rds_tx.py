#!/usr/bin/env python

from gnuradio import gr, usrp, optfir, blks2, rds
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
		parser.add_option("--wavfile", type="string", default="",
						help="open .wav audio file FILE")
		parser.add_option("--xml", type="string", default="rds_data.xml",
						help="open .xml RDS data FILE")
		(options, args) = parser.parse_args()
		if len(args) != 0:
			parser.print_help()
			sys.exit(1)

		self.usrp_interp = 500
		self.u = usrp.sink_c (0, self.usrp_interp)
		print "USRP Serial: ", self.u.serial_number()
		self.dac_rate = self.u.dac_rate()			# 128 MS/s
		self.usrp_rate = self.dac_rate / self.usrp_interp	# 256 kS/s

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
		print nchans, "channels,", sample_rate, "samples/sec,", bits_per_sample, "bits/sample"

		# resample to audio rate
		self.resample_left = blks2.rational_resampler_fff(self.usrp_rate,sample_rate)
		self.resample_right = blks2.rational_resampler_fff(self.usrp_rate,sample_rate)
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
		audio_lpr_taps = gr.firdes.low_pass (1,			# gain
						self.usrp_rate,		# sampling rate
						15e3,			# passband cutoff
						2e3,			# transition width
						gr.firdes.WIN_HANN)
		self.audio_lpr_filter = gr.fir_filter_fff (1, audio_lpr_taps)
		self.preemph_lpr = blks2.fm_preemph(self.usrp_rate, tau=50e-6)
		self.connect (self.audio_lpr, self.audio_lpr_filter, self.preemph_lpr)

		# create pilot tone at 19 kHz
		self.pilot = gr.sig_source_f(self.usrp_rate,		# sampling freq
						gr.GR_SIN_WAVE,		# waveform
						19e3,			# frequency
						3e-2)			# amplitude

		# create the L-R signal carrier at 38 kHz, high-pass to remove 0Hz tone
		self.stereo_carrier = gr.multiply_ff()
		self.connect (self.pilot, (self.stereo_carrier, 0))
		self.connect (self.pilot, (self.stereo_carrier, 1))
		stereo_carrier_taps = gr.firdes.high_pass (1,		# gain
						self.usrp_rate,		# sampling rate
						1e4,			# cutoff freq
						2e3,			# transition width
						gr.firdes.WIN_HANN)
		self.stereo_carrier_filter = gr.fir_filter_fff(1, stereo_carrier_taps)
		self.connect (self.stereo_carrier, self.stereo_carrier_filter)

		# upconvert L-R to 23-53 kHz and band-pass
		self.mix_stereo = gr.multiply_ff()
		audio_lmr_taps = gr.firdes.band_pass (1e2,		# gain
						self.usrp_rate,		# sampling rate
						23e3,			# low cutoff
						53e3,			# high cutoff
						2e3,			# transition width
						gr.firdes.WIN_HANN)
		self.audio_lmr_filter = gr.fir_filter_fff (1, audio_lmr_taps)
		self.preemph_lmr = blks2.fm_preemph(self.usrp_rate, tau=50e-6)
		self.connect (self.audio_lmr, (self.mix_stereo, 0))
		self.connect (self.stereo_carrier_filter, (self.mix_stereo, 1))
		self.connect (self.mix_stereo, self.audio_lmr_filter, self.preemph_lmr)

		# rds_encoder, diff_encoder, NRZ
		self.rds_encoder = rds.data_encoder('rds_data.xml')
		self.diff_encoder = gr.diff_encoder_bb(2)
		self.c2s = gr.chunks_to_symbols_bf([1, -1])
		self.connect (self.rds_encoder, self.diff_encoder, self.c2s)

		# resample from 1187.5Hz (=19e3/16) to self.usrp_rate,
		# band-pass to remove harmonics
		self.resample = blks2.rational_resampler_fff(int(self.usrp_rate*16/1e3), 19)
		rds_data_taps = gr.firdes.band_pass (1,			# gain
						self.usrp_rate,		# sampling rate
						1e3,			# low cutoff
						2e3,			# high cutoff
						2e2,			# transition width
						gr.firdes.WIN_HANN)
		self.rds_data_filter = gr.fir_filter_fff (1, rds_data_taps)
		self.connect (self.c2s, self.resample, self.rds_data_filter)

		# mutliply NRZ with 57kHz RDS carrier (equivalent to BPSK)
		self.bpsk_mod = gr.multiply_ff()
		self.connect (self.rds_data_filter, (self.bpsk_mod, 0))
		self.connect (self.pilot, (self.bpsk_mod, 1))
		self.connect (self.pilot, (self.bpsk_mod, 2))
		self.connect (self.pilot, (self.bpsk_mod, 3))

		# RDS band-pass filter
		rds_filter_taps = gr.firdes.band_pass (	1e5,		# gain
						self.usrp_rate,		# sampling rate
						55e3,			# low cutoff
						59e3,			# high cutoff
						3e3,			# transition width
						gr.firdes.WIN_HANN)
		self.rds_filter = gr.fir_filter_fff (1, rds_filter_taps)
		self.connect (self.bpsk_mod, self.rds_filter)

		# mix L+R, pilot, L-R and RDS
		self.mixer = gr.add_ff()
		self.connect (self.preemph_lpr, (self.mixer, 0))
		self.connect (self.pilot, (self.mixer, 1))
		self.connect (self.preemph_lmr, (self.mixer, 2))
		self.connect (self.rds_filter, (self.mixer, 3))

		# interpolation, channel filter
		interp_taps = gr.firdes.low_pass (1,			# gain
						self.usrp_rate,		# Fs
						60e3,			# passband cutoff
						5e3,			# stopband cutoff
						gr.firdes.WIN_HAMMING)
		self.interpolator = gr.interp_fir_filter_fff (1, interp_taps)
		self.connect (self.mixer, self.interpolator)

		# fm modulation, gain & TX
		max_dev = 120e3
		k = 2 * math.pi * max_dev / self.usrp_rate		# modulator sensitivity
		self.modulator = gr.frequency_modulator_fc (k)
		self.gain = gr.multiply_const_cc (1e3)
		self.connect (self.interpolator, self.modulator, self.gain, self.u)

		# plot an FFT to verify we are sending what we want
		if 0:
			self.fft = fftsink2.fft_sink_f(panel, title="After Interpolation",
				fft_size=512, sample_rate=self.usrp_rate, y_per_div=30, ref_level=20)
			self.connect (self.interpolator, self.fft)
			vbox.Add (self.fft.win, 1, wx.EXPAND)
		if 1:
			self.fft = fftsink2.fft_sink_f(panel, title="Before Interpolation",
				fft_size=512, sample_rate=self.usrp_rate, y_per_div=20, ref_level=20)
			self.connect (self.mixer, self.fft)
			vbox.Add (self.fft.win, 1, wx.EXPAND)
		if 0:
			self.fft = fftsink2.fft_sink_f(panel, title="BPSK output",
				fft_size=512*4, sample_rate=self.usrp_rate, y_per_div=20, ref_level=-100)
			self.connect (self.bpsk_mod, self.fft)
			vbox.Add (self.fft.win, 1, wx.EXPAND)
		if 0:
			self.scope = scopesink2.scope_sink_f(panel, title="BPSK output",
				sample_rate=self.usrp_rate, size=2048, v_scale=2e-7, t_scale=1e-4)
			self.connect (self.bpsk_mod, self.scope)
			vbox.Add (self.scope.win, 1, wx.EXPAND)

if __name__ == '__main__':
	app = stdgui2.stdapp(rds_tx_block, "RDS Tx")
	app.MainLoop ()
