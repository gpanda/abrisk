cd `dirname $0`

./frank.sh
./frank2.sh

. funcs.sh

./gen-ctags.sh

echo "Cron job done."
print_separator
cd -
