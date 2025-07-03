#!/bin/bash
# 組織活動状態管理スクリプト（ファイルベース）
# 環境変数に依存しない、ペイン間で共有可能な状態管理

ORGANIZATION_STATE_FILE="/home/devuser/workspace/.claude/organization_state.json"
ORGANIZATION_LOG_FILE="/home/devuser/workspace/.claude/organization_activity.log"

# 組織活動状態を開始
start_organization_state() {
    local session_id="${1:-auto-$(date +%Y%m%d-%H%M%S)}"
    local initiator_pane="${2:-$(tmux display-message -p "#{pane_index}" 2>/dev/null || echo "unknown")}"
    
    # 状態ファイル作成
    cat > "$ORGANIZATION_STATE_FILE" <<EOF
{
  "active": true,
  "session_id": "$session_id",
  "started_at": "$(date -Iseconds)",
  "initiator_pane": "$initiator_pane",
  "panes": {},
  "hooks_activated": true,
  "auto_report_enabled": true
}
EOF
    
    # ログ記録
    log_organization_state "ORGANIZATION_START" "Session: $session_id, Initiator: pane-$initiator_pane"
    
    # hooks設定の自動切り替え
    activate_organization_hooks
    
    echo "✅ Organization state started: $session_id"
    return 0
}

# 組織活動状態を終了
stop_organization_state() {
    if [[ -f "$ORGANIZATION_STATE_FILE" ]]; then
        local session_id=$(jq -r '.session_id' "$ORGANIZATION_STATE_FILE" 2>/dev/null || echo "unknown")
        
        # 状態ファイル削除
        rm -f "$ORGANIZATION_STATE_FILE"
        
        # hooks設定の復元
        restore_original_hooks
        
        log_organization_state "ORGANIZATION_STOP" "Session: $session_id ended"
        echo "✅ Organization state stopped: $session_id"
    else
        echo "⚠️ Organization state not active"
    fi
    return 0
}

# 組織活動状態の確認
is_organization_active() {
    if [[ -f "$ORGANIZATION_STATE_FILE" ]]; then
        local active=$(jq -r '.active' "$ORGANIZATION_STATE_FILE" 2>/dev/null || echo "false")
        [[ "$active" == "true" ]]
    else
        return 1
    fi
}

# ペイン情報の登録
register_pane() {
    local pane_index="$1"
    local role="$2"
    local status="${3:-active}"
    
    if is_organization_active; then
        # 既存の状態ファイルを更新
        jq --arg pane "$pane_index" --arg role "$role" --arg status "$status" \
           '.panes[$pane] = {"role": $role, "status": $status, "updated_at": now | strftime("%Y-%m-%dT%H:%M:%SZ")}' \
           "$ORGANIZATION_STATE_FILE" > "${ORGANIZATION_STATE_FILE}.tmp" && \
        mv "${ORGANIZATION_STATE_FILE}.tmp" "$ORGANIZATION_STATE_FILE"
        
        log_organization_state "PANE_REGISTER" "pane-$pane_index: $role ($status)"
    fi
}

# hooks設定のアクティブ化
activate_organization_hooks() {
    local settings_dir="/home/devuser/workspace/.claude"
    local integrated_settings="$settings_dir/settings.integrated.json"
    local local_settings="$settings_dir/settings.local.json"
    local backup_settings="$settings_dir/settings.local.json.backup"
    
    if [[ -f "$integrated_settings" ]]; then
        # 既存設定のバックアップ
        if [[ -f "$local_settings" && ! -f "$backup_settings" ]]; then
            cp "$local_settings" "$backup_settings"
            log_organization_state "HOOKS_BACKUP" "Original settings backed up"
        fi
        
        # 統合設定の適用
        cp "$integrated_settings" "$local_settings"
        log_organization_state "HOOKS_ACTIVATE" "Organization hooks activated"
        return 0
    else
        log_organization_state "HOOKS_ERROR" "Integrated settings not found: $integrated_settings"
        return 1
    fi
}

# hooks設定の復元
restore_original_hooks() {
    local settings_dir="/home/devuser/workspace/.claude"
    local local_settings="$settings_dir/settings.local.json"
    local backup_settings="$settings_dir/settings.local.json.backup"
    
    if [[ -f "$backup_settings" ]]; then
        cp "$backup_settings" "$local_settings"
        rm -f "$backup_settings"
        log_organization_state "HOOKS_RESTORE" "Original hooks settings restored"
    else
        log_organization_state "HOOKS_WARNING" "No backup settings found to restore"
    fi
}

# ログ記録
log_organization_state() {
    local activity="$1"
    local details="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local pane_info="pane-$(tmux display-message -p "#{pane_index}" 2>/dev/null || echo "unknown")"
    
    echo "[$timestamp] $pane_info: $activity: $details" >> "$ORGANIZATION_LOG_FILE"
}

# 状態情報の表示
show_organization_status() {
    if is_organization_active; then
        echo "🎯 Organization Status: ACTIVE"
        echo "📋 Session: $(jq -r '.session_id' "$ORGANIZATION_STATE_FILE" 2>/dev/null)"
        echo "⏰ Started: $(jq -r '.started_at' "$ORGANIZATION_STATE_FILE" 2>/dev/null)"
        echo "🎛️ Hooks: $(jq -r '.hooks_activated' "$ORGANIZATION_STATE_FILE" 2>/dev/null)"
        echo ""
        echo "📱 Registered Panes:"
        jq -r '.panes | to_entries[] | "  pane-\(.key): \(.value.role) (\(.value.status))"' "$ORGANIZATION_STATE_FILE" 2>/dev/null || echo "  No panes registered"
    else
        echo "⚠️ Organization Status: INACTIVE"
        echo "💡 Start with: source /home/devuser/workspace/.claude/hooks/organization_state_manager.sh && start_organization_state <session_id>"
    fi
}

# メイン処理（コマンドライン引数による実行）
case "${1:-}" in
    "start")
        start_organization_state "$2" "$3"
        ;;
    "stop")
        stop_organization_state
        ;;
    "status")
        show_organization_status
        ;;
    "register")
        register_pane "$2" "$3" "$4"
        ;;
    "is_active")
        is_organization_active && echo "true" || echo "false"
        ;;
    *)
        echo "Usage: $0 {start|stop|status|register|is_active} [args...]"
        echo ""
        echo "Commands:"
        echo "  start [session_id] [pane]     - Start organization state"
        echo "  stop                          - Stop organization state"
        echo "  status                        - Show current status"
        echo "  register <pane> <role> [status] - Register pane with role"
        echo "  is_active                     - Check if organization is active"
        ;;
esac