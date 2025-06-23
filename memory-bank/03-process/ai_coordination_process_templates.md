# AI Coordination Process Templates

---
KEYWORDS: ai-coordination, process-template, tmux-management, multi-agent, automation
DOMAIN: process
PRIORITY: HIGH
WHEN: Setting up multi-agent AI coordination projects requiring systematic management
---

## RULE: Standardized templates ensure consistent, reliable AI agent coordination across projects

## TEMPLATE 1: Project Initialization

### **Complete Project Setup Script**
```bash
#!/bin/bash
# ai_project_setup.sh - Complete AI coordination project initialization

set -euo pipefail

PROJECT_NAME="${1:-ai-coordination-project}"
echo "🏗️ AI Coordination Project Setup: $PROJECT_NAME"
echo "===================================================="

# Phase 0: Environment validation
echo "🔍 Phase 0: Environment Validation"
command -v tmux >/dev/null || { echo "❌ tmux required but not installed"; exit 1; }
command -v git >/dev/null || { echo "❌ git required but not installed"; exit 1; }
echo "✅ Environment validation passed"

# Phase 1: Work management protocol
echo "🔍 Phase 1: Work Management Protocol"
current_branch=$(git branch --show-current)
if [[ "$current_branch" == "main" ]] || [[ "$current_branch" == "master" ]]; then
    echo "🚨 CRITICAL: Currently on main branch"
    echo "📋 Creating task branch: task/${PROJECT_NAME}"
    git checkout -b "task/${PROJECT_NAME}" || exit 1
    echo "✅ Task branch created and checked out"
else
    echo "✅ Work management verified: Active on '$current_branch'"
fi

# Phase 2: Knowledge loading setup
echo "🔍 Phase 2: Knowledge Loading Setup"
function setup_knowledge_loading() {
    echo "🧠 Setting up smart knowledge loading..."
    
    # Verify knowledge base structure
    if [[ ! -d "memory-bank" ]]; then
        echo "⚠️ No memory-bank directory found"
        mkdir -p memory-bank/{00-core,01-cognee,02-organization,03-process,09-meta}
        echo "✅ Memory bank structure created"
    fi
    
    # Create smart loading function
    cat > smart_knowledge_load.sh << 'EOF'
#!/bin/bash
# Smart Knowledge Loading Function

function smart_knowledge_load() {
    local domain="$1"
    local task_context="${2:-general}"
    echo "⚡ SMART: Quick Knowledge Loading for: $domain"
    echo "📅 Date: $(date '+%Y-%m-%d %H:%M')"
    
    # Domain-specific search
    echo "🔍 Domain search: $domain"
    find memory-bank/ -name "*${domain}*.md" -o -name "*mandatory*.md" | head -5
    
    # Essential constraints
    echo "🚨 Core rules check:"
    ls memory-bank/00-core/*mandatory*.md 2>/dev/null | head -5
    
    echo "✅ Smart Loading Complete (5-15s)"
}

# Export function for use
export -f smart_knowledge_load
EOF
    
    chmod +x smart_knowledge_load.sh
    echo "✅ Knowledge loading system ready"
}

setup_knowledge_loading

# Phase 3: tmux coordination session
echo "🔍 Phase 3: tmux Coordination Session"
function setup_coordination_session() {
    local session_name="coord-${PROJECT_NAME}"
    
    # Create or attach to session
    if tmux has-session -t "$session_name" 2>/dev/null; then
        echo "📋 Session '$session_name' already exists"
    else
        echo "🎯 Creating coordination session: $session_name"
        tmux new-session -d -s "$session_name" -c "$PWD"
        
        # Setup manager pane (pane-0)
        tmux send-keys -t "$session_name:0" "echo 'Project Manager - pane-0 active'" Enter
        
        # Create additional panes as needed
        tmux split-window -h -t "$session_name:0"
        tmux send-keys -t "$session_name:0.1" "echo 'Worker pane-1 active'" Enter
        
        echo "✅ Coordination session '$session_name' created"
    fi
    
    echo "📊 Session status:"
    tmux list-sessions | grep "$session_name" || echo "No matching sessions"
}

setup_coordination_session

# Phase 4: Communication protocol activation
echo "🔍 Phase 4: Communication Protocol"
function setup_communication_protocol() {
    cat > tmux_communication.sh << 'EOF'
#!/bin/bash
# Enhanced tmux Communication Protocol v2.0

function send_tmux_message() {
    local pane="$1"
    local message="$2"
    local session="${3:-coord-project}"
    
    echo "📡 Sending message to $session:$pane"
    
    # Send message
    tmux send-keys -t "$session:$pane" "$message"
    
    # CRITICAL: Always send Enter
    tmux send-keys -t "$session:$pane" Enter
    
    # Verification (2-3 second rule)
    sleep 2
    local response=$(tmux capture-pane -t "$session:$pane" -p | tail -3)
    
    if [[ -z "$response" ]]; then
        echo "⚠️ WARNING: No response from $session:$pane"
        return 1
    fi
    
    echo "✅ Message delivered to $session:$pane"
    return 0
}

function verify_worker_status() {
    local session="$1"
    local panes=("${@:2}")
    
    echo "📋 Worker Status Verification"
    for pane in "${panes[@]}"; do
        local activity=$(tmux capture-pane -t "$session:$pane" -p | tail -1)
        local timestamp=$(date '+%H:%M:%S')
        
        if [[ -z "$activity" ]] || [[ "$activity" =~ (idle|inactive) ]]; then
            echo "[$timestamp] ⚠️ Pane $pane: IDLE"
        else
            echo "[$timestamp] ✅ Pane $pane: ACTIVE"
        fi
    done
}

function emergency_direct_assignment() {
    local worker_pane="$1"
    local task="$2"
    local session="${3:-coord-project}"
    
    echo "🚨 EMERGENCY: Direct assignment to $session:$worker_pane"
    send_tmux_message "$worker_pane" "
🚨 EMERGENCY DIRECT ASSIGNMENT
From: Project Manager
Task: $task
Priority: IMMEDIATE
Report: Direct to manager upon completion
" "$session"
}

# Export functions
export -f send_tmux_message
export -f verify_worker_status
export -f emergency_direct_assignment
EOF
    
    chmod +x tmux_communication.sh
    echo "✅ Communication protocol ready"
}

setup_communication_protocol

echo ""
echo "✅ AI Coordination Project Setup Complete!"
echo "=========================================="
echo "🎯 Project: $PROJECT_NAME"
echo "🔧 Branch: $(git branch --show-current)"
echo "📊 Session: coord-${PROJECT_NAME}"
echo ""
echo "🚀 Next Steps:"
echo "1. Source knowledge loading: source smart_knowledge_load.sh"
echo "2. Source communication: source tmux_communication.sh" 
echo "3. Attach to session: tmux attach -t coord-${PROJECT_NAME}"
echo "4. Start your project tasks!"
```

