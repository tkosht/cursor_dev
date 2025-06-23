#!/usr/bin/sh

d=$(cd $(dirname $0) && pwd)
cd $d/../

sh bin/splitter.sh auto_claude

