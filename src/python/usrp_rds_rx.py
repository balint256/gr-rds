#!/usr/bin/env python

from gnuradio import gr, usrp, optfir, blks2, rds, audio
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import slider, form, stdgui2, fftsink2, scopesink2
from optparse import OptionParser
from rdspanel import rdsPanel
from usrpm import usrp_dbid
import sys, math, wx, time


class rds_rx_graph (stdgui2.std_top_block):
	def __init__(self,frame,panel,vbox,argv):
		stdgui2.std_top_block.__init__ (self,frame,panel,vbox,argv)

		parser=OptionParser(option_class=eng_option)
		parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
						  help="select USRP Rx side A or B (default=A)")
		parser.add_option("-f", "--freq", type="eng_float", default=92.4e6,
						  help="set frequency to FREQ", metavar="FREQ")
		parser.add_option("-g", "--gain", type="eng_float", default=None,
						  help="set gain in dB")
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
		
		self.vol = .5
		self.state = "FREQ"
		self.freq = 0

		# build graph

		usrp_decim = 250
		self.u = usrp.source_c(0, usrp_decim)
		print "USRP Serial: ", self.u.serial_number()
		adc_rate = self.u.adc_rate()				# 64 MS/s
		demod_rate = adc_rate / usrp_decim			# 256 kS/s
		audio_decim = 8
		audio_rate = demod_rate / audio_decim		# 32 kS/s

		if options.rx_subdev_spec is None:
			options.rx_subdev_spec = usrp.pick_subdev(self.u, 
				(usrp_dbid.TV_RX, usrp_dbid.TV_RX_REV_2, usrp_dbid.BASIC_RX))

		self.u.set_mux(usrp.determine_rx_mux_value(self.u, options.rx_subdev_spec))
		self.subdev = usrp.selected_subdev(self.u, options.rx_subdev_spec)
		print "Using d'board", self.subdev.side_and_name()

		# channel filter, wfm_rcv_pll
		chan_filt_coeffs = optfir.low_pass (1,
											demod_rate,
											80e3,
											115e3,
											0.1,
											60)
		self.chan_filt = gr.fir_filter_ccf (1, chan_filt_coeffs)
		self.guts = blks2.wfm_rcv_pll (demod_rate, audio_decim, 50e-6)
		self.connect(self.u, self.chan_filt, self.guts)

		# volume control, audio sink
		self.volume_control_l = gr.multiply_const_ff(self.vol)
		self.volume_control_r = gr.multiply_const_ff(self.vol)
		self.audio_sink = audio.sink(int(audio_rate),
									options.audio_output, False)
		self.connect ((self.guts, 0), self.volume_control_l, (self.audio_sink, 0))
		self.connect ((self.guts, 1), self.volume_control_r, (self.audio_sink, 1))

		# fm filter (low-pass 70kHz)
		coeffs = gr.firdes.low_pass (50,
										demod_rate,
										70e3,
										10e3,
										gr.firdes.WIN_HAMMING)
		self.fm_filter = gr.fir_filter_fff (1, coeffs)
		self.connect(self.guts.fm_demod, self.fm_filter)

		# pilot channel filter (band-pass, 18.5-19.5kHz)
		pilot_filter_coeffs = gr.firdes.band_pass(1, 
													demod_rate,
													18.5e3,
													19.5e3,
													1e3,
													gr.firdes.WIN_HAMMING)
		self.pilot_filter = gr.fir_filter_fff(1, pilot_filter_coeffs)
		self.connect(self.fm_filter, self.pilot_filter)

		# RDS channel filter (band-pass, 54-60kHz)
		rds_filter_coeffs = gr.firdes.band_pass (1,
													demod_rate,
													54e3,
													60e3,
													3e3,
													gr.firdes.WIN_HAMMING)
		self.rds_filter = gr.fir_filter_fff (1, rds_filter_coeffs)
		self.connect(self.fm_filter, self.rds_filter)

		# create 57kHz subcarrier from 19kHz pilot, downconvert RDS channel
		self.mixer = gr.multiply_ff()
		self.connect(self.pilot_filter, (self.mixer, 0))
		self.connect(self.pilot_filter, (self.mixer, 1))
		self.connect(self.pilot_filter, (self.mixer, 2))
		self.connect(self.rds_filter, (self.mixer, 3))

		# low-pass the baseband RDS signal at 1.5kHz
		rds_bb_filter_coeffs = gr.firdes.low_pass (1,
													demod_rate,
													1500,
													2e3,
													gr.firdes.WIN_HAMMING)
		self.rds_bb_filter = gr.fir_filter_fff (1, rds_bb_filter_coeffs)
		self.connect(self.mixer, self.rds_bb_filter)


		# 1187.5bps = 19kHz/16
		self.rds_data_clock = rds.freq_divider(16)
		#self.rds_data_clock = gr.fractional_interpolator_ff(0, 1/16.)
		data_clock_taps = gr.firdes.low_pass (1,			# gain
											demod_rate,		# sampling rate
											1.2e3,			# passband cutoff
											1.5e3,			# transition width
											gr.firdes.WIN_HANN)
		self.data_clock_filter = gr.fir_filter_fff (1, data_clock_taps)
		self.connect(self.pilot_filter, self.rds_data_clock,
						self.data_clock_filter)

		# bpsk_demod, diff_decoder, rds_decoder
		self.bpsk_demod = rds.bpsk_demod(demod_rate)
		self.differential_decoder = gr.diff_decoder_bb(2)
		self.msgq = gr.msg_queue()
		self.rds_decoder = rds.data_decoder(self.msgq)
		self.connect(self.rds_bb_filter, (self.bpsk_demod, 0))
		self.connect(self.data_clock_filter, (self.bpsk_demod, 1))
		self.connect(self.bpsk_demod, self.differential_decoder)
		self.connect(self.differential_decoder, self.rds_decoder)

		# this is used for tuning to stations automatically
		self.probe = gr.probe_avg_mag_sqrd_c(5, 0.1)
		self.connect (self.chan_filt, self.probe)

		self._build_gui(vbox, demod_rate, audio_rate)

		# if no gain was specified, use the mid-point in dB
		if options.gain is None:
			g = self.subdev.gain_range()
