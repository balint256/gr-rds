# python code implementing RDS's syndrome calculation:
import sys, math

# 0x5B9 = 10110111001, g(x)=x^10+x^8+x^7+x^5+x^4+x^3+1
POLY = int('5B9', 16)
PLEN = 10
OFFSET=[252, 408, 360, 436, 848]
OFFSET_NAME=['A', 'B', 'C', 'D', 'C\'']

message = int(sys.argv[1], 16)
mlen = int(sys.argv[2])
offset = int(sys.argv[3])	# should be in [0:4]
print 'message:', message, '(', hex(message), '), mlen:', mlen
print 'poly:', POLY, '(', hex(POLY), ')'
print 'offset ', OFFSET_NAME[offset], ': ', hex(OFFSET[offset])

reg = 0
for i in range(mlen,0,-1):
	reg=(reg<<1)|((message>>(i-1))&0x01)
	if(reg&(1<<PLEN)):
		reg=reg^POLY
for i in range(PLEN,0,-1):
	reg=reg<<1
	if(reg&(1<<PLEN)):
		reg=reg^POLY
checkword=reg&((1<<PLEN)-1)

print 'checkword:', checkword, '(', hex(checkword), ')'
block=(message<<10)+(checkword^OFFSET[offset])
print 'message + syndrome:', hex(block)
