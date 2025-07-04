#!/bin/bash
# Claude Code Hooks for tmux Organization - テストスクリプト

echo "🧪 Testing Claude Code Hooks for tmux Organization"
echo "=================================================="

# 基本環境確認
echo ""
echo "1. 基本環境確認"
echo "----------------"

# tmux環境確認
if command -v tmux >/dev/null 2>&1; then
    echo "✅ tmux: $(tmux -V)"
    if [[ -n "$TMUX" ]]; then
        echo "✅ tmux session: active"
        echo "   Session: $(tmux display-message -p "#{session_name}" 2>/dev/null)"
        echo "   Pane: $(tmux display-message -p "#{pane_index}" 2>/dev/null)"
    else
        echo "⚠️ tmux session: not active (testing outside tmux)"
    fi
else
    echo "❌ tmux: not installed"
fi

# git環境確認
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "✅ git repository: $(pwd)"
    echo "   Branch: $(git branch --show-current)"
else
    echo "⚠️ git repository: not detected"
fi

# Claude設定ディレクトリ確認
echo ""
echo "2. Claude設定ファイル確認"
echo "------------------------"

SETTINGS_DIR="/home/devuser/workspace/.claude"
if [[ -d "$SETTINGS_DIR" ]]; then
    echo "✅ Claude settings directory: $SETTINGS_DIR"
    ls -la "$SETTINGS_DIR" | grep -E "\.(json|sh)$" | while read -r line; do
        echo "   $line"
    done
else
    echo "❌ Claude settings directory: not found"
fi

# Hooksスクリプト確認
echo ""
echo "3. Hooksスクリプト確認"
echo "---------------------"

HOOKS_DIR="$SETTINGS_DIR/hooks"
if [[ -d "$HOOKS_DIR" ]]; then
    echo "✅ Hooks directory: $HOOKS_DIR"
    
    REQUIRED_SCRIPTS=(
        "tmux_organization_utils.sh"
        "auto_review_trigger.sh"
        "auto_task_report.sh"
        "pre_commit_worktree_check.sh"
        "post_commit_merge_request.sh"
        "start_organization_context.sh"
        "stop_organization_context.sh"
    )
    
    for script in "${REQUIRED_SCRIPTS[@]}"; do
        script_path="$HOOKS_DIR/$script"
        if [[ -f "$script_path" ]]; then
            if [[ -x "$script_path" ]]; then
                echo "   ✅ $script (executable)"
            else
                echo "   ⚠️ $script (not executable)"
            fi
        else
            echo "   ❌ $script (missing)"
        fi
    done
else
    echo "❌ Hooks directory: not found"
fi

# 環境変数確認
echo ""
echo "4. 組織活動環境変数確認"
echo "----------------------"

if [[ -n "$TMUX_ORGANIZATION_CONTEXT" ]]; then
    echo "✅ TMUX_ORGANIZATION_CONTEXT: $TMUX_ORGANIZATION_CONTEXT"
    echo "✅ TMUX_ORGANIZATION_SESSION: ${TMUX_ORGANIZATION_SESSION:-not set}"
    echo "✅ TMUX_ORGANIZATION_ROLE: ${TMUX_ORGANIZATION_ROLE:-not set}"
    echo "   → Organization context is ACTIVE"
else
    echo "⚠️ Organization context: not active"
    echo "   To activate: source $HOOKS_DIR/start_organization_context.sh <issue_id> [role]"
fi

# 機能テスト
echo ""
echo "5. 機能テスト"
echo "------------"

# ユーティリティ関数テスト
if [[ -f "$HOOKS_DIR/tmux_organization_utils.sh" ]]; then
    echo "Testing utility functions..."
    source "$HOOKS_DIR/tmux_organization_utils.sh"
    
    get_current_pane_info
    echo "   Current pane: ${CURRENT_PANE:-unknown}"
    echo "   Pane title: ${PANE_TITLE:-unknown}"
    
    if is_organization_context; then
        echo "   ✅ Organization context: detected"
    else
        echo "   ⚠️ Organization context: not detected"
    fi
    
    if is_worker_pane; then
        echo "   ✅ Worker pane: detected"
    else
        echo "   ⚠️ Worker pane: not detected"
    fi
else
    echo "❌ Cannot test utility functions (tmux_organization_utils.sh missing)"
fi

# 設定ファイルのJSON検証
echo ""
echo "6. 設定ファイル検証"
echo "------------------"

for settings_file in "$SETTINGS_DIR"/*.json; do
    if [[ -f "$settings_file" ]]; then
        filename=$(basename "$settings_file")
        if python3 -m json.tool "$settings_file" >/dev/null 2>&1; then
            echo "   ✅ $filename: valid JSON"
        else
            echo "   ❌ $filename: invalid JSON"
        fi
    fi
done

# ログディレクトリ確認
echo ""
echo "7. ログディレクトリ確認"
echo "---------------------"

LOG_DIRS=(
    "${HOME}/.claude/task_reports"
    "${HOME}/.claude/merge_requests"
)

for log_dir in "${LOG_DIRS[@]}"; do
    if [[ -d "$log_dir" ]]; then
        file_count=$(find "$log_dir" -type f | wc -l)
        echo "   ✅ $log_dir ($file_count files)"
    else
        echo "   ⚠️ $log_dir (not created yet)"
    fi
done

LOG_FILE="${HOME}/.claude/tmux_organization.log"
if [[ -f "$LOG_FILE" ]]; then
    line_count=$(wc -l < "$LOG_FILE")
    echo "   ✅ Activity log: $LOG_FILE ($line_count lines)"
else
    echo "   ⚠️ Activity log: not created yet"
fi

# 使用方法表示
echo ""
echo "8. クイックスタートガイド"
echo "------------------------"
echo "組織活動を開始するには:"
echo "   source $HOOKS_DIR/start_organization_context.sh issue-123 TaskExecutionWorker"
echo ""
echo "組織活動を終了するには:"
echo "   source $HOOKS_DIR/stop_organization_context.sh"
echo ""
echo "詳細な使用方法:"
echo "   cat $HOOKS_DIR/README.md"

echo ""
echo "🧪 Test completed!"
echo "=================="