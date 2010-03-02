#!/bin/bash
# print rds-tmc event statistics

if [ $# -ne 1 ]; then
	echo "Usage: $0 logfile.log"
	exit 1;
fi
if [ ! -f $1 ]; then
	echo $1 'not found';
	exit 1;
fi
grep 'event:' $1|cut -d " " -f 3|sed -e 's/,//g'|sort|uniq -c|sort -g -r
