#!/usr/bin/env python
# record samples to a .wav file for replaying offline
from gnuradio import gr, usrp
from usrpm import usrp_dbid
import sys

usrp_decim = 250
freq = 102.2e6
dblist = (usrp_dbid.TV_RX, usrp_dbid.TV_RX_REV_2, usrp_dbid.TV_RX_REV_3, usrp_dbid.BASIC_RX)

class rds_rx_graph (gr.top_block):
	def __init__(self):
		gr.top_block.__init__ (self)
		
		self.u = usrp.source_c(0, usrp_decim)
		print "USRP Serial: ", self.u.serial_number()
		usrp_rate = self.u.adc_rate() / usrp_decim		# 256 kS/s
		rx_subdev_spec = usrp.pick_subdev(self.u, dblist)
		self.u.set_mux(usrp.determine_rx_mux_value(self.u, rx_subdev_spec))
		self.subdev = usrp.selected_subdev(self.u, rx_subdev_spec)
		print "Using d'board", self.subdev.side_and_name()
		
		self.gain = self.subdev.gain_range()[1]
		self.subdev.set_gain(self.gain)
		r = usrp.tune(self.u, 0, self.subdev, freq)
		if r:
			print "Freq: ", freq/1e6, "MHz"
		else:
			print "Failed to set frequency, quitting!"
			sys.exit(1)
		
		chan_filter_coeffs = gr.firdes.low_pass(
			1.0,			# gain
			usrp_rate,		# sampling rate
			80e3,			# passband cutoff
			35e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.chan_filter = gr.fir_filter_ccf(1, chan_filter_coeffs)
		print "# channel filter:", len(chan_filter_coeffs), "taps"
		
		self.file_sink = gr.file_sink(gr.sizeof_gr_complex*1, "/home/azimout/rds_samples.dat")
		
		self.connect(self.u, self.chan_filter, self.file_sink)

if __name__ == '__main__':
	tb =rds_rx_graph()
	try:
		tb.run()
	except KeyboardInterrupt:
		pass
