#!/bin/sh

os=`uname -a`

if  echo $os | grep -q "Linux"
then
    export os="Linux"
elif echo $os | grep -q "Darwin"
then
    export os="macOS"
elif echo $os | grep -q "Cygwin"
then
    export os="Cygwin"
elif echo $os | grep -q "AIX"
then
    export os="AIX"
else
    export os="Windows"
fi
echo os=$os
