#!/usr/bin/env python

" This code is for testing Tx/Rx without a USRP (via loopback) "

from gnuradio import gr, rds, blks2, audio, optfir
import math

class rds_txrx(gr.top_block):
	def __init__(self):
		gr.top_block.__init__ (self)

		usrp_rate=128e3
		wavfile='/home/azimout/limmenso_stereo.wav'
		xmlfile='/home/azimout/sandbox/gr/rds_data.xml'

		self.src = gr.wavfile_source(wavfile, True)
		nchans = self.src.channels()
		sample_rate = self.src.sample_rate()
		bits_per_sample = self.src.bits_per_sample()
		print nchans, "channels,", sample_rate, "samples/sec,", bits_per_sample, "bits/sample"

		# resample from 44.1kS/s to 256kS/s
		self.resample_left = blks2.rational_resampler_fff(2560,441)
		self.resample_right = blks2.rational_resampler_fff(2560,441)
		self.connect ((self.src, 0), self.resample_left)
		self.connect ((self.src, 1), self.resample_right)

		# create L+R (mono) and L-R (stereo)
		self.audio_lpr = gr.add_ff()
		self.audio_lmr = gr.sub_ff()
		self.connect (self.resample_left, (self.audio_lpr, 0))
		self.connect (self.resample_left, (self.audio_lmr, 0))
		self.connect (self.resample_right, (self.audio_lpr, 1))
		self.connect (self.resample_right, (self.audio_lmr, 1))

		# low-pass filter for L+R
		audio_lpr_taps = gr.firdes.low_pass (1,			# gain
						usrp_rate,	# sampling rate
						15e3,			# passband cutoff
						2e3,			# transition width
						gr.firdes.WIN_HANN)
		self.audio_lpr_filter = gr.fir_filter_fff (1, audio_lpr_taps)
		self.preemph_lpr = blks2.fm_preemph(usrp_rate, tau=50e-6)
		self.connect (self.audio_lpr, self.audio_lpr_filter, self.preemph_lpr)

		# create pilot tone at 19 kHz
		self.pilot = gr.sig_source_f(usrp_rate,		# sampling freq
						gr.GR_SIN_WAVE,		# waveform
						19e3,			# frequency
						3e-2)			# amplitude

		# create the L-R signal carrier at 38 kHz, high-pass to remove 0Hz tone
		self.stereo_carrier = gr.multiply_ff()
		self.connect (self.pilot, (self.stereo_carrier, 0))
		self.connect (self.pilot, (self.stereo_carrier, 1))
		stereo_carrier_taps = gr.firdes.high_pass (1,		# gain
						usrp_rate,		# sampling rate
						1e4,			# cutoff freq
						2e3,			# transition width
						gr.firdes.WIN_HANN)
		self.stereo_carrier_filter = gr.fir_filter_fff(1, stereo_carrier_taps)
		self.connect (self.stereo_carrier, self.stereo_carrier_filter)

		# upconvert L-R to 23-53 kHz and band-pass
		self.mix_stereo = gr.multiply_ff()
		audio_lmr_taps = gr.firdes.band_pass (1e2,		# gain
						usrp_rate,		# sampling rate
						23e3,			# low cutoff
						53e3,			# high cutoff
						2e3,			# transition width
						gr.firdes.WIN_HANN)
		self.audio_lmr_filter = gr.fir_filter_fff (1, audio_lmr_taps)
		self.preemph_lmr = blks2.fm_preemph(usrp_rate, tau=50e-6)
		self.connect (self.audio_lmr, (self.mix_stereo, 0))
		self.connect (self.stereo_carrier_filter, (self.mix_stereo, 1))
		self.connect (self.mix_stereo, self.audio_lmr_filter, self.preemph_lmr)

		# rds_encoder, diff_encoder, NRZ
		self.rds_encoder = rds.data_encoder(xmlfile)
		self.diff_encoder = gr.diff_encoder_bb(2)
		self.c2s = gr.chunks_to_symbols_bf([1, -1])
		self.connect (self.rds_encoder, self.diff_encoder, self.c2s)

		# resample from 1187.5Hz (=19e3/16) to usrp_rate,
		# band-pass to remove harmonics
		self.resample = blks2.rational_resampler_fff(int(usrp_rate*16/1e3), 19)
		rds_data_taps = gr.firdes.band_pass (1,			# gain
						usrp_rate,		# sampling rate
						1e3,			# low cutoff
						2e3,			# high cutoff
						2e2,			# transition width
						gr.firdes.WIN_HANN)
		self.rds_data_filter = gr.fir_filter_fff (1, rds_data_taps)
		self.connect (self.c2s, self.resample, self.rds_data_filter)

		# mutliply NRZ with 57kHz RDS carrier (equivalent to BPSK)
		self.bpsk_mod = gr.multiply_ff()
		self.connect (self.rds_data_filter, (self.bpsk_mod, 0))
		self.connect (self.pilot, (self.bpsk_mod, 1))
		self.connect (self.pilot, (self.bpsk_mod, 2))
		self.connect (self.pilot, (self.bpsk_mod, 3))

		# RDS band-pass filter
		rds_filter_taps = gr.firdes.band_pass (	1e5,		# gain
						usrp_rate,		# sampling rate
						55e3,			# low cutoff
						59e3,			# high cutoff
						3e3,			# transition width
						gr.firdes.WIN_HANN)
		self.rds_filter = gr.fir_filter_fff (1, rds_filter_taps)
		self.connect (self.bpsk_mod, self.rds_filter)

		# mix L+R, pilot, L-R and RDS
		self.mixer = gr.add_ff()
		self.connect (self.preemph_lpr, (self.mixer, 0))
		self.connect (self.pilot, (self.mixer, 1))
		self.connect (self.preemph_lmr, (self.mixer, 2))
		self.connect (self.rds_filter, (self.mixer, 3))

		# fm modulation, gain & TX
		max_dev = 120e3
		k = 2 * math.pi * max_dev / usrp_rate		# modulator sensitivity
		self.modulator = gr.frequency_modulator_fc (k)
		self.gain = gr.multiply_const_cc (1e3)
		self.connect (self.mixer, self.modulator, self.gain)

		self.u = gr.kludge_copy(gr.sizeof_gr_complex)
		self.connect (self.gain, self.u)





