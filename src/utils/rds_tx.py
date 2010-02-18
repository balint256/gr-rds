#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Rds Tx
# Generated: Thu Feb 18 13:49:16 2010
##################################################

from gnuradio import blks2
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import gr, rds
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.wxgui import fftsink2
from grc_gnuradio import usrp as grc_usrp
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import math
import wx

class rds_tx(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Rds Tx")
		_icon_path = "/home/azimout/.local/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
		self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

		##################################################
		# Variables
		##################################################
		self.usrp_interp = usrp_interp = 500
		self.dac_rate = dac_rate = 128e6
		self.wav_rate = wav_rate = 44100
		self.usrp_rate = usrp_rate = int(dac_rate/usrp_interp)
		self.fm_max_dev = fm_max_dev = 120e3

		##################################################
		# Blocks
		##################################################
		self.band_pass_filter_0 = gr.interp_fir_filter_fff(1, firdes.band_pass(
			1, usrp_rate, 54e3, 60e3, 3e3, firdes.WIN_HAMMING, 6.76))
		self.band_pass_filter_1 = gr.interp_fir_filter_fff(1, firdes.band_pass(
			1, usrp_rate, 23e3, 53e3, 2e3, firdes.WIN_HAMMING, 6.76))
		self.blks2_rational_resampler_xxx_1 = blks2.rational_resampler_fff(
			interpolation=usrp_rate,
			decimation=wav_rate,
			taps=None,
			fractional_bw=None,
		)
		self.blks2_rational_resampler_xxx_1_0 = blks2.rational_resampler_fff(
			interpolation=usrp_rate,
			decimation=wav_rate,
			taps=None,
			fractional_bw=None,
		)
		self.gr_add_xx_0 = gr.add_vff(1)
		self.gr_add_xx_1 = gr.add_vff(1)
		self.gr_char_to_float_0 = gr.char_to_float()
		self.gr_diff_encoder_bb_0 = gr.diff_encoder_bb(2)
		self.gr_frequency_modulator_fc_0 = gr.frequency_modulator_fc(2*math.pi*fm_max_dev/usrp_rate)
		self.gr_map_bb_0 = gr.map_bb(([-1,1]))
		self.gr_map_bb_1 = gr.map_bb(([1,2]))
		self.gr_multiply_xx_0 = gr.multiply_vff(1)
		self.gr_multiply_xx_1 = gr.multiply_vff(1)
		self.gr_rds_data_encoder_0 = rds.data_encoder("/media/dimitris/mywork/gr/dimitris/rds/trunk/src/test/rds_data.xml")
		self.gr_rds_rate_enforcer_0 = rds.rate_enforcer(256000)
		self.gr_sig_source_x_0 = gr.sig_source_f(usrp_rate, gr.GR_COS_WAVE, 19e3, 0.3, 0)
		self.gr_sub_xx_0 = gr.sub_ff(1)
		self.gr_unpack_k_bits_bb_0 = gr.unpack_k_bits_bb(2)
		self.gr_wavfile_source_0 = gr.wavfile_source("/media/dimitris/mywork/gr/dimitris/rds/trunk/src/python/limmenso_stereo.wav", True)
		self.low_pass_filter_0 = gr.interp_fir_filter_fff(1, firdes.low_pass(
			1, usrp_rate, 1.5e3, 2e3, firdes.WIN_HAMMING, 6.76))
		self.low_pass_filter_0_0 = gr.interp_fir_filter_fff(1, firdes.low_pass(
			1, usrp_rate, 15e3, 2e3, firdes.WIN_HAMMING, 6.76))
		self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side="A")
		self.usrp_simple_sink_x_0.set_interp_rate(500)
		self.usrp_simple_sink_x_0.set_frequency(107.2e6, verbose=True)
		self.usrp_simple_sink_x_0.set_gain(0)
		self.usrp_simple_sink_x_0.set_enable(True)
		self.usrp_simple_sink_x_0.set_auto_tr(True)
		self.wxgui_fftsink2_0 = fftsink2.fft_sink_f(
			self.GetWin(),
			baseband_freq=0,
			y_per_div=20,
			y_divs=10,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=usrp_rate,
			fft_size=1024,
			fft_rate=30,
			average=False,
			avg_alpha=None,
			title="FFT Plot",
			peak_hold=False,
		)
		self.Add(self.wxgui_fftsink2_0.win)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_sig_source_x_0, 0), (self.gr_rds_rate_enforcer_0, 1))
		self.connect((self.gr_char_to_float_0, 0), (self.gr_rds_rate_enforcer_0, 0))
		self.connect((self.gr_map_bb_0, 0), (self.gr_char_to_float_0, 0))
		self.connect((self.gr_frequency_modulator_fc_0, 0), (self.usrp_simple_sink_x_0, 0))
		self.connect((self.gr_add_xx_1, 0), (self.gr_frequency_modulator_fc_0, 0))
		self.connect((self.gr_sig_source_x_0, 0), (self.gr_add_xx_1, 1))
		self.connect((self.gr_sub_xx_0, 0), (self.gr_multiply_xx_1, 2))
		self.connect((self.gr_sig_source_x_0, 0), (self.gr_multiply_xx_1, 1))
		self.connect((self.gr_sig_source_x_0, 0), (self.gr_multiply_xx_1, 0))
		self.connect((self.gr_sig_source_x_0, 0), (self.gr_multiply_xx_0, 3))
		self.connect((self.gr_sig_source_x_0, 0), (self.gr_multiply_xx_0, 2))
		self.connect((self.blks2_rational_resampler_xxx_1_0, 0), (self.gr_add_xx_0, 1))
		self.connect((self.blks2_rational_resampler_xxx_1, 0), (self.gr_add_xx_0, 0))
		self.connect((self.blks2_rational_resampler_xxx_1_0, 0), (self.gr_sub_xx_0, 1))
		self.connect((self.blks2_rational_resampler_xxx_1, 0), (self.gr_sub_xx_0, 0))
		self.connect((self.gr_wavfile_source_0, 1), (self.blks2_rational_resampler_xxx_1_0, 0))
		self.connect((self.gr_wavfile_source_0, 0), (self.blks2_rational_resampler_xxx_1, 0))
		self.connect((self.gr_rds_data_encoder_0, 0), (self.gr_diff_encoder_bb_0, 0))
		self.connect((self.gr_diff_encoder_bb_0, 0), (self.gr_map_bb_1, 0))
		self.connect((self.gr_map_bb_1, 0), (self.gr_unpack_k_bits_bb_0, 0))
		self.connect((self.gr_unpack_k_bits_bb_0, 0), (self.gr_map_bb_0, 0))
		self.connect((self.gr_rds_rate_enforcer_0, 0), (self.low_pass_filter_0, 0))
		self.connect((self.low_pass_filter_0, 0), (self.gr_multiply_xx_0, 0))
		self.connect((self.gr_multiply_xx_0, 0), (self.band_pass_filter_0, 0))
		self.connect((self.band_pass_filter_0, 0), (self.gr_add_xx_1, 0))
		self.connect((self.gr_multiply_xx_1, 0), (self.band_pass_filter_1, 0))
		self.connect((self.band_pass_filter_1, 0), (self.gr_add_xx_1, 3))
		self.connect((self.gr_add_xx_1, 0), (self.wxgui_fftsink2_0, 0))
		self.connect((self.gr_sig_source_x_0, 0), (self.gr_multiply_xx_0, 1))
		self.connect((self.gr_add_xx_0, 0), (self.low_pass_filter_0_0, 0))
		self.connect((self.low_pass_filter_0_0, 0), (self.gr_add_xx_1, 2))

	def set_usrp_interp(self, usrp_interp):
		self.usrp_interp = usrp_interp
		self.set_usrp_rate(int(self.dac_rate/self.usrp_interp))

	def set_dac_rate(self, dac_rate):
		self.dac_rate = dac_rate
		self.set_usrp_rate(int(self.dac_rate/self.usrp_interp))

	def set_wav_rate(self, wav_rate):
		self.wav_rate = wav_rate

	def set_usrp_rate(self, usrp_rate):
		self.usrp_rate = usrp_rate
		self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.usrp_rate, 54e3, 60e3, 3e3, firdes.WIN_HAMMING, 6.76))
		self.band_pass_filter_1.set_taps(firdes.band_pass(1, self.usrp_rate, 23e3, 53e3, 2e3, firdes.WIN_HAMMING, 6.76))
		self.gr_sig_source_x_0.set_sampling_freq(self.usrp_rate)
		self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.usrp_rate, 1.5e3, 2e3, firdes.WIN_HAMMING, 6.76))
		self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.usrp_rate, 15e3, 2e3, firdes.WIN_HAMMING, 6.76))
		self.wxgui_fftsink2_0.set_sample_rate(self.usrp_rate)

	def set_fm_max_dev(self, fm_max_dev):
		self.fm_max_dev = fm_max_dev

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = rds_tx()
	tb.Run(True)

