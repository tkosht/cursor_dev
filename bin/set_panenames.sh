#!/usr/bin/sh

# 各ペインにタイトルを設定
tmux set -g pane-border-status top
tmux set -g pane-border-format "#{pane_index}: #{pane_title}"

tmux select-pane -t "0" -T "Project Manager"
tmux select-pane -t "1" -T "PMO/Consultant"

tmux select-pane -t "2" -T "Task Execution Manager"
tmux select-pane -t "3" -T "Task Review Manager"
tmux select-pane -t "4" -T "Task Knowledge/Rule Manager"

tmux select-pane -t "5" -T "Task Execution Worker"
tmux select-pane -t "8" -T "Task Execution Worker"
tmux select-pane -t "11" -T "Task Execution Worker"

tmux select-pane -t "6" -T "Task Review Worker"
tmux select-pane -t "9" -T "Task Review Worker"
tmux select-pane -t "12" -T "Task Review Worker"

tmux select-pane -t "7" -T "Task Knowledge/Rule Worker"
tmux select-pane -t "10" -T "Task Knowledge/Rule Worker"
tmux select-pane -t "13" -T "Task Knowledge/Rule Worker"

