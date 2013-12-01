#
# Copyright 2013 Free Software Foundation, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

########################################################################
# Include swig generation macros
########################################################################
include(GrPython)
find_package(SWIG)
find_package(PythonLibs)
if(NOT SWIG_FOUND OR NOT PYTHONLIBS_FOUND)
    return()
endif()
include(GrSwig)

########################################################################
# Setup swig generation
########################################################################
set(GR_SWIG_INCLUDE_DIRS
    ${GR_RDS_INCLUDE_DIRS}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/../lib
)

foreach(incdir ${GNURADIO_RUNTIME_INCLUDE_DIRS})
    list(APPEND GR_SWIG_INCLUDE_DIRS ${incdir}/gnuradio/swig)
endforeach(incdir)

set(GR_SWIG_LIBRARIES gnuradio-rds)
set(GR_SWIG_DOC_FILE ${CMAKE_CURRENT_BINARY_DIR}/rds_swig_doc.i)
set(GR_SWIG_DOC_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/../lib)

GR_SWIG_MAKE(rds_swig rds_swig.i)

########################################################################
# Install the build swig module
########################################################################
GR_SWIG_INSTALL(
    TARGETS rds_swig
    DESTINATION ${GR_PYTHON_DIR}/rds
    COMPONENT "rds_python"
)

########################################################################
# Install swig .i files for development
########################################################################
list(APPEND swig_sources
    rds_swig.i
    ${CMAKE_CURRENT_BINARY_DIR}/rds_swig_doc.i
)

install(
    FILES ${swig_sources}
    DESTINATION ${GR_INCLUDE_DIR}/rds/swig
    COMPONENT "rds_swig"
)
