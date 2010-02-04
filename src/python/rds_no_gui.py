#!/usr/bin/env python

from gnuradio import gr, usrp, optfir, blks2, rds, audio
from gnuradio.eng_option import eng_option
from usrpm import usrp_dbid
from optparse import OptionParser
import sys, math

dblist = (usrp_dbid.TV_RX, usrp_dbid.TV_RX_REV_2,
		usrp_dbid.TV_RX_REV_3, usrp_dbid.BASIC_RX)

class rds_rx_graph (gr.top_block):
	def __init__(self):
		gr.top_block.__init__ (self)

		parser=OptionParser(option_class=eng_option)
		parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
						  help="select USRP Rx side A or B (default=A)")
		parser.add_option("-f", "--freq", type="eng_float", default=102.2e6,
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

		# connect to USRP
		usrp_decim = 250
		self.u = usrp.source_c(0, usrp_decim)
		print "USRP Serial: ", self.u.serial_number()
		demod_rate = self.u.adc_rate() / usrp_decim		# 256 kS/s
		audio_decim = 8
		audio_rate = demod_rate / audio_decim			# 32 kS/s
		if options.rx_subdev_spec is None:
			options.rx_subdev_spec = usrp.pick_subdev(self.u, dblist)

		self.u.set_mux(usrp.determine_rx_mux_value(self.u, options.rx_subdev_spec))
		self.subdev = usrp.selected_subdev(self.u, options.rx_subdev_spec)
		print "Using d'board", self.subdev.side_and_name()


		# gain, volume, frequency
		self.gain = options.gain
		if options.gain is None:
			self.gain = self.subdev.gain_range()[1]

		self.vol = options.volume
		if self.vol is None:
			g = self.volume_range()
			self.vol = float(g[0]+g[1])/2

		self.freq = options.freq
		if abs(self.freq) < 1e6:
			self.freq *= 1e6
		
		print "Volume:%r, Gain:%r, Freq:%3.1f MHz" % (self.vol, self.gain, self.freq/1e6)

		# channel filter, wfm_rcv_pll
		chan_filt_coeffs = optfir.low_pass(
			1,				# gain
			demod_rate,		# rate
			80e3,			# passband cutoff
			115e3,			# stopband cutoff
			0.1,			# passband ripple
			60)				# stopband attenuation
		self.chan_filt = gr.fir_filter_ccf (1, chan_filt_coeffs)
		self.guts = blks2.wfm_rcv_pll (demod_rate, audio_decim)
		self.connect(self.u, self.chan_filt, self.guts)

		# volume control, audio sink
		self.volume_control_l = gr.multiply_const_ff(self.vol)
		self.volume_control_r = gr.multiply_const_ff(self.vol)
		self.audio_sink = audio.sink(int(audio_rate), options.audio_output, False)
		self.connect ((self.guts, 0), self.volume_control_l, (self.audio_sink, 0))
		self.connect ((self.guts, 1), self.volume_control_r, (self.audio_sink, 1))

		# pilot channel filter (band-pass, 18.5-19.5kHz)
		pilot_filter_coeffs = gr.firdes.band_pass(
			1,				# gain
			demod_rate,		# sampling rate
			18.5e3,			# low cutoff
			19.5e3,			# high cutoff
			1e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.pilot_filter = gr.fir_filter_fff(1, pilot_filter_coeffs)
		self.connect(self.guts.fm_demod, self.pilot_filter)

		# RDS channel filter (band-pass, 54-60kHz)
		rds_filter_coeffs = gr.firdes.band_pass(
			1,				# gain
			demod_rate,		# sampling rate
			54e3,			# low cutoff
			60e3,			# high cutoff
			3e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.rds_filter = gr.fir_filter_fff(1, rds_filter_coeffs)
		self.connect(self.guts.fm_demod, self.rds_filter)

		# create 57kHz subcarrier from 19kHz pilot, downconvert RDS channel
		self.mixer = gr.multiply_ff()
		self.connect(self.pilot_filter, (self.mixer, 0))
		self.connect(self.pilot_filter, (self.mixer, 1))
		self.connect(self.pilot_filter, (self.mixer, 2))
		self.connect(self.rds_filter, (self.mixer, 3))

		# low-pass the baseband RDS signal at 1.5kHz
		rds_bb_filter_coeffs = gr.firdes.low_pass(
			1,				# gain
			demod_rate,		# sampling rate
			1.5e3,			# passband cutoff
			2e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.rds_bb_filter = gr.fir_filter_fff(1, rds_bb_filter_coeffs)
		self.connect(self.mixer, self.rds_bb_filter)

		# 1187.5bps = 19kHz/16
		self.rds_clock = rds.freq_divider(16)
		clock_taps = gr.firdes.low_pass(
			1,				# gain
			demod_rate,		# sampling rate
			1.2e3,			# passband cutoff
			1.5e3,			# transition width
			gr.firdes.WIN_HANN)
		self.clock_filter = gr.fir_filter_fff(1, clock_taps)
		self.connect(self.pilot_filter, self.rds_clock, self.clock_filter)

		# bpsk_demod, diff_decoder, rds_decoder
		self.bpsk_demod = rds.bpsk_demod(demod_rate)
		self.differential_decoder = gr.diff_decoder_bb(2)
		self.msgq = gr.msg_queue()
		self.rds_decoder = rds.data_decoder(self.msgq)
		self.connect(self.rds_bb_filter, (self.bpsk_demod, 0))
		self.connect(self.clock_filter, (self.bpsk_demod, 1))
		self.connect(self.bpsk_demod, self.differential_decoder)
		self.connect(self.differential_decoder, self.rds_decoder)

		# set initial values
		self.subdev.set_gain(self.gain)
		self.set_vol(self.vol)
		self.set_freq(self.freq)

	def volume_range(self):
		return (-20.0, 0.0, 0.5)		# hardcoded values

	def set_vol (self, vol):
		g = self.volume_range()
		self.vol = max(g[0], min(g[1], vol))
		self.volume_control_l.set_k(10**(self.vol/10))
		self.volume_control_r.set_k(10**(self.vol/10))

	def set_freq(self, target_freq):
		r = usrp.tune(self.u, 0, self.subdev, target_freq)
		if r:
			self.freq = target_freq
			self.bpsk_demod.reset()
			self.rds_decoder.reset()
			return True
		else:
			return False

if __name__ == '__main__':
	tb =rds_rx_graph()
	try:
		tb.run()
	except KeyboardInterrupt:
		pass
