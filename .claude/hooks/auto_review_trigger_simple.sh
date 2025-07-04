#!/bin/bash
# 自動レビュー依頼スクリプト（シンプル版）
# Team4組織活動に特化

FILE_PATH="$1"
WORKER_PANE="$2"

# ファイルパスの検証
if [[ -z "$FILE_PATH" || ! -f "$FILE_PATH" ]]; then
    echo "❌ Invalid file path: $FILE_PATH"
    exit 1
fi

# Team4組織活動での固定ペイン指定
PROJECT_MANAGER_PANE="0"
REVIEW_WORKER_PANE="2"

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

# レビュー依頼メッセージの構築
REVIEW_MESSAGE="🔍 REVIEW REQUEST for: $RELATIVE_PATH
Focus areas: $REVIEW_FOCUS
Modified at $(date '+%Y-%m-%d %H:%M:%S')
File size: $(stat -c%s "$FILE_PATH" 2>/dev/null || echo "unknown") bytes

Please review and provide feedback."

# tmuxメッセージ送信関数
send_message() {
    local target_pane="$1"
    local message="$2"
    
    if tmux send-keys -t "$target_pane" "$message" 2>/dev/null; then
        tmux send-keys -t "$target_pane" Enter 2>/dev/null
        return 0
    else
        return 1
    fi
}

# レビュー依頼の送信
if send_message "$REVIEW_WORKER_PANE" "$REVIEW_MESSAGE"; then
    echo "✅ Review request sent to pane-${REVIEW_WORKER_PANE}"
    
    # Project Managerにも通知
    PM_NOTIFICATION="📋 Review requested: $RELATIVE_PATH → pane-$REVIEW_WORKER_PANE"
    send_message "$PROJECT_MANAGER_PANE" "$PM_NOTIFICATION"
    echo "📋 Notification sent to Project Manager (pane-${PROJECT_MANAGER_PANE})"
else
    echo "❌ Failed to send review request to pane-${REVIEW_WORKER_PANE}"
    exit 1
fi