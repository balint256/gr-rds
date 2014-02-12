#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Create Vector
# Generated: Thu Feb 18 14:30:05 2010
##################################################

from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import gr, rds
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from optparse import OptionParser

class create_vector(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "Create Vector")

		##################################################
		# Blocks
		##################################################
		self.gr_file_sink_0 = gr.file_sink(gr.sizeof_char*1, "/media/dimitris/mywork/gr/dimitris/rds/trunk/src/utils/rds_vector.dat")
		self.gr_head_0 = gr.head(gr.sizeof_char*1, 13)
		self.gr_rds_data_encoder_0 = rds.data_encoder("/media/dimitris/mywork/gr/dimitris/rds/trunk/src/utils/rds_data.xml")
		self.gr_unpacked_to_packed_xx_0 = gr.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_unpacked_to_packed_xx_0, 0), (self.gr_head_0, 0))
		self.connect((self.gr_head_0, 0), (self.gr_file_sink_0, 0))
		self.connect((self.gr_rds_data_encoder_0, 0), (self.gr_unpacked_to_packed_xx_0, 0))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = create_vector()
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

