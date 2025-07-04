#!/bin/bash
# tmux組織活動用共通ユーティリティスクリプト

# Claude CLI 処理状態の検出
is_claude_processing() {
    local pane="$1"
    if [[ -z "$pane" ]]; then
        return 1
    fi
    
    # Claude CLI の処理中を示すパターンをチェック
    local recent_output=$(tmux capture-pane -t "$pane" -p | tail -5)
    echo "$recent_output" | grep -q "✶.*Collaborating\|✻.*Considering\|⚒.*tokens\|Running\.\.\.\|Thinking\.\.\."
}

# Claude CLI 処理完了を待機
wait_for_claude_idle() {
    local pane="$1"
    local max_wait="${2:-30}"  # 最大待機時間（秒）
    local wait_count=0
    
    while is_claude_processing "$pane" && [[ $wait_count -lt $max_wait ]]; do
        sleep 2
        ((wait_count += 2))
        echo "⏳ Waiting for Claude CLI idle in pane-$pane... (${wait_count}s)" >&2
    done
    
    if [[ $wait_count -ge $max_wait ]]; then
        echo "⚠️ Warning: Claude CLI still processing after ${max_wait}s, proceeding anyway" >&2
        return 1
    fi
    
    return 0
}

# 現在のペイン情報を取得
get_current_pane_info() {
    export CURRENT_PANE=$(tmux display-message -p "#{pane_index}" 2>/dev/null || echo "unknown")
    export PANE_TITLE=$(tmux display-message -p "#{pane_title}" 2>/dev/null || echo "unknown")
    export SESSION_NAME=$(tmux display-message -p "#{session_name}" 2>/dev/null || echo "unknown")
}

# 特定の役割のペインを検索
find_role_pane() {
    local role="$1"
    tmux list-panes -F "#{pane_index}:#{pane_title}" 2>/dev/null | \
        grep -E "$role" | \
        head -1 | \
        cut -d: -f1
}

# ProjectManagerペインを特定
find_project_manager_pane() {
    find_role_pane "ProjectManager|00"
}

# レビューチームペインを特定
find_review_panes() {
    tmux list-panes -F "#{pane_index}:#{pane_title}" 2>/dev/null | \
        grep -E "TaskReview(Manager|Worker)|0[369]" | \
        cut -d: -f1
}

# tmux環境でメッセージを送信
send_tmux_message() {
    local target_pane="$1"
    local message="$2"
    local sender="${PANE_TITLE:-unknown}(pane-${CURRENT_PANE:-unknown})"
    
    if [[ -n "$target_pane" && -n "$message" ]]; then
        # タイムスタンプ付きメッセージ
        tmux send-keys -t "$target_pane" "# MESSAGE from ${sender} at $(date '+%H:%M:%S')"
        tmux send-keys -t "$target_pane" Enter
        tmux send-keys -t "$target_pane" "$message"
        tmux send-keys -t "$target_pane" Enter
        tmux send-keys -t "$target_pane" "---"
        tmux send-keys -t "$target_pane" Enter
        return 0
    else
        return 1
    fi
}

# 組織活動文脈の確認
is_organization_context() {
    [[ -n "$TMUX_ORGANIZATION_CONTEXT" ]] && [[ -n "$TMUX" ]]
}

# Workerペインかどうかの確認
is_worker_pane() {
    [[ "$PANE_TITLE" =~ Worker ]] || [[ "$PANE_TITLE" =~ 0[5891][01-3] ]]
}

# Managerペインかどうかの確認
is_manager_pane() {
    [[ "$PANE_TITLE" =~ Manager ]] || [[ "$PANE_TITLE" =~ 0[0-4] ]]
}

# git worktreeブランチかどうかの確認
is_competitive_branch() {
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        local branch=$(git branch --show-current 2>/dev/null)
        [[ "$branch" =~ competitive_ ]]
    else
        return 1
    fi
}

# ログ出力
log_organization_activity() {
    local activity="$1"
    local log_file="${HOME}/.claude/tmux_organization.log"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ${PANE_TITLE:-unknown}(${CURRENT_PANE:-unknown}): $activity" >> "$log_file"
}