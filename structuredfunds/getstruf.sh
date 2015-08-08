#!/bin/sh
acount=`awk '/^.*A|优先|稳进|稳健|收益.*$/ {print $2","$3}' list.txt | sort | wc -l`
bcount=`awk '/^.*B|进取|锐进|积极.*$/ {print $2","$3}' list.txt | sort | wc -l`

[ $acount -eq $bcount ] && printf "A count = B count.\r\n"
printf "acount=$acount\r\n"
printf "bcount=$bcount\r\n"

awk '/^.*A|优先|稳进|稳健|收益.*$/ {print $2","$3}' list.txt | sort > A
awk '/^.*B|进取|锐进|积极.*$/ {print $2","$3}' list.txt | sort > B
