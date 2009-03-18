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

#ifndef INCLUDED_GR_RDS_FREQ_STATISTICS_H
#define INCLUDED_GR_RDS_FREQ_STATISTICS_H


#include <gr_sync_block.h>
#include <gr_feval.h>
#include <gr_message.h>
#include <gr_msg_queue.h>

class gr_rds_freq_statistics;
typedef boost::shared_ptr<gr_rds_freq_statistics> gr_rds_freq_statistics_sptr;
gr_rds_freq_statistics_sptr
gr_rds_make_freq_statistics(unsigned int vlen,
			double start_freq,
			double step_freq);


/*!
 * \brief calculate statistics and print frequencies above the threshold
 * \ingroup sink
 */
class gr_rds_freq_statistics : public gr_sync_block
{
  friend gr_rds_freq_statistics_sptr
  gr_rds_make_freq_statistics(unsigned int vlen,
			   double start_freq,
			   double step_freq);

  unsigned int	     d_vlen;
  double	     d_start_freq;
  double	     d_step_freq;

  gr_rds_freq_statistics(unsigned int vlen,
			double start_freq,
			double step_freq);

protected:
//  std::vector<float> d_max;	// per bin maxima
  unsigned int vlen() const { return d_vlen; }
  double start_freq() const { return d_start_freq; }
  double step_freq() const { return d_step_freq; }

public:
  ~gr_rds_freq_statistics();

  int work(int noutput_items,
	   gr_vector_const_void_star &input_items,
	   gr_vector_void_star &output_items);
};

#endif
