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
 * 	Written by : WRITTEN_BY
 * 	Created: CREATED_DATE
 * 
 */


#ifndef INCLUDED_gr_rds_data_decoder_H
#define INCLUDED_gr_rds_data_decoder_H

#include <gr_sync_block.h>
#include <gr_msg_queue.h>
#include <string.h>
#include <vector>
#include <iostream>

class gr_rds_data_decoder;

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
typedef boost::shared_ptr<gr_rds_data_decoder> gr_rds_data_decoder_sptr;
gr_rds_data_decoder_sptr gr_rds_make_data_decoder (gr_msg_queue_sptr msgq);


static const unsigned int syndrome[5]={383,14,303,748,663};

/* offset word C' has been put at the end
   see Annex A, page 59 of the standard */
static const unsigned int offset_pos[5]={0,1,2,2,3};
static const unsigned int offset_word[5]={252,408,360,436,848};
static const char * const offset_name[]={"A","B","C","C1","D"};

/* page 77, Annex F in the standard */
static const char * const pty_table[32]={"None",
								"News",
								"Current Affairs",
								"Information",
								"Sport",
								"Education",
								"Drama",
								"Cultures",
								"Science",
								"Varied Speech",
								"Pop Music",
								"Rock Music",
								"Easy Listening",
								"Light Classics M",
								"Serious Classics",
								"Other Music",
								"Weather & Metr",
								"Finance",
								"Children’s Progs",
								"Social Affairs",
								"Religion",
								"Phone In",
								"Travel & Touring",
								"Leisure & Hobby",
								"Jazz Music",
								"Country Music",
								"National Music",
								"Oldies Music",
								"Folk Music",
								"Documentary",
								"Alarm Test",
								"Alarm - Alarm !"};

/* pages 71-72, Annex D, tables D.1-2 in the standard */
static const char * const pi_country_codes[15][5]={
										{"DE","GR","MA","  ","MD"},
										{"DZ","CY","CZ","IE","EE"},
										{"AD","SM","PL","TR","  "},
										{"IL","CH","VA","MK","  "},
										{"IT","JO","SK","  ","  "},
										{"BE","FI","SY","  ","UA"},
										{"RU","LU","TN","  ","  "},
										{"PS","BG","  ","NL","PT"},
										{"AL","DK","LI","LV","SI"},
										{"AT","GI","IS","LB","  "},
										{"HU","IQ","MC","  ","  "},
										{"MT","GB","LT","HR","  "},
										{"DE","LY","YU","  ","  "},
										{"  ","RO","ES","SE","  "},
										{"EG","FR","NO","BY","BA"}};
static const char * const coverage_area_codes[16]={"Local",
											"International",
											"National",
											"Supra-regional",
											"Regional 1",
											"Regional 2",
											"Regional 3",
											"Regional 4",
											"Regional 5",
											"Regional 6",
											"Regional 7",
											"Regional 8",
											"Regional 9",
											"Regional 10",
											"Regional 11",
											"Regional 12"};

/* page 74, Annex E, table E.1 in the standard */
static const char transform_table[16][8] = {
/* the new, correct characters in the last 2 columns
   cause "multi-character character constant" warnings
					{' ', '0', '@', 'P', 'ǁ', 'p', 'á', 'â'},
					{'!', '1', 'A', 'Q', 'a', 'q', 'à', 'ä'},
					{'"', '2', 'B', 'R', 'b', 'r', 'é', 'ê'},
					{'#', '3', 'C', 'S', 'c', 's', 'è', 'ë'},
					{'°', '4', 'D', 'T', 'd', 't', 'í', 'î'},
					{'%', '5', 'E', 'U', 'e', 'u', 'ì', 'ï'},
					{'&', '6', 'F', 'V', 'f', 'v', 'ó', 'ô'},
					{'\'', '7', 'G', 'W', 'g', 'w', 'ò', 'ö'},
					{'(', '8', 'H', 'X', 'h', 'x', 'ú', 'û'},
					{')', '9', 'I', 'Y', 'i', 'y', 'ù', 'ü'},
					{'*', ':', 'J', 'Z', 'j', 'z', 'Ñ', 'ñ'},
					{'+', ';', 'K', '[', 'k', '{', 'Ç', 'ç'},
					{',', '<', 'L', '\\', 'l', '|', 'Ş', 'ş'},
					{'-', '=', 'M', ']', 'm', '}', 'ß', 'ğ'},
					{'.', '>', 'N', '-', 'n', '-', 'i', 'i'},
					{'/', '?', 'O', '-', 'o', ' ', 'Ĳ', 'ĳ'}};
*/
					{' ', '0', '@', 'P', ' ', 'p', 'a', 'a'},
					{'!', '1', 'A', 'Q', 'a', 'q', 'a', 'a'},
					{'"', '2', 'B', 'R', 'b', 'r', 'e', 'e'},
					{'#', '3', 'C', 'S', 'c', 's', 'e', 'e'},
					{'?', '4', 'D', 'T', 'd', 't', 'i', 'i'},
					{'%', '5', 'E', 'U', 'e', 'u', 'i', 'i'},
					{'&', '6', 'F', 'V', 'f', 'v', 'o', 'o'},
					{'\'', '7', 'G', 'W', 'g', 'w', 'o', 'o'},
					{'(', '8', 'H', 'X', 'h', 'x', 'u', 'u'},
					{')', '9', 'I', 'Y', 'i', 'y', 'u', 'u'},
					{'*', ':', 'J', 'Z', 'j', 'z', 'N', 'n'},
					{'+', ';', 'K', '[', 'k', '{', 'c', 'c'},
					{',', '<', 'L', '\\', 'l', '|', 's', 's'},
					{'-', '=', 'M', ']', 'm', '}', 'b', 'g'},
					{'.', '>', 'N', '-', 'n', '-', 'i', 'i'},
					{'/', '?', 'O', '-', 'o', ' ', 'I', 'i'}};


