/* -*- c++ -*- */
/*
 * Copyright 2004 Free Software Foundation, Inc.
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


#ifndef INCLUDED_GR_RDS_DATA_ENCODER_H
#define INCLUDED_GR_RDS_DATA_ENCODER_H

#include <rds/api.h>
#include <gnuradio/sync_block.h>
#include <gnuradio/thread/thread.h>
#include <string.h>
#include <vector>
#include <iostream>

namespace gr {
namespace rds {

class RDS_API data_encoder : public gr::sync_block
{
private:
	unsigned int  infoword[4];
	unsigned int  checkword[4];
	unsigned int  block[4];
	unsigned char **buffer;

	// FIXME make this a struct (or a class)
	unsigned char PTY;
	char radiotext[64];
	char PS[8];
	bool TA;
	bool TP;
	bool MS;
	unsigned int PI;
	double AF1;
	double AF2;

	int DP;
	int extent;
	int event;
	int location;
	gr::thread::mutex d_mutex;

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
	int groups[32];
/* nbuffers might be != ngroups, e.g. group 0A needs 4 buffers */
	int nbuffers;

// Functions
	data_encoder ();  // private constructor
	void rebuild();
	void set_ms(bool ms);
	void set_tp(bool tp);
	void set_ta(bool ta);
	void set_af1(double af1);
	void set_af2(double af2);
	void set_pty(unsigned int pty);
	void set_pi(unsigned int pty);
	void set_radiotext(std::string text);
	void set_ps(std::string text);
	void count_groups();
	void create_group(const int, const bool);
	void prepare_group0(const bool);
	void prepare_group2(const bool);
	void prepare_group4a();
	void prepare_group8a();
	void prepare_buffer(int);
	unsigned int encode_af(double);
	unsigned int calc_syndrome(unsigned long, unsigned char);
	void rds_in(pmt::pmt_t msg);
	void assign_value(const char *field, const char *value);

public:
	typedef boost::shared_ptr<data_encoder> sptr;
	static sptr make();
	~data_encoder();  // public destructor
	int work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items);
};

}
}

#endif /* INCLUDED_GR_RDS_DATA_ENCODER_H */
