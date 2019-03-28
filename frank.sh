#!/usr/bin/env sh
cd `dirname $0`
. ./getos.sh
. ./getcpu.sh
. ./activate.sh

. ./funcs.sh

CMD="python ./fundlist.py --fin A B --workers $nprocs"
FOLDER="history"

record_history

$CMD

deactivate
cd --
