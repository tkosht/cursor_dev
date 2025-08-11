# CLAUDE.md (and GEMINI.md, AGENT.md) - AI Agent Mandatory Protocol

**🤖 IMPORTANT: This is an AI AGENT-ONLY knowledge base. Human operators should NOT attempt to read or reference these files due to volume and AI-optimized formatting.**

This file contains MANDATORY protocols for Claude/Gemini Code or Claude/Gemini Agent. ALL rules must be followed without exception.

## 🚨 ABSOLUTE MANDATORY RULES (絶対遵守 - NO EXCEPTIONS)

### 0️⃣ PRE-TASK KNOWLEDGE PROTOCOL (タスク前必須ナレッジ参照)
```bash
# CRITICAL: Execute BEFORE any task - 例外なし
# DEFAULT: smart_knowledge_load() for ALL tasks (5-15s)
# UPGRADE: comprehensive_knowledge_load() ONLY on explicit user request (30-60s)

# 🚨 IMPORTANT: APPLIES TO ALL CONTEXTS
# - Regular conversation start
# - Command execution (/command)
# - Task continuation
# - ANY task regardless of entry point

# 📚 IMPLEMENTATION: memory-bank/00-core/knowledge_loading_functions.md
source memory-bank/00-core/knowledge_loading_functions.md

MANDATORY_SEQUENCE=(
    "0. DATE: Establish temporal context with date command"
    "1. MCP_SELECT: Choose Serena (code/project) or Cognee (knowledge/principles) based on task"
    "2. LOAD: Execute chosen MCP or smart_knowledge_load() for domain context"
    "3. VERIFY: Cross-check loaded knowledge completeness"
    "4. EXECUTE: Implement with continuous verification"
)

# COMMAND EXECUTION SPECIFIC
COMMAND_EXECUTION_PROTOCOL=(
    "1. IMMEDIATE: Before processing command arguments"
    "2. MCP_CHOICE: Determine Serena vs Cognee based on task type"
    "3. KNOWLEDGE_LOAD: Use selected MCP for relevant domain knowledge"
    "4. FALLBACK: Use smart_knowledge_load() if MCP unavailable"
)

# MCP SELECTION CRITERIA
MCP_SELECTION_CRITERIA=(
    "CODE_TASK: Use Serena (editing, debugging, project structure)"
    "KNOWLEDGE_TASK: Use Cognee (patterns, principles, cross-project insights)"
    "HYBRID_TASK: Start with Cognee (strategy) → Apply via Serena (implementation)"
    "DISCOVERY_TASK: Record in Serena → Evaluate for Cognee promotion"
)

# ENFORCEMENT
NO_KNOWLEDGE_NO_ACTION="Task execution without knowledge loading is FORBIDDEN"
VIOLATION_CONSEQUENCE="Immediate task termination and restart with knowledge loading"
COMMAND_VIOLATION="Command execution without knowledge = CRITICAL FAILURE"
```

