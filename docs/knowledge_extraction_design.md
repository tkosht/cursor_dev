# Cross-Repository Knowledge Management System Design
## Serena & Cognee Integration for Reusable AI Agent Knowledge

---

## 🎯 Executive Summary

This design enables AI agents (Claude Code, Gemini CLI, Cursor CLI, etc.) to dynamically access and apply knowledge from any repository through strategic use of Serena (project-specific) and Cognee (cross-project patterns) MCPs.

### Core Objectives
1. **Knowledge Portability**: Enable knowledge reuse across different repositories and projects
2. **Dynamic Prompt Enhancement**: Allow runtime loading of .claude/commands as meta-prompts
3. **Hierarchical Organization**: Manage knowledge at repository/project/sub-project levels
4. **Efficiency Balance**: Extract only essential knowledge to minimize processing time

---

## 📊 Knowledge Categorization Framework

### 1. Cognee Knowledge Graph (Cross-Project Patterns)
**Purpose**: Store abstracted, reusable patterns and principles

```yaml
categories:
  architectural_patterns:
    - MCP integration strategies
    - Multi-agent coordination patterns
    - DAG-based task decomposition
    - Sequential thinking frameworks
    
  development_methodologies:
    - Test-driven development principles
    - Checklist-driven execution framework
    - Error analysis protocols
    - Quality gates and validation
    
  ai_agent_patterns:
    - Dynamic prompt loading mechanisms
    - Context management strategies
    - Knowledge loading functions
    - Task design frameworks
    
  command_templates:
    - Meta-prompt structures from .claude/commands
    - Parameter patterns and options
    - Execution models and flows
    - Agent hierarchy templates
```

### 2. Serena Memory Structure (Project-Specific)
**Purpose**: Store project-specific implementations and constraints

```yaml
hierarchy:
  repository_level:
    - Project configuration and setup
    - Directory structures
    - Dependency management
    - CI/CD configurations
    
  project_level:
    - Module-specific implementations
    - API structures
    - Database schemas
    - Business logic patterns
    
  subproject_level:
    - Component-specific details
    - Feature implementations
    - Test suites
    - Documentation references
```

---

## 🔍 Knowledge Extraction Strategy

### Phase 1: Core Knowledge Identification (高優先度)

#### Essential Documents to Extract:
```yaml
mandatory_rules:
  source: AGENTS.md, CLAUDE.md
  target: Cognee
  extraction:
    - Pre-task knowledge protocols
    - MCP selection criteria
    - Security absolutes
    - Value assessment framework
    
architectural_patterns:
  source: docs/02.basic_design/
  target: Cognee
  extraction:
    - System architecture principles
    - Component interaction patterns
    - Integration strategies
    
implementation_guides:
  source: docs/03.detail_design/
  target: Both (patterns → Cognee, specifics → Serena)
  extraction:
    - TDD implementation patterns
    - Code organization strategies
    - Testing frameworks
    
command_templates:
  source: .claude/commands/
  target: Cognee
  extraction:
    - Meta-prompt structures
    - Execution models
    - Agent coordination patterns
    - Dynamic parameter handling
```

### Phase 2: Domain-Specific Knowledge

#### AMS System Knowledge:
```yaml
ams_patterns:
  source: app/ams/docs/
  target: Mixed
  cognee_extraction:
    - DAG debugger patterns
    - Multi-agent orchestration
    - Testing strategies
    - Performance optimization techniques
  serena_extraction:
    - AMS-specific implementations
    - Configuration details
    - Test results and reports
```

#### Memory Bank Patterns:
```yaml
memory_bank:
  source: memory-bank/00-core/
  target: Cognee
  extraction:
    - Knowledge loading functions
    - Session initialization patterns
    - Mandatory rule frameworks
    - Quality control mechanisms
```

---

## 🏗️ Implementation Architecture

### 1. Knowledge Recording Structure

```python
# Cognee Knowledge Graph Structure
cognee_knowledge = {
    "meta_prompts": {
        "dag_debugger": {
            "pattern": "DAG exploration with Serena integration",
            "parameters": ["max_depth", "parallel_width", "time_limit"],
            "execution_model": "hierarchical_agent_coordination",
            "reusable_components": [...]
        },
        "serena_command": {
            "pattern": "Token-efficient structured development",
            "modes": ["quick", "deep", "code-focused"],
            "thinking_steps": "3-15 based on complexity"
        }
    },
    "design_patterns": {
        "checklist_driven_execution": {...},
        "multi_agent_coordination": {...},
        "sequential_thinking": {...}
    },
    "principles": {
        "mandatory_rules": {...},
        "quality_gates": {...},
        "security_protocols": {...}
    }
}

# Serena Memory Structure
serena_memories = {
    "repository": "project_name",
    "project_constraints": {...},
    "module_implementations": {
        "ams": {...},
        "core": {...}
    },
    "configuration": {
        "dependencies": {...},
        "environment": {...}
    }
}
```

