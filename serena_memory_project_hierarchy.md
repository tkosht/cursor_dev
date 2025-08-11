{
  "repository": {
    "name": "ai-agent-workspace",
    "type": "multi-agent-development",
    "structure": {
      "docs": "Documentation and guides",
      "app/ams": "Agent Management System",
      "memory-bank": "Knowledge storage patterns",
      ".claude/commands": "Dynamic prompt templates",
      "scripts": "Automation and utilities",
      "checklists": "Execution checklists"
    }
  },
  "modules": {
    "ams": {
      "description": "Multi-agent orchestration system",
      "key_patterns": [
        "DAG exploration",
        "Sequential thinking",
        "Agent hierarchy"
      ]
    },
    "memory_bank": {
      "description": "Knowledge management system",
      "key_patterns": [
        "Knowledge loading",
        "Session initialization",
        "Rule enforcement"
      ]
    },
    "commands": {
      "description": "Dynamic prompt system",
      "key_patterns": [
        "Meta-prompts",
        "Parameter handling",
        "Context adaptation"
      ]
    }
  },
  "constraints": {
    "branch_patterns": "feature/*, docs/*, fix/*, task/*",
    "testing": "TDD mandatory, no mocks in integration tests",
    "quality_gates": "Pre-commit hooks, type checking, linting"
  }
}