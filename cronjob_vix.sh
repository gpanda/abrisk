cd `dirname $0`
. getos.sh
. ./venv.incl
. $VENV/bin/activate
./vix.sh
deactivate
cd -
