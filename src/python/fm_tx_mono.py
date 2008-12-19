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
		parser.add_option("-i", "--filename", type="string", default="",
						help="read input from FILE")
		(options, args) = parser.parse_args()
		if len(args) != 0:
			parser.print_help()
			sys.exit(1)

		self.u = usrp.sink_c ()

		self.dac_rate = self.u.dac_rate()					# 128 MS/s
		self.usrp_interp = 400
		self.u.set_interp_rate(self.usrp_interp)
		self.usrp_rate = self.dac_rate / self.usrp_interp	# 320 kS/s
		self.sw_interp = 10
		self.audio_rate = self.usrp_rate / self.sw_interp	# 32 kS/s

		# determine the daughterboard subdevice we're using
		if options.tx_subdev_spec is None:
			options.tx_subdev_spec = usrp.pick_tx_subdevice(self.u)
		self.u.set_mux(usrp.determine_tx_mux_value(self.u, options.tx_subdev_spec))
		self.subdev = usrp.selected_subdev(self.u, options.tx_subdev_spec)
		print "Using TX d'board %s" % (self.subdev.side_and_name(),)

		# set max Tx gain, tune frequency and enable transmitter
		self.subdev.set_gain(self.subdev.gain_range()[1])
		self.u.tune(self.subdev._which, self.subdev, options.freq)
		self.subdev.set_enable(True)

		# open file containing floats in the [-1, 1] range, repeat
		self.src = gr.wavfile_source (options.filename, True)
		nchans = self.src.channels()
		sample_rate = self.src.sample_rate()
		bits_per_sample = self.src.bits_per_sample()
		print nchans, "channels,", sample_rate, "kS/s,", bits_per_sample, "bits/sample"
		# resample to 32kS/s
		if sample_rate == 44100:
			self.resample = blks2.rational_resampler_fff(8,11)
		elif sample_rate == 48000:
			self.resample == blks2.rational_resampler_fff(2,3)
		else:
			print sample_rate, "is an unsupported sample rate"
			exit()
		# apply preemphasis
		self.emph = blks2.fm_preemph(self.audio_rate, tau=75e-6)

		# fm modulation & gain
		self.fmtx = blks2.wfm_tx (self.audio_rate, self.usrp_rate, tau=75e-6, max_dev=15e3)
		self.gain = gr.multiply_const_cc (4e3)

		# connect it all
		self.connect (self.src, self.resample, self.emph, self.fmtx, self.gain, self.u)

		# plot an FFT to verify we are sending what we want
		pre_mod = fftsink2.fft_sink_f(panel, title="Pre-Modulation",
			fft_size=512, sample_rate=self.usrp_rate, y_per_div=10, ref_level=0)
		self.connect (self.emph, pre_mod)
		vbox.Add (pre_mod.win, 1, wx.EXPAND)

if __name__ == '__main__':
	app = stdgui2.stdapp(fm_tx_block, "FM Tx")
	app.MainLoop ()
