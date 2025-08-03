# Mandatory Rules Integration Guide

## 🚀 Quick Integration

Add to your shell configuration or run at session start:

```bash
# Load mandatory rules quick access
source /home/devuser/workspace/scripts/mandatory_rules_quick_access.sh
```

## 📋 Available Commands

### 1. Interactive Checklist Display
```bash
show_rules
# Displays the mandatory rules checklist with confirmation prompt
```

### 2. Full Rules Reference
```bash
full_rules
# Shows the complete mandatory rules documentation
```

### 3. Quick Summary
```bash
rules_summary
# Displays a concise summary of the 10 key mandatory rules
```

### 4. Create Task Checklist
```bash
new_task_checklist "feature_name"
# Creates a new task-specific checklist from template
```

## 📁 File Locations

- **Full Checklist**: `/home/devuser/workspace/checklists/mandatory_rules_checklist.md`
- **Display Script**: `/home/devuser/workspace/scripts/display_mandatory_rules.sh`
- **Quick Access**: `/home/devuser/workspace/scripts/mandatory_rules_quick_access.sh`
- **Task Template**: `/home/devuser/workspace/checklists/task_execution_template.md`

## 🎯 Usage Pattern

1. **Start of Session**:
   ```bash
   source scripts/mandatory_rules_quick_access.sh
   rules_summary  # Quick reminder
   ```

2. **Before Any Task**:
   ```bash
   show_rules  # Interactive verification
   new_task_checklist "my_task"  # Create specific checklist
   ```

3. **During Task Execution**:
   - Keep task checklist open
   - Mark items as completed
   - Refer to full_rules for details when needed

## 🔗 Integration with Session Initialization

Add to `memory-bank/00-core/session_initialization_script.md`:

```bash
# Load mandatory rules tools
source /home/devuser/workspace/scripts/mandatory_rules_quick_access.sh

# Display quick summary at session start
rules_summary
```

## ⚡ Quick Reference Card

```
┌─────────────────────────────────────────┐
│  MANDATORY RULES QUICK REFERENCE        │
├─────────────────────────────────────────┤
│  show_rules     - Interactive checklist │
│  full_rules     - Complete documentation│
│  rules_summary  - 10 key rules summary  │
│  new_task_checklist - Create checklist  │
└─────────────────────────────────────────┘
```