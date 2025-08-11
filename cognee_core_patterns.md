# Core Patterns for Cognee Knowledge Graph
## Abstracted Patterns and Principles for Cross-Repository Use

---

## 🎯 Mandatory AI Agent Rules

### Pre-Task Knowledge Protocol
```yaml
pattern: "Knowledge Loading Before Execution"
description: "Every task must load relevant knowledge before execution"
implementation:
  - Establish temporal context (date command)
  - Select appropriate MCP (Serena for code, Cognee for patterns)
  - Load domain knowledge via selected MCP
  - Verify knowledge completeness
  - Execute with continuous verification

application_contexts:
  - Regular conversation start
  - Command execution (/command)
  - Task continuation
  - Any task regardless of entry point
```

### MCP Selection Strategy
```yaml
pattern: "Context-Based MCP Selection"
criteria:
  CODE_TASK: 
    mcp: Serena
    use_cases: [editing, debugging, project structure, symbol operations]
  KNOWLEDGE_TASK:
    mcp: Cognee
    use_cases: [patterns, principles, cross-project insights]
  HYBRID_TASK:
    flow: Cognee(strategy) → Serena(implementation)
  DISCOVERY_TASK:
    flow: Serena(record) → Cognee(promote)
```

### Value Assessment Framework
```yaml
pattern: "5-Point Action Validation"
checklist:
  0_SECURITY: "No credential exposure"
  1_USER_VALUE: "Serves user not convenience"
  2_LONG_TERM: "Sustainable not quick-fix"
  3_FACT_BASED: "Verified not speculation"
  4_KNOWLEDGE: "Related rules loaded"
  5_ALTERNATIVES: "Better approach evaluated"
```

---

## 🏗️ Architectural Patterns

### DAG-Based Task Decomposition
```yaml
pattern: "Hierarchical DAG Exploration"
components:
  orchestrator:
    - DAG topology management
    - Strategy coordination
    - Sub-agent allocation
    
  node_execution:
    - Hypothesis generation
    - Verification planning
    - Scoring algorithm
    - Context propagation
    
  validation:
    - Initial state capture
    - Root cause validation
    - Regression testing
    
scoring_formula: |
  priority = (suspicion_score * urgency) / (1 + cost_estimate)
```

### Multi-Agent Coordination
```yaml
pattern: "Specialized Agent Hierarchy"
structure:
  orchestrator:
    role: "Central coordination"
    persistent_knowledge: [problem_definition, validation_criteria]
    
  specialized_agents:
    serena_analyst:
      capabilities: [semantic_analysis, symbol_mapping, dependency_graphs]
    sequential_thinker:
      capabilities: [step_reasoning, hypothesis_testing, parallel_exploration]
    fix_validator:
      capabilities: [test_execution, regression_checking, performance_validation]
      
communication:
  upward: [validated_findings, new_hypotheses]
  downward: [search_targets, assumptions]
  lateral: [shared_patterns, correlated_insights]
```

### Sequential Thinking Framework
```yaml
pattern: "Staged Reasoning Process"
stages:
  1_premise_validation:
    - Confirm assumptions
    - Verify inputs
    
  2_hypothesis_design:
    - Generate test cases
    - Define expected results
    
  3_verification:
    - Execute tests
    - Observe results
    
  4_interpretation:
    - Analyze observations
    - Determine next actions
    
parallel_exploration:
  - Top 3 hypotheses concurrent
  - First confirmed result wins
  - Partial results retained
```

---

## 📝 Command Template Patterns

### Token-Efficient Development Pattern
```yaml
pattern: "Serena Command Structure"
modes:
  quick: {thoughts: 3-5, use_case: "simple bugs"}
  standard: {thoughts: 6-10, use_case: "features"}
  deep: {thoughts: 10-15, use_case: "architecture"}
  
options:
  -c: "code-focused analysis"
  -s: "step-by-step implementation"
  -v: "verbose process output"
  -r: "include research phase"
  -t: "create implementation todos"
```

