#!/bin/bash
# 自動レビュー依頼スクリプト
# PostToolUse hook で Write|Edit|MultiEdit 後に実行

source "/home/devuser/workspace/.claude/hooks/tmux_organization_utils.sh"

FILE_PATH="$1"
WORKER_PANE="$2"

# 組織活動文脈の確認
if ! is_organization_context; then
    exit 0  # 通常の作業では何もしない
fi

# 現在のペイン情報を取得
get_current_pane_info

# ファイルパスの検証
if [[ -z "$FILE_PATH" || ! -f "$FILE_PATH" ]]; then
    log_organization_activity "AUTO_REVIEW_TRIGGER: Invalid file path: $FILE_PATH"
    exit 1
fi

# レビューチームペインの特定
REVIEW_PANES=($(find_review_panes))

if [[ ${#REVIEW_PANES[@]} -eq 0 ]]; then
    log_organization_activity "AUTO_REVIEW_TRIGGER: No review panes found"
    # ProjectManagerに通知
    PM_PANE=$(find_project_manager_pane)
    if [[ -n "$PM_PANE" ]]; then
        send_tmux_message "$PM_PANE" "⚠️ Review team unavailable for file: $FILE_PATH"
    fi
    exit 1
fi

# 最初の利用可能なレビューペインを選択
REVIEW_PANE=${REVIEW_PANES[0]}

# ファイルタイプに応じたレビュー内容の決定
get_review_focus() {
    case "$1" in
        *.py) echo "Code quality, security, test coverage" ;;
        *.js|*.ts) echo "Code quality, performance, type safety" ;;
        *.md) echo "Documentation clarity, accuracy, completeness" ;;
        *.json|*.yaml|*.yml) echo "Configuration correctness, security" ;;
        *) echo "General review" ;;
    esac
}

REVIEW_FOCUS=$(get_review_focus "$FILE_PATH")
RELATIVE_PATH=$(realpath --relative-to="$(pwd)" "$FILE_PATH" 2>/dev/null || echo "$FILE_PATH")

# レビュー依頼メッセージの構築と送信
REVIEW_MESSAGE="🔍 REVIEW REQUEST for: $RELATIVE_PATH
Focus areas: $REVIEW_FOCUS
Modified by: ${PANE_TITLE:-unknown} at $(date '+%Y-%m-%d %H:%M:%S')
File size: $(stat -c%s "$FILE_PATH" 2>/dev/null || echo "unknown") bytes

Please review and provide feedback. Reply with 'REVIEW_COMPLETE' when done."

if send_tmux_message "$REVIEW_PANE" "$REVIEW_MESSAGE"; then
    echo "✅ Review request sent to pane-${REVIEW_PANE}"
    log_organization_activity "AUTO_REVIEW_TRIGGER: Sent review request for $RELATIVE_PATH to pane-$REVIEW_PANE"
    
    # ProjectManagerにも通知
    PM_PANE=$(find_project_manager_pane)
    if [[ -n "$PM_PANE" ]]; then
        send_tmux_message "$PM_PANE" "📋 Review requested: $RELATIVE_PATH → pane-$REVIEW_PANE"
    fi
else
    echo "❌ Failed to send review request"
    log_organization_activity "AUTO_REVIEW_TRIGGER: Failed to send review request for $RELATIVE_PATH"
    exit 1
fi