#!/bin/python
import math

# an implementation of RDS's syndrome calculation
def rds_syndrome(message, mlen):
	POLY = 0x5B9	# 10110111001, g(x)=x^10+x^8+x^7+x^5+x^4+x^3+1
	PLEN = 10
	OFFSET=[252, 408, 360, 436, 848]
	SYNDROME=[383, 14, 303, 663, 748]
	OFFSET_NAME=['A', 'B', 'C', 'D', 'C\'']
	reg = 0
	message=int(message, 16)
	if((mlen!=16)and(mlen!=26)):
		raise ValueError, "mlen must be either 16 or 26"
	# start calculation
	for i in range(mlen,0,-1):
		reg=(reg<<1)|((message>>(i-1))&0x1)
		if(reg&(1<<PLEN)):
			reg=reg^POLY
	for i in range(PLEN,0,-1):
		reg=reg<<1
		if(reg&(1<<PLEN)):
			reg=reg^POLY
	checkword=reg&((1<<PLEN)-1)
	# end calculation
	for i in range(0,5):
		if(mlen==16):
			print OFFSET_NAME[i], hex((message<<10)+(checkword^OFFSET[i]))
		else:
			if(checkword==SYNDROME[i]):
				print "checkword matches syndrome for offset", OFFSET_NAME[i]

# reads an ascii string of a decimal, and outputs the equivalent binary
# ascii string
def dec2bin(dec_string):
	bin_string=''
	dec=int(dec_string)
	if(dec<0): raise ValueError, "must be a positive integer"
	if(dec==0): return '0'
	while(dec):
		bin_string = str(dec%2) + bin_string
		dec = dec >> 1
	return bin_string
