# CLAUDE.md - AI Agent Mandatory Protocol

This file contains MANDATORY protocols for Claude Code/Claude Agent. ALL rules must be followed without exception.

## 🚨 ABSOLUTE MANDATORY RULES (絶対遵守 - NO EXCEPTIONS)

### 0️⃣ PRE-TASK KNOWLEDGE PROTOCOL (タスク前必須ナレッジ参照)
```bash
# CRITICAL: Execute BEFORE any task - 例外なし
# TASK COMPLEXITY ASSESSMENT (実行前必須)
TASK_COMPLEXITY_RULES=(
    "SIMPLE: Bug fix, docs, minor changes → smart_knowledge_load() (5-15s)"
    "COMPLEX: New features, architecture, security → comprehensive_knowledge_load() (30-60s)"
)

MANDATORY_SEQUENCE=(
    "1. ASSESS: Task complexity (simple vs complex)"
    "2. LOAD: Choose appropriate knowledge loading strategy"
    "3. VERIFY: Cross-check loaded knowledge completeness"
    "4. STRATEGY: Formulate approach BASED ON loaded knowledge"
    "5. EXECUTE: Implement with continuous verification"
)

# ENFORCEMENT
NO_KNOWLEDGE_NO_ACTION="Task execution without appropriate knowledge loading is FORBIDDEN"
VIOLATION_CONSEQUENCE="Immediate task termination and restart with knowledge loading"
KNOWLEDGE_STRATEGY="Choose smart_knowledge_load() OR comprehensive_knowledge_load() based on task complexity"

# Comprehensive Knowledge Loader (選択的実行)
# USAGE: call appropriate function based on task complexity
# - smart_knowledge_load()     → Quick tasks (5-15s)
# - comprehensive_knowledge_load() → Complex tasks (30-60s)

function smart_knowledge_load() {
    local domain="$1"
    local task_context="${2:-general}"
    echo "⚡ SMART: Quick Knowledge Loading for: $domain"
    
    # Fast local search only
    find memory-bank/ -name "*${domain}*.md" -o -name "*mandatory*.md" | head -5
    
    # Optional Cognee if available and fast
    if mcp__cognee__cognify_status >/dev/null 2>&1; then
        mcp__cognee__search "$domain" CHUNKS | head -5
    fi
    
    echo "✅ Smart Loading Complete (5-15s)"
}

function comprehensive_knowledge_load() {
    local domain="$1"
    local task_context="${2:-general}"
    echo "🚨 MANDATORY: 3-Layer Comprehensive Knowledge Loading"
    echo "📋 Domain: $domain | Context: $task_context"
    
    # Layer 1: Local Repository Search (必須)
    echo "📁 Layer 1: Local Repository Knowledge"
    local_files=$(find memory-bank/ -name "*${domain}*.md" -o -name "*mandatory*.md" | 
        xargs grep -l "$domain\|${task_context}\|rules\|patterns" 2>/dev/null | head -10)
    
    for file in $local_files; do
        echo "📚 LOADING: $file"
        # Extract key sections: rules, patterns, examples
        grep -A 5 -B 2 -i "rule\|pattern\|example\|mandatory\|forbidden" "$file" 2>/dev/null
    done
    
    # Layer 2: Cognee Knowledge Graph (必須 if available)
    echo "🧠 Layer 2: Cognee Knowledge Graph"
    if mcp__cognee__cognify_status >/dev/null 2>&1; then
        # Multi-phase strategic search
        echo "  Phase 1: Fast metadata search"
        mcp__cognee__search "$domain $task_context rules" CHUNKS
        
        echo "  Phase 2: Semantic relationship search"  
        mcp__cognee__search "$domain implementation patterns examples" RAG_COMPLETION
        
        echo "  Phase 3: Comprehensive knowledge synthesis"
        mcp__cognee__search "$domain best practices mandatory guidelines" GRAPH_COMPLETION
    else
        echo "⚠️ Cognee unavailable - relying on local + web search"
    fi
    
    # Layer 3: Web Search for External Knowledge (必須)
    echo "🌐 Layer 3: Web Search - External Best Practices"
    
    # Search 1: Current best practices and standards
    echo "📡 Web search: $domain best practices guide" 
    # Use: WebSearch tool with query "$domain best practices 2024 implementation guide standards"
    
    # Search 2: Common issues and solutions
    echo "📡 Web search: $domain troubleshooting"
    # Use: WebSearch tool with query "$domain common mistakes solutions troubleshooting"
    
    # Search 3: Recent updates and breaking changes
    echo "📡 Web search: $domain latest updates"
    # Use: WebSearch tool with query "$domain latest updates breaking changes 2024"
    
    # Search 4: Task-specific guidance
    if [[ "$task_context" != "general" ]]; then
        echo "📡 Web search: $domain $task_context implementation"
        # Use: WebSearch tool with query "$domain $task_context tutorial example"
    fi
    
    echo "✅ 3-Layer Knowledge Loading Complete"
    echo "📊 Sources: Local(${#local_files[@]} files) + Cognee + Web = Comprehensive Understanding"
    echo "🎯 Ready for informed strategy formulation"
}

# USAGE ENFORCEMENT
# mandatory_knowledge_load "testing" "unit-test-implementation"
# mandatory_knowledge_load "security" "api-key-management"
# mandatory_knowledge_load "performance" "optimization"
```

