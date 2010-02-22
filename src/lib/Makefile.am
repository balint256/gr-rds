#
# Copyright 2004,2005 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
# 

include $(top_srcdir)/Makefile.common

# Install this stuff so that it ends up as the gnuradio.howto module
# This usually ends up at:
#   ${prefix}/lib/python${python_version}/site-packages/gnuradio

ourpythondir = $(grpythondir)
ourlibdir    = $(grpyexecdir)

INCLUDES = $(STD_DEFINES_AND_INCLUDES) $(PYTHON_CPPFLAGS) \
	-I/usr/include/libxml2

SWIGCPPPYTHONARGS = -python $(PYTHON_CPPFLAGS) \
	-I$(swigincludedir) -I$(grincludedir)

ALL_IFILES = 				\
	$(LOCAL_IFILES)			\
	$(NON_LOCAL_IFILES)

NON_LOCAL_IFILES =			\
	$(GNURADIO_I)


LOCAL_IFILES = 				\
	rds.i

# These files are built by SWIG.  The first is the C++ glue.
# The second is the python wrapper that loads the _howto shared library
# and knows how to call our extensions.

BUILT_SOURCES = 			\
	rds.cc				\
	rds.py

# This gets howto.py installed in the right place
ourpython_PYTHON =			\
	rds.py

ourlib_LTLIBRARIES = _rds.la

# These are the source files that go into the shared library
_rds_la_SOURCES = 			\
	rds.cc				\
	gr_rds_bpsk_demod.cc		\
	gr_rds_data_decoder.cc		\
	gr_rds_data_encoder.cc		\
	gr_rds_rate_enforcer.cc		\
	gr_rds_freq_divider.cc

# magic flags
_rds_la_LDFLAGS = -module -avoid-version

# link the library against some comon swig runtime code and the 
# c++ standard library
_rds_la_LIBADD = 			\
	$(GNURADIO_CORE_LIBS)		\
	$(PYTHON_LDFLAGS)		\
	-lxml2				\
	-lstdc++

rds.cc rds.py: rds.i $(ALL_IFILES)
	$(SWIG) $(SWIGCPPPYTHONARGS) -module rds -o rds.cc $<

# These headers get installed in ${prefix}/include/gnuradio
grinclude_HEADERS =			\
	gr_rds_bpsk_demod.h		\
	gr_rds_data_decoder.h		\
	gr_rds_data_encoder.h		\
	gr_rds_rate_enforcer.h		\
	gr_rds_freq_divider.h		\
	gr_rds_constants.h

# These swig headers get installed in ${prefix}/include/gnuradio/swig
swiginclude_HEADERS = 			\
	$(LOCAL_IFILES)


MOSTLYCLEANFILES = $(BUILT_SOURCES) *.pyc

