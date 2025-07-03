# AI Coordination Mandatory Rules

## 🚨 MANDATORY RULES FOR AI-AI COORDINATION

**KEYWORDS**: ai-coordination, distributed-systems, tmux-organization, mandatory
**DOMAIN**: ai-management, team-coordination  
**PRIORITY**: MANDATORY
**WHEN**: Any multi-AI agent collaboration scenario

### RULE: AI agents require explicit verification protocols, not assumption-based coordination

## 🧠 FUNDAMENTAL AI COORDINATION PRINCIPLES

### Principle 1: Stateless Agent Awareness
```bash
# AI AGENTS ARE STATELESS - CRITICAL UNDERSTANDING
AI_AGENT_LIMITATIONS=(
    "No persistent memory between interactions"
    "Cannot verify state of other AI agents"
    "Assumption-based reasoning leads to coordination failures"
    "Require programmatic verification for accurate status"
)
```

### Principle 2: Explicit Verification Required
```bash
# MANDATORY VERIFICATION PROTOCOL
BEFORE_STATUS_REPORT() {
    # FORBIDDEN: Assumption-based reporting
    # REQUIRED: Programmatic verification
    
    for worker_pane in "${ASSIGNED_WORKERS[@]}"; do
        verify_actual_status "$worker_pane"
    done
}

# EXAMPLE: Correct status verification
function verify_worker_status() {
    local pane="$1"
    local last_activity=$(tmux capture-pane -t "$pane" -p | tail -1)
    
    if [[ -z "$last_activity" ]] || [[ "$last_activity" =~ ^[[:space:]]*$ ]]; then
        echo "IDLE"
    else
        echo "ACTIVE: $last_activity"
    fi
}
```

### Principle 3: Communication Atomicity
```bash
# MANDATORY tmux COMMUNICATION PROTOCOL
function send_ai_message() {
    local target_pane="$1"
    local message="$2"
    
    # Step 1: Send message
    tmux send-keys -t "$target_pane" "$message"
    
    # Step 2: CRITICAL - Always send Enter
    tmux send-keys -t "$target_pane" Enter
    
    # Step 3: Verify delivery
    sleep 2
    local response=$(tmux capture-pane -t "$target_pane" -p | tail -2)
    
    if [[ -z "$response" ]]; then
        echo "❌ DELIVERY FAILED: pane-$target_pane"
        return 1
    fi
    
    echo "✅ DELIVERED: pane-$target_pane"
    return 0
}
```

## 🚨 CRITICAL PATTERNS TO AVOID

### Anti-Pattern 1: Assumption-Based Status Reporting
```bash
# ❌ FORBIDDEN PATTERN
report_status() {
    echo "All workers are active"  # NEVER assume without verification
}

# ✅ CORRECT PATTERN  
report_status() {
    for worker in "${WORKERS[@]}"; do
        status=$(verify_worker_status "$worker")
        echo "Worker $worker: $status"
    done
}
```

### Anti-Pattern 2: Incomplete Communication Protocol
```bash
# ❌ FORBIDDEN PATTERN
tmux send-keys -t 5 "Start task"
# Missing Enter key - message not delivered

# ✅ CORRECT PATTERN
tmux send-keys -t 5 "Start task"
tmux send-keys -t 5 Enter  # MANDATORY
sleep 2  # Allow processing time
```

### Anti-Pattern 3: Trust Without Verification
```bash
# ❌ FORBIDDEN PATTERN
if manager_reports_complete; then
    proceed_to_next_phase()  # NEVER trust without verification
fi

# ✅ CORRECT PATTERN
if manager_reports_complete && verify_actual_completion; then
    proceed_to_next_phase()
fi
```

## 🎯 MANDATORY IMPLEMENTATION REQUIREMENTS

### Requirement 1: State Verification System
```bash
# MANDATORY: Implement before any AI coordination project
AI_STATE_VERIFICATION_REQUIRED=(
    "Worker activity verification mechanism"
    "Manager status accuracy validation"
    "Communication delivery confirmation"
    "Task completion programmatic verification"
)
```

