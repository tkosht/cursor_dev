#!/bin/bash

# Quick access commands for mandatory rules

# Alias for displaying mandatory rules
alias show_rules='bash /home/devuser/workspace/scripts/display_mandatory_rules.sh'

# Alias for opening full checklist
alias full_rules='cat /home/devuser/workspace/checklists/mandatory_rules_checklist.md'

# Function to create a new task checklist from template
function new_task_checklist() {
    local task_name="${1:-new_task}"
    local date=$(date +%Y%m%d)
    local filename="/home/devuser/workspace/checklists/task_${task_name}_${date}.md"
    
    cp /home/devuser/workspace/checklists/task_execution_template.md "$filename"
    sed -i "s/\[INSERT TASK NAME\]/$task_name/g" "$filename"
    sed -i "s/\[INSERT DATE\]/$(date)/g" "$filename"
    sed -i "s/\[INSERT BRANCH NAME\]/$(git branch --show-current)/g" "$filename"
    
    echo "✅ Created task checklist: $filename"
    echo "📝 Edit with: code $filename"
}

# Quick mandatory rules summary
function rules_summary() {
    echo "🚨 MANDATORY RULES QUICK SUMMARY"
    echo "================================"
    echo "1. 📚 ALWAYS: smart_knowledge_load() before tasks"
    echo "2. 🔒 NEVER: Expose secrets/credentials"
    echo "3. 🌿 ALWAYS: Work on feature branch"
    echo "4. 🚫 NEVER: Use mocks in tests"
    echo "5. 🔍 ALWAYS: Research unknowns via WebSearch"
    echo "6. 📝 ALWAYS: Record knowledge findings"
    echo "7. ✅ ALWAYS: Use checklists for complex tasks"
    echo "8. 🎯 NEVER: Speculate - facts only"
    echo "9. 💎 ALWAYS: 5-point value assessment"
    echo "10. 🏗️ ALWAYS: TDD - test first"
    echo ""
    echo "Full rules: show_rules | full_rules | new_task_checklist [name]"
}

echo "✅ Mandatory rules quick access loaded!"
echo "Commands available:"
echo "  • show_rules - Display interactive checklist"
echo "  • full_rules - Show complete mandatory rules"
echo "  • rules_summary - Quick summary of key rules"
echo "  • new_task_checklist [name] - Create task checklist from template"