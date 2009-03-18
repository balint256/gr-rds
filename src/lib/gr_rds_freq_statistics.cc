/* -*- c++ -*- */
/*
 * Copyright 2006 Free Software Foundation, Inc.
 * 
 * This file is part of GNU Radio
 * 
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * GNU Radio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with GNU Radio; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_rds_freq_statistics.h>
#include <gr_io_signature.h>
#include <string.h>

gr_rds_freq_statistics_sptr
gr_rds_make_freq_statistics(unsigned int vlen,
			double start_freq,
			double step_freq)
{
	return gr_rds_freq_statistics_sptr(new gr_rds_freq_statistics(vlen,
							start_freq,
							step_freq));
}

gr_rds_freq_statistics::gr_rds_freq_statistics(unsigned int vlen,
				double start_freq,
				double step_freq)
	: gr_sync_block("rds_freq_statistics",
		  gr_make_io_signature(1, 1, sizeof(float) * vlen),
		  gr_make_io_signature(0, 0, 0)),
		d_vlen(vlen), d_start_freq(start_freq), d_step_freq(step_freq)
{
}

gr_rds_freq_statistics::~gr_rds_freq_statistics()
{
}

int gr_rds_freq_statistics::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
{
	const float *input = (const float *) input_items[0];

	unsigned int n=0, i=0;
	float avg=0, thresh=0, freq=0;

	while ((int)n < noutput_items){
		avg=thresh=0;
		for(i=n*d_vlen; i<(n+1)*d_vlen; i++) avg += input[i];
		avg /= d_vlen;
		thresh = 1.2*avg;
//		printf("avg=%.2f, thresh=%.2f\n", avg, thresh);
		for(i=0; i<d_vlen; i++){
			if(input[i]>thresh){
				freq = (d_start_freq+i*d_step_freq)/1000000;
//				printf("%.2fMHz, level=%.0f; ", freq, input[i]);
			}
		}
//		printf("\n");
		n++;
	}

	return noutput_items;
}
