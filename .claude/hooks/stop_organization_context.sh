#!/bin/bash
# tmux組織活動コンテキスト終了スクリプト

# 環境変数のクリア
unset TMUX_ORGANIZATION_CONTEXT
unset TMUX_ORGANIZATION_SESSION
unset TMUX_ORGANIZATION_ROLE

# 通常の設定ファイルに戻す（バックアップがある場合）
SETTINGS_DIR="/home/devuser/workspace/.claude"
LOCAL_SETTINGS="$SETTINGS_DIR/settings.local.json"
BACKUP_SETTINGS="$SETTINGS_DIR/settings.local.json.backup"

if [[ -f "$BACKUP_SETTINGS" ]]; then
    mv "$BACKUP_SETTINGS" "$LOCAL_SETTINGS"
    echo "✅ Restored original Claude settings from backup"
else
    echo "⚠️ No backup settings found - organization settings remain active"
fi

# 終了ログの記録
LOG_FILE="${HOME}/.claude/tmux_organization.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ORGANIZATION_STOP: Session ended" >> "$LOG_FILE"

echo "🛑 tmux Organization Context Stopped"
echo "   Environment variables cleared"
echo "   Hooks deactivated"
echo ""
echo "Session summary available in:"
echo "   Log: $LOG_FILE"
echo "   Task reports: ${HOME}/.claude/task_reports/"
echo "   Merge requests: ${HOME}/.claude/merge_requests/"