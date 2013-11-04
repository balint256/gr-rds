#!/usr/bin/env python

from gnuradio import gr, rds, audio
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import slider, form, stdgui2, fftsink2, scopesink2, constsink_gl
from optparse import OptionParser
from rdspanel import rdsPanel
import sys, math, wx, time

usrp_rate = 256e3
audio_decim = 8
audio_rate = usrp_rate / audio_decim			# 32 kS/s
offline_samples = "/home/sdr/rds_samples.dat"

class rds_rx_graph (stdgui2.std_top_block):
	def __init__(self,frame,panel,vbox,argv):
		stdgui2.std_top_block.__init__ (self,frame,panel,vbox,argv)

		parser=OptionParser(option_class=eng_option)
		parser.add_option("-V", "--volume", type="eng_float", default=None,
						  help="set volume (default is midpoint)")
		parser.add_option("-O", "--audio-output", type="string", default="plughw:0,0",
						  help="pcm device name (default is plughw:0,0)")

		# print help when called with wrong arguments
		(options, args) = parser.parse_args()
		if len(args) != 0:
			parser.print_help()
			sys.exit(1)

		self.file_source = gr.file_source(gr.sizeof_gr_complex*1, offline_samples, True)

		chan_filter_coeffs = gr.firdes.low_pass(
			1.0,			# gain
			usrp_rate,		# sampling rate
			80e3,			# passband cutoff
			35e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.chan_filter = gr.fir_filter_ccf(1, chan_filter_coeffs)
		print "# channel filter:", len(chan_filter_coeffs), "taps"

		# PLL-based WFM demod
		fm_alpha = 0.25 * 250e3 * math.pi / usrp_rate		# 0.767
		fm_beta = fm_alpha * fm_alpha / 4.0					# 0.147
		fm_max_freq = 2.0 * math.pi * 90e3 / usrp_rate		# 2.209
		self.fm_demod = gr.pll_freqdet_cf(
			fm_alpha,			# phase gain
			fm_beta,			# freq gain
			fm_max_freq,		# in radians/sample
			-fm_max_freq)
		self.connect(self.file_source, self.chan_filter, self.fm_demod)

		# L+R, pilot, L-R, RDS filters
		lpr_filter_coeffs = gr.firdes.low_pass(
			1.0,			# gain
			usrp_rate,		# sampling rate
			15e3,			# passband cutoff
			1e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.lpr_filter = gr.fir_filter_fff(audio_decim, lpr_filter_coeffs)
		pilot_filter_coeffs = gr.firdes.band_pass(
			1.0,			# gain
			usrp_rate,		# sampling rate
			19e3-500,		# low cutoff
			19e3+500,		# high cutoff
			1e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.pilot_filter = gr.fir_filter_fff(1, pilot_filter_coeffs)
		dsbsc_filter_coeffs = gr.firdes.band_pass(
			1.0,			# gain
			usrp_rate,		# sampling rate
			38e3-15e3/2,	# low cutoff
			38e3+15e3/2,	# high cutoff
			1e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.dsbsc_filter = gr.fir_filter_fff(1, dsbsc_filter_coeffs)
		rds_filter_coeffs = gr.firdes.band_pass(
			1.0,			# gain
			usrp_rate,		# sampling rate
			57e3-3e3,		# low cutoff
			57e3+3e3,		# high cutoff
			3e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.rds_filter = gr.fir_filter_fff(1, rds_filter_coeffs)
		print "# lpr filter:", len(lpr_filter_coeffs), "taps"
		print "# pilot filter:", len(pilot_filter_coeffs), "taps"
		print "# dsbsc filter:", len(dsbsc_filter_coeffs), "taps"
		print "# rds filter:", len(rds_filter_coeffs), "taps"
		self.connect(self.fm_demod, self.lpr_filter)
		self.connect(self.fm_demod, self.pilot_filter)
		self.connect(self.fm_demod, self.dsbsc_filter)
		self.connect(self.fm_demod, self.rds_filter)

		# down-convert L-R, RDS
		self.stereo_baseband = gr.multiply_ff()
		self.connect(self.pilot_filter, (self.stereo_baseband, 0))
		self.connect(self.pilot_filter, (self.stereo_baseband, 1))
		self.connect(self.dsbsc_filter, (self.stereo_baseband, 2))
		self.rds_baseband = gr.multiply_ff()
		self.connect(self.pilot_filter, (self.rds_baseband, 0))
		self.connect(self.pilot_filter, (self.rds_baseband, 1))
		self.connect(self.pilot_filter, (self.rds_baseband, 2))
		self.connect(self.rds_filter, (self.rds_baseband, 3))

		# low-pass and downsample L-R
		lmr_filter_coeffs = gr.firdes.low_pass(
			1.0,			# gain
			usrp_rate,		# sampling rate
			15e3,			# passband cutoff
			1e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.lmr_filter = gr.fir_filter_fff(audio_decim, lmr_filter_coeffs)
		self.connect(self.stereo_baseband, self.lmr_filter)

		# create L, R from L-R, L+R
		self.left = gr.add_ff()
		self.right = gr.sub_ff()
		self.connect(self.lpr_filter, (self.left, 0))
		self.connect(self.lmr_filter, (self.left, 1))
		self.connect(self.lpr_filter, (self.right, 0))
		self.connect(self.lmr_filter, (self.right, 1))

		# send audio to null sink
		self.null0 = gr.null_sink(gr.sizeof_float)
		self.null1 = gr.null_sink(gr.sizeof_float)
		self.connect(self.left, self.null0)
		self.connect(self.right, self.null1)

		# low-pass the baseband RDS signal at 1.5kHz
		rds_bb_filter_coeffs = gr.firdes.low_pass(
			1,				# gain
			usrp_rate,		# sampling rate
			1.5e3,			# passband cutoff
			2e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.rds_bb_filter = gr.fir_filter_fff(audio_decim, rds_bb_filter_coeffs)
		print "# rds bb filter:", len(rds_bb_filter_coeffs), "taps"
		self.connect(self.rds_baseband, self.rds_bb_filter)

		# 1187.5bps = 19kHz/16
		self.clock_divider = rds.freq_divider(16)
		rds_clock_taps = gr.firdes.low_pass(
			1,				# gain
			usrp_rate,		# sampling rate
			1.2e3,			# passband cutoff
			1.5e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.rds_clock = gr.fir_filter_fff(audio_decim, rds_clock_taps)
		print "# rds clock filter:", len(rds_clock_taps), "taps"
		self.connect(self.pilot_filter, self.clock_divider, self.rds_clock)

		# bpsk_demod, diff_decoder, rds_decoder
		self.bpsk_demod = rds.bpsk_demod(audio_rate)
		self.differential_decoder = gr.diff_decoder_bb(2)
		self.msgq = gr.msg_queue()
		self.rds_decoder = rds.data_decoder(self.msgq)
		self.connect(self.rds_bb_filter, (self.bpsk_demod, 0))
		self.connect(self.rds_clock, (self.bpsk_demod, 1))
		self.connect(self.bpsk_demod, self.differential_decoder)
		self.connect(self.differential_decoder, self.rds_decoder)


		self.frame = frame
		self.panel = panel
		self._build_gui(vbox, usrp_rate, audio_rate)


####################### GUI ################################

	def _set_status_msg(self, msg, which=0):
		self.frame.GetStatusBar().SetStatusText(msg, which)

	def _build_gui(self, vbox, usrp_rate, audio_rate):

		def _form_set_freq(kv):
			return self.set_freq(kv['freq'])

		if 1:
			self.fft = fftsink2.fft_sink_f (self.panel, title="Post FM Demod",
				fft_size=512, sample_rate=usrp_rate, y_per_div=10, ref_level=0)
			self.connect (self.fm_demod, self.fft)
			vbox.Add (self.fft.win, 4, wx.EXPAND)
		if 0:
			self.scope = scopesink2.scope_sink_f(self.panel, title="RDS timedomain",
				sample_rate=usrp_rate, num_inputs=2)
			self.connect (self.rds_bb_filter, (rds_scope,1))
			self.connect (self.rds_clock, (rds_scope,0))
			vbox.Add(self.scope.win, 4, wx.EXPAND)

		self.rdspanel = rdsPanel(self.msgq, self.panel)
		vbox.Add(self.rdspanel, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 20)

		# control area form at bottom
		self.myform = form.form()




if __name__ == '__main__':
	app = stdgui2.stdapp (rds_rx_graph, "USRP RDS RX")
	app.MainLoop ()
