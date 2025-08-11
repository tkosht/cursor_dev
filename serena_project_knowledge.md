# Project-Specific Knowledge for Serena
## Repository: ai-agent-workspace

---

## 📁 Project Hierarchy

```yaml
repository_name: ai-agent-workspace
repository_type: multi-agent-development-framework
primary_language: python
secondary_languages: [typescript, bash, markdown]

structure:
  docs/:
    purpose: "Comprehensive documentation hub"
    subdirs:
      01.requirements: "Target personas and requirements"
      02.basic_design: "Architecture and design patterns"
      03.detail_design: "Implementation guides"
      04.implementation_reports: "Status and analysis reports"
      05.articles: "Guides and tutorials"
      90.references: "Configuration and templates"
      91.notes: "Development notes and methodologies"
      
  app/ams/:
    purpose: "Agent Management System implementation"
    structure:
      agents/: "Agent implementations"
      core/: "Core system components"
      docs/: "AMS-specific documentation"
      tests/: "Test suites"
    key_features:
      - DAG-based task orchestration
      - Multi-agent coordination
      - Sequential thinking integration
      
  memory-bank/:
    purpose: "Knowledge storage and management"
    categories:
      00-core: "Mandatory rules and frameworks"
      01-cognee: "Cognee integration patterns"
      02-organization: "Project organization"
      03-implementation: "Implementation patterns"
      04-quality: "Quality frameworks"
      
  .claude/commands/:
    purpose: "Dynamic command templates"
    structure:
      tasks/: "Task-specific commands"
      meta/: "Meta-command patterns"
      organization/: "Organization commands"
      templates/: "Reusable templates"
      
  scripts/:
    purpose: "Automation and utilities"
    key_scripts:
      - extract_core_knowledge.py
      - pre_action_check.py
      - mandatory_rules_quick_access.sh
      
  checklists/:
    purpose: "Execution checklists"
    templates:
      - mandatory_rules_checklist.md
      - knowledge_extraction_implementation_checklist.md
```

---

## 🔧 Project Configuration

### Development Environment
```yaml
python_version: "3.10+"
node_version: "18.x"
package_manager: "npm"

virtual_environments:
  python: ".venv"
  location: "project_root"
  
dependencies_management:
  python: "requirements.txt"
  javascript: "package.json"
```

### Git Configuration
```yaml
default_branch: "main"
branch_patterns:
  feature: "feature/*"
  docs: "docs/*"
  fix: "fix/*"
  task: "task/*"
  
workflow:
  - Create feature branch
  - Implement with TDD
  - Run quality gates
  - Create pull request
  - Merge after review
```

### CI/CD Pipeline
```yaml
pre_commit_hooks:
  - Type checking (mypy)
  - Linting (flake8, black)
  - Unit tests
  
github_actions:
  - Automated testing
  - Coverage reporting
  - Security scanning
  
quality_gates:
  coverage_threshold: 80%
  max_complexity: 10
  max_line_length: 120
```

---

## 📋 Project Constraints

### Testing Requirements
```yaml
methodology: "Test-Driven Development"

rules:
  - Write test first (RED)
  - Minimal implementation (GREEN)
  - Refactor with safety (REFACTOR)
  
constraints:
  - NO mocks in integration/E2E tests
  - Real API calls preferred
  - 3-5 external calls max in CI
  - All tests must pass before commit
```

### Code Quality Standards
```yaml
formatting:
  python:
    - black formatter
    - isort for imports
    - Line length: 120
    
  typescript:
    - prettier
    - ESLint rules
    
documentation:
  - Docstrings for all public functions
  - Type hints mandatory
  - README for each module
```

### Security Policies
```yaml
forbidden:
  - Hardcoded credentials
  - API keys in code
  - Secrets in logs
  - Unencrypted sensitive data
  
required:
  - Environment variables for secrets
  - Secure credential storage
  - Input validation
  - SQL injection prevention
```

---

## 🎯 Project-Specific Patterns

### AMS Architecture
```yaml
core_components:
  TaskOrchestrator:
    - Manages DAG execution
    - Coordinates agents
    - Tracks progress
    
  AgentPool:
    - Agent lifecycle management
    - Resource allocation
    - Performance monitoring
    
  KnowledgeManager:
    - Knowledge loading
    - Context management
    - Memory updates
```

### Command System
```yaml
command_structure:
  base_path: ".claude/commands"
  
  execution_flow:
    1. Parse command and arguments
    2. Load command template
    3. Inject project context
    4. Execute with tools
    5. Return formatted results
    
  available_commands:
    - /dag-debug-enhanced
    - /serena
    - /checklistdriven
    - /design
    - /note_article
```

### Memory Bank Organization
```yaml
knowledge_categories:
  core_rules:
    path: "memory-bank/00-core"
    access: "High frequency"
    
  implementation_patterns:
    path: "memory-bank/03-implementation"
    access: "Task-specific"
    
  quality_frameworks:
    path: "memory-bank/04-quality"
    access: "Pre-commit"
```

---

## 🔄 Integration Points

### MCP Connections
```yaml
serena:
  purpose: "Code and project management"
  memories:
    - project_hierarchy
    - project_constraints
    - implementation_details
    
cognee:
  purpose: "Pattern and principle storage"
  knowledge:
    - Command templates
    - Design patterns
    - Best practices
```

### Tool Integrations
```yaml
available_tools:
  file_operations: [Read, Write, Edit, MultiEdit]
  search: [Grep, Glob, Find]
  execution: [Bash, Python]
  mcp: [serena_*, cognee_*]
  ai: [WebSearch, TodoWrite]
```

---

## 📊 Metrics & Monitoring

### Performance Targets
```yaml
response_times:
  knowledge_loading: "<5 seconds"
  pattern_retrieval: "<3 seconds"
  command_execution: "<30 seconds"
  
resource_limits:
  memory_usage: "500MB max"
  token_usage: "Optimize for <10k per task"
```

### Success Metrics
```yaml
code_quality:
  test_coverage: ">80%"
  zero_critical_bugs: true
  documentation_complete: true
  
development_velocity:
  feature_completion: "Within sprint"
  bug_fix_time: "<24 hours"
  PR_review_time: "<4 hours"
```

---

## 🚀 Deployment Configuration

### Environment Variables
```yaml
required:
  - OPENAI_API_KEY
  - ANTHROPIC_API_KEY
  - GITHUB_TOKEN
  
optional:
  - DEBUG_MODE
  - LOG_LEVEL
  - MAX_RETRIES
```

### Service Configuration
```yaml
ams_service:
  host: "localhost"
  port: 8000
  workers: 4
  
database:
  type: "postgresql"
  connection_pool: 10
  
cache:
  type: "redis"
  ttl: 3600
```

---

This project-specific knowledge provides the complete context needed for AI agents to work effectively within this repository while maintaining the ability to apply learned patterns to other projects.