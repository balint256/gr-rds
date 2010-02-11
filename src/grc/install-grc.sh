#!/bin/bash
[ -a ~/.grc_gnuradio ] || mkdir ~/.grc_gnuradio
install *.xml -t ~/.grc_gnuradio
