#!/bin/bash
# git commit後のマージ要求スクリプト
# PostToolUse hook で git commit 成功後に実行

source "/home/devuser/workspace/.claude/hooks/tmux_organization_utils.sh"

# 組織活動文脈の確認
if ! is_organization_context; then
    exit 0  # 通常の作業では何もしない
fi

# 現在のペイン情報を取得
get_current_pane_info

# git環境でない場合はスキップ
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    exit 0
fi

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
WORK_DIR=$(pwd)

# Workerペインからの競争的ブランチコミットのみ処理
if ! is_worker_pane || ! is_competitive_branch; then
    log_organization_activity "POST_COMMIT_MERGE: Not a worker competitive branch commit, skipping"
    exit 0
fi

# ProjectManagerペインの特定
PM_PANE=$(find_project_manager_pane)

if [[ -z "$PM_PANE" ]]; then
    log_organization_activity "POST_COMMIT_MERGE: ProjectManager pane not found"
    exit 1
fi

# 最新コミット情報の取得
LATEST_COMMIT=$(git log -1 --oneline 2>/dev/null || echo "No commit info available")
COMMIT_HASH=$(git rev-parse HEAD 2>/dev/null | cut -c1-8)
COMMIT_MESSAGE=$(git log -1 --pretty=format:"%s" 2>/dev/null || echo "No message")
COMMIT_AUTHOR=$(git log -1 --pretty=format:"%an" 2>/dev/null || echo "Unknown")
COMMIT_TIME=$(git log -1 --pretty=format:"%ci" 2>/dev/null || echo "Unknown time")

# 変更ファイルの統計
CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null | wc -l)
INSERTIONS=$(git diff --stat HEAD~1 HEAD 2>/dev/null | tail -1 | grep -o '[0-9]\+ insertion' | cut -d' ' -f1 || echo "0")
DELETIONS=$(git diff --stat HEAD~1 HEAD 2>/dev/null | tail -1 | grep -o '[0-9]\+ deletion' | cut -d' ' -f1 || echo "0")

# ブランチ名から情報を抽出
if [[ "$CURRENT_BRANCH" =~ competitive_([a-zA-Z_]+)_([a-zA-Z0-9_]+)_([0-9]{8})_([0-9]{6}) ]]; then
    ROLE_INFO="${BASH_REMATCH[1]}"
    ISSUE_INFO="${BASH_REMATCH[2]}"
    DATE_INFO="${BASH_REMATCH[3]}"
    TIME_INFO="${BASH_REMATCH[4]}"
else
    ROLE_INFO="unknown"
    ISSUE_INFO="unknown"
    DATE_INFO="unknown"
    TIME_INFO="unknown"
fi

# マージ要求メッセージの構築
MERGE_REQUEST="🔀 MERGE REQUEST from ${PANE_TITLE}

Branch Information:
- Branch: $CURRENT_BRANCH
- Role: $ROLE_INFO
- Issue: $ISSUE_INFO
- Created: $DATE_INFO $TIME_INFO
- Working Directory: $WORK_DIR

Latest Commit:
- Hash: $COMMIT_HASH
- Message: $COMMIT_MESSAGE
- Author: $COMMIT_AUTHOR
- Time: $COMMIT_TIME

Changes Summary:
- Files changed: $CHANGED_FILES
- Insertions: ${INSERTIONS:-0}
- Deletions: ${DELETIONS:-0}

Merge Readiness Check:
$(if git diff --quiet HEAD~1 HEAD; then echo "⚠️ No changes in latest commit"; else echo "✅ Changes confirmed in latest commit"; fi)
$(if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then echo "⚠️ Working directory has uncommitted changes"; else echo "✅ Working directory clean"; fi)

Action Required:
Please review the changes and merge when appropriate.
Consider running tests before merging.
Ensure no conflicts with main branch.

Commands to review and merge:
1. cd $WORK_DIR
2. git log --oneline -3  # Review recent commits
3. git diff main..$CURRENT_BRANCH  # Review all changes
4. git checkout main && git merge $CURRENT_BRANCH  # Merge if approved"

# マージ要求の送信
if send_tmux_message "$PM_PANE" "$MERGE_REQUEST"; then
    echo "🔀 Merge request sent to ProjectManager (pane-${PM_PANE})"
    log_organization_activity "POST_COMMIT_MERGE: Sent merge request for branch '$CURRENT_BRANCH' to PM pane-$PM_PANE"
    
    # レビューチームにも通知（オプション）
    REVIEW_PANES=($(find_review_panes))
    if [[ ${#REVIEW_PANES[@]} -gt 0 ]]; then
        REVIEW_PANE=${REVIEW_PANES[0]}
        REVIEW_NOTIFICATION="📋 CODE REVIEW NOTIFICATION
New commit available for review on branch: $CURRENT_BRANCH
Commit: $LATEST_COMMIT
Worker: ${PANE_TITLE}
Merge request sent to ProjectManager."
        
        send_tmux_message "$REVIEW_PANE" "$REVIEW_NOTIFICATION"
        echo "📋 Review notification sent to pane-${REVIEW_PANE}"
    fi
else
    echo "❌ Failed to send merge request"
    log_organization_activity "POST_COMMIT_MERGE: Failed to send merge request for branch '$CURRENT_BRANCH'"
    exit 1
fi

# マージ要求履歴の保存
MERGE_LOG="${HOME}/.claude/merge_requests/$(date '+%Y%m%d_%H%M%S')_${CURRENT_BRANCH}_merge_request.txt"
mkdir -p "$(dirname "$MERGE_LOG")"
echo "$MERGE_REQUEST" > "$MERGE_LOG"

log_organization_activity "POST_COMMIT_MERGE: Merge request saved to $MERGE_LOG"