#!/bin/bash
# print group statistics for the rds decoder output log

if [ $# -ne 1 ]; then
	echo "Usage: $0 logfile.log"
	exit 1;
fi
if [ ! -f $1 ]; then
	echo $1 'not found';
	exit 1;
fi
for i in `seq 0 15`; do
	t=`grep $i'A' $1 -c`
	if [ $t -ne 0 ]; then echo 'group' $i'A:' $t 'instances'; fi
done
