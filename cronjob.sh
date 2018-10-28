cd `dirname $0`
date +'%Y%m%d %H:%M:%S' >&2

./frank.sh
./frank2.sh

. ./funcs.sh

./gen-ctags.sh

echo "Cron job done."
print_separator
cd -
