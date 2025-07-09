#!/usr/bin/sh

d=$(cd $(dirname $0) && pwd)
cd $d/../

if [ "$1" = "large" ]; then
    sh bin/splitter_13.sh auto_claude
else
    sh bin/splitter.sh auto_claude
fi

