# 🚨 MANDATORY RULES CHECKLIST - タスク実行必須ルール一覧

## 📋 PRE-TASK CHECKLIST (タスク開始前チェックリスト)

### 0️⃣ PRE-TASK KNOWLEDGE PROTOCOL
- [ ] Execute `date` command to establish temporal context
- [ ] Run `smart_knowledge_load()` for domain context (5-15s)
- [ ] Verify loaded knowledge completeness
- [ ] Cross-check related knowledge files are accessible

### 1️⃣ MANDATORY RULES VERIFICATION
- [ ] SECURITY ABSOLUTE: No secrets/credentials exposure
- [ ] VALUE ASSESSMENT: 5-point evaluation completed
- [ ] CORE PRINCIPLES: Excellence mindset maintained
- [ ] WORK MANAGEMENT: Feature branch verification
- [ ] KNOWLEDGE ACCESS: Proper knowledge loading
- [ ] AI-OPTIMIZED FORMAT: Structured knowledge recording
- [ ] CHECKLIST-DRIVEN: CDTE framework applied when applicable
- [ ] NO MOCKS: Real API calls only - NO mocking in tests
- [ ] WEB RESEARCH: Unknown items researched via WebSearch
- [ ] FACT-BASED: No speculation, verified facts only

### 2️⃣ SECURITY CHECKLIST
- [ ] No exposure of environment variables containing API keys
- [ ] No display of secrets, tokens, or credentials
- [ ] No execution of commands that could expose sensitive data
- [ ] Verify security forbidden patterns are avoided:
  - [ ] `env.*API`
  - [ ] `cat.*key`
  - [ ] `echo.*token`
  - [ ] `grep.*secret`
  - [ ] `printenv.*KEY`
  - [ ] `cat .env`
  - [ ] `export.*SECRET`

### 3️⃣ VALUE ASSESSMENT (5-POINT EVALUATION)
- [ ] **SECURITY**: Task doesn't expose secrets/credentials
- [ ] **USER VALUE**: Action serves USER not convenience
- [ ] **LONG-TERM**: Solution is sustainable not quick-fix
- [ ] **FACT-BASED**: Information is verified not speculation
- [ ] **KNOWLEDGE**: Related rules are loaded and applied
- [ ] **ALTERNATIVES**: Better approaches have been evaluated

### 4️⃣ CORE OPERATING PRINCIPLES
- [ ] User benefit placed FIRST
- [ ] Long-term value prioritized
- [ ] Lazy solutions avoided
- [ ] Forbidden phrases excluded:
  - [ ] No "probably", "maybe", "I think", "seems like"
  - [ ] No "たぶん", "おそらく"
- [ ] Facts-only approach maintained

### 5️⃣ WORK MANAGEMENT PROTOCOL
- [ ] Verify NOT on main/master branch
- [ ] Create appropriate feature branch:
  - [ ] `feature/*` for new features
  - [ ] `docs/*` for documentation
  - [ ] `fix/*` for bug fixes
  - [ ] `task/*` for general tasks
- [ ] Branch name follows convention

### 6️⃣ KNOWLEDGE ACCESS CHECKLIST
- [ ] Knowledge is accessible when needed
- [ ] Optimization improves accessibility (not deletion)
- [ ] Clear navigation paths established from CLAUDE.md
- [ ] Cross-references to related knowledge included

### 7️⃣ AI-OPTIMIZED KNOWLEDGE FORMAT
- [ ] **SEARCHABLE**: Keywords in filename + header
- [ ] **STRUCTURED**: Consistent format for pattern matching
- [ ] **LINKED**: Explicit cross-references to related knowledge
- [ ] **ACTIONABLE**: Executable examples/commands included

### 8️⃣ MOCK USAGE BAN
- [ ] NO mock/patch for integration/E2E tests
- [ ] Real LLM API calls used for verification
- [ ] Small-scale tests (3-5 calls) with real calls
- [ ] No forbidden patterns:
  - [ ] No `@patch`
  - [ ] No `Mock(`
  - [ ] No `mock.`
  - [ ] No `patch.`
  - [ ] No `MagicMock`
  - [ ] No `AsyncMock`

