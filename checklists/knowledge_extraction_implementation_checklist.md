# Knowledge Extraction Implementation Checklist
## Priority-Based Execution Plan for Serena & Cognee Integration

---

## 📋 Phase 1: Critical Core Knowledge (MUST EXTRACT)
**Target: Cognee** | **Time Estimate: 30-45 minutes**

### Mandatory Rules & Frameworks
- [ ] Extract mandatory rules from AGENTS.md
  - [ ] Pre-task knowledge protocol
  - [ ] MCP selection criteria  
  - [ ] Security absolutes
  - [ ] Value assessment framework
  - [ ] Work management protocol

- [ ] Extract core patterns from memory-bank/00-core/
  - [ ] Knowledge loading functions pattern
  - [ ] Checklist-driven execution framework
  - [ ] Test-driven development principles
  - [ ] Error analysis protocols

### Dynamic Command Templates
- [ ] Extract meta-prompts from .claude/commands/tasks/
  - [ ] dag-debug-enhanced.md → DAG exploration patterns
  - [ ] serena.md → Token-efficient development patterns
  - [ ] checklistdriven.md → Checklist execution patterns
  - [ ] design.md → Design task patterns

---

## 📋 Phase 2: Architectural Patterns (HIGH PRIORITY)
**Target: Cognee** | **Time Estimate: 20-30 minutes**

### System Design Patterns
- [ ] Extract from docs/02.basic_design/
  - [ ] a2a_architecture.md → Architecture principles
  - [ ] Component interaction patterns
  
### Implementation Patterns  
- [ ] Extract from docs/03.detail_design/
  - [ ] TDD implementation guide patterns
  - [ ] Implementation methodologies

### AMS Advanced Patterns
- [ ] Extract from app/ams/docs/
  - [ ] DAG debugger methodology
  - [ ] Multi-agent coordination patterns
  - [ ] Testing strategies
  - [ ] Performance optimization patterns

---

## 📋 Phase 3: Project-Specific Knowledge (MEDIUM PRIORITY)
**Target: Serena** | **Time Estimate: 20-30 minutes**

### Repository Structure
- [ ] Create project hierarchy memory
  ```yaml
  repository: "ai-agent-workspace"
  modules:
    - ams: "Agent Management System"
    - docs: "Documentation hub"
    - memory-bank: "Knowledge storage"
    - .claude/commands: "Dynamic prompts"
  ```

### Configuration & Setup
- [ ] Extract from docs/90.references/
  - [ ] Directory structure
  - [ ] Git workflow patterns
  - [ ] Configuration templates

### Project Constraints
- [ ] Document project-specific rules
  - [ ] Branch naming patterns
  - [ ] Testing requirements
  - [ ] Quality gates

---

## 📋 Phase 4: Knowledge Optimization (SELECTIVE)
**Time Estimate: 15-20 minutes**

### Pattern Abstraction
- [ ] Convert specific implementations to patterns
  - [ ] Remove path-specific references
  - [ ] Abstract concrete examples to templates
  - [ ] Generalize project-specific rules

### Deduplication
- [ ] Identify overlapping knowledge
  - [ ] Merge similar patterns
  - [ ] Create single source of truth
  - [ ] Link related concepts

---

## 🚀 Execution Script Template

```python
# Phase 1: Core Knowledge to Cognee
core_knowledge = {
    "mandatory_rules": extract_from("AGENTS.md", rules_only=True),
    "command_templates": extract_from(".claude/commands/tasks/*.md", 
                                     pattern_only=True),
    "core_patterns": extract_from("memory-bank/00-core/*.md", 
                                 essential_only=True)
}

for category, content in core_knowledge.items():
    cognee.cognify(
        data=abstract_pattern(content),
        graph_model_name=f"{category}_patterns"
    )

# Phase 2: Architecture to Cognee  
architecture_patterns = {
    "system_design": extract_patterns("docs/02.basic_design/*.md"),
    "implementation": extract_patterns("docs/03.detail_design/*.md"),
    "ams_patterns": extract_patterns("app/ams/docs/*guide.md")
}

for pattern_type, patterns in architecture_patterns.items():
    cognee.cognify(
        data=patterns,
        graph_model_name="architectural_patterns"
    )

# Phase 3: Project Specifics to Serena
project_knowledge = {
    "hierarchy": build_hierarchy_structure(),
    "constraints": extract_project_rules(),
    "configurations": extract_configs()
}

for memory_type, content in project_knowledge.items():
    serena.write_memory(
        memory_name=f"project_{memory_type}",
        content=content
    )
```

---

## ✅ Quality Validation Checklist

### Knowledge Completeness
- [ ] All mandatory rules captured
- [ ] Core command templates extracted
- [ ] Essential patterns documented
- [ ] Project structure recorded

### Cross-Repository Readiness
- [ ] No hardcoded paths
- [ ] Patterns are abstracted
- [ ] Templates are parameterized
- [ ] Context variables defined

### Performance Optimization
- [ ] Knowledge is deduplicated
- [ ] Only essential content included
- [ ] Search indices optimized
- [ ] Retrieval paths established

---

## 📊 Success Criteria

1. **Cognee Knowledge Graph**
   - [ ] Contains all core patterns
   - [ ] Searchable within 5 seconds
   - [ ] Returns relevant results

2. **Serena Memory Structure**
   - [ ] Project hierarchy established
   - [ ] Constraints documented
   - [ ] Configurations stored

3. **Dynamic Loading**
   - [ ] Commands loadable as prompts
   - [ ] Context adaptation works
   - [ ] Cross-CLI compatible

4. **Efficiency**
   - [ ] Total extraction < 2 hours
   - [ ] Storage < 50% of original
   - [ ] Retrieval < 10 seconds

---

## 🔄 Post-Extraction Tasks

- [ ] Test knowledge retrieval
- [ ] Validate cross-repository usage
- [ ] Document access patterns
- [ ] Create usage examples
- [ ] Set up monitoring

---

## 📝 Notes

- Focus on patterns over implementations
- Prioritize reusability over completeness
- Abstract project-specific details
- Maintain searchability
- Document assumptions

---

**Execution Order**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Validation