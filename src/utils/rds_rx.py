#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Rds Rx
# Generated: Thu Feb 18 13:51:40 2010
##################################################

from gnuradio import audio
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import gr, rds
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from grc_gnuradio import usrp as grc_usrp
from optparse import OptionParser

class rds_rx(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "Rds Rx")

		##################################################
		# Variables
		##################################################
		self.usrp_rate = usrp_rate = 256000
		self.audio_decim = audio_decim = 8
		self.volume = volume = 0.1
		self.audio_rate = audio_rate = usrp_rate/audio_decim

		##################################################
		# Blocks
		##################################################
		self.audio_sink_0 = audio.sink(32000, "plughw:0,0", False)
		self.chan_filter = gr.fir_filter_ccf(1, firdes.low_pass(
			1, usrp_rate, 80e3, 35e3, firdes.WIN_HAMMING, 6.76))
		self.gr_diff_decoder_bb_0 = gr.diff_decoder_bb(2)
		self.gr_multiply_xx_0 = gr.multiply_vff(1)
		self.gr_multiply_xx_1 = gr.multiply_vff(1)
		self.gr_pll_freqdet_cf_0 = gr.pll_freqdet_cf(0.767, 0.147, 2.209, -2.209)
		self.gr_rds_bpsk_demod_0 = rds.bpsk_demod(audio_rate)
		self.gr_rds_data_decoder_0 = rds.data_decoder(gr.msg_queue())
		self.gr_rds_freq_divider_0 = rds.freq_divider(16)
		self.left = gr.add_vff(1)
		self.lmr_bb_filter = gr.fir_filter_fff(audio_decim, firdes.low_pass(
			1, usrp_rate, 15e3, 1e3, firdes.WIN_HAMMING, 6.76))
		self.lmr_filter = gr.fir_filter_fff(1, firdes.band_pass(
			1, usrp_rate, 23e3, 53e3, 1e3, firdes.WIN_HAMMING, 6.76))
		self.lpr_filter = gr.fir_filter_fff(audio_decim, firdes.low_pass(
			1, usrp_rate, 15e3, 1e3, firdes.WIN_HAMMING, 6.76))
		self.pilot_filter = gr.fir_filter_fff(1, firdes.band_pass(
			1, usrp_rate, 18.5e3, 19.5e3, 1e3, firdes.WIN_HAMMING, 6.76))
		self.rds_bb_filter = gr.fir_filter_fff(audio_decim, firdes.low_pass(
			1e3, audio_rate, 1.5e3, 2e3, firdes.WIN_HAMMING, 6.76))
		self.rds_clk_filter = gr.fir_filter_fff(audio_decim, firdes.low_pass(
			1, audio_rate, 1.2e3, 1.5e3, firdes.WIN_HAMMING, 6.76))
		self.rds_filter = gr.fir_filter_fff(1, firdes.band_pass(
			1, usrp_rate, 54e3, 60e3, 3e3, firdes.WIN_HAMMING, 6.76))
		self.right = gr.sub_ff(1)
		self.usrp_simple_source_x_0 = grc_usrp.simple_source_c(which=0, side="B", rx_ant="RXA")
		self.usrp_simple_source_x_0.set_decim_rate(250)
		self.usrp_simple_source_x_0.set_frequency(102.2e6, verbose=True)
		self.usrp_simple_source_x_0.set_gain(20)
		self.vol_left = gr.multiply_const_vff((volume, ))
		self.vol_right = gr.multiply_const_vff((volume, ))

		##################################################
		# Connections
		##################################################
		self.connect((self.usrp_simple_source_x_0, 0), (self.chan_filter, 0))
		self.connect((self.chan_filter, 0), (self.gr_pll_freqdet_cf_0, 0))
		self.connect((self.gr_pll_freqdet_cf_0, 0), (self.lmr_filter, 0))
		self.connect((self.gr_pll_freqdet_cf_0, 0), (self.pilot_filter, 0))
		self.connect((self.gr_pll_freqdet_cf_0, 0), (self.rds_filter, 0))
		self.connect((self.pilot_filter, 0), (self.gr_multiply_xx_0, 3))
		self.connect((self.pilot_filter, 0), (self.gr_multiply_xx_0, 2))
		self.connect((self.pilot_filter, 0), (self.gr_multiply_xx_0, 1))
		self.connect((self.rds_filter, 0), (self.gr_multiply_xx_0, 0))
		self.connect((self.gr_multiply_xx_0, 0), (self.rds_bb_filter, 0))
		self.connect((self.pilot_filter, 0), (self.gr_rds_freq_divider_0, 0))
		self.connect((self.gr_rds_freq_divider_0, 0), (self.rds_clk_filter, 0))
		self.connect((self.pilot_filter, 0), (self.gr_multiply_xx_1, 0))
		self.connect((self.pilot_filter, 0), (self.gr_multiply_xx_1, 1))
		self.connect((self.lmr_filter, 0), (self.gr_multiply_xx_1, 2))
		self.connect((self.gr_multiply_xx_1, 0), (self.lmr_bb_filter, 0))
		self.connect((self.left, 0), (self.vol_left, 0))
		self.connect((self.vol_left, 0), (self.audio_sink_0, 1))
		self.connect((self.vol_right, 0), (self.audio_sink_0, 0))
		self.connect((self.right, 0), (self.vol_right, 0))
		self.connect((self.lmr_bb_filter, 0), (self.left, 0))
		self.connect((self.lpr_filter, 0), (self.left, 1))
		self.connect((self.lpr_filter, 0), (self.right, 1))
		self.connect((self.lmr_bb_filter, 0), (self.right, 0))
		self.connect((self.gr_pll_freqdet_cf_0, 0), (self.lpr_filter, 0))
		self.connect((self.gr_diff_decoder_bb_0, 0), (self.gr_rds_data_decoder_0, 0))
		self.connect((self.gr_rds_bpsk_demod_0, 0), (self.gr_diff_decoder_bb_0, 0))
		self.connect((self.rds_clk_filter, 0), (self.gr_rds_bpsk_demod_0, 1))
		self.connect((self.rds_bb_filter, 0), (self.gr_rds_bpsk_demod_0, 0))

	def set_usrp_rate(self, usrp_rate):
		self.usrp_rate = usrp_rate
		self.set_audio_rate(self.usrp_rate/self.audio_decim)
		self.chan_filter.set_taps(firdes.low_pass(1, self.usrp_rate, 80e3, 35e3, firdes.WIN_HAMMING, 6.76))
		self.rds_filter.set_taps(firdes.band_pass(1, self.usrp_rate, 54e3, 60e3, 3e3, firdes.WIN_HAMMING, 6.76))
		self.pilot_filter.set_taps(firdes.band_pass(1, self.usrp_rate, 18.5e3, 19.5e3, 1e3, firdes.WIN_HAMMING, 6.76))
		self.lmr_bb_filter.set_taps(firdes.low_pass(1, self.usrp_rate, 15e3, 1e3, firdes.WIN_HAMMING, 6.76))
		self.lpr_filter.set_taps(firdes.low_pass(1, self.usrp_rate, 15e3, 1e3, firdes.WIN_HAMMING, 6.76))
		self.lmr_filter.set_taps(firdes.band_pass(1, self.usrp_rate, 23e3, 53e3, 1e3, firdes.WIN_HAMMING, 6.76))

	def set_audio_decim(self, audio_decim):
		self.audio_decim = audio_decim
		self.set_audio_rate(self.usrp_rate/self.audio_decim)

	def set_volume(self, volume):
		self.volume = volume
		self.vol_left.set_k((self.volume, ))
		self.vol_right.set_k((self.volume, ))

	def set_audio_rate(self, audio_rate):
		self.audio_rate = audio_rate
		self.rds_bb_filter.set_taps(firdes.low_pass(1e3, self.audio_rate, 1.5e3, 2e3, firdes.WIN_HAMMING, 6.76))
		self.rds_clk_filter.set_taps(firdes.low_pass(1, self.audio_rate, 1.2e3, 1.5e3, firdes.WIN_HAMMING, 6.76))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = rds_rx()
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

