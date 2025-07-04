#!/bin/bash
# Worker自動報告スクリプト v2（ファイルベース状態管理対応）
# Stop hook で Claude Code セッション終了時に実行

source "/home/devuser/workspace/.claude/hooks/tmux_organization_utils.sh"
source "/home/devuser/workspace/.claude/hooks/organization_state_manager.sh"

# 組織活動状態の確認（ファイルベース）
if ! is_organization_active; then
    exit 0  # 組織活動が非アクティブの場合は何もしない
fi

# 現在のペイン情報を取得
get_current_pane_info

# Workerペインからの報告のみ処理
if ! is_worker_pane; then
    log_organization_state "AUTO_TASK_REPORT" "Not a worker pane, skipping report"
    exit 0
fi

# ProjectManagerペインで特定
PM_PANE=$(find_project_manager_pane)

if [[ -z "$PM_PANE" ]]; then
    log_organization_state "AUTO_TASK_REPORT" "ProjectManager pane not found"
    exit 1
fi

# 組織活動状態から情報を取得
ORGANIZATION_STATE_FILE="/home/devuser/workspace/.claude/organization_state.json"
SESSION_ID=$(jq -r '.session_id' "$ORGANIZATION_STATE_FILE" 2>/dev/null || echo "unknown")
STARTED_AT=$(jq -r '.started_at' "$ORGANIZATION_STATE_FILE" 2>/dev/null || echo "unknown")

# 作業状況の収集
WORK_DIR=$(pwd)
GIT_STATUS=""
BRANCH_INFO=""

# git情報の収集
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    BRANCH_INFO=$(git branch --show-current 2>/dev/null || echo "detached HEAD")
    COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    LAST_COMMIT=$(git log -1 --oneline 2>/dev/null || echo "No commits")
    
    # git statusの簡潔な要約
    if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
        GIT_STATUS="⚠️ Uncommitted changes detected"
    else
        GIT_STATUS="✅ Working directory clean"
    fi
fi

# タスク報告メッセージの構築
TASK_REPORT="📋 AUTOMATED TASK REPORT v2
Worker: ${PANE_TITLE} (pane-${CURRENT_PANE})
Session ended: $(date '+%Y-%m-%d %H:%M:%S')
Working directory: $WORK_DIR

Organization Context:
- Session ID: ${SESSION_ID}
- Started: ${STARTED_AT}
- State Management: File-based (no env vars)

Git Status:
- Branch: ${BRANCH_INFO}
- Status: ${GIT_STATUS}
- Last commit: ${LAST_COMMIT}
- Total commits: ${COMMIT_COUNT}

Next Actions Needed:
- Review completed work if necessary
- Merge branch if task complete
- Archive or cleanup if appropriate

🤖 Auto-reported via Claude Code Hooks v2"

# 報告メッセージの送信
if send_tmux_message "$PM_PANE" "$TASK_REPORT"; then
    echo "📢 Task completion reported to ProjectManager (pane-${PM_PANE})"
    log_organization_state "AUTO_TASK_REPORT" "Successfully sent task report to PM pane-$PM_PANE"
    
    # git worktreeブランチの場合はマージ推奨メッセージも送信
    if is_competitive_branch; then
        MERGE_SUGGESTION="💡 SUGGESTION: Branch '$BRANCH_INFO' appears to be a competitive worktree branch. 
Consider reviewing and merging if task is complete."
        send_tmux_message "$PM_PANE" "$MERGE_SUGGESTION"
    fi
else
    echo "❌ Failed to send task report"
    log_organization_state "AUTO_TASK_REPORT" "Failed to send task report"
    exit 1
fi

# 作業完了の記録をローカルファイルにも保存
REPORT_FILE="${HOME}/.claude/task_reports/$(date '+%Y%m%d_%H%M%S')_${PANE_TITLE}_report.txt"
mkdir -p "$(dirname "$REPORT_FILE")"
echo "$TASK_REPORT" > "$REPORT_FILE"

log_organization_state "AUTO_TASK_REPORT" "Task report saved to $REPORT_FILE"