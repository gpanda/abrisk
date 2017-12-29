cd `dirname $0`
. getos.sh
. .venv/bin/activate
#./monitor.py --fin B1.mon A1.mon today.mon
./monitor.py --fin today.mon
deactivate
echo "Cron job done."
cd -