#			options.gain = float(g[0]+g[1])/2
			options.gain = g[1]

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





####################### GUI ################################

	def _set_status_msg(self, msg, which=0):
		self.frame.GetStatusBar().SetStatusText(msg, which)

	def _build_gui(self, vbox, demod_rate, audio_rate):

		def _form_set_freq(kv):
			return self.set_freq(kv['freq'])

		if 0:
			self.src_fft = fftsink2.fft_sink_c (self.panel, title="Data from USRP",
											fft_size=512, sample_rate=demod_rate)
			self.connect (self.u, self.src_fft)
			vbox.Add (self.src_fft.win, 4, wx.EXPAND)

		if 0:
			post_fm_demod_fft = fftsink2.fft_sink_f (self.panel, title="Post FM Demod",
				fft_size=512, sample_rate=demod_rate, y_per_div=10, ref_level=0)
			self.connect (self.guts.fm_demod, post_fm_demod_fft)
			vbox.Add (post_fm_demod_fft.win, 4, wx.EXPAND)

		if 0:
			rds_fft = fftsink2.fft_sink_f (self.panel, title="RDS baseband",
				fft_size=512, sample_rate=demod_rate, y_per_div=20, ref_level=20)
			self.connect (self.rds_data_clock, rds_fft)
			vbox.Add (rds_fft.win, 4, wx.EXPAND)

		if 0:
			rds_scope = scopesink2.scope_sink_f(self.panel, title="RDS timedomain",
				sample_rate=demod_rate,num_inputs=2)
			self.connect (self.rds_bb_filter, (rds_scope,1))
			self.connect (self.rds_data_clock, (rds_scope,0))
			vbox.Add(rds_scope.win, 4, wx.EXPAND)

		self.rdspanel = rdsPanel(self.msgq, self.panel)
		vbox.Add(self.rdspanel, 4, wx.EXPAND)

		# control area form at bottom
		self.myform = form.form()

		# 1st line
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.myform.btn_down = wx.Button(self.panel, -1, "<<")
		self.myform.btn_down.Bind(wx.EVT_BUTTON, self.Seek_Down)
		hbox.Add(self.myform.btn_down, 0)
		self.myform['freq'] = form.float_field(
			parent=self.panel, sizer=hbox, label="Freq", weight=1,
			callback=self.myform.check_input_and_call(_form_set_freq, self._set_status_msg))
		hbox.Add((5,0), 0)
#		myform.freq_field = wx.TextCtrl(self.panel, name="freq")
#		hbox.Add(myform.freq_field, 0)
		self.myform.btn_up = wx.Button(self.panel, -1, ">>")
		self.myform.btn_up.Bind(wx.EVT_BUTTON, self.Seek_Up)
		hbox.Add(self.myform.btn_up, 0)
		self.myform['freq_slider'] = form.quantized_slider_field(
			parent=self.panel, sizer=hbox, weight=3,
			range=(87.5e6, 108e6, 0.1e6), callback=self.set_freq)
		hbox.Add((5,0), 0)
		vbox.Add(hbox, 0, wx.EXPAND)


		# 2nd line
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((5,0), 0)
		self.myform['volume'] = form.quantized_slider_field(parent=self.panel, sizer=hbox,
			label="Volume", weight=3, range=self.volume_range(), callback=self.set_vol)
		hbox.Add((5,0), 1)
		self.myform['gain'] = form.quantized_slider_field(parent=self.panel, sizer=hbox,
			label="Gain", weight=3, range=self.subdev.gain_range(), callback=self.set_gain)
		hbox.Add((5,0), 0)
		vbox.Add(hbox, 0, wx.EXPAND)



########################### EVENTS ############################

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
		r = usrp.tune(self.u, 0, self.subdev, target_freq)
		if r:
			self.freq = target_freq
			self.myform['freq'].set_value(target_freq)
#			self.myform.freq_field.SetValue(str(target_freq/1e6))
#			self.myform.freq_field.AppendText(" MHz")
			self.myform['freq_slider'].set_value(target_freq)
			self.rdspanel.frequency.SetLabel('%3.2f' % (target_freq/1e6))
			self.update_status_bar()
			self.bpsk_demod.reset()
			self.rds_decoder.reset()
			self.rdspanel.clear_data()
			self._set_status_msg("OK", 0)
			return True
		else:
			self._set_status_msg("Failed", 0)
			return False

	def set_gain(self, gain):
		self.myform['gain'].set_value(gain)
		self.subdev.set_gain(gain)


	def update_status_bar (self):
		msg = "Volume:%r  Setting:%s" % (self.vol, self.state)
		self._set_status_msg(msg, 1)

	def volume_range(self):
		return (-20.0, 0.0, 0.5)		# hardcoded values

	def Seek_Up(self, event):
		new_freq = self.freq + 1e5
		if new_freq > 108e6:
			new_freq=88e6
		self.set_freq(new_freq)
		print self.probe.level()

	def Seek_Down(self, event):
		new_freq = self.freq - 1e5
		if new_freq < 88e6:
			new_freq=108e6
		self.set_freq(new_freq)
		print self.probe.level()


if __name__ == '__main__':
	app = stdgui2.stdapp (rds_rx_graph, "USRP RDS RX")
	app.MainLoop ()
