#!/bin/sh

CMD="python ./fundlist.py --fin B A --workers 10"
time=`date +'%H%M'`
weekday=`date +'%w'`

[ "$weekday" -eq 0 ] || [ "$weekday" -eq 6 ] && \
        date=$(date -d"last Fri" +'%Y%m%d') \
        && $CMD > history/$date && exit
[ "$time" -lt "900" ] && date=$(date -d"1 day ago" +'%Y%m%d') \
        && $CMD > history/$date && exit
[ "$time" -gt "1600" ] && date=$(date +'%Y%m%d') \
        && $CMD > history/$date && exit

$CMD
