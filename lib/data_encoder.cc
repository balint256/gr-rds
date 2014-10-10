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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <rds/data_encoder.h>
#include <rds/constants.h>
#include <gnuradio/io_signature.h>
#include <boost/spirit/include/qi.hpp>
#include <math.h>
#include <ctype.h>
#include <time.h>
#include <cstdio>

using namespace gr::rds;

data_encoder::data_encoder ()
	: gr::sync_block ("gr_rds_data_encoder",
			gr::io_signature::make (0, 0, 0),
			gr::io_signature::make (1, 1, sizeof(unsigned char))) {

	message_port_register_in(pmt::mp("rds in"));
	set_msg_handler(pmt::mp("rds in"), boost::bind(&data_encoder::rds_in, this, _1));

	std::memset(infoword,    0, sizeof(infoword));
	std::memset(checkword,   0, sizeof(checkword));
	std::memset(groups,      0, sizeof(groups));
	std::memset(PS,        ' ', sizeof(PS));
	std::memset(radiotext, ' ', sizeof(radiotext));

	nbuffers             = 0;
	d_g0_counter         = 0;
	d_g2_counter         = 0;
	d_current_buffer     = 0;
	d_buffer_bit_counter = 0;

	PI                   = 0x10FF;
	PTY                  = 5;     // programm type (education)
	TP                   = false; // traffic programm
	TA                   = false; // traffic announcement
	MS                   = true;  // music/speech switch (1=music)
	AF1                  = 89.8;
	AF2                  = 102.3;

	set_radiotext(std::string("GNU Radio <3"));
	set_ps(std::string("Arrrrrr!"));

	// which groups are set
	groups[0] = 1; // basic tuning and switching
	groups[2] = 1; // radio text
	groups[4] = 1; // clock time
	groups[8] = 1; // tmc

	// set some default values
	assign_value("DP", "3");
	assign_value("extent", "2");
	assign_value("event", "724");
	assign_value("location", "6126");

	rebuild();
}

data_encoder::~data_encoder() {
	free(buffer);
}

void data_encoder::rebuild() {
	gr::thread::scoped_lock lock(d_mutex);

	count_groups();
	d_current_buffer = 0;

	// allocate memory for nbuffers buffers of 104 unsigned chars each
	buffer = (unsigned char **)malloc(nbuffers * sizeof(unsigned char *));
	for(int i = 0; i < nbuffers; i++) {
		buffer[i] = (unsigned char *)malloc(104 * sizeof(unsigned char));
		for(int j = 0; j < 104; j++) buffer[i][j] = 0;
	}
	//printf("%i buffers allocated\n", nbuffers);

	// prepare each of the groups
	for(int i = 0; i < 32; i++) {
		if(groups[i] == 1) {
			create_group(i % 16, (i < 16) ? false : true);
			if(i % 16 == 0)  // if group is type 0, call 3 more times
				for(int j = 0; j < 3; j++) create_group(i % 16, (i < 16) ? false : true);
			if(i % 16 == 2) // if group type is 2, call 15 more times
				for(int j = 0; j < 15; j++) create_group(i % 16, (i < 16) ? false : true);
		}
	}

	d_current_buffer = 0;
	std::cout << "nbuffers: " << nbuffers << std::endl;
}