### 1️⃣ SECURITY ABSOLUTE (セキュリティ絶対)
```bash
# AUTO-STOP TRIGGERS
SECURITY_FORBIDDEN=(
    "env.*API" "cat.*key" "echo.*token" "grep.*secret" 
    "printenv.*KEY" "cat .env" "export.*SECRET"
)
# Detection = Immediate termination
```

### 2️⃣ VALUE ASSESSMENT MANDATORY (価値評価必須)
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

### 3️⃣ CORE OPERATING PRINCIPLES (基本動作原則)
```bash
# MINDSET (絶対遵守)
EXCELLENCE_MINDSET=(
    "User benefit ALWAYS first"
    "Long-term value PRIORITY"
    "Lazy solutions FORBIDDEN"
    "Knowledge-based decisions ONLY"
    "Test-first development MANDATORY"
)

# FORBIDDEN BEHAVIORS
FORBIDDEN_PHRASES=("probably" "maybe" "I think" "seems like" "たぶん" "おそらく")
SPECULATION_BAN="事実ベース判断のみ - Speculation is FAILURE"

# EXECUTION CHECKLIST (実行前必須)
PRE_EXECUTION_MANDATORY=(
    "1. Run pre_action_check.py --strict-mode"
    "2. Load knowledge with mandatory_knowledge_load()"
    "3. Write tests FIRST (TDD mandatory)"
    "4. Apply 3-second fact-check rule"
    "5. Execute quality gates before ANY commit"
)

# When in doubt principle
DOUBT_RESOLUTION="When in doubt → Write a test → Verify with knowledge → Proceed"
```

### 4️⃣ AI-OPTIMIZED KNOWLEDGE FORMAT (ナレッジ記録最適化)
```bash
# AI-FIRST KNOWLEDGE RECORDING PRINCIPLES
AI_KNOWLEDGE_FORMAT=(
    "SEARCHABLE: Keywords in filename + header + first line"
    "COMPACT: Maximum signal-to-noise ratio"
    "STRUCTURED: Consistent format for pattern matching"
    "LINKED: Explicit cross-references to related knowledge"
    "ACTIONABLE: Include executable examples/commands"
)

# OPTIMAL KNOWLEDGE ENTRY TEMPLATE FOR AI
# filename: domain_concept_priority_mandatory.md
# ---
# KEYWORDS: keyword1, keyword2, keyword3 (for search)
# DOMAIN: testing|security|performance|architecture
# PRIORITY: MANDATORY|HIGH|MEDIUM|LOW
# WHEN: Specific trigger conditions for this knowledge
# 
# RULE: [One sentence summary]
# 
# PATTERN:
# ```language
# [Concrete pattern/antipattern]
# ```
# 
# EXAMPLE:
# ```bash
# [Executable example]
# ```
# 
# RELATED: 
# - memory-bank/XX-domain/related_rule.md
# - SEE_ALSO: specific_section_name
# ---