############## END TRANSMIT, START RECEIVE ###########################

		# channel filter, wfm_rcv_pll
		chan_filt_coeffs = optfir.low_pass (1,
						usrp_rate,
						60e3,
						64e3,
						0.1,
						60)
		self.chan_filt = gr.fir_filter_ccf (1, chan_filt_coeffs)
		self.guts = blks2.wfm_rcv_pll (usrp_rate, 1)
		self.connect(self.u, self.chan_filt, self.guts)

		# audio sink
		self.audio_sink = audio.sink(int(usrp_rate), "plughw:0,0", False)
		self.connect ((self.guts, 0), (self.audio_sink, 0))
		self.connect ((self.guts, 1), (self.audio_sink, 1))
#		self.connect (self.guts, self.audio_sink)

		# pilot channel filter (band-pass, 18.5-19.5kHz)
		pilot_filter_coeffs = gr.firdes.band_pass(1, 
						usrp_rate,
						18.5e3,
						19.5e3,
						1e3,
						gr.firdes.WIN_HAMMING)
		self.pilot_filter = gr.fir_filter_fff(1, pilot_filter_coeffs)
		self.connect(self.guts.fm_demod, self.pilot_filter)

		# RDS channel filter (band-pass, 54-60kHz)
		rds_filter_coeffs = gr.firdes.band_pass (1,
						usrp_rate,
						54e3,
						60e3,
						3e3,
						gr.firdes.WIN_HAMMING)
		self.rds_filter = gr.fir_filter_fff (1, rds_filter_coeffs)
		self.connect(self.guts.fm_demod, self.rds_filter)

		# create 57kHz subcarrier from 19kHz pilot, downconvert RDS channel
		self.rds_carrier = gr.multiply_ff()
		self.connect(self.pilot_filter, (self.rds_carrier, 0))
		self.connect(self.pilot_filter, (self.rds_carrier, 1))
		self.connect(self.pilot_filter, (self.rds_carrier, 2))
		self.connect(self.rds_filter, (self.rds_carrier, 3))

		# low-pass the baseband RDS signal at 1.5kHz
		rds_bb_filter_coeffs = gr.firdes.low_pass (1,
						usrp_rate,
						1500,
						2e3,
						gr.firdes.WIN_HAMMING)
		self.rds_bb_filter = gr.fir_filter_fff (1, rds_bb_filter_coeffs)
		self.connect(self.rds_carrier, self.rds_bb_filter)


		# 1187.5bps = 19kHz/16
		self.rds_clock = rds.freq_divider(16)
		#self.rds_clock = gr.fractional_interpolator_ff(0, 1/16.)
		clock_taps = gr.firdes.low_pass (1,	# gain
						usrp_rate,	# sampling rate
						1.2e3,		# passband cutoff
						1.5e3,		# transition width
						gr.firdes.WIN_HANN)
		self.clock_filter = gr.fir_filter_fff (1, clock_taps)
		self.connect(self.pilot_filter, self.rds_clock, self.clock_filter)

		# bpsk_demod, diff_decoder, rds_decoder
		self.bpsk_demod = rds.bpsk_demod(usrp_rate)
		self.differential_decoder = gr.diff_decoder_bb(2)
		self.msgq = gr.msg_queue()
		self.rds_decoder = rds.data_decoder(self.msgq)
		self.connect(self.rds_bb_filter, (self.bpsk_demod, 0))
		self.connect(self.clock_filter, (self.bpsk_demod, 1))
		self.connect(self.bpsk_demod, self.differential_decoder)
		self.connect(self.differential_decoder, self.rds_decoder)


if __name__ == '__main__':
	tb =rds_txrx()
	try:
		tb.run()
	except KeyboardInterrupt:
		pass