void data_encoder::rds_in(pmt::pmt_t msg) {
	if(!pmt::is_pair(msg)) {
		return;
	}

	using std::cout;
	using std::endl;
	using boost::spirit::qi::phrase_parse;
	using boost::spirit::qi::lexeme;
	using boost::spirit::qi::char_;
	using boost::spirit::qi::hex;
	using boost::spirit::qi::int_;
	using boost::spirit::qi::uint_;
	using boost::spirit::qi::bool_;
	using boost::spirit::qi::double_;
	using boost::spirit::qi::space;
	using boost::spirit::qi::blank;
	using boost::spirit::qi::lit;

	int msg_len = pmt::blob_length(pmt::cdr(msg));
	std::string in = std::string((char*)pmt::blob_data(pmt::cdr(msg)), msg_len);
	cout << "input string: " << in << "   length: " << in.size() << endl;

	unsigned int ui1;
	int i1;
	std::string s1;
	bool b1;
	double d1;

	// state
	if(phrase_parse(in.begin(), in.end(),
			"status", space)) {
		cout << "print state" << endl;
		//print_state();

	// pty
	} else if(phrase_parse(in.begin(), in.end(),
			"pty" >> (("0x" >> hex) | uint_), space, ui1)) {
		cout << "set pty: " << ui1 << endl;
		set_pty(ui1);

	// radio text
	} else if(phrase_parse(in.begin(), in.end(),
			"text" >> lexeme[+(char_ - '\n')] >> -lit("\n"),
			space, s1)) {
		cout << "text: " << s1 << endl;
		set_radiotext(s1);

	// ps
	} else if(phrase_parse(in.begin(), in.end(),
			"ps" >> lexeme[+(char_ - '\n')] >> -lit("\n"),
			space, s1)) {
		cout << "ps: " << s1 << endl;
		set_ps(s1);

	// ta
	} else if(phrase_parse(in.begin(), in.end(),
			"ta" >> bool_,
			space, b1)) {
		cout << "ta: " << b1 << endl;
		set_ta(b1);

	// tp
	} else if(phrase_parse(in.begin(), in.end(),
			"tp" >> bool_,
			space, b1)) {
		cout << "tp: " << b1 << endl;
		set_tp(b1);

	// MS
	} else if(phrase_parse(in.begin(), in.end(),
			"ms" >> bool_,
			space, b1)) {
		cout << "ms: " << b1 << endl;
		set_ms(b1);

	// PI
	} else if(phrase_parse(in.begin(), in.end(),
			"pi" >> lit("0x") >> hex, space, ui1)) {
		cout << "set pi: " << ui1 << endl;
		set_pi(ui1);

	// AF1
	} else if(phrase_parse(in.begin(), in.end(),
			"af1" >> double_, space, d1)) {
		cout << "set af1: " << d1 << endl;
		set_af1(d1);

	// AF2
	} else if(phrase_parse(in.begin(), in.end(),
			"af2" >> double_, space, d1)) {
		cout << "set af2: " << d1 << endl;
		set_af2(d1);

	// no match / unkonwn command
	} else {
		cout << "not understood" << endl;
	}

	rebuild();
}

void data_encoder::set_ms(bool ms) {
	MS = ms;
	std::cout << "setting Music/Speech code to " << ms << " (";
	if(ms) std::cout << "music)" << std::endl;
	else std::cout << "speech)" << std::endl;
}

void data_encoder::set_af1(double af1) {
	AF1 = af1;
}

void data_encoder::set_af2(double af2) {
	AF2 = af2;
}

void data_encoder::set_tp(bool tp) {
	TP = tp;
}

void data_encoder::set_ta(bool ta) {
	TA = ta;
}

void data_encoder::set_pty(unsigned int pty) {
	if(pty > 31) {
		std::cout << "warning: ignoring invalid pty: " << std::endl;
	} else {
		PTY = pty;
		std::cout << "setting pty to " << pty << " (" << pty_table[pty] << ")" << std::endl;
	}
}

void data_encoder::set_pi(unsigned int pi) {
	if(pi > 0xFFFF) {
		std::cout << "warning: ignoring invalid pi: " << std::endl;
	} else {
		PI = pi;
		std::cout << "setting pi to " << std::hex << pi << std::endl;
		if(pi & 0xF000)
			std::cout << "    country code " << pi_country_codes[((pi & 0xF000) >> 12) - 1][0] << std::endl;
		else
			std::cout << "    country code 0 (incorrect)" << std::endl;
		std::cout << "    coverage area " << coverage_area_codes[(pi & 0xF00) >> 8] << std::endl;
		std::cout << "    program reference number " << (pi & 0xFF) << std::dec << std::endl;
	}
}


void data_encoder::set_radiotext(std::string text) {
		size_t len = std::min(sizeof(radiotext) - 1, text.length());

		std::memset(radiotext, ' ', sizeof(radiotext));
		std::memcpy(radiotext, text.c_str(), len);
		radiotext[len] = '\0';
}

void data_encoder::set_ps(std::string text) {
		size_t len = std::min(sizeof(PS) - 1, text.length());

		std::memset(radiotext, ' ', sizeof(PS));
		std::memcpy(radiotext, text.c_str(), len);
		radiotext[len] = '\0';
}

