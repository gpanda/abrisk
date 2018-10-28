RETRY=4
RETRY_INTERVAL=5

get_trade_date () {
    # $1 time before but close to (like in an hour) trade start time, e.g 900
    # $2 time after but close to (like in an hour) trade end time, e.g. 1600
    time=`date +'%H%M'`
    weekday=`date +'%w'`
    _date=""

    if [ "$os" = "Linux" ]; then
        if [ "$weekday" -eq 0 ] || [ "$weekday" -eq 6 ]; then
            _date=$(date -d"last Fri" +'%Y%m%d')
        elif [ "$time" -lt "$1" ]; then
            _date=$(date -d"1 day ago" +'%Y%m%d')
        elif [ "$time" -gt "$2" ]; then
            _date=$(date +'%Y%m%d')
        fi
    elif [ "$os" = "macOS" ]; then
        if [ "$weekday" -eq 0 ] || [ "$weekday" -eq 6 ]; then
            _date=$(date -v-fri +'%Y%m%d')
        elif [ "$time" -lt "$1" ]; then
            _date=$(date -v-1d +'%Y%m%d')
        elif [ "$time" -gt "$2" ]; then
            _date=$(date +'%Y%m%d')
        fi
    fi
    echo "$_date"
}

record_history () {

    network_ok || exit
    _date=$( get_trade_date 900 1600 )
    [ -z "$_date" ] && return # Trading time, no record to be saved.

    f="$FOLDER/$_date"
    if  ! file_exists "$f" ; then
        ( >&2 echo "RD: `date`" )
        ( >&2 echo "TD: $_date" )
        $CMD > "$f"
    fi
    rc=$?
    i=1
    while [ $rc -ne 0 ] && [ $i -le $RETRY ]
    do
        rm "$f"
        ( >&2 echo "rc=[$rc], failed, sleep for $RETRY_INTERVAL(s)" )
        sleep $RETRY_INTERVAL
        ( >&2 echo "Now retry $i" )
        file_exists "$f" && rm "$f"
        $CMD > "$f"
        rc=$?
        i=`expr $i + 1`
    done
    if [ $rc -ne 0 ]; then
        rm "$f"
    fi
    exit
}

record_history_us () {

    network_ok || exit

    # US stock market time
    # EST: 9:30 - 16:00
    # VIX time
    # ESt: 9:30 - 16:30
    # date="TZ=EST5EDT date" # don't why, ok for standlone, but error in script
    export TZ=EST5EDT
    _date=$( get_trade_date 800 1630 )

    [ -z "$_date" ] && return # Trade time, no record
    f="$FOLDER/$_date"
    file_exists "$f" || $CMD > "$f"
    exit
}

network_ok () {
    test_address=www.163.com
    ping -c 1 $test_address > /dev/null 2>&1
}

file_exists () {
    stat "$1" > /dev/null 2>&1
}

print_separator () {
    echo "============================================================"
    echo ""
}