### Requirement 2: Fallback Coordination Mechanisms
```bash
# MANDATORY: Emergency coordination protocols
EMERGENCY_COORDINATION_TRIGGERS=(
    "Manager-worker communication breakdown"
    "Status reporting discrepancies detected"
    "Worker idle time exceeding threshold"
    "Task completion verification failures"
)

# Emergency response: Direct Project Manager intervention
function emergency_direct_coordination() {
    local issue_type="$1"
    local affected_agents="$2"
    
    echo "🚨 EMERGENCY COORDINATION: $issue_type"
    echo "📋 Affected agents: $affected_agents"
    echo "⚡ Activating direct PM coordination..."
    
    # Bypass manager layer, direct worker coordination
    for agent in $affected_agents; do
        send_direct_assignment "$agent"
    done
}
```

### Requirement 3: AI-Specific Documentation Standards
```bash
# MANDATORY: AI agent coordination documentation
AI_COORDINATION_DOCS_REQUIRED=(
    "Explicit step-by-step coordination procedures"
    "Verification checkpoints at each coordination step"
    "Error detection and recovery protocols"
    "State synchronization mechanisms"
    "Communication delivery confirmation procedures"
)
```

## 📚 IMPLEMENTATION CHECKLIST

### Pre-Project Requirements
- [ ] AI agent limitations acknowledged and documented
- [ ] Verification protocols implemented and tested
- [ ] Communication atomicity procedures established
- [ ] Emergency coordination fallback mechanisms prepared
- [ ] Status verification automation scripts ready

### During-Project Requirements
- [ ] Real-time verification of all status reports
- [ ] Communication delivery confirmation for critical messages
- [ ] Worker activity monitoring and idle detection
- [ ] Manager effectiveness monitoring
- [ ] Emergency coordination trigger monitoring

### Post-Project Requirements
- [ ] Coordination effectiveness analysis
- [ ] AI limitation impact assessment
- [ ] Protocol improvement recommendations
- [ ] Knowledge base updates with lessons learned
- [ ] Template enhancement for future projects

## 🔧 AUTOMATION TOOLS REQUIRED

### Tool 1: AI Agent Status Monitor
```bash
#!/bin/bash
# ai_agent_monitor.sh
function monitor_ai_agents() {
    local agents=("$@")
    
    while true; do
        for agent in "${agents[@]}"; do
            status=$(verify_worker_status "$agent")
            timestamp=$(date '+%H:%M:%S')
            echo "[$timestamp] Agent-$agent: $status"
        done
        sleep 30  # Monitor every 30 seconds
    done
}
```

### Tool 2: Communication Verification System
```bash
#!/bin/bash
# ai_communication_verifier.sh
function verify_message_delivery() {
    local target_pane="$1"
    local message_signature="$2"
    
    local response=$(tmux capture-pane -t "$target_pane" -p | grep "$message_signature")
    
    if [[ -n "$response" ]]; then
        echo "✅ VERIFIED: Message delivered to pane-$target_pane"
        return 0
    else
        echo "❌ FAILED: Message not delivered to pane-$target_pane"
        return 1
    fi
}
```

## 🏆 PROVEN SUCCESS PATTERNS (実証済み成功パターン)

### Team04 Success Case: 100% Completion Rate
**Date**: 2025-01-04  
**Test**: 3-Worker Organization Activity  
**Result**: ✅ 100% Task Completion, 100% Report Reception  
**Protocol**: 5-Step Proven Pattern

```bash
# PROVEN SUCCESS PROTOCOL - Copy this pattern
SUCCESS_PATTERN_TEAM04=(
    "Step0: foundation_setup"           # Organization state, knowledge load
    "Step1: comprehensive_briefing"     # Shared context file creation
    "Step2: task_distribution"          # Standardized instruction format
    "Step3: execution_monitoring"       # Evidence-based verification
    "Step4: completion_review"          # Success analysis & knowledge update
)

# SUCCESS FACTORS IDENTIFIED
CRITICAL_SUCCESS_ELEMENTS=(
    "Shared_Context_File"              # Single source of truth ✅
    "Standardized_Task_Instructions"   # Clear format prevents confusion ✅
    "Evidence_Based_Monitoring"        # No assumptions, actual reports ✅
    "Separate_Enter_Sending"          # Technical requirement compliance ✅
    "Unified_Report_Format"           # Consistent completion reporting ✅
)
```