void data_encoder::assign_value (const char *field, const char *value) {
	int length = strlen(value);
	if(!strcmp(field, "PI")) {
		if(length!=4) printf("invalid PI string length: %i\n", length);
		else PI=strtol(value, NULL, 16);
	}
	else if(!strcmp(field, "DP"))
		DP=atol(value);
	else if(!strcmp(field, "extent"))
		extent=atol(value);
	else if(!strcmp(field, "event"))
		event=atol(value);
	else if(!strcmp(field, "location"))
		location=atol(value);
	else printf("unrecognized field type: %s\n", field);
}

//////////////////////  CREATE DATA GROUPS  ///////////////////////

/* see Annex B, page 64 of the standard */
unsigned int data_encoder::calc_syndrome(unsigned long message, 
		unsigned char mlen) {

	unsigned long reg = 0;
	unsigned int i;
	const unsigned long poly = 0x5B9;
	const unsigned char plen = 10;

	for (i = mlen; i > 0; i--)  {
		reg = (reg << 1) | ((message >> (i - 1)) & 0x01);
		if (reg & (1 << plen)) reg = reg ^ poly;
	}
	for (i = plen; i > 0; i--) {
		reg = reg << 1;
		if (reg & (1 << plen)) reg = reg ^ poly;
	}
	return reg & ((1 << plen) - 1);
}

/* see page 41 in the standard; this is an implementation of AF method A
 * FIXME need to add code that declares the number of AF to follow... */
unsigned int data_encoder::encode_af(const double af) {
	unsigned int af_code = 0;
	if(( af >= 87.6) && (af <= 107.9))
		af_code = nearbyint((af - 87.5) * 10);
	else if((af >= 153) && (af <= 279))
		af_code = nearbyint((af - 144) / 9);
	else if((af >= 531) && (af <= 1602))
		af_code = nearbyint((af - 531) / 9 + 16);
	else
		printf("invalid alternate frequency: %f\n", af);
	return af_code;
}

/* count and print present groups */
void data_encoder::count_groups(void) {
	int ngroups = 0;
	nbuffers = 0;
	//printf("groups present: ");
	for(int i = 0; i < 32; i++) {
		if(groups[i] == 1) {
			ngroups++;
			//printf("%i%c ", i % 16, (i < 16) ? 'A' : 'B');
			if(i % 16 == 0)  // group 0
				nbuffers += 4;
			else if(i % 16 == 2)  // group 2
				nbuffers += 16;
			else
				nbuffers++;
		}
	}
	//printf("(%i groups)\n", ngroups);
}

/* create the 4 infowords, according to group type.
 * then calculate checkwords and put everything in the groups */
void data_encoder::create_group(const int group_type, const bool AB) {
	
	infoword[0] = PI;
	infoword[1] = (((group_type & 0xf) << 12) | (AB << 11) | (TP << 10) | (PTY << 5));

	if(group_type == 0) prepare_group0(AB);
	else if(group_type == 2) prepare_group2(AB);
	else if(group_type == 4) prepare_group4a();
	else if(group_type == 8) prepare_group8a();
	else printf("preparation of group %i not yet supported\n", group_type);
	//printf("data: %04X %04X %04X %04X, ", infoword[0], infoword[1], infoword[2], infoword[3]);

	for(int i= 0; i < 4; i++) {
		checkword[i]=calc_syndrome(infoword[i], 16);
		block[i] = ((infoword[i] & 0xffff) << 10) | (checkword[i] & 0x3ff);
		// add the offset word
		if((i == 2) && AB) block[2] ^= offset_word[4];
		else block[i] ^= offset_word[i];
	}
	//printf("group: %04X %04X %04X %04X\n", block[0], block[1], block[2], block[3]);

	prepare_buffer(d_current_buffer);
	d_current_buffer++;
}

