#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Testbb
# Generated: Thu Feb 18 11:34:03 2010
##################################################

from gnuradio import audio
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import gr, rds
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx

class testbb(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Testbb")
		_icon_path = "/home/sdr/.local/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
		self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 32000

		##################################################
		# Blocks
		##################################################
		self.audio_source_0_0 = audio.source(32000, "hw:0,0", True)
		self.gr_add_xx_0_0 = gr.add_vff(1)
		self.gr_binary_slicer_fb_1 = gr.binary_slicer_fb()
		self.gr_char_to_float_0 = gr.char_to_float()
		self.gr_char_to_float_1 = gr.char_to_float()
		self.gr_diff_decoder_bb_1 = gr.diff_decoder_bb(2)
		self.gr_diff_encoder_bb_1 = gr.diff_encoder_bb(2)
		self.gr_map_bb_0 = gr.map_bb(([-1,1]))
		self.gr_null_sink_0_0 = gr.null_sink(gr.sizeof_float*1)
		self.gr_rds_data_decoder_0_0 = rds.data_decoder(gr.msg_queue())
		self.gr_rds_data_encoder_1 = rds.data_encoder("/media/dimitris/mywork/gr/dimitris/rds/trunk/src/utils/rds_data.xml")

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_rds_data_encoder_1, 0), (self.gr_diff_encoder_bb_1, 0))
		self.connect((self.gr_char_to_float_0, 0), (self.gr_binary_slicer_fb_1, 0))
		self.connect((self.gr_map_bb_0, 0), (self.gr_char_to_float_0, 0))
		self.connect((self.gr_rds_data_encoder_1, 0), (self.gr_char_to_float_1, 0))
		self.connect((self.gr_add_xx_0_0, 0), (self.gr_null_sink_0_0, 0))
		self.connect((self.gr_char_to_float_1, 0), (self.gr_add_xx_0_0, 1))
		self.connect((self.audio_source_0_0, 0), (self.gr_add_xx_0_0, 0))
		self.connect((self.gr_diff_encoder_bb_1, 0), (self.gr_map_bb_0, 0))
		self.connect((self.gr_diff_decoder_bb_1, 0), (self.gr_rds_data_decoder_0_0, 0))
		self.connect((self.gr_binary_slicer_fb_1, 0), (self.gr_diff_decoder_bb_1, 0))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = testbb()
	tb.Run(True)

