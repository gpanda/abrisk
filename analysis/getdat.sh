#!/bin/bash - 
#==============================================================================
#
#          FILE: getdat.sh
# 
#         USAGE: ./getdat.sh <fid>
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Ren, Letian (), retaelppa@gmail.com
#  ORGANIZATION: SelfRef
#       CREATED: 01/30/2018 15:05:33
#      REVISION:  ---
#==============================================================================

set -o nounset                              # Treat unset variables as an error

grep "$1" -r ../history.favourites | sort \
| awk -F"|" '!/\W0.0\W/ {gsub(/ /, "", $0); print $5, $6, $7, $8}' > "$1"

