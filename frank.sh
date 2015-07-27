#!/bin/sh

CMD="./fundlist.py --fin B.txt A.txt --workers 10"
time=`date +'%H%M'`

[ "$time" -lt "900" ] && date=$(date -d"1 day ago" +'%Y%m%d') \
        && $CMD > history/$date && exit
[ "$time" -gt "1600" ] && date=$(date +'%Y%m%d') \
        && $CMD > history/$date && exit

$CMD
