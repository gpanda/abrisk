#!/bin/bash - 
#==============================================================================
#
#          FILE: gen-ctags.sh
# 
#         USAGE: ./gen-ctags.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Ren, Letian (), gpanda.next@gmail.com
#  ORGANIZATION: ---
#       CREATED: 06/14/2017 11:05
#      REVISION:  ---
#==============================================================================

set -o nounset                              # Treat unset variables as an error
ctags --exclude=.venv --languages=C,C++,Java,Python,Sh -R .
