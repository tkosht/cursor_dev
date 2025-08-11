# Dynamic Command Templates for AI Agents

## DAG Debug Enhanced Command

### Meta Structure
```yaml
name: Enhanced_DAG_Debugger
version: 2.0.0
purpose: Complex debugging with DAG exploration and multi-agent coordination
```

### Execution Model
```yaml
phases:
  1_initial_diagnosis:
    tool: Sequential Thinking
    action: Analyze symptoms and generate hypotheses
    
  2_dag_exploration:
    tool: DAG + Serena + Multi-Agent
    actions:
      - Semantic analysis per node
      - Checklist-driven execution
      - Sequential thinking recording
      - Sub-agent specialization
      
  3_verification:
    tool: All Tools
    actions:
      - Implement fixes
      - Run test suites
      - Validate regressions
```

### Agent Hierarchy Template
```yaml
orchestrator:
  responsibilities: [dag_management, strategy_coordination, agent_allocation]
  
specialized_agents:
  serena_analyst:
    tasks: [find_symbol, find_references, get_overview]
    
  sequential_thinker:
    tasks: [premise_validation, hypothesis_testing, parallel_exploration]
    
  fix_validator:
    tasks: [test_execution, regression_checking, performance_validation]
```

### Options Pattern
```yaml
--max-depth: DAG exploration depth (default: 8)
--time-limit: Execution timeout in minutes (default: 30)
--parallel-width: Concurrent hypotheses (default: 3)
--test-mode: Dry run without changes
--verbose: Show detailed process
--focus: Target area (frontend/backend/db/infra)
--sub-agents: Available agents (default: 5)
--serena-depth: Semantic search depth (default: 3)
```

## Serena Command Template

### Token-Efficient Development Pattern
```yaml
usage: /serena <problem> [options]

modes:
  quick: 
    thoughts: 3-5
    use_case: simple_bugs
    
  standard:
    thoughts: 6-10
    use_case: feature_development
    
  deep:
    thoughts: 10-15
    use_case: architecture_design
```

### Option Flags
```yaml
-q: Quick mode for simple tasks
-d: Deep mode for complex systems
-c: Code-focused analysis
-s: Step-by-step implementation
-v: Verbose output
-r: Include research phase
-t: Create implementation todos
```

## Checklist-Driven Command

### Execution Pattern
```yaml
trigger: Multi-step or complex tasks
process:
  1. Parse task requirements
  2. Generate execution checklist
  3. Execute each item sequentially
  4. Mark progress in real-time
  5. Verify completion
  6. Save successful template
```

### Checklist Structure
```yaml
format:
  header: Task description and goals
  items:
    - [ ] Action item with clear deliverable
    - [ ] Verification step
    - [ ] Quality check
  footer: Success criteria and next steps
```

## Design Command Template

### Task Design Framework
```yaml
stages:
  1_self_analysis:
    - Consider context constraints
    - Acknowledge thinking limits
    
  2_task_definition:
    - Define specific deliverables
    - Clarify requirements
    
  3_holistic_analysis:
    - Map goal to components
    - Identify dependencies
    
  4_hierarchical_decomposition:
    - Break into subtasks
    - Create tree structure
    
  5_density_adjustment:
    - Ensure single actions
    - Review granularity
    
  6_execution_planning:
    - Order tasks
    - Define outputs
```

## Universal Command Patterns

### Parameter Handling
```yaml
pattern: Dynamic parameter injection
mechanism:
  - Parse user arguments
  - Load default values
  - Override with specifics
  - Validate constraints
  - Execute with merged params
```

### Context Adaptation
```yaml
pattern: Project-aware execution
steps:
  - Detect project type
  - Load project constraints
  - Adapt command behavior
  - Apply project rules
  - Execute with context
```

### Error Handling
```yaml
pattern: Graceful failure recovery
strategy:
  - Capture error state
  - Log detailed context
  - Attempt recovery
  - Fallback to safe state
  - Report to user
```

### Result Formatting
```yaml
pattern: Structured output
format:
  summary: Brief overview
  details: Full execution log
  artifacts: Generated files
  next_steps: Recommended actions
  metrics: Performance data
```

## Meta-Command Patterns

### Command Composition
```yaml
pattern: Combine multiple commands
example: |
  composite = dag-debug + serena + checklist
  execute(composite, unified_context)
```

### Command Learning
```yaml
pattern: Improve from execution
process:
  - Record execution patterns
  - Analyze success metrics
  - Refine templates
  - Update knowledge base
```

### Cross-CLI Adaptation
```yaml
pattern: Universal command interface
compatibility:
  claude_code: Native support
  gemini_cli: Syntax adaptation
  cursor_cli: Parameter mapping
  codex_cli: Format conversion
```

These command templates enable dynamic prompt loading and cross-repository execution for any AI agent CLI system.