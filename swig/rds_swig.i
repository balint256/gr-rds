#define RDS_API

%include <gnuradio.i>
%include "rds_swig_doc.i"

%{
#include "rds/data_decoder.h"
#include "rds/data_encoder.h"
%}

%include "rds/data_decoder.h"
%include "rds/data_encoder.h"

GR_SWIG_BLOCK_MAGIC2 (rds, data_decoder);
GR_SWIG_BLOCK_MAGIC2 (rds, data_encoder);
