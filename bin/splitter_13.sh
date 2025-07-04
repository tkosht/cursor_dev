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


# 横に分割
## 2分割
for i in $(seq 1 $(expr $n + 1))
do
    # p=$(expr \( $i - 1 \) \* 2 + 1)
    p=$(expr \( $i - 1 \) \* 2)
    tmux select-pane -t $p && tmux split-window -v
done



## 3分割目
for i in $(seq 1 $(expr $n))
do
    p=$(expr \( $i - 1 \) \* 3 + 2)
    tmux select-pane -t $p && tmux split-window -v
    tmux select-layout -E
done


# 最初のペインを選択
tmux select-pane -t 0
tmux send-keys -t 0 'sh bin/set_panenames.sh' Enter
tmux send-keys -t 0 'clear' Enter

# Window名を変更
tmux rename-session "CC PJ"
tmux rename-window "AI Agents Team"


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