## TEMPLATE 2: Communication Protocol Implementation

### **Enhanced tmux Communication Functions**
```bash
#!/bin/bash
# tmux_communication_enhanced.sh - Production-ready communication protocol

# Global configuration
COMMUNICATION_TIMEOUT=3
VERIFICATION_DELAY=2
MAX_RETRIES=3

function send_tmux_message_with_retry() {
    local pane="$1"
    local message="$2"
    local session="${3:-default}"
    local retries=0
    
    while [[ $retries -lt $MAX_RETRIES ]]; do
        echo "📡 Attempt $((retries + 1)): Sending to $session:$pane"
        
        # Send message
        tmux send-keys -t "$session:$pane" "$message" 2>/dev/null
        
        # CRITICAL: Always send Enter
        tmux send-keys -t "$session:$pane" Enter 2>/dev/null
        
        # Verification with timeout
        sleep $VERIFICATION_DELAY
        local response=$(tmux capture-pane -t "$session:$pane" -p 2>/dev/null | tail -3)
        
        if [[ -n "$response" ]] && [[ ! "$response" =~ ^[[:space:]]*$ ]]; then
            echo "✅ Message delivered to $session:$pane (attempt $((retries + 1)))"
            return 0
        fi
        
        ((retries++))
        echo "⚠️ Retry $retries/$MAX_RETRIES for $session:$pane"
        sleep 1
    done
    
    echo "❌ FAILED: Could not deliver message to $session:$pane after $MAX_RETRIES attempts"
    return 1
}

function batch_worker_status_check() {
    local session="$1"
    shift
    local panes=("$@")
    
    echo "📋 Batch Worker Status Check - Session: $session"
    echo "================================================"
    
    local active_count=0
    local idle_count=0
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    for pane in "${panes[@]}"; do
        local activity=$(tmux capture-pane -t "$session:$pane" -p 2>/dev/null | tail -1)
        
        if [[ -z "$activity" ]] || [[ "$activity" =~ (idle|inactive|waiting) ]]; then
            echo "[$timestamp] ⚠️ Pane $pane: IDLE"
            ((idle_count++))
        else
            echo "[$timestamp] ✅ Pane $pane: ACTIVE - $(echo "$activity" | cut -c1-50)..."
            ((active_count++))
        fi
    done
    
    echo "================================================"
    echo "📊 Summary: $active_count active, $idle_count idle"
    
    # Return status based on activity
    [[ $active_count -gt 0 ]]
}

function coordinated_task_assignment() {
    local session="$1"
    local task_description="$2"
    shift 2
    local worker_panes=("$@")
    
    echo "🎯 Coordinated Task Assignment"
    echo "Session: $session"
    echo "Task: $task_description"
    echo "Workers: ${worker_panes[*]}"
    echo "=============================="
    
    # Pre-assignment status check
    batch_worker_status_check "$session" "${worker_panes[@]}"
    
    # Assign tasks to available workers
    local assignment_count=0
    for pane in "${worker_panes[@]}"; do
        local worker_status=$(tmux capture-pane -t "$session:$pane" -p 2>/dev/null | tail -1)
        
        if [[ "$worker_status" =~ (idle|ready|waiting) ]] || [[ -z "$worker_status" ]]; then
            echo "📋 Assigning to pane $pane..."
            
            local assignment_message="
🎯 TASK ASSIGNMENT
From: Coordination Manager
Task: $task_description
Priority: NORMAL
Time: $(date '+%H:%M:%S')
Report: Status update every 5 minutes
"
            
            if send_tmux_message_with_retry "$pane" "$assignment_message" "$session"; then
                ((assignment_count++))
                echo "✅ Task assigned to pane $pane"
            else
                echo "❌ Failed to assign task to pane $pane"
            fi
        else
            echo "⚠️ Pane $pane appears busy, skipping"
        fi
    done
    
    echo "=============================="
    echo "📊 Assignment complete: $assignment_count workers assigned"
    
    # Post-assignment verification
    sleep 3
    batch_worker_status_check "$session" "${worker_panes[@]}"
}
```

