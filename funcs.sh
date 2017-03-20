record_history () {

    time=`date +'%H%M'`
    weekday=`date +'%w'`

    if [ "$os" = "Linux" ]; then
        [ "$weekday" -eq 0 ] || [ "$weekday" -eq 6 ] \
                && _date=$(date -d"last Fri" +'%Y%m%d') \
                && $CMD > "$FOLDER/$_date" \
                && exit
        [ "$time" -lt "900" ] \
                && _date=$(date -d"1 day ago" +'%Y%m%d') \
                && $CMD > "$FOLDER/$_date" \
                && exit
        [ "$time" -gt "1600" ] \
                && _date=$(date +'%Y%m%d') \
                && $CMD > "$FOLDER/$_date" \
                && exit
    elif [ "$os" = "macOS" ]; then
        [ "$weekday" -eq 0 ] || [ "$weekday" -eq 6 ] \
                && _date=$(date -v-fri +'%Y%m%d') \
                && $CMD > "$FOLDER/$_date" \
                && exit
        [ "$time" -lt "900" ] \
                && _date=$(date -v-1d +'%Y%m%d') \
                && $CMD > "$FOLDER/$_date" \
                && exit
        [ "$time" -gt "1600" ] \
                && _date=$(date +'%Y%m%d') \
                && $CMD > "$FOLDER/$_date" \
                && exit
    fi

}