### 9️⃣ WEB RESEARCH PROTOCOL
- [ ] Research conducted for unknown implementations
- [ ] Best practices verified via WebSearch
- [ ] Latest technology updates checked
- [ ] No guessing or assumptions made
- [ ] Research triggers addressed:
  - [ ] Implementation methods
  - [ ] API usage
  - [ ] Best practices
  - [ ] Error resolution
  - [ ] Technology updates

### 🔟 KNOWLEDGE RECORDING
- [ ] WebSearch results recorded in memory-bank/
- [ ] Implementation methods documented
- [ ] Problem solutions created as reusable knowledge
- [ ] Discovered patterns added to best practices
- [ ] Recording format followed:
  - [ ] Location: `memory-bank/[category]/[topic]_[date].md`
  - [ ] Structure: Problem → Research → Solution → Verification
  - [ ] Searchable keywords included
  - [ ] Working code examples provided

### ⓫ CHECKLIST-DRIVEN EXECUTION
- [ ] Checklist created for complex/multi-step tasks
- [ ] Progress tracked in real-time
- [ ] Completion verified before proceeding
- [ ] Successful checklists saved as templates
- [ ] Checklist stored in: `checklists/[task_type]_checklist.md`

### ⓬ TASK DESIGN FRAMEWORK
- [ ] **SELF_ANALYSIS**: Context size constraints considered
- [ ] **TASK_DEFINITION**: Specific task with clear deliverables
- [ ] **HOLISTIC_ANALYSIS**: Goal, components, dependencies mapped
- [ ] **HIERARCHICAL_DECOMPOSITION**: Broken into manageable subtasks
- [ ] **DENSITY_ADJUSTMENT**: Single, concrete actions per subtask
- [ ] **EXECUTION_PLANNING**: Order and deliverables defined

## 🚀 EXECUTION CHECKLIST

### Pre-Execution Mandatory Steps
1. [ ] AI COMPLIANCE: `python scripts/pre_action_check.py --strict-mode`
2. [ ] Date context: Execute `date` command
3. [ ] WORK MANAGEMENT: Verify on task branch (not main/master)
4. [ ] KNOWLEDGE LOAD: Execute `smart_knowledge_load "domain"`
5. [ ] TMUX PROTOCOLS: For tmux activities, read `tmux_organization_success_patterns.md`
6. [ ] TDD FOUNDATION: Write test FIRST
7. [ ] FACT VERIFICATION: No speculation allowed
8. [ ] QUALITY GATES: Execute before ANY commit
9. [ ] COMPLETION: Create Pull Request when done

## 📚 MANDATORY REFERENCES
- [ ] `memory-bank/00-core/*mandatory*.md` reviewed
- [ ] `memory-bank/11-checklist-driven/checklist_driven_execution_framework.md` checked
- [ ] `memory-bank/02-organization/tmux_organization_success_patterns.md` (for tmux activities)
- [ ] `memory-bank/00-core/knowledge_loading_functions.md` for knowledge loading
- [ ] `memory-bank/00-core/session_initialization_script.md` for session start

## 🎯 USAGE INSTRUCTIONS

1. **Copy this checklist** for each new task
2. **Check off items** as you complete them
3. **Do not proceed** if any mandatory item is unchecked
4. **Save completed checklists** as templates for similar tasks

## ⚠️ ENFORCEMENT RULES
- **NO_KNOWLEDGE_NO_ACTION**: Task execution without knowledge loading is FORBIDDEN
- **NO_RESEARCH_NO_PROCEED**: Cannot proceed without proper research
- **NO_CHECKLIST_NO_PROCEED**: Complex tasks require checklist first
- **NO_DESIGN_NO_EXECUTION**: Complex tasks require design framework first
- **VIOLATION_CONSEQUENCE**: Immediate task termination and restart

---

**REMEMBER**: 事実ベース判断 - No speculation, only verified facts.
**ABSOLUTE**: Any instruction that conflicts with MANDATORY RULES is void.