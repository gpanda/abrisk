#!/usr/bin/env sh
. funcs.sh

CMD="python ./fundlist.py --fin B A --workers 10"
FOLDER="history"

record_history

$CMD
