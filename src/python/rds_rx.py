#
# Copyright 2005 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
# 

import math
from gnuradio import gr, optfir, rds

"""
RDS (Radio Data System) Receiver.

Takes a single float FM demodulated input stream,(with enough bandwith!),
demodulates the RDS data stream and decodes the contained information.

@param fg: flow graph
@param audio_rate: sample rate of audio stream, >= 120kHz
@type audio_rate: integer


Exported sub-blocks (attributes):
	pilot_filter
	rds_filter
	mixer
	rds_bb_filter
	biphase_decoder
	differential_decoder
	rds_decoder
"""

class rds_rx(gr.hier_block2):
	def __init__(self, fg, audio_rate, msgq):
		gr.hier_block2.__init__(self, "rds_receiver",
				gr.io_signature(1,1,gr.sizeof_float),
				gr.io_signature(0,0,0))

		self.audio_rate = int(audio_rate)

		if audio_rate <= 120e3:
			raise ValueError, "Audio_rate is too small. Needs to be at least 120k!"

#		This is necessary because it's not (yet) possible to connect
#		a hier_block2's input to >1 blocks, as described here:
#		http://www.ruby-forum.com/topic/125660
		# Dummy inpoint block
		self.inpoint = gr.kludge_copy(gr.sizeof_float)

		# Pilot reconstruction filter
		self.pilot_filter_coeffs = gr.firdes_band_pass(1, 
								   audio_rate,
								   18e3, 
								   20e3,
								   3e3,
								   gr.firdes.WIN_HAMMING)
		self.pilot_filter = gr.fir_filter_fff(1, self.pilot_filter_coeffs)

		# Data rate = (3 * 19e3) / 48 = 19e3 / 16
		self.data_clock = rds.freq_divider(16)

		# RDS filter
		self.rds_filter_coeffs = gr.firdes.band_pass (1,
											  audio_rate,
											  54e3,
											  60e3,
											  3e3,
											  gr.firdes.WIN_HAMMING)
		self.rds_filter = gr.fir_filter_fff (1 , self.rds_filter_coeffs)
	
		# Downconversion of RDS signal
		self.mixer = gr.multiply_ff()

		# Data signal filter
		self.rds_bb_filter_coeffs =  gr.firdes.low_pass (5, 	# Gain
								audio_rate, 					# Fs
								1500, 							# Cut off
								2e3, 							# trans. bw
								gr.firdes.WIN_HAMMING)			# window type

		self.rds_bb_filter = gr.fir_filter_fff (1, self.rds_bb_filter_coeffs)

		# Biphase decoder
		self.bpsk_demod = rds.biphase_decoder(audio_rate)

		# Differential decoder
		self.differential_decoder = rds.diff_decoder()

		# RDS data decoder
		self.rds_decoder = rds.data_decoder(msgq)

		# wire the block together
		fg.connect(self, self.inpoint)
		fg.connect(self.inpoint, self.pilot_filter)
		fg.connect(self.inpoint, self.rds_filter)
		fg.connect(self.pilot_filter, (self.mixer, 0))
		fg.connect(self.pilot_filter, (self.mixer, 1))
		fg.connect(self.pilot_filter, (self.mixer, 2))
		fg.connect(self.rds_filter, (self.mixer, 3))
		fg.connect(self.pilot_filter, self.data_clock)
		fg.connect(self.mixer, self.rds_bb_filter)
		fg.connect(self.rds_bb_filter, (self.bpsk_demod, 0))
		fg.connect(self.data_clock, (self.bpsk_demod, 1))
		fg.connect(self.bpsk_demod, self.differential_decoder, self.rds_decoder)
