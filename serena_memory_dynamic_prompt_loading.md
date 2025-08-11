
# Dynamic Prompt Loading System

## Loading Mechanism
1. Query available commands from Cognee
2. Fetch command template structure
3. Get project context from Serena
4. Merge template with context
5. Execute adapted prompt

## Adaptation Rules
- Replace {PROJECT_ROOT} with actual path
- Substitute {PARAMETERS} with task-specific values
- Inject project constraints from Serena
- Apply security and quality rules

## Cross-CLI Compatibility
- Extract core prompt structure
- Adapt to CLI-specific syntax
- Maintain parameter compatibility
- Preserve execution model
