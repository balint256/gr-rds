# python code implementing RDS's syndrome calculation:
# 4 examples, for testing purposes
# A210 - 28841DF
# 07E8 - 1FA389
# 1794 - 5E5193
# 415A - 10569C2

import sys, math

POLY = int('5b9', 16)
PLEN = 10
message = int(sys.argv[1], 16)
mlen = int(sys.argv[2])
print 'message:', message, '(', hex(message), '), mlen:', mlen
print 'poly:', POLY, '(', hex(POLY), ')'

reg = 0
for i in range(mlen,0,-1):
	reg=(reg<<1)|((message>>(i-1))&0x01)
	if(reg&(1<<PLEN)):
		reg=reg^POLY
for i in range(PLEN,0,-1):
	reg=reg<<1
	if(reg&(1<<PLEN)):
		reg=reg^POLY
syndrome=reg&((1<<PLEN)-1)

print 'syndrome:', syndrome, '(', hex(syndrome), ')'
block=(message<<10)+syndrome
print 'message + syndrome:', hex(block)
