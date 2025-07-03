#!/bin/bash
# tmux組織活動コンテキスト開始スクリプト

ISSUE_ID="$1"
ROLE="$2"

if [[ -z "$ISSUE_ID" ]]; then
    echo "Usage: $0 <issue_id> [role]"
    echo "Example: $0 issue-123 TaskExecutionWorker"
    exit 1
fi

# 環境変数の設定
export TMUX_ORGANIZATION_CONTEXT="competitive_framework"
export TMUX_ORGANIZATION_SESSION="$ISSUE_ID"
export TMUX_ORGANIZATION_ROLE="${ROLE:-auto-detected}"

# Claude設定ファイルの切り替え
SETTINGS_DIR="/home/devuser/workspace/.claude"
INTEGRATED_SETTINGS="$SETTINGS_DIR/settings.integrated.json"
LOCAL_SETTINGS="$SETTINGS_DIR/settings.local.json"
BACKUP_SETTINGS="$SETTINGS_DIR/settings.local.json.backup"

if [[ -f "$INTEGRATED_SETTINGS" ]]; then
    # 既存のlocal設定をバックアップ
    if [[ -f "$LOCAL_SETTINGS" && ! -f "$BACKUP_SETTINGS" ]]; then
        cp "$LOCAL_SETTINGS" "$BACKUP_SETTINGS"
        echo "✅ Backed up existing settings to $(basename "$BACKUP_SETTINGS")"
    fi
    
    # 統合設定ファイルを適用
    cp "$INTEGRATED_SETTINGS" "$LOCAL_SETTINGS"
    echo "✅ Switched to tmux organization hooks configuration (integrated)"
else
    echo "⚠️ Integrated organization hooks configuration not found"
fi

# ログディレクトリの準備
mkdir -p "${HOME}/.claude/task_reports"
mkdir -p "${HOME}/.claude/merge_requests"

# 開始ログの記録
LOG_FILE="${HOME}/.claude/tmux_organization.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ORGANIZATION_START: Issue=$ISSUE_ID, Role=$ROLE, Session=$(tmux display-message -p "#{session_name}" 2>/dev/null || echo "unknown")" >> "$LOG_FILE"

echo "🚀 tmux Organization Context Started"
echo "   Issue: $ISSUE_ID"
echo "   Role: $ROLE"
echo "   Session: $(tmux display-message -p "#{session_name}" 2>/dev/null || echo "unknown")"
echo "   Pane: $(tmux display-message -p "#{pane_index}" 2>/dev/null || echo "unknown")"
echo ""
echo "Environment variables set:"
echo "   TMUX_ORGANIZATION_CONTEXT=$TMUX_ORGANIZATION_CONTEXT"
echo "   TMUX_ORGANIZATION_SESSION=$TMUX_ORGANIZATION_SESSION"
echo "   TMUX_ORGANIZATION_ROLE=$TMUX_ORGANIZATION_ROLE"
echo ""
echo "Hooks active for:"
echo "   📝 Auto review trigger on file modifications"
echo "   📢 Auto task reports on session end"
echo "   🔀 Auto merge requests on git commits"
echo "   ⚠️ Pre-commit validation for worktree branches"
echo ""
echo "To stop organization context:"
echo "   source /home/devuser/workspace/.claude/hooks/stop_organization_context.sh"