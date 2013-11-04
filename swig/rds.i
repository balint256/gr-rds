#define GR_RDS_API

%include <gnuradio.i>
%include "rds_swig_doc.i"

%{
#include "bpsk_demod.h"
#include "data_decoder.h"
#include "data_encoder.h"
#include "rate_enforcer.h"
#include "freq_divider.h"
%}

%include "bpsk_demod.h"
%include "data_decoder.h"
%include "data_encoder.h"
%include "rate_enforcer.h"
%include "freq_divider.h"

GR_SWIG_BLOCK_MAGIC2 (rds, data_decoder);
GR_SWIG_BLOCK_MAGIC2 (rds, data_encoder);
GR_SWIG_BLOCK_MAGIC2 (rds, rate_enforcer);
GR_SWIG_BLOCK_MAGIC2 (rds, freq_divider);
GR_SWIG_BLOCK_MAGIC2 (rds, bpsk_demod);
