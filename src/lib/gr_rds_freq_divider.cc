/* -*- c++ -*- */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_rds_freq_divider.h>
#include <gr_io_signature.h>

/*
 * Create a new instance of gr_rds_freq_divider and return
 * a boost shared_ptr.  This is effectively the public constructor.
 */
gr_rds_freq_divider_sptr gr_rds_make_freq_divider (int divider)
{
	return gr_rds_freq_divider_sptr (new gr_rds_freq_divider (divider));
}

/*
 * The private constructor
 */
gr_rds_freq_divider::gr_rds_freq_divider (int divider)
	: gr_sync_block ("gr_rds_freq_divider",
		gr_make_io_signature (1, 1, sizeof (float)),
		gr_make_io_signature (1, 1, sizeof (float)))
{
	d_divider = 0;
	DIVIDER = divider;
	d_sign_last = d_sign_current = false;
	d_out = 1;
}

/*
 * Our virtual destructor.
 */
gr_rds_freq_divider::~gr_rds_freq_divider (){
}

int 
gr_rds_freq_divider::work (int noutput_items,
					gr_vector_const_void_star &input_items,
					gr_vector_void_star &output_items)
{
	const float *in = (const float *) input_items[0];
	float *out = (float *) output_items[0];

	for (int i = 0; i < noutput_items; i++){
		d_sign_current = (in[i] > 0 ? true : false);
		if(d_sign_current != d_sign_last) {		// A zero cross
			if(++d_divider ==  DIVIDER) {
				d_out *= -1;
				d_divider = 0;
			}
		}
		out[i] = d_out;
		d_sign_last = d_sign_current;
	}

// Tell runtime system how many output items we produced.
	return noutput_items;
}
