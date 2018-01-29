#!/usr/bin/env sh
. .venv/bin/activate

. funcs.sh

CMD="python ./fundlist.py --fin B A --workers 16"
FOLDER="history"

record_history

$CMD

deactivate

