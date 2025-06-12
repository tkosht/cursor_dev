#!/bin/bash
# 組織統制強化システム - 統合ラッパースクリプト
# 13ペイン階層組織の確実な運営を技術的に保証

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENFORCEMENT_SYSTEM="${SCRIPT_DIR}/enforced_reporting_system.py"
HIERARCHY_CHECK="${SCRIPT_DIR}/hierarchy_violation_check.py"
LOG_FILE="/tmp/organizational_enforcement.log"

# 色付きログ出力
log() {
    echo -e "\033[36m[$(date '+%H:%M:%S')]\033[0m $*" | tee -a "$LOG_FILE"
}

error() {
    echo -e "\033[31m[ERROR]\033[0m $*" | tee -a "$LOG_FILE"
}

success() {
    echo -e "\033[32m[SUCCESS]\033[0m $*" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "\033[33m[WARNING]\033[0m $*" | tee -a "$LOG_FILE"
}

# 13ペイン階層組織の定義
declare -A HIERARCHY=(
    [0]="1,2,3"        # Project Manager → Managers
    [1]="4,7,10"       # Task Manager → Task Workers
    [2]="5,8,11"       # Review Manager → Review Workers  
    [3]="6,9,12"       # Knowledge Manager → Knowledge Workers
)

declare -A ROLE_NAMES=(
    [0]="Project Manager"
    [1]="Task Manager"
    [2]="Review Manager"
    [3]="Knowledge Manager"
    [4]="Task Execution Worker"
    [5]="Review Worker"
    [6]="Knowledge Worker"
    [7]="Task Execution Worker"
    [8]="Review Worker"
    [9]="Knowledge Worker"
    [10]="Task Execution Worker"
    [11]="Review Worker"
    [12]="Knowledge Worker"
)

# 階層遵守チェック
check_hierarchy_compliance() {
    local executor=$1
    local target=$2
    
    if python3 "$HIERARCHY_CHECK" check "$executor" "$target" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 安全なtmux送信（階層チェック付き）
safe_tmux_send() {
    local executor_pane=$1
    local target_pane=$2
    local message="$3"
    
    log "Checking hierarchy compliance: pane-$executor_pane → pane-$target_pane"
    
    if check_hierarchy_compliance "$executor_pane" "$target_pane"; then
        success "✅ Hierarchy compliant - sending message"
        tmux send-keys -t "$target_pane" "$message"
        tmux send-keys -t "$target_pane" Enter
        return 0
    else
        error "🚨 Hierarchy violation detected: pane-$executor_pane → pane-$target_pane"
        error "Blocked unauthorized communication"
        return 1
    fi
}

# 強制報告付きタスク開始
start_enforced_task() {
    local worker_pane=$1
    local task_name="$2"
    local task_details="$3"
    
    log "Starting enforced task for Worker pane-$worker_pane"
    log "Task: $task_name"
    
    # 階層構造確認
    local manager_pane=""
    for mgr in 1 2 3; do
        local subordinates="${HIERARCHY[$mgr]}"
        if [[ ",$subordinates," == *",$worker_pane,"* ]]; then
            manager_pane=$mgr
            break
        fi
    done
    
    if [[ -z "$manager_pane" ]]; then
        error "No manager found for Worker pane-$worker_pane"
        return 1
    fi
    
    log "Manager for Worker pane-$worker_pane: pane-$manager_pane (${ROLE_NAMES[$manager_pane]})"
    
    # 強制報告システムでタスク開始
    local task_id
    task_id=$(python3 "$ENFORCEMENT_SYSTEM" start_task "$worker_pane" "$task_name" "$task_details" | grep -o 'task_[0-9_]*' | head -1)
    
    if [[ -n "$task_id" ]]; then
        success "✅ Enforced task $task_id started for Worker pane-$worker_pane"
        success "Automatic monitoring and escalation activated"
        echo "$task_id"
        return 0
    else
        error "Failed to start enforced task"
        return 1
    fi
}

# Manager責任強化システム
enforce_manager_responsibilities() {
    local manager_pane=$1
    
    log "Enforcing responsibilities for Manager pane-$manager_pane"
    
    case $manager_pane in
        1)
            local subordinates="4,7,10"
            local role="Task Manager"
            ;;
        2)
            local subordinates="5,8,11"
            local role="Review Manager"
            ;;
        3)
            local subordinates="6,9,12"
            local role="Knowledge Manager"
            ;;
        *)
            error "Invalid manager pane: $manager_pane"
            return 1
            ;;
    esac
    
    # Manager責任の技術的強制
    local enforcement_message="🎯 MANAGER RESPONSIBILITY ENFORCEMENT ACTIVATED

