#!/usr/bin/env sh
cd `dirname $0`
. ./getos.sh
. ./getcpu.sh
. ./activate.sh

. ./funcs.sh

CMD="python ./fundlist.py --fin B A --workers $nprocs"
FOLDER="history"

record_history

$CMD

deactivate
cd --
