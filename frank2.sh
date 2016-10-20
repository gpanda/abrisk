#!/usr/bin/env sh
. funcs.sh

CMD="python ./fundlist.py --fin B1 A1 --workers 10"
FOLDER="history.favorites"
time=`date +'%H%M'`
weekday=`date +'%w'`

record_history

$CMD
