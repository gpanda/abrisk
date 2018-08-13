cd `dirname $0`
. getos.sh
. ./venv.incl
. $VENV/bin/activate
./frank.sh
./frank2.sh
deactivate
. funcs.sh

./gen-ctags.sh

echo "Cron job done."
print_separator
cd -
