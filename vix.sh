#!/usr/bin/env sh
cd `dirname $0`

. ./activate.sh
. funcs.sh

CMD="python ./vix.py"
FOLDER="vix.history"

record_history_us

$CMD

deactivate
cd --
