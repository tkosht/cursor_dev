#!/bin/sh

latest_session_no=$(tmux ls | perl -pe 's/:.+$//' | sort -n | tail -n 1)
echo $latest_session_no
if [ "$latest_session_no" = "" ]; then
    cmd="tmux"
else
    cmd="tmux attach -t $latest_session_no"
fi
exec $cmd

