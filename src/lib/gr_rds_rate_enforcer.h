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


#ifndef INCLUDED_gr_rds_rate_enforcer_H
#define INCLUDED_gr_rds_rate_enforcer_H

#include <gnuradio/sync_block.h>
#include <vector>
#include <iostream>

class gr_rds_rate_enforcer;

/*
 * We use boost::shared_ptr's instead of raw pointers for all access
 * to gr_blocks (and many other data structures).  The shared_ptr gets
 * us transparent reference counting, which greatly simplifies storage
 * management issues.  This is especially helpful in our hybrid
 * 
 * * C++ / Python system.
 *
 * See http://www.boost.org/libs/smart_ptr/smart_ptr.htm
 *
 * As a convention, the _sptr suffix indicates a boost::shared_ptr
 */
typedef boost::shared_ptr<gr_rds_rate_enforcer> gr_rds_rate_enforcer_sptr;
/*!
 * \ingroup RDS
 */
gr_rds_rate_enforcer_sptr gr_rds_make_rate_enforcer (double samp_rate);

class gr_rds_rate_enforcer : public gr::block
{
private:
// Functions
	friend gr_rds_rate_enforcer_sptr gr_rds_make_rate_enforcer (double samp_rate);
	gr_rds_rate_enforcer (double samp_rate);	// private constructor

public:
	~gr_rds_rate_enforcer();		// public destructor
	int general_work (int noutput_items,
		gr_vector_int &ninput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items);
};

#endif /* INCLUDED_gr_rds_rate_enforcer_H */
