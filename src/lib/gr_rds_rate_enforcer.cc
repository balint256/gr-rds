/* -*- c++ -*- */
/*
 * Copyright 2004 Free Software Foundation, Inc.
 * 
 * This file is part of GNU Radio
 * 
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 * 
 * GNU Radio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with GNU Radio; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */


/*
 * This block enforces the RDS data rate of 1187.5bps
 * 
 * Input "Data" is an RDS bitstream (1 sample per symbol); Input "Clock"
 * is a 19kHz sampled at the desired sampling rate. The output runs at
 * the Clock's sampling rate carrying the same RDS bitstream ("Data")
 * with a data rate of 1187.5bps.
 * 
 * This is done by pushing the next RDS bit after 32 zero-crossings in the
 * clock.
 */


#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

//#define DEBUG

#ifdef DEBUG
#define DBG(x) x
#else
#define DBG(x)
#endif

#include <gr_rds_rate_enforcer.h>
#include <gnuradio/io_signature.h>
#include <math.h>

gr_rds_rate_enforcer_sptr gr_rds_make_rate_enforcer (double samp_rate) {
	return gr_rds_rate_enforcer_sptr (new gr_rds_rate_enforcer (samp_rate));
}

gr_rds_rate_enforcer::gr_rds_rate_enforcer (double samp_rate)
  : gr::block ("gr_rds_rate_enforcer",
			gr::io_signature::make (2, 2, sizeof(float)),
			gr::io_signature::make (1, 1, sizeof(float)))
{
	set_relative_rate(samp_rate/1187.5);
}

gr_rds_rate_enforcer::~gr_rds_rate_enforcer () {

}

int gr_rds_rate_enforcer::general_work (int noutput_items,
		gr_vector_int &ninput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	const float *data = (const float *) input_items[0];
	const float *clock = (const float *) input_items[1];
	float *out = (float *) output_items[0];
	
	int sign_current=0;
	int current_out=0;
	
	static int symlen=0;		// symbol length
	static int zero_cross=0;	// count zero-crossings
	static int sign_last=(clock[0]>0?1:-1);
	
	for(int i=0; i<noutput_items; i++){
		symlen++;
		sign_current=(clock[i]>0?1:-1);
		if(sign_current!=sign_last){
			if(++zero_cross>15){		// push next bit
				current_out++;
				DBG(printf("%f (len=%i)", data[current_out], symlen);)
				zero_cross=symlen=0;
			}
		}
		out[i]=data[current_out];
		sign_last=sign_current;
	}
	
	consume(0, current_out);
	consume(1, noutput_items);
	return noutput_items;
}
