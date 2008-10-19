/* -*- c++ -*- */

%feature("autodoc", "1");		// generate python docstrings

%include "exception.i"
%import "gnuradio.i"			// the common stuff

%{
#include "gnuradio_swig_bug_workaround.h"	// mandatory bug fix
#include "gr_rds_diff_decoder.h"
#include "gr_rds_biphase_decoder.h"
#include "gr_rds_data_decoder.h"
#include "gr_rds_freq_divider.h"
#include <stdexcept>
%}

// ----------------------------------------------------------------

GR_SWIG_BLOCK_MAGIC ( gr_rds, diff_decoder);

gr_rds_diff_decoder_sptr gr_rds_make_diff_decoder ();

class gr_rds_diff_decoder : public gr_sync_block
{
private:
	gr_rds_diff_decoder ();
};

// -----------------------------------------------------------------

GR_SWIG_BLOCK_MAGIC (gr_rds, biphase_decoder);

gr_rds_biphase_decoder_sptr gr_rds_make_biphase_decoder (double input_sample_rate);

class gr_rds_biphase_decoder: public gr_block
{
private:
	gr_rds_biphase_decoder (double input_sample_rate);
public:
	void reset(void);
};

//------------------------------------------------------------------

GR_SWIG_BLOCK_MAGIC (gr_rds, data_decoder);

gr_rds_data_decoder_sptr gr_rds_make_data_decoder(gr_msg_queue_sptr msgq);

class gr_rds_data_decoder: public gr_sync_block
{
private:
	gr_rds_data_decoder(gr_msg_queue_sptr msgq);
public:
	void reset(void);
};

// ------------------------------------------------------------------

GR_SWIG_BLOCK_MAGIC (gr_rds, freq_divider);

gr_rds_freq_divider_sptr gr_rds_make_freq_divider (unsigned int divider);

class gr_rds_freq_divider: public gr_sync_block
{
private:
	gr_rds_freq_divider (unsigned int divider);
};

