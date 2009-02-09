#!/usr/bin/env python

from gnuradio import gr, gru, usrp, audio, optfir, blks2, rds
from usrpm import usrp_dbid
import sys, math

class rds_rx_graph (gr.top_block):
	def __init__(self):
		gr.top_block.__init__ (self)

####################
		vol = .5
		freq = 89.8e6
		usrp_decim = 250
		audio_decim = 8
####################

		self.u = usrp.source_c(0, usrp_decim)
		print "USRP Serial: ", self.u.serial_number()
		adc_rate = self.u.adc_rate()				# 64 MS/s
		demod_rate = adc_rate / usrp_decim			# 256 kS/s
		audio_rate = demod_rate / audio_decim		# 32 kS/s

		rx_subdev_spec = usrp.pick_subdev(self.u, [usrp_dbid.BASIC_RX])
		self.u.set_mux(usrp.determine_rx_mux_value(self.u, rx_subdev_spec))
		self.subdev = usrp.selected_subdev(self.u, rx_subdev_spec)
		print "Using d'board", self.subdev.side_and_name()

		g = self.subdev.gain_range()
		gain = g[1] #float(g[0]+g[1])/2
		self.subdev.set_gain(gain)
		if usrp.tune(self.u, 0, self.subdev, freq):
			print "Tuned to", freq/1e6, "MHz"
		else:
			sys.exit(1)

		chan_filt_coeffs = optfir.low_pass (1,
											demod_rate,
											80e3,
											115e3,
											0.1,
											60)
		self.chan_filt = gr.fir_filter_ccf (1, chan_filt_coeffs)

		fm_demod_gain = demod_rate/(2*math.pi*55e3)
		self.fm_demod = gr.quadrature_demod_cf(fm_demod_gain)

		audio_coeffs = gr.firdes.low_pass(5,	# gain
											demod_rate,
											15e3,	# cut-off
											1e3,	# transition band
											gr.firdes.WIN_HAMMING)
		self.audio_filter = gr.fir_filter_fff (audio_decim, audio_coeffs)

		self.deemph = blks2.fm_deemph (demod_rate)

		self.volume_control = gr.multiply_const_ff(vol)
		self.audio_sink = audio.sink(int(audio_rate), 'plughw:0,0', False)

		coeffs = gr.firdes.low_pass (50,
										demod_rate,
										70e3,
										10e3,
										gr.firdes.WIN_HAMMING)
		self.fm_filter = gr.fir_filter_fff (1, coeffs)



		pilot_filter_coeffs = gr.firdes_band_pass(1, 
													demod_rate,
													18e3,
													20e3,
													3e3,
													gr.firdes.WIN_HAMMING)
		self.pilot_filter = gr.fir_filter_fff(1, pilot_filter_coeffs)

# Data rate = (3 * 19e3) / 48 = 19e3 / 16
		self.rds_data_clock = rds.freq_divider(16)

		rds_filter_coeffs = gr.firdes.band_pass (1,
													demod_rate,
													54e3,
													60e3,
													3e3,
													gr.firdes.WIN_HAMMING)
		self.rds_filter = gr.fir_filter_fff (1, rds_filter_coeffs)

		self.mixer = gr.multiply_ff()

		rds_bb_filter_coeffs = gr.firdes.low_pass (1,
													demod_rate,
													1500,
													2e3,
													gr.firdes.WIN_HAMMING)
		self.rds_bb_filter = gr.fir_filter_fff (1, rds_bb_filter_coeffs)

		self.data_clock = rds.freq_divider(16)
		self.bpsk_demod = rds.bpsk_demod(demod_rate)
#		self.differential_decoder = rds.diff_decoder()
		self.differential_decoder = gr.diff_decoder_bb(2)
		self.msgq = gr.msg_queue()
		self.rds_decoder = rds.data_decoder(self.msgq)

		self.connect(self.u, self.chan_filt, self.fm_demod, self.audio_filter, \
								self.deemph, self.volume_control, self.audio_sink)
		self.connect(self.fm_demod, self.fm_filter)
		self.connect(self.fm_filter, self.pilot_filter)
		self.connect(self.fm_filter, self.rds_filter)
		self.connect(self.pilot_filter, (self.mixer, 0))
		self.connect(self.pilot_filter, (self.mixer, 1))
		self.connect(self.pilot_filter, (self.mixer, 2))
		self.connect(self.rds_filter, (self.mixer, 3))
		self.connect(self.pilot_filter, self.data_clock)
		self.connect(self.mixer, self.rds_bb_filter)
		self.connect(self.rds_bb_filter, (self.bpsk_demod, 0))
		self.connect(self.data_clock, (self.bpsk_demod, 1))
		self.connect(self.bpsk_demod, self.differential_decoder)
		self.connect(self.differential_decoder, self.rds_decoder)

if __name__ == '__main__':
	tb =rds_rx_graph()
	try:
		tb.run()
	except KeyboardInterrupt:
		pass
