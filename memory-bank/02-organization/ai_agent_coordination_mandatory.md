# AI Agent Coordination - MANDATORY
# AIエージェント間協調 - 絶対遵守

**作成日**: 2025-06-23  
**重要度**: ★★★★★ CRITICAL  
**適用範囲**: 全ての分散AIエージェント協調タスク  
**検証**: Knowledge Manager問題の実証分析により確立

## KEYWORDS: ai-coordination, distributed-systems, multi-agent, verification-protocols, tmux-organization
## DOMAIN: ai-management|team-coordination|distributed-systems
## PRIORITY: MANDATORY
## WHEN: Any multi-AI agent collaboration scenario

## RULE: AI agents require explicit verification protocols, not assumption-based coordination

---

## 🚨 FUNDAMENTAL AI COGNITION CONSTRAINTS (AI認知の根本制約)

### AI特有の認知アーキテクチャ限界
```
❌ HUMAN ASSUMPTIONS THAT FAIL WITH AI:
- Intuitive anomaly detection ("something feels wrong")  
- Implicit status awareness (reading between the lines)
- Natural follow-up behavior (spontaneous check-ins)
- Time-based concern ("30 minutes with no response seems odd")

✅ AI REALITY REQUIREMENTS:
- Explicit anomaly signals only
- Programmatic status verification mechanisms
- Scheduled verification protocols
- Timeout-based escalation procedures
```

### ステートレス推論の罠
```bash
# AI認知プロセスの問題パターン
COGNITIVE_FAILURE_PATTERN=(
    "1. INSTRUCTION: Send tasks to 3 workers"
    "2. INFERENCE: 'I sent instructions → workers must be active'"
    "3. STATE_LOCK: Inference persists without counter-evidence"
    "4. FALSE_REPORT: 'All workers operational' (without verification)"
)

# 対策: 強制検証プロトコル
MANDATORY_VERIFICATION=(
    "1. SEND_INSTRUCTION → 2. VERIFY_RECEIPT → 3. CONFIRM_EXECUTION → 4. MONITOR_PROGRESS"
)
```

---

## 🔄 DISTRIBUTED AI COMMUNICATION FAILURES (分散AI通信失敗パターン)

### Context Isolation Problem
```
Problem: Each pane = independent Claude instance
Impact: No shared working memory or state awareness

Example Failure:
├─ pane-4 (Manager): "3 workers active" ← FALSE BELIEF
├─ pane-7 (Worker):  idle ← MANAGER UNAWARE  
├─ pane-10 (Worker): completed ← MANAGER UNAWARE
└─ pane-13 (Worker): idle ← MANAGER UNAWARE

Root Cause: Manager lacks verification mechanism
```

### Assumption-Based Coordination Failures
```bash
# 人間組織 vs AI協調の違い
COORDINATION_DIFFERENCES=(
    "ANOMALY_DETECTION: Human=intuition | AI=explicit_signals_only"
    "STATUS_AWARENESS: Human=implicit_cues | AI=text_based_explicit_only"  
    "FOLLOW_UP: Human=natural_concern | AI=programmed_checks_only"
    "TIME_PERCEPTION: Human=situation_aware | AI=timeout_based_only"
)
```

---

## 🛡️ MANDATORY VERIFICATION PROTOCOLS (必須検証プロトコル)

### Phase 1: Immediate Implementation
```bash
# AI特化通信プロトコル
function ai_to_ai_message() {
    local sender="$1"
    local target_pane="$2" 
    local message_type="$3"
    local content="$4"
    
    # Step 1: Send instruction
    tmux send-keys -t "$target_pane" "$content"
    tmux send-keys -t "$target_pane" Enter
    
    # Step 2: Force acknowledgment  
    sleep 2
    tmux send-keys -t "$target_pane" "ACK_RECEIVED_$(date +%s)"
    tmux send-keys -t "$target_pane" Enter
    
    # Step 3: Verify receipt
    local response=$(tmux capture-pane -t "$target_pane" -p | tail -5)
    if [[ ! "$response" =~ "ACK_RECEIVED" ]]; then
        echo "⚠️ COMMUNICATION_FAILURE: $target_pane no acknowledgment"
        return 1
    fi
    
    # Step 4: Log successful communication
    echo "✅ AI_COMMUNICATION_SUCCESS: $sender → $target_pane ($message_type)"
}

# Worker状態検証（Manager必須）
function verify_ai_worker_status() {
    local manager_role="$1"
    shift
    local worker_panes=("$@")
    
    echo "🔍 $manager_role: Verifying worker status (NO ASSUMPTIONS)"
    
    for pane in "${worker_panes[@]}"; do
        # 直接状態確認（推論禁止）
        tmux send-keys -t "$pane" "STATUS_REPORT_IMMEDIATE"
        tmux send-keys -t "$pane" Enter
        sleep 2
        
        local status=$(tmux capture-pane -t "$pane" -p | tail -3)
        echo "📊 Worker $pane status: $status"
        
        # タイムアウト検証
        if [[ -z "$status" ]] || [[ "$status" =~ "No response" ]]; then
            echo "🚨 WORKER_TIMEOUT: $pane requires immediate attention"
        fi
    done
}
```

