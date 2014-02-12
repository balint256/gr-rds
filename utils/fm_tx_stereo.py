#!/usr/bin/env python

from gnuradio import gr, usrp, blks2
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import stdgui2, fftsink2
from optparse import OptionParser
from usrpm import usrp_dbid
import math, sys, wx

class fm_tx_block(stdgui2.std_top_block):
	def __init__(self, frame, panel, vbox, argv):
		stdgui2.std_top_block.__init__ (self, frame, panel, vbox, argv)

		parser = OptionParser (option_class=eng_option)
		parser.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
						help="select USRP Tx side A or B")
		parser.add_option("-f", "--freq", type="eng_float", default=107.2e6,
						help="set Tx frequency to FREQ [required]", metavar="FREQ")
		parser.add_option("--wavfile", type="string", default="",
						help="read input from FILE")
		(options, args) = parser.parse_args()
		if len(args) != 0:
			parser.print_help()
			sys.exit(1)

		self.usrp_interp = 200
		self.u = usrp.sink_c (0, self.usrp_interp)
		print "USRP Serial: ", self.u.serial_number()
		self.dac_rate = self.u.dac_rate()					# 128 MS/s
		self.usrp_rate = self.dac_rate / self.usrp_interp	# 640 kS/s
		self.sw_interp = 5
		self.audio_rate = self.usrp_rate / self.sw_interp	# 128 kS/s

		# determine the daughterboard subdevice we're using
		if options.tx_subdev_spec is None:
			options.tx_subdev_spec = usrp.pick_tx_subdevice(self.u)
		self.u.set_mux(usrp.determine_tx_mux_value(self.u, options.tx_subdev_spec))
		self.subdev = usrp.selected_subdev(self.u, options.tx_subdev_spec)
		print "Using d'board: ", self.subdev.side_and_name()

		# set max Tx gain, tune frequency and enable transmitter
		self.subdev.set_gain(self.subdev.gain_range()[1])
		if self.u.tune(self.subdev.which(), self.subdev, options.freq):
			print "Tuned to", options.freq/1e6, "MHz"
		else:
			sys.exit(1)
		self.subdev.set_enable(True)

		# open wav file containing floats in the [-1, 1] range, repeat
		if options.wavfile is None:
			print "Please provide a wavfile to transmit! Exiting\n"
			sys.exit(1)
		self.src = gr.wavfile_source (options.wavfile, True)
		nchans = self.src.channels()
		sample_rate = self.src.sample_rate()
		bits_per_sample = self.src.bits_per_sample()
		print nchans, "channels,", sample_rate, "kS/s,", bits_per_sample, "bits/sample"

		# resample to 128kS/s
		if sample_rate == 44100:
			self.resample_left = blks2.rational_resampler_fff(32,11)
			self.resample_right = blks2.rational_resampler_fff(32,11)
		elif sample_rate == 48000:
			self.resample_left == blks2.rational_resampler_fff(8,3)
			self.resample_right == blks2.rational_resampler_fff(8,3)
		elif sample_rate == 8000:
			self.resample_left == blks2.rational_resampler_fff(16,1)
			self.resample_right == blks2.rational_resampler_fff(16,1)
		else:
			print sample_rate, "is an unsupported sample rate"
			sys.exit(1)
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
		audio_lpr_taps = gr.firdes.low_pass (0.3,	# gain
											self.audio_rate,	# sampling rate
											15e3,				# passband cutoff
											2e3,				# transition width
											gr.firdes.WIN_HANN)
		self.audio_lpr_filter = gr.fir_filter_fff (1, audio_lpr_taps)
		self.connect (self.audio_lpr, self.audio_lpr_filter)

		# create pilot tone at 19 kHz
		self.pilot = gr.sig_source_f(self.audio_rate,	# sampling freq
									gr.GR_SIN_WAVE,		# waveform
									19e3,				# frequency
									3e-2)				# amplitude

		# create the L-R signal carrier at 38 kHz, high-pass to remove 0Hz tone
		self.stereo_carrier = gr.multiply_ff()
		self.connect (self.pilot, (self.stereo_carrier, 0))
		self.connect (self.pilot, (self.stereo_carrier, 1))
		stereo_carrier_taps = gr.firdes.high_pass (1,			# gain
											self.audio_rate,	# sampling rate
											1e4,				# cutoff freq
											2e3,				# transition width
											gr.firdes.WIN_HANN)
		self.stereo_carrier_filter = gr.fir_filter_fff(1, stereo_carrier_taps)
		self.connect (self.stereo_carrier, self.stereo_carrier_filter)

		# upconvert L-R to 23-53 kHz and band-pass
		self.mix_stereo = gr.multiply_ff()
		audio_lmr_taps = gr.firdes.band_pass (3e3,				# gain
											self.audio_rate,	# sampling rate
											23e3,				# low cutoff
											53e3,				# high cuttof
											2e3,				# transition width
											gr.firdes.WIN_HANN)
		self.audio_lmr_filter = gr.fir_filter_fff (1, audio_lmr_taps)
		self.connect (self.audio_lmr, (self.mix_stereo, 0))
		self.connect (self.stereo_carrier_filter, (self.mix_stereo, 1))
		self.connect (self.mix_stereo, self.audio_lmr_filter)

		# mix L+R, pilot and L-R
		self.mixer = gr.add_ff()
		self.connect (self.audio_lpr_filter, (self.mixer, 0))
		self.connect (self.pilot, (self.mixer, 1))
		self.connect (self.audio_lmr_filter, (self.mixer, 2))

		# interpolation & pre-emphasis
		interp_taps = gr.firdes.low_pass (self.sw_interp,	# gain
										self.audio_rate,	# Fs
										60e3,				# cutoff freq
										5e3,				# transition width
										gr.firdes.WIN_HAMMING)
		self.interpolator = gr.interp_fir_filter_fff (self.sw_interp, interp_taps)
		self.pre_emph = blks2.fm_preemph(self.usrp_rate, tau=50e-6)
		self.connect (self.mixer, self.interpolator, self.pre_emph)

		# fm modulation, gain & TX
		max_dev = 100e3
		k = 2 * math.pi * max_dev / self.usrp_rate		# modulator sensitivity
		self.modulator = gr.frequency_modulator_fc (k)
		self.gain = gr.multiply_const_cc (1e3)
		self.connect (self.pre_emph, self.modulator, self.gain, self.u)

		# plot an FFT to verify we are sending what we want
		pre_mod = fftsink2.fft_sink_f(panel, title="Before Interpolation",
			fft_size=512, sample_rate=self.audio_rate, y_per_div=20, ref_level=20)
		self.connect (self.mixer, pre_mod)
		vbox.Add (pre_mod.win, 1, wx.EXPAND)

if __name__ == '__main__':
	app = stdgui2.stdapp(fm_tx_block, "FM Tx")
	app.MainLoop ()
