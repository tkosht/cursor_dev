#!/usr/bin/sh

d=$(cd $(dirname $0) && pwd)
cd $d/../

# 縦の数
n=4

# 縦に分割
for _ in $(seq 1 $n)
do
    tmux split-window -h
done
tmux select-layout even-horizontal 



# 最初のペインを選択
tmux select-pane -t 0
# 各ペインにタイトルを設定
tmux set -g pane-border-status top
tmux set -g pane-border-format "#{pane_index}: #{pane_title}"

tmux select-pane -t "0" -T "Project/Task Manager"
tmux select-pane -t "1" -T "Task Worker"
tmux select-pane -t "2" -T "Task Worker"
tmux select-pane -t "3" -T "Task Worker"
tmux select-pane -t "4" -T "Task Worker"
tmux send-keys -t 0 'clear' Enter

# Window名を変更
tmux rename-session "AI PJ"
tmux rename-window "AI Agent Team"


# 引数からコマンド設定
cmd=$*
if [ "$1" = "" ]; then
    exit 0
fi

# 各ペインでコマンドを実行
pane_list=$(tmux list-panes -F "#{pane_index}")
for p in $pane_list
do
    tmux send-keys -t $p "$cmd" && sleep 0.1 && tmux send-keys -t $p Enter
    sleep 0.1
done

