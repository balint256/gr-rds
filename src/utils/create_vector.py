#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Create Vector
# Generated: Thu Feb 18 11:40:42 2010
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
		self.gr_file_source_0 = gr.file_source(gr.sizeof_char*1, "/media/dimitris/mywork/gr/dimitris/rds/trunk/src/utils/rds_vector.dat", True)
		self.gr_packed_to_unpacked_xx_0 = gr.packed_to_unpacked_bb(1, gr.GR_MSB_FIRST)
		self.gr_rds_data_decoder_0 = rds.data_decoder(gr.msg_queue())

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_file_source_0, 0), (self.gr_packed_to_unpacked_xx_0, 0))
		self.connect((self.gr_packed_to_unpacked_xx_0, 0), (self.gr_rds_data_decoder_0, 0))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = create_vector()
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