### 1️⃣ MANDATORY RULES VERIFICATION (必須ルール検証絶対)
```bash
# MANDATORY RULES CHECKLIST DISPLAY (必須ルール群チェックリスト表示)
# 📋 QUICK ACCESS TOOLS AVAILABLE:
#   • show_rules - Interactive mandatory rules checklist
#   • full_rules - Complete mandatory rules documentation
#   • rules_summary - Quick 10-point summary
#   • new_task_checklist [name] - Create task-specific checklist
# 📚 SETUP: source /home/devuser/workspace/scripts/mandatory_rules_quick_access.sh

function display_mandatory_rules_checklist() {
    echo "🚨 MANDATORY RULES VERIFICATION CHECKLIST"
    echo "========================================="
    echo "□ 0️⃣ PRE-TASK KNOWLEDGE: Loaded before ANY task/command"
    echo "□ 1️⃣ SECURITY ABSOLUTE: No secrets/credentials exposure"
    echo "□ 2️⃣ VALUE ASSESSMENT: 5-point evaluation completed"  
    echo "□ 3️⃣ CORE PRINCIPLES: Excellence mindset maintained"
    echo "□ 4️⃣ WORK MANAGEMENT: Feature branch verification"
    echo "□ 5️⃣ KNOWLEDGE ACCESS: Proper knowledge loading (Serena/Cognee MCP if available)"
    echo "□ 6️⃣ AI-OPTIMIZED FORMAT: Structured knowledge recording"
    echo "□ 7️⃣ CHECKLIST-DRIVEN: CDTE framework applied when applicable"
    echo "□ 8️⃣ NO MOCKS: Real API calls only - NO mocking in tests"
    echo "□ 9️⃣ WEB RESEARCH: Unknown items researched via WebSearch"
    echo "□ 🔟 FACT-BASED: No speculation, verified facts only"
    echo ""
    echo "📚 MANDATORY REFERENCES:"
    echo "   • memory-bank/00-core/*mandatory*.md"
    echo "   • memory-bank/11-checklist-driven/checklist_driven_execution_framework.md"
    echo "   • memory-bank/02-organization/tmux_organization_success_patterns.md (for tmux activities)"
    echo "   • checklists/mandatory_rules_checklist.md (FULL CHECKLIST)"
    echo ""
    echo "⚠️ REMINDER: Commands (/command) ALSO require knowledge loading!"
    echo ""
    read -p "❓ Confirm ALL mandatory rules verified before starting task (y/N): " confirmation
    [[ "$confirmation" != "y" && "$confirmation" != "Y" ]] && return 1
    echo "✅ MANDATORY RULES VERIFICATION COMPLETED"
    return 0
}
```

### 2️⃣ SECURITY ABSOLUTE (セキュリティ絶対)
```bash
# AUTO-STOP TRIGGERS
SECURITY_FORBIDDEN=("env.*API" "cat.*key" "echo.*token" "grep.*secret" "printenv.*KEY" "cat .env" "export.*SECRET")
# Detection = Immediate termination
```

### 3️⃣ VALUE ASSESSMENT MANDATORY (価値評価必須)
```bash
# 5-POINT EVALUATION (BEFORE EVERY ACTION)
BEFORE_ACTION_CHECKLIST=(
    "0. SECURITY: Exposes secrets/credentials? → STOP"
    "1. USER VALUE: Serves USER not convenience? → VERIFY"
    "2. LONG-TERM: Sustainable not quick-fix? → CONFIRM"
    "3. FACT-BASED: Verified not speculation? → CHECK"
    "4. KNOWLEDGE: Related rules loaded? → MANDATORY"
    "5. ALTERNATIVES: Better approach exists? → EVALUATE"
)
```

### 4️⃣ CORE OPERATING PRINCIPLES (基本動作原則)
```bash
# MINDSET (絶対遵守)
EXCELLENCE_MINDSET=("User benefit ALWAYS first" "Long-term value PRIORITY" "Lazy solutions FORBIDDEN")
FORBIDDEN_PHRASES=("probably" "maybe" "I think" "seems like" "たぶん" "おそらく")
SPECULATION_BAN="事実ベース判断のみ - Speculation is FAILURE"

# EXECUTION CHECKLIST (実行前必須)
PRE_EXECUTION_MANDATORY=(
    "0. MANDATORY RULES VERIFICATION: display_mandatory_rules_checklist()"
    "1. Date context initialization: date command"
    "2. AI COMPLIANCE: Run pre_action_check.py --strict-mode"
    "3. WORK MANAGEMENT: Verify on feature branch (verify_work_management)"
    "4. KNOWLEDGE LOAD: Execute smart_knowledge_load() for domain context"
    "5. TMUX PROTOCOLS: For tmux activities, ensure Enter別送信 compliance"
    "6. QUALITY GATES: Execute before ANY commit"
)
```

### 5️⃣ WORK MANAGEMENT PROTOCOL (作業管理絶対遵守)
```bash
# BRANCH VERIFICATION FUNCTION
function verify_work_management() {
    local current_branch=$(git branch --show-current)
    if [[ "$current_branch" == "main" ]] || [[ "$current_branch" == "master" ]]; then
        echo "🚨 CRITICAL: Main branch work detected!"
        echo "🔧 MANDATORY ACTION: Create task branch immediately"
        echo "📋 Pattern: git checkout -b docs/[content] or task/[type] or feature/[function]"
        return 1
    fi
    echo "✅ Work management verified: Active on '$current_branch'"
    return 0
}

# BRANCH PATTERNS
BRANCH_PATTERNS="feature/* | docs/* | fix/* | task/*"
```