### 2. Dynamic Loading Mechanism

```python
# Dynamic Command Loading Pattern
def load_dynamic_prompt(command_name, context):
    """
    Load and adapt command template for current context
    """
    # 1. Fetch base template from Cognee
    base_template = cognee.search(
        f"command_template:{command_name}",
        search_type="GRAPH_COMPLETION"
    )
    
    # 2. Get project-specific adaptations from Serena
    project_context = serena.read_memory(
        f"{context.repository}_constraints"
    )
    
    # 3. Merge and adapt
    adapted_prompt = merge_template_with_context(
        base_template,
        project_context
    )
    
    return adapted_prompt
```

---

## 📝 Knowledge Extraction Rules

### Inclusion Criteria (Include in Knowledge Base)
1. **Patterns**: Reusable design patterns, architectural decisions
2. **Frameworks**: Execution models, coordination strategies
3. **Principles**: Core rules, quality standards, best practices
4. **Templates**: Command structures, prompt templates
5. **Strategies**: Problem-solving approaches, optimization techniques

### Exclusion Criteria (Skip or Minimize)
1. **Temporal Data**: Dates, version-specific information
2. **Instance-Specific**: Specific test results, individual bug reports
3. **Redundant**: Duplicate information across documents
4. **Verbose**: Lengthy explanations that can be summarized
5. **Path-Specific**: Absolute paths, environment-specific configs

---

## 🚀 Implementation Plan

### Stage 1: Infrastructure Setup
```bash
# 1. Initialize Serena project structure
serena.activate_project("/home/devuser/workspace")
serena.write_memory("project_hierarchy", hierarchy_structure)

# 2. Prepare Cognee knowledge graph
cognee.prune()  # Clean slate
cognee.add_developer_rules(base_path=".")
```

### Stage 2: Core Knowledge Extraction
```yaml
priority_1_extraction:
  - AGENTS.md → Cognee (mandatory rules)
  - .claude/commands/* → Cognee (meta-prompts)
  - memory-bank/00-core/* → Cognee (core patterns)
  
priority_2_extraction:
  - docs/0[2-3].* → Mixed (patterns vs implementations)
  - app/ams/docs/*guide.md → Cognee (strategies)
  - docs/90.references/* → Serena (project configs)
```

### Stage 3: Knowledge Recording
```python
# Recording Strategy
for document in priority_documents:
    content = extract_core_knowledge(document)
    
    if is_pattern_or_principle(content):
        cognee.cognify(
            data=abstract_to_pattern(content),
            graph_model_file="pattern_model.py"
        )
    
    if is_project_specific(content):
        serena.write_memory(
            memory_name=f"{project}_{module}_{topic}",
            content=content
        )
```

### Stage 4: Validation
```yaml
validation_tests:
  - Cross-repository pattern application
  - Dynamic command loading
  - Knowledge retrieval performance
  - Context adaptation accuracy
```

---

## 🔄 Dynamic Prompt System Design

### Command as Meta-Prompt Architecture
```yaml
capability:
  description: "Commands become runtime-loadable prompt fragments"
  
mechanism:
  1_discovery:
    - Agent queries available commands
    - Cognee returns command patterns
    
  2_loading:
    - Agent loads command template
    - Serena provides project context
    
  3_adaptation:
    - Merge template with context
    - Generate task-specific prompt
    
  4_execution:
    - Execute adapted prompt
    - Record results for learning

benefits:
  - Runtime prompt composition
  - Context-aware adaptation
  - Cross-CLI compatibility
  - Learning from execution
```

---

## 📊 Success Metrics

1. **Knowledge Density**: 80% reduction in stored volume while maintaining 100% critical knowledge
2. **Retrieval Speed**: <5 seconds for pattern retrieval, <10 seconds for complex searches
3. **Cross-Repository Success**: 90% successful pattern application across different projects
4. **Dynamic Loading**: 100% command templates loadable and executable
5. **Agent Compatibility**: Works with Claude Code, Gemini CLI, Cursor CLI, Codex CLI

---

## 🎯 Next Steps

1. **Immediate**: Create knowledge extraction scripts
2. **Short-term**: Record core patterns to Cognee
3. **Medium-term**: Build Serena memory hierarchy
4. **Long-term**: Implement dynamic loading system
5. **Continuous**: Refine and optimize based on usage

---

## 📚 References

- Original Requirements: User task specification
- Project Documentation: docs/**, app/ams/docs/**
- Command Templates: .claude/commands/**
- Memory Bank: memory-bank/**
- Agent Rules: AGENTS.md, CLAUDE.md