/* see page 84, Annex J in the standard */
static const char * const language_codes[44]={"Unkown/not applicable",
										"Albanian",
										"Breton",
										"Catalan",
										"Croatian",
										"Welsh",
										"Czech",
										"Danish",
										"German",
										"English",
										"Spanish",
										"Esperanto",
										"Estonian",
										"Basque",
										"Faroese",
										"French",
										"Frisian",
										"Irish",
										"Gaelic",
										"Galician",
										"Icelandic",
										"Italian",
										"Lappish",
										"Latin",
										"Latvian",
										"Luxembourgian",
										"Lithuanian",
										"Hungarian",
										"Maltese",
										"Dutch",
										"Norwegian",
										"Occitan",
										"Polish",
										"Portuguese",
										"Romanian",
										"Romansh",
										"Serbian",
										"Slovak",
										"Slovene",
										"Finnish",
										"Swedish",
										"Turkish",
										"Flemish",
										"Walloon"};

class gr_rds_data_decoder : public gr_sync_block
{
private:
	unsigned long bit_counter, lastseen_offset_counter, reg;
	unsigned char lastseen_offset, block_number;
	unsigned int block_bit_counter, wrong_blocks_counter, blocks_counter, group_good_blocks_counter;
	bool presync,good_block, group_assembly_started;
	unsigned int group[4];
	enum state_t { ST_NO_SYNC, ST_SYNC };
	state_t d_state;
	char radiotext[65];
	char clocktime_string[33];
	char af1_string[10];
	char af2_string[10];
	char af_string[21];
	bool radiotext_AB_flag;
	bool traffic_program;
	bool traffic_announcement;
	bool music_speech;
	bool mono_stereo;
	bool artificial_head;
	bool compressed;
	bool static_pty;
	unsigned char program_type;
	unsigned int program_identification;
	unsigned char pi_country_identification;
	unsigned char pi_area_coverage;
	unsigned char pi_program_reference_number;
	char program_service_name[9];
	gr_msg_queue_sptr	d_msgq;

// Functions
	friend gr_rds_data_decoder_sptr gr_rds_make_data_decoder (gr_msg_queue_sptr msgq);
	gr_rds_data_decoder (gr_msg_queue_sptr msgq);		// private constructor
	void enter_no_sync();
	void enter_sync(unsigned int sync_block_number);
	void reset_rds_data();
	unsigned int calc_syndrome(unsigned long message, unsigned char mlen,
			unsigned long poly, unsigned char plen);
	void printbin(unsigned long number,unsigned char bits);
	unsigned long bin2dec(char *string);
	char  transform_char(char z);
	void send_message(long msgtype, std::string msgtext);
	void decode_group(unsigned int *group);
	double decode_af(unsigned int af_code);
	void decode_type0(unsigned int *group, bool version_code);
	void decode_type1(unsigned int *group, bool version_code);
	void decode_type2(unsigned int *group, bool version_code);
	void decode_type4a(unsigned int *group);
	void decode_type8a(unsigned int *group);
	void decode_type14(unsigned int *group, bool version_code);
	void decode_type15b(unsigned int *group);


public:
	~gr_rds_data_decoder();		// public destructor
	void reset(void);
	int work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items);
};

#endif /* INCLUDED_gr_rds_data_decoder_H */