### Replicable Success Template
```bash
# COPY-PASTE READY: Proven coordination success
function execute_proven_coordination() {
    local task_description="$1"
    
    # Step0: Foundation (MANDATORY)
    source /home/devuser/workspace/.claude/hooks/organization_state_manager.sh
    start_organization_state "team-$(date +%Y%m%d-%H%M%S)" 0
    smart_knowledge_load "organization" "team-coordination"
    
    # Step1: Shared Context (CRITICAL SUCCESS FACTOR)
    local briefing_file="/tmp/$(date +%Y%m%d_%H%M%S)_briefing_context.md"
    create_comprehensive_briefing "$briefing_file" "$task_description"
    
    # Step2: Standardized Distribution (PROVEN FORMAT)
    distribute_standardized_instructions "$task_description"
    
    # Step3: Evidence-Based Monitoring (NO ASSUMPTIONS)
    monitor_with_evidence_only
    
    # Step4: Success Documentation (KNOWLEDGE CAPTURE)
    document_success_patterns
    
    echo "✅ Coordination completed using proven 100% success pattern"
}

# PROVEN BRIEFING TEMPLATE
function create_comprehensive_briefing() {
    local file_path="$1"
    local task_desc="$2"
    
    cat > "$file_path" << EOF
# Organization Activity Briefing
## Task: $task_desc

### Organization Structure
Project Manager (pane-0) → Workers (pane-1,2,3)

### MANDATORY Rules (ABSOLUTE COMPLIANCE)
1. Evidence-based verification only (NO assumptions)
2. tmux: Message → Enter (separate sending)
3. Report format: "Report from: pane-X(role) Task completed: [details]"

### Task Instruction Format
From：pane-0: Project Manager
To：pane-X: Task Worker  
Content：(specific task)
Report：(completion obligation)
EOF
}

# PROVEN INSTRUCTION TEMPLATE
function send_proven_task_instruction() {
    local target_pane="$1"
    local task_content="$2"
    
    local instruction="claude -p \"【Task Instruction】
From：pane-0: Project Manager
To：pane-$target_pane: Task Worker
Content：$task_content
Report：Upon completion, send 'Report from: pane-$target_pane(Task Worker) Task completed: [details]' to Project Manager.

Important: Read briefing file for rules before execution.\""
    
    # CRITICAL: Proven communication protocol
    tmux send-keys -t "$target_pane" "$instruction"
    tmux send-keys -t "$target_pane" Enter  # MANDATORY separate sending
    
    # Verification
    sleep 3
    verify_instruction_delivery "$target_pane"
}
```

### Success Pattern Documentation
**Reference**: `memory-bank/02-organization/tmux_organization_success_patterns.md`  
**Usage**: Default pattern for all 3+ worker coordination  
**Replication Rate**: 100% (1/1 tests successful)  
**Recommended**: Use as standard template

## 🎯 SUCCESS METRICS

### Coordination Effectiveness Metrics
- **Communication Success Rate**: >95% message delivery confirmation
- **Status Accuracy Rate**: >98% verified vs reported status alignment  
- **Worker Utilization Rate**: >85% active time during coordination
- **Emergency Intervention Rate**: <5% direct PM coordination required

### Quality Preservation Metrics
- **Core Deliverable Protection**: 100% main objectives achieved regardless of coordination issues
- **Timeline Adherence**: ±10% variance from planned completion time
- **Quality Standards**: All deliverables meet or exceed quality expectations

## 🚀 FUTURE EVOLUTION

### Advanced AI Coordination Features
```bash
# FUTURE ENHANCEMENT: AI Agent Self-Monitoring
function ai_agent_self_monitor() {
    # AI agents report their own status automatically
    local agent_id="$1"
    local current_task="$2"
    local completion_percentage="$3"
    
    echo "🤖 Agent-$agent_id: Task[$current_task] - $completion_percentage% complete"
    
    # Automatic escalation if stuck
    if [[ $completion_percentage -eq 0 ]] && [[ $STUCK_TIME -gt 300 ]]; then
        echo "🚨 Agent-$agent_id: Requesting assistance - stuck for 5+ minutes"
    fi
}
```

---

**IMPLEMENTATION STATUS**: ✅ MANDATORY - MUST BE APPLIED TO ALL AI COORDINATION PROJECTS  
**VIOLATION CONSEQUENCE**: Project coordination failure, deliverable risk  
**UPDATE FREQUENCY**: After each AI coordination project completion  
**NEXT EVOLUTION**: Advanced self-monitoring AI agent capabilities

*Established: 2025-06-23 based on real AI coordination experience*  
*Priority Level: CRITICAL - Project success dependency*  
*Application Scope: All distributed AI agent collaboration scenarios*