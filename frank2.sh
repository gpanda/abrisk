#!/usr/bin/env sh
cd `dirname $0`
. ./getos.sh
. ./getcpu.sh

. ./activate.sh

. ./funcs.sh

CMD="python ./fundlist.py --fin B1 A1 --workers $nprocs"
FOLDER="history.favourites"

record_history

$CMD

deactivate
cd --