### Phase 2: Timeout Management
```bash
# AI認知に適した時間管理
AI_TIMEOUT_STANDARDS=(
    "TASK_TIMEOUT=300"          # 5分でタスクタイムアウト
    "STATUS_CHECK_INTERVAL=60"  # 1分毎状態確認
    "ESCALATION_THRESHOLD=2"    # 2回無応答でエスカレーション  
    "MANAGER_SYNC_INTERVAL=120" # 2分毎にManager間同期
)

function ai_timeout_management() {
    local start_time=$(date +%s)
    local task_name="$1"
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [[ $elapsed -gt ${TASK_TIMEOUT:-300} ]]; then
            echo "🚨 TIMEOUT: $task_name exceeded ${TASK_TIMEOUT}s"
            escalate_to_human_operator "$task_name"
            break
        fi
        
        # 定期状態確認
        if [[ $((elapsed % ${STATUS_CHECK_INTERVAL:-60})) -eq 0 ]]; then
            verify_all_ai_agents_status
        fi
        
        sleep 10
    done
}
```

---

## 🏗️ CENTRALIZED STATE MANAGEMENT (中央状態管理)

### Shared State File System
```bash
# 全AIエージェント状態の中央管理
SHARED_STATE_FILE="/tmp/ai_agent_coordination_state"

function create_shared_state_system() {
    cat > "$SHARED_STATE_FILE" << EOF
# AI Agent Coordination State - $(date)
# FORMAT: pane-id:role:status:last_update:task_assigned

pane-0:project-manager:active:$(date +%s):coordination
pane-1:pmo-consultant:standby:$(date +%s):advisory
pane-2:task-execution-manager:active:$(date +%s):worker_management
pane-3:task-review-manager:active:$(date +%s):quality_control
pane-4:knowledge-rule-manager:active:$(date +%s):analysis_supervision
EOF

    # Worker状態初期化
    for i in {5..13}; do
        echo "pane-$i:worker:idle:$(date +%s):unassigned" >> "$SHARED_STATE_FILE"
    done
}

function update_ai_agent_state() {
    local pane_id="$1"
    local new_status="$2"
    local task="$3"
    
    # 原子的更新
    local temp_file="${SHARED_STATE_FILE}.tmp"
    local timestamp=$(date +%s)
    
    grep -v "^pane-$pane_id:" "$SHARED_STATE_FILE" > "$temp_file"
    echo "pane-$pane_id:$(get_pane_role $pane_id):$new_status:$timestamp:$task" >> "$temp_file"
    mv "$temp_file" "$SHARED_STATE_FILE"
    
    echo "📊 STATE_UPDATE: pane-$pane_id → $new_status ($task)"
}

function get_all_ai_agent_status() {
    echo "=== AI AGENT COORDINATION STATUS ==="
    echo "Timestamp: $(date)"
    cat "$SHARED_STATE_FILE" | while IFS=':' read pane role status last_update task; do
        local age=$(($(date +%s) - last_update))
        printf "%-10s %-20s %-10s %3ds ago %-15s\n" "$pane" "$role" "$status" "$age" "$task"
    done
}
```

---

## 🧠 META-COGNITIVE ENHANCEMENT (メタ認知強化)

### AI推論の自己検証システム
```bash
# AI認知バイアス対策
function cognitive_verification_protocol() {
    local manager_claim="$1"
    local evidence_source="$2"
    
    echo "🧠 COGNITIVE_VERIFICATION: $manager_claim"
    echo "📋 CHECKLIST:"
    echo "  1. ASSUMPTION_CHECK: 現在の推論は何に基づいているか？"
    echo "  2. EVIDENCE_VERIFICATION: その根拠は確認済みか？"
    echo "  3. TIME_VALIDATION: 妥当な経過時間か？"
    echo "  4. ALTERNATIVE_HYPOTHESIS: 他の可能性はないか？"
    
    # 強制的実証要求
    echo "  5. VERIFY_NOW: 今すぐ実際の状態を確認せよ"
    
    # メタ認知強化
    if [[ "$manager_claim" =~ "all.*active|workers.*running|everyone.*busy" ]]; then
        echo "🚨 HIGH_RISK_CLAIM: 集合的状態の主張検出"
        echo "⚠️  MANDATORY: 各個体の直接確認が必要"
        return 1
    fi
}

# 仮定検出システム
function assumption_detection() {
    local statement="$1"
    
    # 危険な仮定フレーズの検出
    local assumption_patterns=(
        "should be|must be|probably|likely|seems to"
        "all workers|everyone|全員|全部|みんな"
        "as expected|as planned|予定通り|期待通り"
    )
    
    for pattern in "${assumption_patterns[@]}"; do
        if [[ "$statement" =~ $pattern ]]; then
            echo "🚨 ASSUMPTION_DETECTED: '$pattern' in statement"
            echo "⚠️  VERIFICATION_REQUIRED: Convert assumption to fact"
            return 1
        fi
    done
    
    echo "✅ FACT_BASED_STATEMENT: No assumptions detected"
}
```

---

