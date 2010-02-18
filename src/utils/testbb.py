#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Testbb
# Generated: Thu Feb 18 17:20:30 2010
##################################################

from gnuradio import audio
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import gr, rds
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from optparse import OptionParser

class testbb(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "Testbb")

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 32000

		##################################################
		# Blocks
		##################################################
		self.audio_source_0_0 = audio.source(16000, "plughw:0,0", True)
		self.gr_add_xx_0_0 = gr.add_vff(1)
		self.gr_char_to_float_1 = gr.char_to_float()
		self.gr_null_sink_0_0 = gr.null_sink(gr.sizeof_float*1)
		self.gr_rds_data_decoder_0_0 = rds.data_decoder(gr.msg_queue())
		self.gr_rds_data_encoder_1 = rds.data_encoder("/media/dimitris/mywork/gr/dimitris/rds/trunk/src/utils/rds_data.xml")

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_rds_data_encoder_1, 0), (self.gr_char_to_float_1, 0))
		self.connect((self.gr_rds_data_encoder_1, 0), (self.gr_rds_data_decoder_0_0, 0))
		self.connect((self.gr_add_xx_0_0, 0), (self.gr_null_sink_0_0, 0))
		self.connect((self.gr_char_to_float_1, 0), (self.gr_add_xx_0_0, 0))
		self.connect((self.audio_source_0_0, 0), (self.gr_add_xx_0_0, 1))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = testbb()
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

