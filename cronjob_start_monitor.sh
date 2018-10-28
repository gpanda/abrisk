cd `dirname $0`
. ./getos.sh
. ./getcpu.sh
. ./activate.sh
#./monitor.py --fin B1.mon A1.mon today.mon
./monitor.py --fin today.mon --workers $nprocs
deactivate
echo "Cron job done."
cd -
