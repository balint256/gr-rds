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


#ifndef INCLUDED_gr_rds_data_encoder_H
#define INCLUDED_gr_rds_data_encoder_H

#include <gr_sync_block.h>
#include <string.h>
#include <vector>
#include <iostream>
/* adds dependency: libxml2-dev */
#include <libxml/parser.h>
#include <libxml/tree.h>

class gr_rds_data_encoder;

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
typedef boost::shared_ptr<gr_rds_data_encoder> gr_rds_data_encoder_sptr;
gr_rds_data_encoder_sptr gr_rds_make_data_encoder (const char *xmlfile);


class gr_rds_data_encoder : public gr_sync_block
{
private:

// Functions
	friend gr_rds_data_encoder_sptr gr_rds_make_data_encoder (const char *xmlfile);
	gr_rds_data_encoder (const char *xmlfile);		// private constructor
	int read_xml(const char *xmlfile);

public:
	~gr_rds_data_encoder();		// public destructor
	int work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items);
};

#endif /* INCLUDED_gr_rds_data_encoder_H */
