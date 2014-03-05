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

/*	HSR - MOBKOM LABOR
 *	Semesterarbeit GnuRadio Contributions
 *	U. Schaufelberger and R. Gaensli
 *
 * 	Written by : Ronnie Gaensli
 * 	Created: 2005/05
 * 
 */


#ifndef INCLUDED_gr_rds_bpsk_demod_H
#define INCLUDED_gr_rds_bpsk_demod_H


#include <rds/api.h>
#include <gnuradio/sync_block.h>
#include <iostream>
#include <fstream>

namespace gr {
namespace rds {

/*!
 * \brief Decodes a biphase or manchester coded signal to 1, 0 as bool
 * \ingroup RDS
 */
class RDS_API bpsk_demod : public gr::block
{
private:
	enum state_t { ST_LOOKING, ST_LOCKED };
	state_t d_state;
	int SYMBOL_LENGTH;
	int d_zc;				// Zero crosses in clk
	int d_last_zc;
	int d_sign_last;
	float d_symbol_integrator;
	unsigned int synccounter;

	bpsk_demod (double input_samping_rate);	// private constructor
	void enter_looking();
	void enter_locked();

public:
	typedef boost::shared_ptr<bpsk_demod> sptr;
    static sptr make(double input_samping_rate);

	~bpsk_demod ();
	int general_work (int noutput_items,
		gr_vector_int &ninput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items);
	void reset();
};

}
}

#endif /* INCLUDED_gr_rds_bpsk_demod_H */
