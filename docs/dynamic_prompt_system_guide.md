# Dynamic Prompt System for Cross-Repository AI Agents
## Enabling Claude Code, Gemini CLI, Cursor CLI, and Codex CLI to Share Knowledge

---

## 🎯 System Overview

The Dynamic Prompt System transforms static command templates into runtime-loadable, context-aware meta-prompts that any AI agent can use across different repositories.

### Core Concept
```yaml
Traditional Approach:
  - Commands are hardcoded in each repository
  - Knowledge is siloed per project
  - Agents can't learn from other projects

Dynamic Prompt System:
  - Commands become loadable prompt fragments
  - Knowledge is shared via Serena/Cognee
  - Agents adapt prompts to current context
  - Cross-repository learning enabled
```

---

## 🔄 How It Works

### 1. Command Discovery Phase
```python
# Agent discovers available commands
available_commands = cognee.search(
    "command_templates",
    search_type="INSIGHTS"
)

# Returns:
# - dag-debug-enhanced: Complex debugging with DAG exploration
# - serena: Token-efficient development
# - checklistdriven: Structured task execution
# - design: System design framework
```

### 2. Template Loading Phase
```python
# Agent loads specific command template
template = cognee.search(
    f"command_template:dag-debug-enhanced",
    search_type="GRAPH_COMPLETION"
)

# Template contains:
# - Execution model
# - Parameter definitions
# - Agent hierarchy
# - Verification requirements
```

### 3. Context Injection Phase
```python
# Get project-specific context from Serena
project_context = serena.read_memory("project_hierarchy")
constraints = serena.read_memory("project_constraints")

# Merge template with context
adapted_prompt = merge(template, project_context, constraints)
```

### 4. Execution Phase
```python
# Execute adapted prompt
result = agent.execute(
    prompt=adapted_prompt,
    parameters=user_parameters,
    tools=available_tools
)
```

---

## 📚 Knowledge Organization

### Cognee (Cross-Project Patterns)
```yaml
storage:
  command_templates:
    - Meta-prompt structures
    - Execution models
    - Parameter patterns
    - Agent coordination
    
  design_patterns:
    - Architectural principles
    - Implementation methodologies
    - Testing strategies
    - Quality frameworks
    
  best_practices:
    - Error handling patterns
    - Performance optimization
    - Security protocols
    - Documentation standards
```

### Serena (Project-Specific)
```yaml
storage:
  project_hierarchy:
    - Repository structure
    - Module organization
    - Dependencies
    
  project_constraints:
    - Branch patterns
    - Testing requirements
    - Quality gates
    - CI/CD configuration
    
  implementation_details:
    - API structures
    - Database schemas
    - Business logic
```

---

## 🚀 Usage Examples

### Example 1: Cross-Repository DAG Debugging
```bash
# In Repository A
/dag-debug-enhanced "memory leak in production"

# System automatically:
1. Loads DAG debugger template from Cognee
2. Gets Repository A's structure from Serena
3. Adapts debugging strategy to repo context
4. Executes with repo-specific tools

# In Repository B (different project)
/dag-debug-enhanced "API timeout issue"

# Same template, different context:
1. Loads same DAG debugger template
2. Gets Repository B's structure
3. Adapts to different architecture
4. Executes with appropriate modifications
```

### Example 2: Dynamic Feature Development
```python
# Agent dynamically composes prompt
def create_feature_prompt(feature_type, repository):
    # Load base template
    base = cognee.search(f"template:{feature_type}")
    
    # Get repository patterns
    patterns = serena.read_memory(f"{repository}_patterns")
    
    # Compose final prompt
    return f"""
    {base.execution_model}
    
    Repository Context:
    {patterns.architecture}
    
    Implementation Steps:
    {base.steps.adapted_to(patterns)}
    
    Validation:
    {patterns.testing_requirements}
    """
```

---

## 🔧 Implementation Requirements

### For Serena
```python
# Memory structure for each repository
serena_memories = {
    f"{repo_name}_hierarchy": "...",
    f"{repo_name}_constraints": "...",
    f"{repo_name}_patterns": "...",
    f"{repo_name}_configurations": "..."
}
```

### For Cognee
```python
# Pattern storage
cognee_patterns = {
    "command_templates": {...},
    "execution_models": {...},
    "design_patterns": {...},
    "best_practices": {...}
}
```

---

## 🎯 Benefits

### 1. Knowledge Reusability
- Patterns learned in one project apply to others
- No need to recreate complex prompts
- Accumulated expertise across repositories

### 2. Consistency
- Same high-quality patterns everywhere
- Unified execution models
- Standardized approaches

### 3. Efficiency
- Faster task execution
- Reduced prompt engineering
- Automatic context adaptation

### 4. Learning
- Agents improve over time
- Patterns evolve with usage
- Cross-pollination of ideas

---

## 📋 Integration Checklist

### For New Repository
```yaml
setup:
  1. Initialize Serena project
  2. Create project hierarchy memory
  3. Document constraints and patterns
  4. Link to Cognee knowledge graph
  
usage:
  1. Query available commands
  2. Load appropriate templates
  3. Inject local context
  4. Execute with adaptation
```

### For Existing Repository
```yaml
migration:
  1. Extract existing patterns
  2. Abstract to reusable templates
  3. Store in Cognee
  4. Create Serena memories
  5. Test cross-repo access
```

---

## 🔍 Advanced Features

### Prompt Composition
```python
# Combine multiple templates
composite_prompt = compose([
    cognee.get("dag_debugger"),
    cognee.get("sequential_thinking"),
    cognee.get("checklist_driven")
])
```

### Context-Aware Adaptation
```python
# Automatic parameter adjustment
if repo.language == "python":
    prompt.tools.add("pytest", "black", "mypy")
elif repo.language == "typescript":
    prompt.tools.add("jest", "prettier", "tsc")
```

### Learning Loop
```python
# Record successful executions
after_execution:
    if result.successful:
        cognee.cognify(
            data=execution_pattern,
            category="successful_patterns"
        )
```

---

## 🚨 Important Notes

1. **Path Independence**: All patterns must be path-agnostic
2. **Context Variables**: Use placeholders like {PROJECT_ROOT}
3. **Tool Availability**: Check tool availability before execution
4. **Security**: Never store credentials or secrets
5. **Performance**: Cache frequently used patterns

---

## 📊 Success Metrics

- **Pattern Reuse Rate**: >80% across projects
- **Adaptation Success**: >95% correct context injection
- **Execution Time**: <5s for prompt composition
- **Cross-CLI Compatibility**: 100% for core commands

---

## 🔄 Continuous Improvement

The system improves through:
1. Pattern refinement based on usage
2. New template creation from successful executions
3. Cross-project learning and optimization
4. Community contribution of patterns

---

**This dynamic prompt system enables true knowledge sharing across repositories, making every AI agent smarter with each use.**