#!/usr/bin/env sh
cd `dirname $0`
. ./venv.incl
. $VENV/bin/activate

. funcs.sh

CMD="python ./fundlist.py --fin B A --workers 16"
FOLDER="history"

record_history

$CMD

deactivate
cd --
