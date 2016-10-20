#!/usr/bin/env sh
. funcs.sh

CMD="python ./fundlist.py --fin B A --workers 10"
FOLDER="history"
time=`date +'%H%M'`
weekday=`date +'%w'`

record_history

$CMD
