# CLAUDE.md - Phase 1: Quick Start Implementation

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Quick Start (5-Minute Essentials) - NEW USERS START HERE

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

# 3. Cognee integration (enhanced mode if available)
if mcp__cognee__cognify_status > /dev/null 2>&1; then
    mcp__cognee__cognee_add_developer_rules --base_path /home/devuser/workspace
    echo "✅ Cognee enhanced mode active"
else
    echo "⚠️ Direct constraint mode only"
fi

echo "🎯 Session ready! You can now start development."
```

### 🧠 Core Principles (Absolute Compliance)
```bash
# The 3-Second Rule (MANDATORY before ANY action)
echo "1. Is this fact or speculation?"
echo "2. Have I verified related knowledge?"  
echo "3. Is there a more reliable method?"

# FORBIDDEN PHRASES (auto-stop on detection)
FORBIDDEN=("probably" "maybe" "I think" "seems like" "たぶん" "おそらく")
```

### ⚡ 3-Second Delegation Decision
| Context Size | Duration | State Required | → Use |
|--------------|----------|----------------|-------|
| >2000 tokens | <30 min | No | **Task Tool** |
| Any | ≥30 min | Yes | **tmux + Claude CLI** |
| <2000 tokens | <30 min | No | **Direct Execution** |

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
1. memory-bank/00-core/user_authorization_mandatory.md        # User authorization (absolute compliance)
2. memory-bank/00-core/testing_mandatory.md                  # Automated testing requirements  
3. memory-bank/00-core/code_quality_anti_hacking.md          # Quality anti-hacking rules
4. memory-bank/09-meta/progress_recording_mandatory_rules.md # Progress recording requirements
```

#### Phase 1B: Core Development Knowledge
```bash
5. memory-bank/00-core/tdd_implementation_knowledge.md       # TDD implementation methods
6. memory-bank/00-core/development_workflow.md              # Development workflow
7. memory-bank/01-cognee/memory_resource_management_critical_lessons.md  # Memory resource management
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
```

### Cognee Operations
```bash
mcp__cognee__cognify_status
mcp__cognee__search --search_query "pattern" --search_type "GRAPH_COMPLETION"
mcp__cognee__cognee_add_developer_rules --base_path /home/devuser/workspace
```

### Emergency Protocols
```bash
# Cognee unavailable
if ! mcp__cognee__cognify_status > /dev/null 2>&1; then
    echo "⚠️ Direct constraint mode"
    cat memory-bank/*_mandatory_rules.md | grep -A 5 "MANDATORY"
fi
```

### Current Project Status
- **Project**: A2A MVP - Test-Driven Development
- **Status**: ✅ Implementation Complete  
- **Coverage**: 92% (target: ≥85%)
- **Tests**: 101 tests, 100% passing
- **Quality**: Flake8 0 violations, Black formatted

---

## 🚨 Final Reminders

1. **Always run pre_action_check.py first** - Constraint validation
2. **Always write tests first** - TDD mandatory
3. **3-second rule** - Fact vs speculation check
4. **Quality gates before commit** - Non-negotiable
5. **When in doubt, write a test!**

**Key Principle**: 事実ベース判断 - No speculation, only verified facts.

---

**Note**: This is Phase 1 implementation focusing on immediate usability. For complete details, reference memory-bank/ files and CLAUDE_structured.md.