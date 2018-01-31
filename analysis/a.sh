#!/bin/bash - 
#==============================================================================
#
#          FILE: a.sh
# 
#         USAGE: ./a.sh <fid>
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Ren, Letian (), retaelppa@gmail.com
#  ORGANIZATION: SelfRef
#       CREATED: 01/30/2018 15:20:10
#      REVISION:  ---
#==============================================================================

set -o nounset                              # Treat unset variables as an error

./getdat.sh $1

echo $0
# export OCTAVE_EXEC_PATH=`dirname $0`
octave-cli --no-init-file ./show.m "$1"
