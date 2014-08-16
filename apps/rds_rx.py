#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Stereo FM receiver and RDS Decoder
# Generated: Sat Aug 16 16:29:00 2014
##################################################

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import gr, rds
from gnuradio import uhd
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from gnuradio.wxgui import scopesink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import math
import time
import wx

class rds_rx(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Stereo FM receiver and RDS Decoder")
        _icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.xlate_decim = xlate_decim = 4
        self.samp_rate = samp_rate = 1000000
        self.freq_offset = freq_offset = 250e3
        self.freq = freq = 88.5e6
        self.baseband_rate = baseband_rate = samp_rate/xlate_decim
        self.audio_decim = audio_decim = 4
        self.xlate_bandwidth = xlate_bandwidth = 250e3
        self.volume = volume = 0
        self.loop_bw = loop_bw = 16e3*0 + 18e3*1
        self.gain = gain = 10
        self.freq_tune = freq_tune = freq - freq_offset
        self.audio_rate = audio_rate = 48000
        self.audio_decim_rate = audio_decim_rate = baseband_rate/audio_decim
        self.antenna = antenna = 'TX/RX'

        ##################################################
        # Message Queues
        ##################################################
        gr_rds_data_decoder_0_msgq_out = gr_rds_panel_0_msgq_in = gr.msg_queue(2)

        ##################################################
        # Blocks
        ##################################################
        _volume_sizer = wx.BoxSizer(wx.VERTICAL)
        self._volume_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_volume_sizer,
        	value=self.volume,
        	callback=self.set_volume,
        	label="Volume",
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._volume_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_volume_sizer,
        	value=self.volume,
        	callback=self.set_volume,
        	minimum=-20,
        	maximum=10,
        	num_steps=300,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_volume_sizer)
        self.nb = self.nb = wx.Notebook(self.GetWin(), style=wx.NB_TOP)
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "BB")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "Demod")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "L+R")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "Pilot")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "DSBSC")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "RDS Raw")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "L-R")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "RDS")
        self.Add(self.nb)
        _loop_bw_sizer = wx.BoxSizer(wx.VERTICAL)
        self._loop_bw_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_loop_bw_sizer,
        	value=self.loop_bw,
        	callback=self.set_loop_bw,
        	label="Loop BW",
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._loop_bw_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_loop_bw_sizer,
        	value=self.loop_bw,
        	callback=self.set_loop_bw,
        	minimum=0,
        	maximum=baseband_rate,
        	num_steps=1000,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_loop_bw_sizer)
        _gain_sizer = wx.BoxSizer(wx.VERTICAL)
        self._gain_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_gain_sizer,
        	value=self.gain,
        	callback=self.set_gain,
        	label="Gain",
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._gain_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_gain_sizer,
        	value=self.gain,
        	callback=self.set_gain,
        	minimum=0,
        	maximum=50,
        	num_steps=50,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_gain_sizer)
        self._freq_offset_text_box = forms.text_box(
        	parent=self.GetWin(),
        	value=self.freq_offset,
        	callback=self.set_freq_offset,
        	label="Freq Offset",
        	converter=forms.float_converter(),
        )
        self.Add(self._freq_offset_text_box)
        _freq_sizer = wx.BoxSizer(wx.VERTICAL)
        self._freq_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_freq_sizer,
        	value=self.freq,
        	callback=self.set_freq,
        	label="Freq",
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._freq_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_freq_sizer,
        	value=self.freq,
        	callback=self.set_freq,
        	minimum=87.5e6,
        	maximum=108e6,
        	num_steps=205,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_freq_sizer)
        self._antenna_chooser = forms.drop_down(
        	parent=self.GetWin(),
        	value=self.antenna,
        	callback=self.set_antenna,
        	label="Antenna",
        	choices=['TX/RX', 'RX2'],
        	labels=[],
        )
        self.Add(self._antenna_chooser)
        self.wxgui_scopesink2_0 = scopesink2.scope_sink_f(
        	self.nb.GetPage(3).GetWin(),
        	title="Pilot",
        	sample_rate=baseband_rate,
        	v_scale=0,
        	v_offset=0,
        	t_scale=0,
        	ac_couple=False,
        	xy_mode=False,
        	num_inputs=1,
        	trig_mode=wxgui.TRIG_MODE_AUTO,
        	y_axis_label="Counts",
        )
        self.nb.GetPage(3).Add(self.wxgui_scopesink2_0.win)
        self.wxgui_fftsink2_0_0_0_1_0_1 = fftsink2.fft_sink_f(
        	self.nb.GetPage(7).GetWin(),
        	baseband_freq=0,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=-50,
        	ref_scale=2.0,
        	sample_rate=baseband_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title="RDS",
        	peak_hold=False,
        )
        self.nb.GetPage(7).Add(self.wxgui_fftsink2_0_0_0_1_0_1.win)
        self.wxgui_fftsink2_0_0_0_1_0_0 = fftsink2.fft_sink_f(
        	self.nb.GetPage(6).GetWin(),
        	baseband_freq=0,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=-50,
        	ref_scale=2.0,
        	sample_rate=baseband_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title="L-R",
        	peak_hold=False,
        )
        self.nb.GetPage(6).Add(self.wxgui_fftsink2_0_0_0_1_0_0.win)
        self.wxgui_fftsink2_0_0_0_1_0 = fftsink2.fft_sink_f(
        	self.nb.GetPage(5).GetWin(),
        	baseband_freq=0,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=baseband_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title="RDS",
        	peak_hold=False,
        )
        self.nb.GetPage(5).Add(self.wxgui_fftsink2_0_0_0_1_0.win)
        self.wxgui_fftsink2_0_0_0_1 = fftsink2.fft_sink_f(
        	self.nb.GetPage(4).GetWin(),
        	baseband_freq=0,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=baseband_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title="DSBSC Sub-carrier",
        	peak_hold=False,
        )
        self.nb.GetPage(4).Add(self.wxgui_fftsink2_0_0_0_1.win)
        self.wxgui_fftsink2_0_0_0 = fftsink2.fft_sink_f(
        	self.nb.GetPage(2).GetWin(),
        	baseband_freq=0,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=audio_decim_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title="L+R",
        	peak_hold=False,
        )
        self.nb.GetPage(2).Add(self.wxgui_fftsink2_0_0_0.win)
        self.wxgui_fftsink2_0_0 = fftsink2.fft_sink_f(
        	self.nb.GetPage(1).GetWin(),
        	baseband_freq=0,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=baseband_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=True,
        	avg_alpha=0.8,
        	title="FM Demod",
        	peak_hold=False,
        )
        self.nb.GetPage(1).Add(self.wxgui_fftsink2_0_0.win)
        self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
        	self.nb.GetPage(0).GetWin(),
        	baseband_freq=0,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=-30,
        	ref_scale=2.0,
        	sample_rate=baseband_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=True,
        	avg_alpha=0.8,
        	title="Baseband",
        	peak_hold=False,
        )
        self.nb.GetPage(0).Add(self.wxgui_fftsink2_0.win)
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(freq_tune, 0)
        self.uhd_usrp_source_0.set_gain(gain, 0)
        self.uhd_usrp_source_0.set_antenna(antenna, 0)
        self.rational_resampler_xxx_1 = filter.rational_resampler_fff(
                interpolation=audio_rate,
                decimation=audio_decim_rate,
                taps=None,
                fractional_bw=None,
        )
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=audio_rate,
                decimation=audio_decim_rate,
                taps=None,
                fractional_bw=None,
        )
        self.gr_rds_panel_0 = rds.rdsPanel(gr_rds_panel_0_msgq_in, freq, self.GetWin())
        self.Add(self.gr_rds_panel_0)
        self.gr_rds_freq_divider_0 = rds.freq_divider(16)
        self.gr_rds_data_decoder_0 = rds.data_decoder(gr_rds_data_decoder_0_msgq_out)
        self.gr_rds_bpsk_demod_0 = rds.bpsk_demod(audio_decim_rate)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(xlate_decim, (firdes.low_pass(1, samp_rate, xlate_bandwidth/2, 1000)), freq_offset, samp_rate)
        self.fir_filter_xxx_7 = filter.fir_filter_fff(audio_decim, (firdes.low_pass(1,baseband_rate,1.2e3,1.5e3,firdes.WIN_HAMMING)))
        self.fir_filter_xxx_7.declare_sample_delay(0)
        self.fir_filter_xxx_6 = filter.fir_filter_fff(audio_decim, (firdes.low_pass(1,baseband_rate,1.5e3,2e3,firdes.WIN_HAMMING)))
        self.fir_filter_xxx_6.declare_sample_delay(0)
        self.fir_filter_xxx_5 = filter.fir_filter_fff(audio_decim, (firdes.low_pass(1.0,baseband_rate,15e3,1e3,firdes.WIN_HAMMING)))
        self.fir_filter_xxx_5.declare_sample_delay(0)
        self.fir_filter_xxx_4 = filter.fir_filter_fff(1, (firdes.band_pass(1.0,baseband_rate,57e3-3e3,57e3+3e3,3e3,firdes.WIN_HAMMING)))
        self.fir_filter_xxx_4.declare_sample_delay(0)
        self.fir_filter_xxx_3 = filter.fir_filter_fff(1, (firdes.band_pass(1.0,baseband_rate,38e3-15e3/2,38e3+15e3/2,1e3,firdes.WIN_HAMMING)))
        self.fir_filter_xxx_3.declare_sample_delay(0)
        self.fir_filter_xxx_2 = filter.fir_filter_fff(1, (firdes.band_pass(1.0,baseband_rate,19e3-500,19e3+500,1e3,firdes.WIN_HAMMING)))
        self.fir_filter_xxx_2.declare_sample_delay(0)
        self.fir_filter_xxx_1 = filter.fir_filter_fff(audio_decim, (firdes.low_pass(1.0,baseband_rate,15e3,1e3,firdes.WIN_HAMMING)))
        self.fir_filter_xxx_1.declare_sample_delay(0)
        self.fir_filter_xxx_0 = filter.fir_filter_ccc(1, (firdes.low_pass(1.0, baseband_rate, 80e3,35e3,firdes.WIN_HAMMING)))
        self.fir_filter_xxx_0.declare_sample_delay(0)
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vff(1)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_vff((10**(1.*volume/10), ))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((10**(1.*volume/10), ))
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.audio_sink_0 = audio.sink(audio_rate, "", True)
        self.analog_pll_freqdet_cf_0 = analog.pll_freqdet_cf(1.0*0 + (loop_bw*2*math.pi/baseband_rate), +(2.0 * math.pi * 90e3 / baseband_rate), -(2.0 * math.pi * 90e3 / baseband_rate))
        self.analog_fm_deemph_1 = analog.fm_deemph(fs=baseband_rate, tau=75e-6)
        self.analog_fm_deemph_0 = analog.fm_deemph(fs=baseband_rate, tau=75e-6)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.uhd_usrp_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.fir_filter_xxx_2, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.fir_filter_xxx_2, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.fir_filter_xxx_2, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.fir_filter_xxx_2, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.fir_filter_xxx_3, 0), (self.blocks_multiply_xx_0, 2))
        self.connect((self.fir_filter_xxx_4, 0), (self.blocks_multiply_xx_0_0, 3))
        self.connect((self.fir_filter_xxx_2, 0), (self.blocks_multiply_xx_0_0, 2))
        self.connect((self.fir_filter_xxx_1, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.fir_filter_xxx_2, 0), (self.gr_rds_freq_divider_0, 0))
        self.connect((self.fir_filter_xxx_1, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.fir_filter_xxx_5, 0))
        self.connect((self.gr_rds_freq_divider_0, 0), (self.fir_filter_xxx_7, 0))
        self.connect((self.fir_filter_xxx_7, 0), (self.gr_rds_bpsk_demod_0, 1))
        self.connect((self.digital_diff_decoder_bb_0, 0), (self.gr_rds_data_decoder_0, 0))
        self.connect((self.gr_rds_bpsk_demod_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.fir_filter_xxx_6, 0), (self.gr_rds_bpsk_demod_0, 0))
        self.connect((self.fir_filter_xxx_2, 0), (self.wxgui_scopesink2_0, 0))
        self.connect((self.fir_filter_xxx_1, 0), (self.wxgui_fftsink2_0_0_0, 0))
        self.connect((self.fir_filter_xxx_3, 0), (self.wxgui_fftsink2_0_0_0_1, 0))
        self.connect((self.fir_filter_xxx_4, 0), (self.wxgui_fftsink2_0_0_0_1_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.fir_filter_xxx_6, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.wxgui_fftsink2_0_0_0_1_0_0, 0))
        self.connect((self.fir_filter_xxx_5, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.fir_filter_xxx_5, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.fir_filter_xxx_0, 0), (self.analog_pll_freqdet_cf_0, 0))
        self.connect((self.analog_pll_freqdet_cf_0, 0), (self.wxgui_fftsink2_0_0, 0))
        self.connect((self.analog_pll_freqdet_cf_0, 0), (self.fir_filter_xxx_1, 0))
        self.connect((self.analog_pll_freqdet_cf_0, 0), (self.fir_filter_xxx_2, 0))
        self.connect((self.analog_pll_freqdet_cf_0, 0), (self.fir_filter_xxx_4, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.analog_fm_deemph_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.wxgui_fftsink2_0_0_0_1_0_1, 0))
        self.connect((self.analog_fm_deemph_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.audio_sink_0, 1))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.analog_fm_deemph_1, 0))
        self.connect((self.analog_fm_deemph_1, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.wxgui_fftsink2_0, 0))
        self.connect((self.analog_pll_freqdet_cf_0, 0), (self.fir_filter_xxx_3, 0))



    def get_xlate_decim(self):
        return self.xlate_decim

    def set_xlate_decim(self, xlate_decim):
        self.xlate_decim = xlate_decim
        self.set_baseband_rate(self.samp_rate/self.xlate_decim)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_baseband_rate(self.samp_rate/self.xlate_decim)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.low_pass(1, self.samp_rate, self.xlate_bandwidth/2, 1000)))

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.set_freq_tune(self.freq - self.freq_offset)
        self._freq_offset_text_box.set_value(self.freq_offset)
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.freq_offset)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.set_freq_tune(self.freq - self.freq_offset)
        self._freq_slider.set_value(self.freq)
        self._freq_text_box.set_value(self.freq)
        self.gr_rds_data_decoder_0.reset();self.freq;
        self.gr_rds_panel_0.clear_data();self.freq;
        self.gr_rds_panel_0.set_frequency(self.freq);
        self.gr_rds_bpsk_demod_0.reset();self.freq;

    def get_baseband_rate(self):
        return self.baseband_rate

    def set_baseband_rate(self, baseband_rate):
        self.baseband_rate = baseband_rate
        self.set_audio_decim_rate(self.baseband_rate/self.audio_decim)
        self.wxgui_fftsink2_0.set_sample_rate(self.baseband_rate)
        self.fir_filter_xxx_5.set_taps((firdes.low_pass(1.0,self.baseband_rate,15e3,1e3,firdes.WIN_HAMMING)))
        self.fir_filter_xxx_6.set_taps((firdes.low_pass(1,self.baseband_rate,1.5e3,2e3,firdes.WIN_HAMMING)))
        self.fir_filter_xxx_7.set_taps((firdes.low_pass(1,self.baseband_rate,1.2e3,1.5e3,firdes.WIN_HAMMING)))
        self.wxgui_scopesink2_0.set_sample_rate(self.baseband_rate)
        self.wxgui_fftsink2_0_0_0_1_0.set_sample_rate(self.baseband_rate)
        self.wxgui_fftsink2_0_0_0_1_0_1.set_sample_rate(self.baseband_rate)
        self.wxgui_fftsink2_0_0_0_1_0_0.set_sample_rate(self.baseband_rate)
        self.wxgui_fftsink2_0_0_0_1.set_sample_rate(self.baseband_rate)
        self.fir_filter_xxx_0.set_taps((firdes.low_pass(1.0, self.baseband_rate, 80e3,35e3,firdes.WIN_HAMMING)))
        self.wxgui_fftsink2_0_0.set_sample_rate(self.baseband_rate)
        self.fir_filter_xxx_1.set_taps((firdes.low_pass(1.0,self.baseband_rate,15e3,1e3,firdes.WIN_HAMMING)))
        self.fir_filter_xxx_2.set_taps((firdes.band_pass(1.0,self.baseband_rate,19e3-500,19e3+500,1e3,firdes.WIN_HAMMING)))
        self.fir_filter_xxx_3.set_taps((firdes.band_pass(1.0,self.baseband_rate,38e3-15e3/2,38e3+15e3/2,1e3,firdes.WIN_HAMMING)))
        self.analog_pll_freqdet_cf_0.set_loop_bandwidth(1.0*0 + (self.loop_bw*2*math.pi/self.baseband_rate))
        self.analog_pll_freqdet_cf_0.set_max_freq(+(2.0 * math.pi * 90e3 / self.baseband_rate))
        self.analog_pll_freqdet_cf_0.set_min_freq(-(2.0 * math.pi * 90e3 / self.baseband_rate))
        self.fir_filter_xxx_4.set_taps((firdes.band_pass(1.0,self.baseband_rate,57e3-3e3,57e3+3e3,3e3,firdes.WIN_HAMMING)))

    def get_audio_decim(self):
        return self.audio_decim

    def set_audio_decim(self, audio_decim):
        self.audio_decim = audio_decim
        self.set_audio_decim_rate(self.baseband_rate/self.audio_decim)

    def get_xlate_bandwidth(self):
        return self.xlate_bandwidth

    def set_xlate_bandwidth(self, xlate_bandwidth):
        self.xlate_bandwidth = xlate_bandwidth
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.low_pass(1, self.samp_rate, self.xlate_bandwidth/2, 1000)))

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self._volume_slider.set_value(self.volume)
        self._volume_text_box.set_value(self.volume)
        self.blocks_multiply_const_vxx_0.set_k((10**(1.*self.volume/10), ))
        self.blocks_multiply_const_vxx_1.set_k((10**(1.*self.volume/10), ))

    def get_loop_bw(self):
        return self.loop_bw

    def set_loop_bw(self, loop_bw):
        self.loop_bw = loop_bw
        self.analog_pll_freqdet_cf_0.set_loop_bandwidth(1.0*0 + (self.loop_bw*2*math.pi/self.baseband_rate))
        self._loop_bw_slider.set_value(self.loop_bw)
        self._loop_bw_text_box.set_value(self.loop_bw)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self._gain_slider.set_value(self.gain)
        self._gain_text_box.set_value(self.gain)
        self.uhd_usrp_source_0.set_gain(self.gain, 0)

    def get_freq_tune(self):
        return self.freq_tune

    def set_freq_tune(self, freq_tune):
        self.freq_tune = freq_tune
        self.uhd_usrp_source_0.set_center_freq(self.freq_tune, 0)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate

    def get_audio_decim_rate(self):
        return self.audio_decim_rate

    def set_audio_decim_rate(self, audio_decim_rate):
        self.audio_decim_rate = audio_decim_rate
        self.wxgui_fftsink2_0_0_0.set_sample_rate(self.audio_decim_rate)

    def get_antenna(self):
        return self.antenna

    def set_antenna(self, antenna):
        self.antenna = antenna
        self._antenna_chooser.set_value(self.antenna)
        self.uhd_usrp_source_0.set_antenna(self.antenna, 0)

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = rds_rx()
    tb.Start(True)
    tb.Wait()
