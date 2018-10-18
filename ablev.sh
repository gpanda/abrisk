#!/bin/bash -
#===============================================================================
#
#          FILE: ablev.sh
#
#         USAGE: ./ablev.sh
#
#   DESCRIPTION: 
#
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Ren, Letian (), gpanda.next@gmail.com
#  ORGANIZATION: SelfRef
#       CREATED: 10/18/2018 12:22:33
#      REVISION:  ---
#===============================================================================

set -o nounset                                  # Treat unset variables as an error

[ $# -lt 2 ] && echo "need 2 book values: Va and Vb." && exit 1
echo '(' $1 '+' $2 ')' '/' $2 | bc -l