## TEMPLATE 3: Quality Assurance Integration

### **Comprehensive QA Pipeline**
```bash
#!/bin/bash
# qa_integration.sh - Complete quality assurance pipeline

# Quality gate configuration
COVERAGE_THRESHOLD=85
COMPLEXITY_LIMIT=10
LINE_LENGTH=79

function pre_execution_validation() {
    echo "🚨 PRE-EXECUTION VALIDATION CHECKLIST"
    echo "======================================"
    
    local validation_passed=true
    
    # Security check
    echo -n "0. SECURITY: No credential exposure risk? "
    read -p "(y/N): " security_check
    if [[ ! "$security_check" =~ ^[Yy]$ ]]; then
        echo "❌ Security validation failed"
        validation_passed=false
    else
        echo "✅ Security validated"
    fi
    
    # Value assessment
    echo -n "1. USER VALUE: Serves user interests primarily? "
    read -p "(y/N): " value_check
    if [[ ! "$value_check" =~ ^[Yy]$ ]]; then
        echo "❌ Value assessment failed"
        validation_passed=false
    else
        echo "✅ Value assessment passed"
    fi
    
    # Sustainability check
    echo -n "2. SUSTAINABILITY: Long-term solution approach? "
    read -p "(y/N): " sustainability_check
    if [[ ! "$sustainability_check" =~ ^[Yy]$ ]]; then
        echo "❌ Sustainability check failed"
        validation_passed=false
    else
        echo "✅ Sustainability validated"
    fi
    
    # Fact-based verification
    echo -n "3. EVIDENCE: Based on verified facts, not speculation? "
    read -p "(y/N): " evidence_check
    if [[ ! "$evidence_check" =~ ^[Yy]$ ]]; then
        echo "❌ Evidence verification failed"
        validation_passed=false
    else
        echo "✅ Evidence-based approach confirmed"
    fi
    
    # Knowledge loading verification
    echo -n "4. KNOWLEDGE: Domain knowledge loaded and verified? "
    read -p "(y/N): " knowledge_check
    if [[ ! "$knowledge_check" =~ ^[Yy]$ ]]; then
        echo "❌ Knowledge loading incomplete"
        validation_passed=false
    else
        echo "✅ Knowledge base validated"
    fi
    
    # Alternative evaluation
    echo -n "5. ALTERNATIVES: Best approach selected after comparison? "
    read -p "(y/N): " alternatives_check
    if [[ ! "$alternatives_check" =~ ^[Yy]$ ]]; then
        echo "❌ Alternative evaluation incomplete"
        validation_passed=false
    else
        echo "✅ Alternative evaluation completed"
    fi
    
    echo "======================================"
    
    if [[ "$validation_passed" == "true" ]]; then
        echo "✅ PRE-EXECUTION VALIDATION PASSED"
        return 0
    else
        echo "❌ PRE-EXECUTION VALIDATION FAILED"
        echo "🚨 Address failed validations before proceeding"
        return 1
    fi
}

function automated_quality_gates() {
    echo "🔍 AUTOMATED QUALITY GATES"
    echo "========================"
    
    local quality_passed=true
    
    # Test coverage check
    echo "🧪 Testing coverage..."
    if command -v pytest >/dev/null 2>&1; then
        if pytest --cov=app --cov-fail-under=$COVERAGE_THRESHOLD --quiet; then
            echo "✅ Test coverage: ≥${COVERAGE_THRESHOLD}%"
        else
            echo "❌ Test coverage: <${COVERAGE_THRESHOLD}%"
            quality_passed=false
        fi
    else
        echo "⚠️ pytest not available, skipping coverage check"
    fi
    
    # Code quality check
    echo "🔍 Code quality analysis..."
    if command -v flake8 >/dev/null 2>&1; then
        if flake8 app/ tests/ --max-complexity=$COMPLEXITY_LIMIT --statistics; then
            echo "✅ Code quality: Complexity ≤$COMPLEXITY_LIMIT"
        else
            echo "❌ Code quality: Complexity >$COMPLEXITY_LIMIT"
            quality_passed=false
        fi
    else
        echo "⚠️ flake8 not available, skipping quality check"
    fi
    
    # Code formatting check
    echo "🎨 Code formatting verification..."
    if command -v black >/dev/null 2>&1; then
        if black app/ tests/ --check --line-length=$LINE_LENGTH; then
            echo "✅ Code formatting: Consistent"
        else
            echo "❌ Code formatting: Inconsistent"
            quality_passed=false
        fi
    else
        echo "⚠️ black not available, skipping format check"
    fi
    
    # Type checking
    echo "🔍 Type checking..."
    if command -v mypy >/dev/null 2>&1; then
        if mypy app/ --show-error-codes --no-error-summary; then
            echo "✅ Type checking: Passed"
        else
            echo "❌ Type checking: Errors found"
            quality_passed=false
        fi
    else
        echo "⚠️ mypy not available, skipping type check"
    fi
    
    echo "========================"
    
    if [[ "$quality_passed" == "true" ]]; then
        echo "✅ ALL QUALITY GATES PASSED"
        return 0
    else
        echo "❌ QUALITY GATES FAILED"
        echo "🔧 Address quality issues before proceeding"
        return 1
    fi
}

function complete_qa_pipeline() {
    echo "🏁 COMPLETE QA PIPELINE EXECUTION"
    echo "================================"
    
    # Phase 1: Pre-execution validation
    if ! pre_execution_validation; then
        echo "❌ QA Pipeline failed at pre-execution validation"
        return 1
    fi
    
    echo ""
    
    # Phase 2: Automated quality gates
    if ! automated_quality_gates; then
        echo "❌ QA Pipeline failed at automated quality gates"
        return 1
    fi
    
    echo ""
    echo "✅ COMPLETE QA PIPELINE PASSED"
    echo "=============================="
    return 0
}
```