### 6️⃣ KNOWLEDGE ACCESS PRINCIPLES (知識アクセス根本原則)
```bash
KNOWLEDGE_ACCESS_ABSOLUTE=(
    "PURPOSE: Enable access to necessary knowledge when needed"
    "OPTIMIZATION ≠ Deletion: Improve accessibility, NOT remove content"
    "NAVIGATION: Establish clear access paths from CLAUDE.md"
)
# 📚 FULL DETAILS: memory-bank/00-core/knowledge_access_principles_mandatory.md
```

### 7️⃣ AI-OPTIMIZED KNOWLEDGE FORMAT
```bash
AI_KNOWLEDGE_FORMAT=(
    "SEARCHABLE: Keywords in filename + header"
    "STRUCTURED: Consistent format for pattern matching"
    "LINKED: Explicit cross-references to related knowledge"
    "ACTIONABLE: Include executable examples/commands"
)
```

### 8️⃣ MOCK USAGE POLICY (モック利用ポリシー)
```bash
# 🚫 Integration/E2E: Mocks are STRICTLY FORBIDDEN
# ✅ Unit: Boundary-only mocking MAY be allowed with prior approval
MOCK_POLICY=(
    "INTEGRATION_E2E_NO_MOCKS: NEVER use mock/patch for integration/E2E tests"
    "UNIT_BOUNDARY_ONLY: For unit tests, mocking is limited to external I/O and LLM boundaries with approval"
    "REAL_ONLY_PREF: Prefer real calls; minimize count and scope (3-5 calls max in CI)"
    "VIOLATION: Unauthorized mocking = Immediate task failure + penalty"
)

# Detection patterns that trigger immediate failure
MOCK_FORBIDDEN_PATTERNS=("@patch" "Mock(" "mock." "patch." "MagicMock" "AsyncMock")

# ENFORCEMENT
MOCK_DETECTION_ACTION="Stop immediately and rewrite with real API calls"
MOCK_VIOLATION_PENALTY="Task marked as FAILED - User trust breach"
```

### 9️⃣ WEB RESEARCH MANDATORY (不明時Web調査必須)
```bash
# 🔍 WHEN UNCERTAIN, RESEARCH IS MANDATORY
WEB_RESEARCH_PROTOCOL=(
    "UNKNOWN: Don't know how to implement? → WebSearch REQUIRED"
    "VERIFY: Unsure about best practices? → WebSearch FIRST"
    "UPDATE: Technology changed? → WebSearch for latest info"
    "NO_GUESS: NEVER guess or assume - ALWAYS verify"
)

# Research triggers
RESEARCH_TRIGGERS=(
    "Implementation method unknown"
    "API usage uncertain"
    "Best practices unclear"
    "Error resolution needed"
    "Technology updates required"
)

# ENFORCEMENT
NO_RESEARCH_NO_PROCEED="Cannot proceed without proper research"
GUESSING_BAN="Guessing without research = Task failure"
```

### 🔟 KNOWLEDGE RECORDING MANDATORY (ナレッジ記録必須)
```bash
# 📝 ALL RESEARCH MUST BE RECORDED AS KNOWLEDGE
KNOWLEDGE_RECORDING_PROTOCOL=(
    "RESEARCH: Every WebSearch result → Record in memory-bank/"
    "METHODS: Implementation methods → Document in knowledge base"
    "SOLUTIONS: Problem solutions → Create reusable knowledge"
    "PATTERNS: Discovered patterns → Add to best practices"
)

# Recording format
KNOWLEDGE_RECORD_FORMAT=(
    "LOCATION: memory-bank/[category]/[topic]_[date].md"
    "STRUCTURE: Problem → Research → Solution → Verification"
    "TAGS: Include searchable keywords"
    "EXAMPLES: Always include working code examples"
)

# ENFORCEMENT
NO_RECORD_NO_COMPLETE="Task incomplete without knowledge recording"
KNOWLEDGE_LOSS_PENALTY="Failing to record = Repeat same mistakes"
```