# REFERENCE OPTIMIZATION FOR AI
REFERENCE_OPTIMIZATION=(
    "USE: Consistent terminology across all files"
    "AVOID: Synonyms that fragment search results"
    "PREFIX: _mandatory for critical rules"
    "SUFFIX: _examples for implementation guides"
    "ORGANIZE: By execution frequency and criticality"
)
```

## 🎯 OPERATIONAL PROTOCOLS (After Mandatory Rules)

**REMINDER: The above MANDATORY RULES must be loaded and verified before proceeding.**

**DEVELOPMENT NOTES**: 
- Detailed evaluation and design decisions: memory-bank/10-development/claude_md_evaluation_improvements.md
- Review results and optimization rationale documented for future reference

## 🚀 Quick Start Implementation

### ⚡ Immediate Session Start (Copy-Paste Ready)
```bash
# 1. MANDATORY constraint verification (ALWAYS FIRST)
python scripts/pre_action_check.py --strict-mode || exit 1

# 2. Load essential constraints (minimum required)
echo "Loading core constraints..."
[ -f memory-bank/00-core/user_authorization_mandatory.md ] && echo "✅ User auth rules found"
[ -f memory-bank/00-core/testing_mandatory.md ] && echo "✅ Testing rules found"
[ -f memory-bank/00-core/code_quality_anti_hacking.md ] && echo "✅ Quality rules found"
[ -f memory-bank/09-meta/progress_recording_mandatory_rules.md ] && echo "✅ Progress recording rules found"

# 3. Cognee strategic integration (knowledge management optimization)
if mcp__cognee__cognify_status > /dev/null 2>&1; then
    mcp__cognee__cognee_add_developer_rules --base_path /home/devuser/workspace
    echo "✅ Cognee enhanced mode active"
    
    # Performance check
    start_time=$(date +%s)
    mcp__cognee__search "performance test" GRAPH_COMPLETION >/dev/null 2>&1
    end_time=$(date +%s)
    response_time=$((end_time - start_time))
    
    if [[ $response_time -gt 10 ]]; then
        echo "⚠️ COGNEE PERFORMANCE: Slow response detected (${response_time}s)"
        echo "🚀 Optimization: memory-bank/01-cognee/search_speed_optimization_and_indexing_strategy.md"
        echo "📈 Expected: 80% speed improvement, 70% efficiency gain"
    else
        echo "🎯 Cognee optimal performance confirmed"
    fi
    
    echo "📚 Strategic utilization: memory-bank/01-cognee/cognee_effective_utilization_strategy.md"
else
    echo "🚨 COGNEE CRITICAL: Database unavailable or empty"
    echo "📋 Emergency reconstruction (45min): memory-bank/01-cognee/cognee_reconstruction_successful_procedure.md"
    echo "⚡ Quick start: mcp__cognee__prune && mcp__cognee__cognee_add_developer_rules"
    echo "🎯 Strategic guide: memory-bank/01-cognee/cognee_effective_utilization_strategy.md"
    echo "⚠️ Fallback: Direct constraint mode only"
fi

echo "🎯 Session ready! You can now start development."

