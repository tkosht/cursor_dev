#!/usr/bin/sh

d=$(cd $(dirname $0) && pwd)
cd $d/../

sh bin/splitter_13.sh auto_claude