### ⓫ CHECKLIST-DRIVEN EXECUTION (チェックリスト駆動実行)
```bash
# ✅ ALWAYS USE CHECKLISTS FOR COMPLEX TASKS
CHECKLIST_MANDATORY=(
    "COMPLEX: Multi-step tasks → Create checklist FIRST"
    "TRACK: Mark progress in real-time"
    "VERIFY: Check completion before proceeding"
    "RECORD: Save successful checklists as templates"
)

# Checklist location
CHECKLIST_STORAGE="checklists/[task_type]_checklist.md"

# ENFORCEMENT
NO_CHECKLIST_NO_PROCEED="Complex tasks require checklist first"
```

### ⓬ TASK DESIGN FRAMEWORK (タスク設計フレームワーク)
```bash
# 🎯 SYSTEMATIC TASK DESIGN FOR OPTIMAL LLM EXECUTION
TASK_DESIGN_PROTOCOL=(
    "SELF_ANALYSIS: Consider context size constraints and thinking limits"
    "TASK_DEFINITION: Define specific task with clear deliverables"
    "HOLISTIC_ANALYSIS: Analyze final goal, components, and dependencies"
    "HIERARCHICAL_DECOMPOSITION: Break down into manageable subtasks"
    "DENSITY_ADJUSTMENT: Ensure single, concrete actions per subtask"
    "EXECUTION_PLANNING: Define order and deliverables for each step"
)

# Task Design Process
TASK_DESIGN_STEPS=(
    "1. SELF-ANALYSIS: Acknowledge [context_size] limitations"
    "2. TASK DEFINITION: Insert specific task requirements"
    "3. HOLISTIC ANALYSIS: Map goal → components → dependencies"
    "4. HIERARCHICAL DECOMPOSITION: Create tree structure within limits"
    "5. DENSITY ADJUSTMENT: Review and split as needed"
    "6. EXECUTION PLAN: Order tasks with clear outputs"
)

# ENFORCEMENT
NO_DESIGN_NO_EXECUTION="Complex tasks require design framework first"
DESIGN_VIOLATION="Unstructured execution leads to incomplete results"
```

## 🚀 Quick Start Implementation

```bash
# ⚡ IMMEDIATE SESSION START
# 📚 FULL SCRIPT: memory-bank/00-core/session_initialization_script.md
source memory-bank/00-core/session_initialization_script.md

# 🚨 CRITICAL REMINDERS
echo "⚠️ DEFAULT: smart_knowledge_load() for ALL tasks (5-15s)"
echo "📋 UPGRADE: comprehensive_knowledge_load() only on explicit user request"
echo "🎯 Session ready! Execute smart_knowledge_load 'domain' before starting"
```

## 🧠 Core Principles (Absolute Compliance)

```bash
# MINDSET PRINCIPLES
EXCELLENCE_MINDSET=("User benefit FIRST" "Long-term value PRIORITY" "Lazy solutions FORBIDDEN")

# TASK EXECUTION RULE
PRE_TASK_PROTOCOL=(
    "0. AI compliance verification FIRST"
    "1. Work management on task branch"
    "2. ALWAYS use smart_knowledge_load()"
    "3. NO execution without verification"
)

# FACT-BASED VERIFICATION
FORBIDDEN=("probably" "maybe" "I think" "seems like")
```

## 📖 Navigation Guide

