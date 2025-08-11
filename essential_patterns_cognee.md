# Essential Development Patterns for AI Agents

## Checklist-Driven Execution Framework

### Pre-Execution Checklist Pattern
```yaml
pattern: "Mandatory Pre-Task Validation"
checklist:
  - Rule confirmation: Read relevant documentation
  - Requirement understanding: Accurately grasp user needs
  - Existing check: Verify no duplicate implementation
  - Design validation: Ensure simple design
  - TDD confirmation: Write tests first
```

### Implementation Checklist Pattern
```yaml
pattern: "Quality-Assured Implementation"
checklist:
  - Directory placement: Correct location
  - Naming conventions: Follow existing patterns
  - Configuration: No hardcoded values
  - Error handling: Appropriate exceptions
  - Documentation: Minimal necessary comments
```

### Task Execution Flow
```yaml
pattern: "Structured Task Management"
flow:
  start_task:
    - Mark task as in_progress
    - Load relevant rules
    - Survey existing code
    - Create implementation plan
    
  during_implementation:
    - Follow existing patterns
    - Prefer modification over creation
    - Maintain simplicity
    - Use configuration values
    
  complete_task:
    - Verify tests pass
    - Remove unnecessary files
    - Update minimal documentation
    - Mark task as completed
```

## Test-Driven Development Patterns

### TDD Cycle
```yaml
pattern: "Red-Green-Refactor"
stages:
  RED:
    - Write failing test first
    - Define expected behavior
    - Run test to confirm failure
    
  GREEN:
    - Write minimal code to pass
    - Focus on functionality
    - Avoid premature optimization
    
  REFACTOR:
    - Improve code quality
    - Maintain test passing
    - Enhance readability
```

### Test Organization
```yaml
pattern: "Structured Test Management"
structure:
  unit_tests:
    location: tests/unit/
    naming: test_*.py
    scope: Single function/class
    
  integration_tests:
    location: tests/integration/
    naming: test_*_integration.py
    scope: Multiple components
    
  e2e_tests:
    location: tests/e2e/
    naming: test_*_e2e.py
    scope: Full workflow
```

## Knowledge Management Patterns

### Smart Knowledge Loading
```yaml
pattern: "Efficient Knowledge Access"
implementation:
  default_mode:
    time: 5-15 seconds
    scope: Essential patterns
    usage: All standard tasks
    
  comprehensive_mode:
    time: 30-60 seconds
    scope: Full knowledge base
    usage: Complex or new tasks
    
loading_sequence:
  1. Identify task domain
  2. Select relevant categories
  3. Load core patterns
  4. Cache for session
```

### Memory Bank Organization
```yaml
pattern: "Hierarchical Knowledge Storage"
structure:
  00-core: Mandatory rules and frameworks
  01-cognee: Cross-project patterns
  02-organization: Project structure
  03-implementation: Code patterns
  04-quality: Testing and validation
  
access_pattern:
  - High frequency: Core rules
  - Task-specific: Implementation patterns
  - Pre-commit: Quality frameworks
```

## Multi-Agent Coordination Patterns

### Agent Communication
```yaml
pattern: "Structured Agent Messaging"
channels:
  upward:
    - Validated findings
    - New hypotheses
    - Completion status
    
  downward:
    - Task assignments
    - Context updates
    - Priority changes
    
  lateral:
    - Shared discoveries
    - Resource requests
    - Synchronization
```

### Task Distribution
```yaml
pattern: "Optimal Agent Allocation"
strategy:
  complexity_based:
    simple: Single agent
    moderate: 2-3 agents
    complex: 5+ agents
    
  specialization_based:
    code_analysis: Serena agent
    reasoning: Sequential thinker
    validation: Test runner
```

## Error Handling Patterns

### Error Analysis Protocol
```yaml
pattern: "Systematic Error Resolution"
stages:
  1_detection:
    - Capture full error context
    - Log stack trace
    - Save environment state
    
  2_analysis:
    - Identify error type
    - Trace root cause
    - Check similar issues
    
  3_resolution:
    - Develop fix strategy
    - Implement solution
    - Add regression test
    
  4_prevention:
    - Update error handling
    - Document solution
    - Share knowledge
```

### Recovery Strategies
```yaml
pattern: "Graceful Failure Management"
strategies:
  retry_with_backoff:
    - Initial wait: 1 second
    - Max retries: 3
    - Exponential backoff
    
  fallback_execution:
    - Primary method fails
    - Switch to alternative
    - Log degradation
    
  safe_mode:
    - Disable risky operations
    - Continue core functionality
    - Alert user
```

## Performance Optimization Patterns

### Token Optimization
```yaml
pattern: "Efficient Token Usage"
strategies:
  search_first:
    - Use Grep/Glob before Read
    - Semantic search with Serena
    - Load only necessary sections
    
  batch_operations:
    - Combine related queries
    - Parallel tool execution
    - Single response for multiple tasks
    
  caching:
    - Store frequently used patterns
    - Reuse search results
    - Session-level memory
```

### Parallel Execution
```yaml
pattern: "Concurrent Task Processing"
implementation:
  tool_parallelization:
    - Multiple Bash commands
    - Simultaneous file reads
    - Parallel searches
    
  hypothesis_testing:
    - Top 3 concurrent
    - First success wins
    - Aggregate learnings
```

## Documentation Patterns

### Minimal Documentation
```yaml
pattern: "Just Enough Documentation"
principles:
  - Document why, not what
  - Code should be self-explanatory
  - Examples over explanations
  - Update only when necessary
  
structure:
  README: Project overview and setup
  API: Public interface documentation
  CHANGELOG: Version history
  CONTRIBUTING: Development guidelines
```

### Knowledge Recording
```yaml
pattern: "Systematic Knowledge Capture"
triggers:
  - New pattern discovered
  - Problem solved
  - Research completed
  - Error resolved
  
format:
  title: Clear, searchable
  problem: Context and symptoms
  solution: Step-by-step approach
  verification: How to confirm success
  tags: Keywords for retrieval
```

## Git Workflow Patterns

### Branch Management
```yaml
pattern: "Feature Branch Workflow"
naming:
  feature/*: New functionality
  fix/*: Bug fixes
  docs/*: Documentation
  task/*: General tasks
  
workflow:
  1. Create from main
  2. Implement with TDD
  3. Pass quality gates
  4. Create pull request
  5. Merge after review
```

### Commit Patterns
```yaml
pattern: "Semantic Commits"
format:
  feat: New feature
  fix: Bug fix
  docs: Documentation
  test: Test addition
  refactor: Code improvement
  
message_structure:
  type(scope): description
  
  body: detailed explanation
  
  footer: breaking changes
```

These patterns form the essential knowledge base for consistent, high-quality development across any repository and AI agent system.