record_history () {

    time=`date +'%H%M'`
    weekday=`date +'%w'`

    if [ $os = "Linux" ]; then
        [ "$weekday" -eq 0 ] || [ "$weekday" -eq 6 ] && \
                date=$(date -d"last Fri" +'%Y%m%d') \
                && $CMD > $FOLDER/$date && exit
        [ "$time" -lt "900" ] && date=$(date -d"1 day ago" +'%Y%m%d') \
                && $CMD > $FOLDER/$date && exit
        [ "$time" -gt "1600" ] && date=$(date +'%Y%m%d') \
                && $CMD > $FOLDER/$date && exit
    elif [ $os = "macOS" ]; then
        [ "$weekday" -eq 0 ] || [ "$weekday" -eq 6 ] && \
                date=$(date -v-fri +'%Y%m%d') \
                && $CMD > $FOLDER/$date && exit
        [ "$time" -lt "900" ] && date=$(date -v-1d +'%Y%m%d') \
                && $CMD > $FOLDER/$date && exit
        [ "$time" -gt "1600" ] && date=$(date +'%Y%m%d') \
            && $CMD > $FOLDER/$date && exit
    fi

}