### Checklist-Driven Execution
```yaml
pattern: "Structured Task Management"
principles:
  - Create checklist for multi-step tasks
  - Mark progress in real-time
  - Verify completion before proceeding
  - Save successful checklists as templates
  
storage_pattern: "checklists/{task_type}_checklist.md"
```

---

## 🔧 Development Methodologies

### Test-Driven Development
```yaml
pattern: "TDD Implementation"
cycle:
  1_RED: "Write failing test first"
  2_GREEN: "Minimal code to pass"
  3_REFACTOR: "Improve without breaking"
  
constraints:
  - No mocks in integration tests
  - Real API calls preferred
  - 3-5 external calls max in CI
```

### Error Analysis Protocol
```yaml
pattern: "Systematic Error Resolution"
steps:
  1_capture: "Complete state snapshot"
  2_reproduce: "Minimal test case"
  3_analyze: "Root cause identification"
  4_fix: "Targeted solution"
  5_validate: "Regression prevention"
```

---

## 🚀 Execution Models

### Dynamic Prompt Loading
```yaml
pattern: "Runtime Prompt Composition"
mechanism:
  1_discovery: "Query available templates"
  2_loading: "Fetch template structure"
  3_context: "Get project specifics"
  4_merge: "Combine template + context"
  5_execute: "Run adapted prompt"
  
benefits:
  - Cross-CLI compatibility
  - Context-aware adaptation
  - Learning from execution
```

### Knowledge Recording Protocol
```yaml
pattern: "Systematic Knowledge Capture"
triggers:
  - WebSearch results
  - Implementation methods
  - Problem solutions
  - Discovered patterns
  
format:
  location: "{KNOWLEDGE_DIR}/{category}/{topic}_{date}.md"
  structure: "Problem → Research → Solution → Verification"
  requirements: [searchable_keywords, working_examples]
```

---

## 🛡️ Quality & Security Patterns

### Security Absolutes
```yaml
pattern: "Credential Protection"
forbidden_patterns:
  - "env.*API"
  - "cat.*key"
  - "echo.*token"
  - "grep.*secret"
  
enforcement: "Immediate termination on detection"
```

### Quality Gates
```yaml
pattern: "Progressive Quality Assurance"
stages:
  pre_commit:
    - Type checking
    - Linting
    - Unit tests
    
  pre_merge:
    - Integration tests
    - Performance tests
    - Security scan
    
  post_deployment:
    - Smoke tests
    - Monitoring
    - Rollback readiness
```

---

## 📊 Performance Optimization Patterns

### Token Efficiency
```yaml
pattern: "Minimal Token Usage"
strategies:
  - Use semantic search over full reads
  - Abstract patterns over implementations
  - Cache frequently accessed knowledge
  - Batch related queries
```

### Parallel Processing
```yaml
pattern: "Concurrent Exploration"
implementation:
  - Multiple hypothesis testing
  - Parallel tool execution
  - Async result aggregation
  - Early termination on success
```

---

## 🔄 Adaptation Patterns

### Context Variable System
```yaml
pattern: "Path-Independent References"
variables:
  {PROJECT_ROOT}: "Repository base path"
  {KNOWLEDGE_DIR}: "Knowledge storage location"
  {FILE}: "Generic file reference"
  {PARAMETERS}: "Task-specific values"
  
usage: "Replace at runtime with actual values"
```

### Cross-Repository Compatibility
```yaml
pattern: "Universal Pattern Application"
requirements:
  - No hardcoded paths
  - Language-agnostic principles
  - Tool-independent strategies
  - Framework-neutral patterns
```

---

## 📚 Meta-Patterns

### Pattern Evolution
```yaml
pattern: "Continuous Pattern Improvement"
process:
  1_usage: "Track pattern application"
  2_feedback: "Collect success metrics"
  3_refinement: "Update based on results"
  4_promotion: "Elevate successful patterns"
```

### Knowledge Hierarchy
```yaml
pattern: "Layered Knowledge Organization"
levels:
  principles: "Universal truths"
  patterns: "Reusable solutions"
  practices: "Implementation guides"
  examples: "Concrete instances"
```

---

These patterns form the core reusable knowledge that can be applied across any repository, enabling consistent, high-quality AI agent behavior regardless of the specific project context.