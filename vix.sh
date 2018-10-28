#!/usr/bin/env sh
cd `dirname $0`

. ./getos.sh
. ./activate.sh
. ./funcs.sh

CMD="python ./vix.py"
FOLDER="history.vix"

record_history_us

$CMD

deactivate
cd --
