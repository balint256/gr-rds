#!/usr/bin/env python

from gnuradio import gr, gru, eng_notation, optfir, audio, usrp, blks2, rds
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import slider, powermate, stdgui2, fftsink2, form, scopesink2
from optparse import OptionParser
import rds_rx
from rdspanel import rdsPanel
import gnuradio.gr.gr_threading as _threading
from usrpm import usrp_dbid
import sys, math, wx

def pick_subdevice(u):
	"""
	The user didn't specify a subdevice on the command line.
	Try for one of these, in order: TV_RX, BASIC_RX, whatever is on side A.

	@return a subdev_spec
	"""
	return usrp.pick_subdev(u, (usrp_dbid.TV_RX,
								usrp_dbid.TV_RX_REV_2,
								usrp_dbid.BASIC_RX))
	
class rds_rx_graph (stdgui2.std_top_block):
	def __init__(self,frame,panel,vbox,argv):
		stdgui2.std_top_block.__init__ (self,frame,panel,vbox,argv)

		parser=OptionParser(option_class=eng_option)
		parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
						  help="select USRP Rx side A or B (default=A)")
		parser.add_option("-f", "--freq", type="eng_float", default=96.3e6,
						  help="set frequency to FREQ", metavar="FREQ")
		parser.add_option("-g", "--gain", type="eng_float", default=10,
						  help="set gain in dB (default is 10)")
		parser.add_option("-s", "--squelch", type="eng_float", default=0,
						  help="set squelch level (default is 0)")
		parser.add_option("-V", "--volume", type="eng_float", default=None,
						  help="set volume (default is midpoint)")
		parser.add_option("-O", "--audio-output", type="string", default="plughw:0,0",
						  help="pcm device name (default is plughw:0,0)")


		(options, args) = parser.parse_args()
		if len(args) != 0:
			parser.print_help()
			sys.exit(1)
		
		self.frame = frame
		self.panel = panel
		
		self.vol = 0
		self.state = "FREQ"
		self.freq = 0

		# build graph
		self.u = usrp.source_c()

		adc_rate = self.u.adc_rate()				# 64 MS/s
		usrp_decim = 250
		self.u.set_decim_rate(usrp_decim)
		usrp_rate = adc_rate / usrp_decim			# 256 kS/s
		chanfilt_decim = 1
		demod_rate = usrp_rate / chanfilt_decim		# 256 kS/s
		audio_decim = 8
		audio_rate = demod_rate / audio_decim		# 32 kHz

		if options.rx_subdev_spec is None:
			options.rx_subdev_spec = pick_subdevice(self.u)

		self.u.set_mux(usrp.determine_rx_mux_value(self.u, options.rx_subdev_spec))
		self.subdev = usrp.selected_subdev(self.u, options.rx_subdev_spec)

		chan_filt_coeffs = optfir.low_pass (1,
											demod_rate,
											80e3,
											115e3,
											0.1,
											60)
		self.chan_filt = gr.fir_filter_ccf (1, chan_filt_coeffs)

		self.guts = blks2.wfm_rcv_pll (demod_rate, audio_decim)

		self.volume_control_l = gr.multiply_const_ff(self.vol)
		self.volume_control_r = gr.multiply_const_ff(self.vol)
		self.audio_sink = audio.sink(int(audio_rate), \
									options.audio_output, False)

		coeffs = gr.firdes.low_pass (50,
										demod_rate,
										70e3,
										10e3,
										gr.firdes.WIN_HAMMING)
		self.fm_filter = gr.fir_filter_fff (1, coeffs)

		self.msgq = gr.msg_queue()
		self.rds_receiver = rds_rx.rds_rx(self, demod_rate, self.msgq)

		self.connect(self.u, self.chan_filt, self.guts)
		self.connect ((self.guts, 0), self.volume_control_l, (self.audio_sink, 0))
		self.connect ((self.guts, 1), self.volume_control_r, (self.audio_sink, 1))
		self.connect(self.guts.fm_demod, self.fm_filter, self.rds_receiver)

		self._build_gui(vbox, usrp_rate, demod_rate, audio_rate)

		if options.gain is None:
			# if no gain was specified, use the mid-point in dB
			g = self.subdev.gain_range()
			options.gain = float(g[0]+g[1])/2

		if options.volume is None:
			g = self.volume_range()
			options.volume = float(g[0]+g[1])/2

		if abs(options.freq) < 1e6:
			options.freq *= 1e6

		# set initial values

		self.set_gain(options.gain)
		self.set_vol(options.volume)
		if not(self.set_freq(options.freq)):
			self._set_status_msg("Failed to set initial frequency")

	def _set_status_msg(self, msg, which=0):
		self.frame.GetStatusBar().SetStatusText(msg, which)


	def _build_gui(self, vbox, usrp_rate, demod_rate, audio_rate):

		def _form_set_freq(kv):
			return self.set_freq(kv['freq'])

		if 0:
			self.src_fft = fftsink2.fft_sink_c (self.panel, title="Data from USRP",
											   fft_size=512, sample_rate=usrp_rate)
			self.connect (self.u, self.src_fft)
			vbox.Add (self.src_fft.win, 4, wx.EXPAND)

		if 0:
			post_fm_demod_fft = fftsink2.fft_sink_f (self.panel, title="Post FM Demod",
												  fft_size=512, sample_rate=demod_rate,
												  y_per_div=10, ref_level=0)
			self.connect (self.fm_demod, post_fm_demod_fft)
			vbox.Add (post_fm_demod_fft.win, 4, wx.EXPAND)

		if 0:
			rds_fft1 = fftsink2.fft_sink_f (self.panel, title="RDS baseband",
												  fft_size=512, sample_rate=demod_rate,
												  y_per_div=10, ref_level=20)
			self.connect (self.rds_bb_filter, rds_fft1)
			vbox.Add (rds_fft1.win, 4, wx.EXPAND)

		if 0:
			rds_scope = scopesink2.scope_sink_f(self.panel, title="RDS timedomain",sample_rate=demod_rate,\
												num_inputs=2)
			self.connect (self.rds_bb_filter, (rds_scope,1))
			self.connect (self.data_clock, (rds_scope,0))
			vbox.Add(rds_scope.win, 4, wx.EXPAND)

		if 1:
			self.rdspanel = rdsPanel(self.msgq, self.panel)
			vbox.Add(self.rdspanel, 4, wx.EXPAND)

			# control area form at bottom
			self.myform = myform = form.form()

			hbox = wx.BoxSizer(wx.HORIZONTAL)
			hbox.Add((5,0), 0)
			myform['freq'] = form.float_field(
				parent=self.panel, sizer=hbox, label="Freq", weight=1,
				callback=myform.check_input_and_call(_form_set_freq, self._set_status_msg))

			hbox.Add((5,0), 0)
			myform['freq_slider'] = \
				form.quantized_slider_field(parent=self.panel, sizer=hbox, weight=3,
											range=(87.9e6, 108.1e6, 0.1e6),
											callback=self.set_freq)
			hbox.Add((5,0), 0)
			vbox.Add(hbox, 0, wx.EXPAND)

			hbox = wx.BoxSizer(wx.HORIZONTAL)
			hbox.Add((5,0), 0)

			myform['volume'] = \
				form.quantized_slider_field(parent=self.panel, sizer=hbox, label="Volume",
											weight=3, range=self.volume_range(),
											callback=self.set_vol)
			hbox.Add((5,0), 1)

			myform['gain'] = \
				form.quantized_slider_field(parent=self.panel, sizer=hbox, label="Gain",
											weight=3, range=self.subdev.gain_range(),
											callback=self.set_gain)
			hbox.Add((5,0), 0)

			vbox.Add(hbox, 0, wx.EXPAND)


	def on_rotate (self, event):
		self.rot += event.delta
		if (self.state == "FREQ"):
			if self.rot >= 3:
				self.set_freq(self.freq + .05e6)
				self.rot -= 3
			elif self.rot <=-3:
				self.set_freq(self.freq - .05e6)
				self.rot += 3
		else:
			step = self.volume_range()[2]
			if self.rot >= 3:
				self.set_vol(self.vol + step)
				self.rot -= 3
			elif self.rot <=-3:
				self.set_vol(self.vol - step)
				self.rot += 3
			
	def on_button (self, event):
		if event.value == 0:		# button up
			return
		self.rot = 0
		if self.state == "FREQ":
			self.state = "VOL"
		else:
			self.state = "FREQ"
		self.update_status_bar ()

	def set_vol (self, vol):
		g = self.volume_range()
		self.vol = max(g[0], min(g[1], vol))
		self.volume_control_l.set_k(10**(self.vol/10))
		self.volume_control_r.set_k(10**(self.vol/10))
		self.myform['volume'].set_value(self.vol)
		self.update_status_bar ()

	def set_freq(self, target_freq):
		"""
		Set the center frequency we're interested in.

		@param target_freq: frequency in Hz
		@rypte: bool

		Tuning is a two step process.  First we ask the front-end to
		tune as close to the desired frequency as it can.  Then we use
		the result of that operation and our target_frequency to
		determine the value for the digital down converter.
		"""
		r = usrp.tune(self.u, 0, self.subdev, target_freq)
		
		if r:
			self.freq = target_freq
			self.myform['freq'].set_value(target_freq)		 # update displayed value
			self.myform['freq_slider'].set_value(target_freq)  # update displayed value
			self.rdspanel.frequency.SetLabel('%3.2f' % (target_freq/1000000.0))
			self.update_status_bar()
			self.rds_receiver.bpsk_demod.reset()
			self.rds_receiver.rds_decoder.reset()
			self._set_status_msg("OK", 0)
			return True

		self._set_status_msg("Failed", 0)
		return False

	def set_gain(self, gain):
		self.myform['gain'].set_value(gain)		 # update displayed value
		self.subdev.set_gain(gain)

	def update_status_bar (self):
		msg = "Volume:%r  Setting:%s" % (self.vol, self.state)
		self._set_status_msg(msg, 1)
		#self.src_fft.set_baseband_freq(self.freq)

	def volume_range(self):
		return (-20.0, 0.0, 0.5)


if __name__ == '__main__':
	app = stdgui2.stdapp (rds_rx_graph, "USRP RDS RX")
	app.MainLoop ()
