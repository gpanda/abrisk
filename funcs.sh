record_history () {

    network_ok || exit

    time=`date +'%H%M'`
    weekday=`date +'%w'`

    if [ "$os" = "Linux" ]; then
        [ "$weekday" -eq 0 ] || [ "$weekday" -eq 6 ] \
                && _date=$(date -d"last Fri" +'%Y%m%d')
        [ "$time" -lt "900" ] \
                && _date=$(date -d"1 day ago" +'%Y%m%d')
        [ "$time" -gt "1600" ] \
                && _date=$(date +'%Y%m%d')
    elif [ "$os" = "macOS" ]; then
        [ "$weekday" -eq 0 ] || [ "$weekday" -eq 6 ] \
                && _date=$(date -v-fri +'%Y%m%d')
        [ "$time" -lt "900" ] \
                && _date=$(date -v-1d +'%Y%m%d')
        [ "$time" -gt "1600" ] \
                && _date=$(date +'%Y%m%d')
    fi
    [ -z "$_date" ] && return # Trade time, no record
    f="$FOLDER/$_date"
    file_exists "$f" || $CMD > "$f"
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
    time=`date +'%H%M'`
    weekday=`date +'%w'`

    if [ "$os" = "Linux" ]; then
        [ "$weekday" -eq 0 ] || [ "$weekday" -eq 6 ] \
                && _date=$(date -d"last Fri" +'%Y%m%d')
        [ "$time" -lt "800" ] \
                && _date=$(date -d"1 day ago" +'%Y%m%d')
        [ "$time" -gt "1630" ] \
                && _date=$(date +'%Y%m%d')
    elif [ "$os" = "macOS" ]; then
        [ "$weekday" -eq 0 ] || [ "$weekday" -eq 6 ] \
                && _date=$(date -v-fri +'%Y%m%d')
        [ "$time" -lt "800" ] \
                && _date=$(date -v-1d +'%Y%m%d')
        [ "$time" -gt "1630" ] \
                && _date=$(date +'%Y%m%d')
    fi
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
