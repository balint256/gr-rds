#!/usr/bin/env python
from gnuradio import gr, rds

fg=gr.top_block()
src=rds.data_encoder('rds_data.xml')
sink=gr.vector_sink_b()
fg.connect(src, sink)
