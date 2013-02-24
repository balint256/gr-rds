# Copyright 2011 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX

add_library(gnuradio-rds SHARED
	gr_rds_bpsk_demod.cc
	gr_rds_data_decoder.cc
	gr_rds_data_encoder.cc
	gr_rds_rate_enforcer.cc
	gr_rds_freq_divider.cc
)
target_link_libraries(gnuradio-rds ${Boost_LIBRARIES} ${GRUEL_LIBRARIES} ${GNURADIO_CORE_LIBRARIES} ${LIBXML2_LIBRARIES})
set_target_properties(gnuradio-rds PROPERTIES DEFINE_SYMBOL "gnuradio_rds_EXPORTS")

########################################################################
# Install built library files
########################################################################
install(TARGETS gnuradio-rds
    LIBRARY DESTINATION lib${LIB_SUFFIX} # .so/.dylib file
    ARCHIVE DESTINATION lib${LIB_SUFFIX} # .lib file
    RUNTIME DESTINATION bin              # .dll file
)

########################################################################
# Build and register unit test
########################################################################
find_package(Boost COMPONENTS unit_test_framework)

include(GrTest)
set(GR_TEST_TARGET_DEPS gnuradio-rds)
#turn each test cpp file into an executable with an int main() function
add_definitions(-DBOOST_TEST_DYN_LINK -DBOOST_TEST_MAIN)

#add_executable(qa_howto_square_ff qa_howto_square_ff.cc)
#target_link_libraries(qa_howto_square_ff gnuradio-howto ${Boost_LIBRARIES})
#GR_ADD_TEST(qa_howto_square_ff qa_howto_square_ff)

#add_executable(qa_howto_square2_ff qa_howto_square2_ff.cc)
#target_link_libraries(qa_howto_square2_ff gnuradio-howto ${Boost_LIBRARIES})
#GR_ADD_TEST(qa_howto_square2_ff qa_howto_square2_ff)

########################################################################
# Python/SWIG ##########################################################
########################################################################

########################################################################
# Include swig generation macros
########################################################################
find_package(SWIG)
find_package(PythonLibs)
if(NOT SWIG_FOUND OR NOT PYTHONLIBS_FOUND)
    return()
endif()
include(GrSwig)
include(GrPython)

########################################################################
# Setup swig generation
########################################################################
foreach(incdir ${GNURADIO_CORE_INCLUDE_DIRS})
    list(APPEND GR_SWIG_INCLUDE_DIRS ${incdir}/swig)
endforeach(incdir)

foreach(incdir ${GRUEL_INCLUDE_DIRS})
    list(APPEND GR_SWIG_INCLUDE_DIRS ${incdir}/gruel/swig)
endforeach(incdir)

set(GR_SWIG_LIBRARIES gnuradio-rds)
#set(GR_SWIG_DOC_FILE ${CMAKE_CURRENT_BINARY_DIR}/rds_doc.i)	# howto_rds_doc
#set(GR_SWIG_DOC_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/../include)

GR_SWIG_MAKE(rds rds.i) # rds_swig rds_swig.i

########################################################################
# Install the build swig module
########################################################################
GR_SWIG_INSTALL(TARGETS rds DESTINATION ${GR_PYTHON_DIR}${RDS_PYTHON_SUBDIR}/rds)	# rds_swig

########################################################################
# Install swig .i files for development
########################################################################
install(
    FILES
    rds.i # rds_swig.i
#    ${CMAKE_CURRENT_BINARY_DIR}/rds_doc.i # rds_swig_doc.i
    DESTINATION ${GR_INCLUDE_DIR}/rds/swig	# Not adding ${RDS_PYTHON_SUBDIR} here
)

