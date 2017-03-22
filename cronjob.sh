cd `dirname $0`
. getos.sh
. .venv/bin/activate
./frank.sh
./frank2.sh
deactivate
. funcs.sh
echo "Cron job done."
print_separator
cd -
