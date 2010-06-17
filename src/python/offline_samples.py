#!/usr/bin/env python
# record samples to a .wav file for replaying offline
from gnuradio import gr, usrp
from usrpm import usrp_dbid
from gnuradio.wxgui import stdgui2

usrp_decim = 250
freq = 91.2e6
dblist = (usrp_dbid.TV_RX, usrp_dbid.TV_RX_REV_2,
		usrp_dbid.TV_RX_REV_3, usrp_dbid.BASIC_RX)

class rds_rx_graph (stdgui2.std_top_block):
	def __init__(self,frame,panel,vbox,argv):
		stdgui2.std_top_block.__init__ (self,frame,panel,vbox,argv)
		
		self.u = usrp.source_c(0, usrp_decim)
		print "USRP Serial: ", self.u.serial_number()
		usrp_rate = self.u.adc_rate() / usrp_decim		# 256 kS/s
		rx_subdev_spec = usrp.pick_subdev(self.u, dblist)
		self.u.set_mux(usrp.determine_rx_mux_value(self.u, rx_subdev_spec))
		self.subdev = usrp.selected_subdev(self.u, rx_subdev_spec)
		print "Using d'board", self.subdev.side_and_name()
		r = usrp.tune(self.u, 0, self.subdev, freq)
		
		chan_filter_coeffs = gr.firdes.low_pass(
			1.0,			# gain
			usrp_rate,		# sampling rate
			80e3,			# passband cutoff
			35e3,			# transition width
			gr.firdes.WIN_HAMMING)
		self.chan_filter = gr.fir_filter_ccf(1, chan_filter_coeffs)
		print "# channel filter:", len(chan_filter_coeffs), "taps"
		
		self.c2f = gr.complex_to_float(1)
		self.wav_sink = gr.wavfile_sink("/home/sdr/912_samples.wav", 2, usrp_rate, 8)
		
		self.connect(self.u, self.chan_filter, self.c2f)
		self.connect((self.c2f,0), (self.wav_sink,0))
		self.connect((self.c2f,1), (self.wav_sink,1))

if __name__ == '__main__':
	app = stdgui2.stdapp (rds_rx_graph, "USRP RDS RX")
	app.MainLoop ()
