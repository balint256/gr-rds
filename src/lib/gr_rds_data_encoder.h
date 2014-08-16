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

#include <gnuradio/sync_block.h>
#include <string.h>
#include <vector>
#include <iostream>
/* adds dependency: libxml2-dev */
#include <libxml/parser.h>
#include <libxml/tree.h>
#include <libxml/xmlmemory.h>

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
/*!
 * \ingroup RDS
 */
gr_rds_data_encoder_sptr gr_rds_make_data_encoder (const char *xmlfile);

class gr_rds_data_encoder : public gr::sync_block
{
private:
	unsigned int infoword[4];
	unsigned int checkword[4];
	unsigned int block[4];
	unsigned char **buffer;

// FIXME make this a struct (or a class)
	unsigned int PI;
	bool TP;
	unsigned char PTY;
	bool TA;
	bool MuSp;
	bool MS;
	bool AH;
	bool compressed;
	bool static_pty;
	double AF1;
	double AF2;
	char PS[8];
	unsigned char radiotext[64];
	int DP;
	int extent;
	int event;
	int location;

/* each type 0 group contains 2 out of 8 PS characters;
 * this is used to count 0..3 and send all PS characters */
	int d_g0_counter;
/* each type 2A group contains 4 out of 64 RadioText characters;
 * each type 2B group contains 2 out of 32 RadioText characters;
 * this is used to count 0..15 and send all RadioText characters */
	int d_g2_counter;
/* points to the current buffer being prepared/streamed
 * used in create_group() and in work() */
	int d_current_buffer;
/* loops through the buffer, pushing out the symbols */
	int d_buffer_bit_counter;
/* 0..16+A/B = 32 groups. 0A is groups[0], 0B is groups[16]. use %16.
 * ==0 means group not present, ==1 means group present */
	int ngroups;
	int groups[32];
/* nbuffers might be != ngroups, e.g. group 0A needs 4 buffers */
	int nbuffers;

// Functions
	friend gr_rds_data_encoder_sptr gr_rds_make_data_encoder (const char*);
	gr_rds_data_encoder (const char*);	// private constructor
	int read_xml(const char*);
	void print_element_names(xmlNode*);
	void assign_from_xml(const char*, const char*, const int);
	void reset_rds_data();
	void count_groups();
	void create_group(const int, const bool);
	void prepare_group0(const bool);
	void prepare_group2(const bool);
	void prepare_group4a();
	void prepare_group8a();
	void prepare_buffer(int);
	unsigned int encode_af(double);
	unsigned int calc_syndrome(unsigned long, unsigned char);

public:
	~gr_rds_data_encoder();		// public destructor
	int work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items);
};

#endif /* INCLUDED_gr_rds_data_encoder_H */