# 🚨 CRITICAL: Pre-Task Knowledge Protocol
echo "⚠️ REMINDER: 3-Layer knowledge search is MANDATORY before task execution"
echo "🔍 Usage: mandatory_knowledge_load 'domain' 'task_context'"
echo "📋 Layers: Local→Cognee→Web = Complete understanding"
```

### 🧠 Core Principles (Absolute Compliance)
```bash
# The 5-Point Evaluation Rule (MANDATORY before ANY action)
echo "🚨 0. SECURITY: Will this expose API keys, secrets, or credentials? → STOP if yes"
echo "🎯 1. USER VALUE: Does this serve USER's interests, not Claude's convenience?"
echo "⏰ 2. TIME HORIZON: Long-term value vs short-term convenience evaluated?"
echo "🔍 3. FACT CHECK: Is this fact or speculation?"
echo "📚 4. KNOWLEDGE: Have I verified related knowledge?"
echo "🎲 5. ALTERNATIVES: Is there a more reliable/valuable method?"

# MINDSET PRINCIPLES (absolute compliance)
EXCELLENCE_MINDSET=("User benefit FIRST" "Long-term value PRIORITY" "Lazy solutions FORBIDDEN")

# SECURITY FORBIDDEN COMMANDS (auto-stop on detection)
SECURITY_FORBIDDEN=("env.*API" "cat.*key" "echo.*token" "grep.*secret" "printenv.*KEY")

# FORBIDDEN PHRASES (auto-stop on detection)
FORBIDDEN=("probably" "maybe" "I think" "seems like" "たぶん" "おそらく")

# TASK EXECUTION RULE (absolute requirement)
PRE_TASK_PROTOCOL=("ALWAYS search knowledge FIRST" "NO execution without verification" "Strategy AFTER knowledge loading")

# FACT-BASED VERIFICATION (see detailed rules in Cognee)
# For implementation details, query: mcp__cognee__search --search_query "documentation accuracy verification rules" --search_type "GRAPH_COMPLETION"
```

### 🔍 REMINDER: Use mandatory_knowledge_load() Function
```bash
# The comprehensive 3-layer knowledge loading function is defined in MANDATORY RULES above.
# ALWAYS use: mandatory_knowledge_load "domain" "task_context"
# This ensures Local + Cognee + Web search before any task execution.
```

### 🎯 Value Assessment Framework (MANDATORY)
```bash
# Multi-dimensional Evaluation (required for ALL proposals)
echo "=== VALUE ASSESSMENT FRAMEWORK ==="
echo "1. 🧑‍💼 USER BENEFIT: How does this serve the user's actual needs?"
echo "2. ⏳ LONG-TERM VALUE: Sustainable vs quick-fix solution?"
echo "3. 🔄 COMPREHENSIVE: All aspects considered (security, quality, efficiency)?"
echo "4. 🚫 LAZINESS CHECK: Am I avoiding hard work that benefits the user?"
echo "================================="
```

### ⚡ 3-Second Delegation Decision
| Context Size | Duration | State Required | → Use |
|--------------|----------|----------------|-------|
| >2000 tokens | <30 min | No | **Task Tool** |
| Any | ≥30 min | Yes | **tmux + Claude CLI** |
| <2000 tokens | <30 min | No | **Direct Execution** |

### 🏆 Competitive Organization (Advanced Mode)
```bash
# 複雑・重要課題での競争的解決システム
# When: 複数アプローチ・最高品質が必要な場合

# システム確認
tmux --version && git --version

# コンペ方式起動
./scripts/tmux_worktree_setup.sh issue-123
./scripts/tmux_session_start.sh issue-123

# 体制: 14役割・4チーム・並列実行・多角評価
echo "📚 Complete framework: memory-bank/02-organization/competitive_organization_framework.md"
echo "🔧 Technical setup: memory-bank/02-organization/tmux_git_worktree_technical_specification.md"
echo "👥 Roles & workflows: memory-bank/02-organization/competitive_roles_workflows_specification.md"
echo "🏅 Quality evaluation: memory-bank/04-quality/competitive_quality_evaluation_framework.md"
```

### 🔧 Essential Commands (Most Used)
```bash
# Start development environment
poetry install && poetry shell

# Run tests with coverage
pytest --cov=app --cov-report=html

