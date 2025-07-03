#!/bin/bash
# Worker自動報告スクリプト
# Stop hook で Claude Code セッション終了時に実行

source "/home/devuser/workspace/.claude/hooks/tmux_organization_utils.sh"

# 組織活動文脈の確認
if ! is_organization_context; then
    exit 0  # 通常の作業では何もしない
fi

# 現在のペイン情報を取得
get_current_pane_info

# Workerペインからの報告のみ処理
if ! is_worker_pane; then
    log_organization_activity "AUTO_TASK_REPORT: Not a worker pane, skipping report"
    exit 0
fi

# ProjectManagerペインで特定
PM_PANE=$(find_project_manager_pane)

if [[ -z "$PM_PANE" ]]; then
    log_organization_activity "AUTO_TASK_REPORT: ProjectManager pane not found"
    exit 1
fi

# 作業状況の収集
WORK_DIR=$(pwd)
SESSION_DURATION="Unknown"
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
TASK_REPORT="📋 TASK SESSION REPORT
Worker: ${PANE_TITLE}
Session ended: $(date '+%Y-%m-%d %H:%M:%S')
Working directory: $WORK_DIR

Git Status:
- Branch: ${BRANCH_INFO}
- Status: ${GIT_STATUS}
- Last commit: ${LAST_COMMIT}
- Total commits: ${COMMIT_COUNT}

Session Context:
- Organization: ${TMUX_ORGANIZATION_CONTEXT}
- Session: ${TMUX_ORGANIZATION_SESSION:-unknown}
- Role: ${TMUX_ORGANIZATION_ROLE:-${PANE_TITLE}}

Next Actions Needed:
- Review completed work if necessary
- Merge branch if task complete
- Archive or cleanup if appropriate"

# 報告メッセージの送信
if send_tmux_message "$PM_PANE" "$TASK_REPORT"; then
    echo "📢 Task completion reported to ProjectManager (pane-${PM_PANE})"
    log_organization_activity "AUTO_TASK_REPORT: Successfully sent task report to PM pane-$PM_PANE"
    
    # git worktreeブランチの場合はマージ推奨メッセージも送信
    if is_competitive_branch; then
        MERGE_SUGGESTION="💡 SUGGESTION: Branch '$BRANCH_INFO' appears to be a competitive worktree branch. 
Consider reviewing and merging if task is complete."
        send_tmux_message "$PM_PANE" "$MERGE_SUGGESTION"
    fi
else
    echo "❌ Failed to send task report"
    log_organization_activity "AUTO_TASK_REPORT: Failed to send task report"
    exit 1
fi

# 作業完了の記録をローカルファイルにも保存
REPORT_FILE="${HOME}/.claude/task_reports/$(date '+%Y%m%d_%H%M%S')_${PANE_TITLE}_report.txt"
mkdir -p "$(dirname "$REPORT_FILE")"
echo "$TASK_REPORT" > "$REPORT_FILE"

log_organization_activity "AUTO_TASK_REPORT: Task report saved to $REPORT_FILE"