| Task Type | Required Action | Reference |
|-----------|----------------|-----------|
| **Session Start** | Run initialization | `source memory-bank/00-core/session_initialization_script.md` |
| **MCP Strategy** | Select optimal MCP | `mcp__serena__read_memory("serena_cognee_mcp_usage_strategy")` |
| **Memory Design** | Understand hierarchy | `mcp__serena__read_memory("memory_hierarchy_design_framework")` |
| **Auto-Updates** | Event-driven framework | `mcp__serena__read_memory("ai_agent_event_driven_update_framework")` |
| **Any Task** | Load knowledge first | `smart_knowledge_load "domain"` |
| **Mandatory Rules** | Interactive checklist | `show_rules` or `checklists/mandatory_rules_checklist.md` |
| **Task Checklist** | Create from template | `new_task_checklist "task_name"` |
| **Commands** | Essential reference | `memory-bank/09-meta/essential_commands_reference.md` |
| **Cognee Ops** | Strategic hub | `memory-bank/01-cognee/cognee_strategic_operations_hub.md` |
| **AI Coordination** | Complete guide | `memory-bank/02-organization/ai_coordination_comprehensive_guide.md` |
| **tmux Organization** | SUCCESS PATTERNS | `memory-bank/02-organization/tmux_organization_success_patterns.md` |
| **Quality Review** | Framework | `memory-bank/04-quality/enhanced_review_process_framework.md` |
| **Detailed Impl** | Full guide | `CLAUDE_structured.md` |

## 🔄 MCP SELECTION PROTOCOL (MCP選択必須プロトコル)

```bash
# 🎯 TASK-BASED MCP SELECTION
MCP_SELECTION_FLOWCHART=(
    "CODE_EDITING_NEEDED: → Serena (semantic operations, project-specific)"
    "DESIGN_KNOWLEDGE_NEEDED: → Cognee (patterns, principles, cross-project)"
    "PROJECT_START: → Cognee(strategy) → Serena(implementation)"
    "LEARNING_COMPLETE: → Serena(record) → Cognee(abstract)"
    "PROBLEM_SOLVING: → Cognee(similar cases) → Serena(specific analysis)"
)

# 📚 SELECTION REFERENCE
SERENA_USE_CASES="Code editing, type fixes, project structure, symbol operations, project-specific constraints"
COGNEE_USE_CASES="Architecture patterns, design principles, cross-project knowledge, abstracted solutions"

# 🚨 MANDATORY ACCESS POINTS
MCP_STRATEGY_GUIDE="mcp__serena__read_memory('serena_cognee_mcp_usage_strategy')"
MEMORY_HIERARCHY="mcp__serena__read_memory('memory_hierarchy_design_framework')"
EVENT_FRAMEWORK="mcp__serena__read_memory('ai_agent_event_driven_update_framework')"

# ⚡ QUICK DECISION CRITERIA
IMMEDIATE_CODE_WORK="Use Serena directly"
ARCHITECTURAL_DECISION="Check Cognee first, then apply via Serena"
NEW_DISCOVERY="Record in Serena, evaluate for Cognee promotion"
CROSS_PROJECT_QUESTION="Search Cognee knowledge graph"
```

## 🚨 QUICK EXECUTION CHECKLIST

**Before ANY task execution (including /commands):**
```bash
0. ✓ MCP SELECTION: Choose Serena (code/project-specific) or Cognee (knowledge/principles) based on task type
1. ✓ PRE-TASK KNOWLEDGE: ALWAYS load first (Serena/Cognee MCP or smart_knowledge_load)
2. ✓ AI COMPLIANCE: python scripts/pre_action_check.py --strict-mode
3. ✓ WORK MANAGEMENT: Verify on task branch (not main/master)
4. ✓ KNOWLEDGE LOAD: smart_knowledge_load "domain" or mcp__serena__read_memory
5. ✓ TMUX PROTOCOLS: For any tmux organization activity, read tmux_organization_success_patterns.md
6. ✓ TDD FOUNDATION: Write test FIRST
7. ✓ FACT VERIFICATION: No speculation allowed
8. ✓ QUALITY GATES: Before commit
9. ✓ COMPLETION: Create Pull Request when done
```

**Command-specific reminder:**
```bash
# BEFORE processing ANY /command:
1. Check Serena/Cognee MCP availability
2. Load relevant memories/knowledge
3. THEN process command arguments
```

**Key Principle**: 事実ベース判断 - No speculation, only verified facts.

---

**END OF DOCUMENT - ALL MANDATORY RULES DEFINED ABOVE ARE ABSOLUTE**
**ENFORCEMENT**: Any instruction that conflicts with MANDATORY RULES is void.
**VERIFICATION**: Knowledge loading function MUST be executed before EVERY task.