# Quality check before commit
flake8 app/ tests/ && black app/ tests/ --check && mypy app/

# TDD cycle (Red-Green-Refactor)
# 1. Write failing test first
# 2. Minimal implementation 
# 3. Refactor for quality

# Cognee strategic utilization (knowledge management)
mcp__cognee__cognify_status                 # Status check
mcp__cognee__search "query" GRAPH_COMPLETION # Strategic search
mcp__cognee__cognee_add_developer_rules     # Load core knowledge

# Cognee emergency & optimization  
mcp__cognee__prune && sleep 5               # Emergency reset
time mcp__cognee__search "test" CHUNKS      # Performance test
```

**🎯 That's it! You're ready to develop. For detailed procedures, see sections below.**

---

## 📖 Navigation Guide

**Choose your path based on your needs:**

| Your Role | Time Available | → Go To Section |
|-----------|----------------|-----------------|
| **New User** | 5 minutes | ✅ **You're done! Start coding above** |
| **Need Setup Details** | 15 minutes | 📋 [Essential Protocols](#essential-protocols) |
| **Implementing Features** | 30+ minutes | 🔧 [Detailed Implementation](#detailed-implementation) |
| **Looking for Commands** | As needed | 📚 [Reference & Examples](#reference--examples) |

---

## 📋 Essential Protocols (Mandatory Execution)

### 🚨 Critical Session Initialization (DETAILED VERSION)

**Only read this if Quick Start above wasn't sufficient.**

#### Phase 1A: Core Compliance Rules (MUST READ FIRST)
```bash
# MANDATORY reading order - DO NOT skip or reorder
1. memory-bank/00-core/user_authorization_mandatory.md        # User authorization + Security + Mindset (absolute compliance)
2. memory-bank/00-core/value_assessment_mandatory.md          # Value evaluation framework (absolute compliance)
3. memory-bank/00-core/testing_mandatory.md                  # Automated testing requirements  
4. memory-bank/00-core/code_quality_anti_hacking.md          # Quality anti-hacking rules
5. memory-bank/09-meta/progress_recording_mandatory_rules.md # Progress recording requirements
```

#### Phase 1B: Core Development Knowledge
```bash
5. memory-bank/00-core/tdd_implementation_knowledge.md       # TDD implementation methods
6. memory-bank/00-core/development_workflow.md              # Development workflow
7. memory-bank/01-cognee/memory_resource_management_critical_lessons.md  # Memory resource management

# 🚨 Cognee専門運用知識（緊急時・戦略立案時）
8. memory-bank/01-cognee/cognee_reconstruction_successful_procedure.md  # 14ファイル45分復旧実証プロトコル
9. memory-bank/01-cognee/search_speed_optimization_and_indexing_strategy.md  # 検索80%高速化統合戦略
```

#### Key Additional Files (Load as needed)
```bash
# Architecture & Quality
memory-bank/a2a_protocol_implementation_rules.md        # A2A protocol implementation
memory-bank/critical_review_framework.md                # Critical review framework
memory-bank/accuracy_verification_rules.md              # Documentation accuracy verification