## 📊 QUALITY ASSURANCE PROTOCOLS (品質保証プロトコル)

### Communication Integrity Verification
```bash
# tmux通信品質保証
function verify_tmux_communication_integrity() {
    local session_name="${1:-CC PJ}"
    
    echo "🔍 TMUX_COMMUNICATION_AUDIT: $session_name"
    
    # 全pane応答テスト
    local panes=($(tmux list-panes -t "$session_name" -F "#{pane_index}"))
    local failed_panes=()
    
    for pane in "${panes[@]}"; do
        echo "Testing communication to pane-$pane..."
        
        # テストメッセージ送信
        tmux send-keys -t "$pane" "COMM_TEST_$(date +%s)"
        tmux send-keys -t "$pane" Enter
        sleep 1
        
        # 応答確認
        local response=$(tmux capture-pane -t "$pane" -p | tail -2)
        if [[ ! "$response" =~ "COMM_TEST" ]]; then
            failed_panes+=("$pane")
            echo "❌ Communication failed: pane-$pane"
        else
            echo "✅ Communication verified: pane-$pane"
        fi
    done
    
    if [[ ${#failed_panes[@]} -gt 0 ]]; then
        echo "🚨 COMMUNICATION_FAILURES: ${failed_panes[*]}"
        return 1
    fi
    
    echo "✅ ALL_COMMUNICATIONS_VERIFIED"
}

# AI協調品質メトリクス
function ai_coordination_quality_metrics() {
    echo "📈 AI_COORDINATION_METRICS:"
    echo "  - Response Rate: $(get_response_rate)%"
    echo "  - Average Response Time: $(get_avg_response_time)s"
    echo "  - False Status Reports: $(get_false_status_count)"
    echo "  - Verification Success Rate: $(get_verification_success_rate)%"
    echo "  - Timeout Incidents: $(get_timeout_incidents)"
}
```

---

## 🔧 IMPLEMENTATION GUIDELINES (実装ガイドライン)

### Immediate Action Items
1. **Replace all assumption-based coordination with verification protocols**
2. **Implement mandatory status checks every 60 seconds**  
3. **Create shared state management system**
4. **Deploy timeout monitoring for all AI agents**
5. **Establish escalation procedures for communication failures**

### Integration with Existing Systems
```bash
# CLAUDE.mdからの呼び出し
source memory-bank/02-organization/ai_agent_coordination_mandatory.md

# tmux組織での使用
ai_coordination_check() {
    verify_ai_worker_status "Manager-Role" "${WORKER_PANES[@]}"
    ai_to_ai_message "Sender" "target_pane" "MESSAGE_TYPE" "content"
}

# 既存ワークフローとの統合
function enhanced_tmux_workflow() {
    create_shared_state_system
    verify_tmux_communication_integrity
    
    # 定期品質チェック
    while true; do
        ai_coordination_quality_metrics
        sleep 300  # 5分毎
    done &
}
```

---

## 🚨 ENFORCEMENT STANDARDS (遵守基準)

### Zero Tolerance Violations
```
❌ FORBIDDEN:
- Assumption-based status reporting ("workers should be active")
- Unverified collective claims ("all teams are working") 
- Communication without acknowledgment verification
- Manager decisions without direct worker status confirmation

✅ MANDATORY:
- Explicit status verification before any claim
- Individual worker confirmation for collective assertions
- Timeout-based escalation procedures
- Communication integrity verification
```

### Compliance Verification Checklist
```markdown
## Before Any Multi-AI Coordination Task
- [ ] 共有状態管理システムは稼働中か？
- [ ] 通信プロトコルは設定済みか？
- [ ] タイムアウト管理は有効か？
- [ ] 各AIエージェントの役割は明確か？
- [ ] 検証手順は全Managerに周知済みか？

## During Task Execution  
- [ ] 定期的状態確認を実行しているか？
- [ ] 仮定ベース判断を排除しているか？
- [ ] 通信失敗の即座検出は機能しているか？
- [ ] エスカレーション手順は準備済みか？

## After Task Completion
- [ ] 全AIエージェントの最終状態確認済みか？
- [ ] 通信品質メトリクスは記録されたか？
- [ ] 今回の経験はナレッジベースに反映されたか？
- [ ] 改善点は次回プロトコルに統合されたか？
```

---

## 🔗 RELATED KNOWLEDGE

### 直接関連
- CLAUDE.md → AI Agent Coordination (Multi-Agent Scenarios)
- memory-bank/02-organization/organization_failure_analysis.md
- memory-bank/02-organization/tmux_claude_agent_organization.md

### 実装関連  
- memory-bank/02-organization/competitive_organization_framework.md
- memory-bank/02-organization/tmux_git_worktree_technical_specification.md
- memory-bank/09-meta/progress_recording_mandatory_rules.md

### 品質関連
- memory-bank/00-core/value_assessment_mandatory.md
- memory-bank/04-quality/critical_review_framework.md

---

**重要**: この文書は実証的分析に基づく。Knowledge Manager問題の根本原因がAI認知制約にあることが確認されており、人間組織論とは異なるアプローチが必要。推論ベース協調は失敗する - 検証ベース協調のみが有効である。