## USAGE EXAMPLES

### **Basic Project Setup**
```bash
# Initialize new AI coordination project
./ai_project_setup.sh "my-complex-task"

# Load communication functions
source tmux_communication.sh

# Verify setup
tmux list-sessions | grep coord-my-complex-task
```

### **Task Coordination Example**
```bash
# Coordinate task across multiple workers
coordinated_task_assignment "coord-my-project" "Implement feature X" "1" "2" "3"

# Check worker status
batch_worker_status_check "coord-my-project" "1" "2" "3"

# Send direct message if needed
send_tmux_message_with_retry "1" "Status update please" "coord-my-project"
```

### **Quality Pipeline Integration**
```bash
# Run complete QA pipeline before commit
if complete_qa_pipeline; then
    echo "🚀 Ready for commit"
    git add .
    git commit -m "Implement feature with QA validation"
else
    echo "🛑 Fix quality issues before committing"
fi
```

## RELATED:
- memory-bank/02-organization/ai_agent_coordination_mandatory.md
- memory-bank/02-organization/tmux_git_worktree_technical_specification.md
- memory-bank/00-core/testing_mandatory.md
- memory-bank/00-core/code_quality_anti_hacking.md

---
**Generated**: 2025-06-23
**Context**: AI coordination process template systematization
**Status**: Production-ready templates available
**Application**: Multi-agent project coordination and quality assurance