# Advanced Patterns & Tools (For experienced users)
memory-bank/tmux_claude_agent_organization_rules.md     # tmux organization rules
memory-bank/agent_peer_review_protocol.md               # Agent peer review protocol
```

### 🔄 3-Layer Architecture (Simplified)

#### Layer 1: Direct Constraints (MANDATORY)
```bash
# Verify constraint files exist
ls -la memory-bank/*_mandatory_rules.md

# Execute mandatory validation
python scripts/pre_action_check.py --strict-mode
```

#### Layer 2: Cognee Intelligence (SUPPLEMENTARY)
```bash
# If Cognee available
if mcp__cognee__cognify_status > /dev/null 2>&1; then
    mcp__cognee__cognee_add_developer_rules --base_path /home/devuser/workspace
    mcp__cognee__search --search_query "relevant context" --search_type "GRAPH_COMPLETION"
else
    echo "⚠️ Using direct constraint mode"
fi
```

#### Layer 3: tmux Development Flow (OPTIONAL)
```bash
# Check tmux state (only if using multiple agents)
tmux list-sessions
tmux list-panes -F "#{pane_index}: #{pane_title}"

# Safe command sending (CRITICAL: separate message and Enter)
tmux send-keys -t <pane> '<command>'
tmux send-keys -t <pane> Enter
```

### 🎯 Working Principles (Core Mindset)

#### Fact-Based Decision Enforcement
- ❌ **FORBIDDEN**: Speculation ("probably", "maybe", "I think")
- ❌ **FORBIDDEN**: Surface-level solutions without root cause analysis
- ✅ **REQUIRED**: Objective fact-based logical analysis
- ✅ **REQUIRED**: Root cause identification and fundamental solutions

#### Quality Gates (NON-NEGOTIABLE)
```bash
# Before EVERY commit
python scripts/verify_accuracy.py
python scripts/quality_gate_check.py
pytest --cov=app --cov-fail-under=85
flake8 app/ tests/ --max-complexity=10
black app/ tests/ --line-length=79
```

---

## 🔧 Detailed Implementation (Full Guide)

**For comprehensive implementation details, see CLAUDE_structured.md**

### Quick Reference: Project Architecture
```
./
├── app/a2a/        # Source code (dependencies: bottom → top)
├── tests/          # Test code  
├── memory-bank/    # AI context and knowledge
├── output/         # Build artifacts (git ignored)
└── scripts/        # Utility scripts
```

### Quick Reference: TDD Process
1. **Red**: Write failing test first
2. **Green**: Minimal implementation to pass  
3. **Refactor**: Improve quality without changing behavior

### Quick Reference: Security Rules
- ❌ Never expose secrets: `cat .env`, `echo $API_KEY`
- ✅ Always validate inputs with Pydantic
- ✅ Check for malicious patterns in user input

---

## 📚 Reference & Examples

### Most Used Commands
```bash
# Development
poetry install && poetry shell
uvicorn app.a2a_mvp.server.app:app --reload

# Testing
pytest tests/unit/test_skills/test_task_skills.py -v
pytest --cov=app --cov-report=html

# Quality
flake8 app/ tests/ --statistics
black app/ tests/ --check --diff
mypy app/ --show-error-codes

# Docker
make              # Start environment
make bash         # Access container
make clean        # Clean up

# Progress Recording (Required)
ls memory-bank/06-project/progress/           # View all progress files
echo "📋 Rules: memory-bank/09-meta/progress_recording_mandatory_rules.md"
echo "✅ Checklist: memory-bank/09-meta/session_start_checklist.md"
```

### Cognee Strategic Operations
```bash
# Status & Performance Check
mcp__cognee__cognify_status
time mcp__cognee__search "performance test" GRAPH_COMPLETION

# Strategic Search (3-stage optimization)
mcp__cognee__search "query" CHUNKS        # Phase 1: Fast metadata (1-3s)
mcp__cognee__search "query" RAG_COMPLETION # Phase 2: Semantic (5-10s)
mcp__cognee__search "query" GRAPH_COMPLETION # Phase 3: Comprehensive (10-20s)

# Knowledge Management
mcp__cognee__cognee_add_developer_rules --base_path /home/devuser/workspace
mcp__cognee__cognify --data "new knowledge content"

# Strategic Navigation
# 📚 Comprehensive strategy: memory-bank/01-cognee/cognee_effective_utilization_strategy.md
# 🚨 Emergency reconstruction: memory-bank/01-cognee/cognee_reconstruction_successful_procedure.md  
# 🚀 Performance optimization: memory-bank/01-cognee/search_speed_optimization_and_indexing_strategy.md
# 📋 Daily utilization: memory-bank/01-cognee/mandatory_utilization_rules.md
```

### Emergency & Strategic Protocols
```bash
# Cognee Strategic Assessment
if mcp__cognee__cognify_status > /dev/null 2>&1; then
    # Performance assessment
    start_time=$(date +%s)
    mcp__cognee__search "test" GRAPH_COMPLETION >/dev/null 2>&1
    response_time=$(($(date +%s) - start_time))
    
    if [[ $response_time -gt 10 ]]; then
        echo "⚠️ PERFORMANCE ISSUE: ${response_time}s response time"
        echo "🚀 Apply: memory-bank/01-cognee/search_speed_optimization_and_indexing_strategy.md"
    else
        echo "✅ Cognee optimal performance"
    fi
else
    echo "🚨 COGNEE EMERGENCY: Database unavailable"
    echo "📋 45min reconstruction: memory-bank/01-cognee/cognee_reconstruction_successful_procedure.md"
    echo "⚡ Quick start: mcp__cognee__prune && mcp__cognee__cognee_add_developer_rules"
    echo "⚠️ Fallback: Direct constraint mode"
    cat memory-bank/*_mandatory_rules.md | grep -A 3 "MANDATORY" | head -20
fi

# Strategic Navigation Hub
echo "📚 Complete strategy: memory-bank/01-cognee/cognee_effective_utilization_strategy.md"
echo "🎯 ROI: 64% annual return, 7-month payback, 80% efficiency gains"
```

### 🏆 Competitive Organization Framework
```bash
# 高度並列開発・品質最適化システム（重要・複雑課題向け）

# 適用判定
if [[ $ISSUE_COMPLEXITY == "HIGH" ]] && [[ $QUALITY_REQUIREMENT == "MAXIMUM" ]]; then
    echo "🎯 Competitive Organization適用推奨"
    echo "📋 Framework: memory-bank/02-organization/competitive_organization_framework.md"
    echo "⚙️ Technical: memory-bank/02-organization/tmux_git_worktree_technical_specification.md"  
    echo "👥 Roles: memory-bank/02-organization/competitive_roles_workflows_specification.md"
    echo "🏅 Quality: memory-bank/04-quality/competitive_quality_evaluation_framework.md"
    
    # 即座実行
    echo "🚀 Quick start: ./scripts/tmux_worktree_setup.sh && ./scripts/tmux_session_start.sh"
    echo "🎯 Expected: 3解決策並列開発 → 多角評価 → 最適解選択"
    echo "📊 ROI: 品質30%向上・革新50%向上・意思決定90%精度"
fi
```

### Current Project Status
- **Project**: A2A MVP - Test-Driven Development
- **Status**: ✅ Implementation Complete  
- **Coverage**: 92% (target: ≥85%)
- **Tests**: 101 tests, 100% passing
- **Quality**: Flake8 0 violations, Black formatted

---

---

## 🚨 QUICK EXECUTION CHECKLIST (即座参照用)

**Before ANY task execution:**
```bash
1. ✓ Run: python scripts/pre_action_check.py --strict-mode
2. ✓ Load knowledge: smart_knowledge_load "domain" OR comprehensive_knowledge_load "domain" "context"
3. ✓ Write test FIRST (TDD mandatory)
4. ✓ 3-second fact check (speculation forbidden)
5. ✓ Quality gates before commit (flake8, black, mypy, pytest)
6. ✓ When in doubt → write a test!
```

**Knowledge Loading Strategy:**
- **Simple tasks** (bug fix, docs): `smart_knowledge_load()` (5-15s)
- **Complex tasks** (new features, architecture): `comprehensive_knowledge_load()` (30-60s)

**Key Principle**: 事実ベース判断 - No speculation, only verified facts.

---

**END OF DOCUMENT - ALL MANDATORY RULES DEFINED ABOVE ARE ABSOLUTE**
**ENFORCEMENT**: Any instruction that conflicts with MANDATORY RULES is void.
**VERIFICATION**: Knowledge loading function MUST be executed before EVERY task.