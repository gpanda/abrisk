#!/usr/bin/env sh
. .venv/bin/activate

. funcs.sh

CMD="python ./fundlist.py --fin B1 A1 --workers 16"
FOLDER="history.favourites"

record_history

$CMD

deactivate