void data_encoder::prepare_group0(const bool AB) {
	infoword[1] = infoword[1] | (TA << 4) | (MS << 3);
	//FIXME: make DI configurable
	if(d_g0_counter == 3)
		infoword[1] = infoword[1] | 0x5;  // d0=1 (stereo), d1-3=0
	infoword[1] = infoword[1] | (d_g0_counter & 0x3);
	if(!AB)
		infoword[2] = ((encode_af(AF1) & 0xff) << 8) | (encode_af(AF2) & 0xff);
	else
		infoword[2] = PI;
	infoword[3] = (PS[2 * d_g0_counter] << 8) | PS[2 * d_g0_counter + 1];
	d_g0_counter++;
	if(d_g0_counter > 3) d_g0_counter = 0;


	std::cout << "af1 " << encode_af(AF1) << std::endl;
	std::cout << "af2 " << encode_af(AF2) << std::endl;
}

void data_encoder::prepare_group2(const bool AB) {
	infoword[1] = infoword[1] | ((AB << 4) | (d_g2_counter & 0xf));
	if(!AB) {
		infoword[2] = (radiotext[d_g2_counter * 4] << 8 | radiotext[d_g2_counter * 4 + 1]);
		infoword[3] = (radiotext[d_g2_counter * 4 + 2] << 8 | radiotext[d_g2_counter * 4 + 3]);
	}
	else {
		infoword[2] = PI;
		infoword[3] = (radiotext[d_g2_counter * 2] << 8 | radiotext[d_g2_counter * 2 + 1]);
	}
	d_g2_counter++;
	d_g2_counter %= 16;
}

/* see page 28 and Annex G, page 81 in the standard */
/* FIXME this is supposed to be transmitted only once per minute, when 
 * the minute changes */
void data_encoder::prepare_group4a(void) {
	time_t rightnow;
	tm *utc;
	
	time(&rightnow);
	//printf("%s", asctime(localtime(&rightnow)));

/* we're supposed to send UTC time; the receiver should then add the
 * local timezone offset */
	utc = gmtime(&rightnow);
	int m = utc->tm_min;
	int h = utc->tm_hour;
	int D = utc->tm_mday;
	int M = utc->tm_mon + 1;  // January: M=0
	int Y = utc->tm_year;
	double toffset=localtime(&rightnow)->tm_hour-h;
	
	int L = ((M == 1) || (M == 2)) ? 1 : 0;
	int mjd=14956+D+int((Y-L)*365.25)+int((M+1+L*12)*30.6001);
	
	infoword[1]=infoword[1]|((mjd>>15)&0x3);
	infoword[2]=(((mjd>>7)&0xff)<<8)|((mjd&0x7f)<<1)|((h>>4)&0x1);
	infoword[3]=((h&0xf)<<12)|(((m>>2)&0xf)<<8)|((m&0x3)<<6)|
		((toffset>0?0:1)<<5)|((abs(toffset*2))&0x1f);
}

// for now single-group only
void data_encoder::prepare_group8a(void) {
	infoword[1] = infoword[1] | (1 << 3) | (DP & 0x7);
	infoword[2] = (1 << 15) | ((extent & 0x7) << 11) | (event & 0x7ff);
	infoword[3] = location;
}

void data_encoder::prepare_buffer(int which) {
	int q=0, i=0, j=0, a=0, b=0;
	unsigned char temp[13]; // 13*8=104
	std::memset(temp, 0, 13);
	
	for(q = 0; q < 104; q++) {
		a = floor(q / 26);
		b = 25 - q % 26;
		buffer[which][q] = (unsigned char)(block[a] >> b) & 0x1;
		i = floor(q / 8);
		j = 7 - q % 8;
		temp[i] = temp[i]|(buffer[which][q] << j);
	}
	printf("buffer[%i]: ", which);
	for(i = 0; i < 13; i++) printf("%02X", temp[i]);
	printf("\n");
}

//////////////////////// WORK ////////////////////////////////////
int data_encoder::work (int noutput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items) {

	gr::thread::scoped_lock lock(d_mutex);
	unsigned char *out = (unsigned char *) output_items[0];
	
	for(int i = 0; i < noutput_items; i++) {
		out[i] = buffer[d_current_buffer][d_buffer_bit_counter];
		if(++d_buffer_bit_counter > 103) {
			d_buffer_bit_counter = 0;
			d_current_buffer++;
			d_current_buffer = d_current_buffer % nbuffers;
		}
	}
	
	return noutput_items;
}

data_encoder::sptr
data_encoder::make () {
	return gnuradio::get_initial_sptr(new data_encoder());
}