You are ${role} (pane-${manager_pane}) with the following MANDATORY responsibilities:

📋 SUBORDINATE MANAGEMENT:
├── Monitor Workers: panes ${subordinates}
├── Confirm all Worker reports within 3 minutes
├── Provide support when Workers need assistance
└── Ensure 100% Worker compliance

📊 REPORTING OBLIGATIONS:
├── Submit aggregated reports to Project Manager
├── Report any Worker compliance issues immediately
├── Maintain 95%+ subordinate performance rate
└── Respond to Project Manager requests within 2 minutes

🚨 ENFORCEMENT ACTIVE:
├── All actions are monitored and logged
├── Non-compliance triggers automatic escalation
├── Performance metrics tracked continuously
└── Manager score affects organizational rating

Your management effectiveness is being measured. Maintain excellence."

    tmux send-keys -t "$manager_pane" "$enforcement_message"
    tmux send-keys -t "$manager_pane" Enter
    
    success "✅ Manager responsibilities enforced for pane-$manager_pane"
    
    # 継続監視の開始
    start_manager_monitoring "$manager_pane" "$subordinates" &
}

# Manager継続監視
start_manager_monitoring() {
    local manager_pane=$1
    local subordinates="$2"
    
    log "Starting continuous monitoring for Manager pane-$manager_pane"
    
    while true; do
        # 配下Worker状況確認
        IFS=',' read -ra SUB_ARRAY <<< "$subordinates"
        for sub in "${SUB_ARRAY[@]}"; do
            # Worker活動確認
            if ! check_worker_wellness "$sub"; then
                warning "Worker pane-$sub may need attention"
                
                # Manager に通知
                tmux send-keys -t "$manager_pane" "⚠️ ATTENTION: Worker pane-$sub may need your assistance. Please check and respond."
                tmux send-keys -t "$manager_pane" Enter
            fi
        done
        
        sleep 120  # 2分間隔監視
    done
}

# Worker健全性確認
check_worker_wellness() {
    local worker_pane=$1
    
    # 最新活動確認
    local recent_output
    recent_output=$(tmux capture-pane -t "$worker_pane" -p 2>/dev/null | tail -5)
    
    # 基本的なレスポンス確認
    if [[ ${#recent_output} -gt 10 ]]; then
        return 0  # 活動あり
    else
        return 1  # 活動不足
    fi
}

# 組織全体監視開始
start_organizational_monitoring() {
    log "🚀 Starting comprehensive organizational monitoring"
    
    # 強制報告システム監視開始
    python3 "$ENFORCEMENT_SYSTEM" start_monitor &
    local enforcement_pid=$!
    
    # 各Manager責任強化
    for manager in 1 2 3; do
        enforce_manager_responsibilities "$manager"
    done
    
    success "✅ Organizational monitoring fully activated"
    success "Target compliance rate: 95%+"
    success "All enforcement systems online"
    
    # 統合ダッシュボード表示
    display_integrated_dashboard &
    
    echo "$enforcement_pid" > /tmp/org_monitoring.pid
}

# 統合ダッシュボード
display_integrated_dashboard() {
    while true; do
        clear
        echo "============================================================"
        echo "🚀 ORGANIZATIONAL ENFORCEMENT DASHBOARD"
        echo "============================================================"
        echo "Timestamp: $(date)"
        echo ""
        
        # 階層遵守状況
        echo "📊 HIERARCHY COMPLIANCE:"
        if [[ -f hierarchy_violations.log ]]; then
            local violations=$(wc -l < hierarchy_violations.log)
            echo "├── Hierarchy Violations: $violations"
        else
            echo "├── Hierarchy Violations: 0"
        fi
        
        # 報告システム状況
        echo "├── Enforcement System: $(check_enforcement_status)"
        
        # 各Manager状況
        echo "├── Manager Status:"
        for mgr in 1 2 3; do
            local mgr_status=$(get_manager_status "$mgr")
            echo "│   ├── ${ROLE_NAMES[$mgr]} (pane-$mgr): $mgr_status"
        done
        
        echo ""
        echo "🎯 COMPLIANCE REPORT:"
        python3 "$ENFORCEMENT_SYSTEM" report 2>/dev/null | grep -E "(compliance_rate|status)" | sed 's/^/├── /'
        
        echo ""
        echo "============================================================"
        
        sleep 300  # 5分間隔更新
    done
}

# システム状況確認
check_enforcement_status() {
    if pgrep -f "enforced_reporting_system.py" >/dev/null; then
        echo "🟢 ACTIVE"
    else
        echo "🔴 INACTIVE"
    fi
}

# Manager状況取得
get_manager_status() {
    local manager_pane=$1
    
    # Manager応答確認
    if check_worker_wellness "$manager_pane"; then
        echo "🟢 Active"
    else
        echo "🔴 Inactive"
    fi
}

# 組織監視停止
stop_organizational_monitoring() {
    log "Stopping organizational monitoring..."
    
    if [[ -f /tmp/org_monitoring.pid ]]; then
        local pid=$(cat /tmp/org_monitoring.pid)
        if ps -p "$pid" > /dev/null; then
            kill "$pid" 2>/dev/null
        fi
        rm -f /tmp/org_monitoring.pid
    fi
    
    python3 "$ENFORCEMENT_SYSTEM" stop_monitor 2>/dev/null
    
    # 監視プロセス終了
    pkill -f "start_manager_monitoring" 2>/dev/null
    pkill -f "display_integrated_dashboard" 2>/dev/null
    
    success "✅ Organizational monitoring stopped"
}

# 使用方法表示
usage() {
    cat << EOF
🚀 Organizational Enforcement System

USAGE:
    $0 <command> [options]

COMMANDS:
    start_task <worker_pane> "<task_name>" "<task_details>"
        強制報告付きタスクを開始

    enforce_manager <manager_pane>
        Manager責任を技術的に強制

    start_monitoring
        組織全体の監視を開始

    stop_monitoring
        組織監視を停止

    dashboard
        リアルタイムダッシュボード表示

    safe_send <executor_pane> <target_pane> "<message>"
        階層チェック付き安全送信

    test_compliance
        コンプライアンステスト実行

EXAMPLES:
    # Worker pane-4 に強制報告付きタスクを開始
    $0 start_task 4 "Greeting Task" "Say hello to the team"

    # Task Manager (pane-1) の責任を強制
    $0 enforce_manager 1

    # 組織全体監視開始
    $0 start_monitoring

    # ダッシュボード表示
    $0 dashboard

TARGET: 報告義務遵守率95%以上達成
EOF
}

# メイン処理
main() {
    if [[ $# -eq 0 ]]; then
        usage
        exit 1
    fi

    local command=$1
    shift

    case $command in
        start_task)
            if [[ $# -ge 3 ]]; then
                start_enforced_task "$1" "$2" "$3"
            else
                error "Usage: $0 start_task <worker_pane> <task_name> <task_details>"
                exit 1
            fi
            ;;
        enforce_manager)
            if [[ $# -ge 1 ]]; then
                enforce_manager_responsibilities "$1"
            else
                error "Usage: $0 enforce_manager <manager_pane>"
                exit 1
            fi
            ;;
        start_monitoring)
            start_organizational_monitoring
            ;;
        stop_monitoring)
            stop_organizational_monitoring
            ;;
        dashboard)
            python3 "$ENFORCEMENT_SYSTEM" dashboard
            ;;
        safe_send)
            if [[ $# -ge 3 ]]; then
                safe_tmux_send "$1" "$2" "$3"
            else
                error "Usage: $0 safe_send <executor_pane> <target_pane> <message>"
                exit 1
            fi
            ;;
        test_compliance)
            log "Running compliance test..."
            # 簡単なコンプライアンステスト
            start_enforced_task 4 "Compliance Test" "Test the enforcement system"
            ;;
        *)
            error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"