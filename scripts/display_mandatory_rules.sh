#!/bin/bash

# 🚨 MANDATORY RULES DISPLAY SCRIPT
# This script displays the mandatory rules checklist for task execution

function display_mandatory_rules_checklist() {
    echo "🚨 MANDATORY RULES VERIFICATION CHECKLIST"
    echo "========================================="
    echo ""
    echo "📋 PRE-TASK KNOWLEDGE PROTOCOL"
    echo "□ 0. Execute date command for temporal context"
    echo "□ 1. Run smart_knowledge_load() for domain context (5-15s)"
    echo "□ 2. Verify loaded knowledge completeness"
    echo ""
    echo "✅ MANDATORY RULES"
    echo "□ 1️⃣ SECURITY ABSOLUTE: No secrets/credentials exposure"
    echo "□ 2️⃣ VALUE ASSESSMENT: 5-point evaluation completed"
    echo "□ 3️⃣ CORE PRINCIPLES: Excellence mindset maintained"
    echo "□ 4️⃣ WORK MANAGEMENT: Feature branch verification"
    echo "□ 5️⃣ KNOWLEDGE ACCESS: Proper knowledge loading"
    echo "□ 6️⃣ AI-OPTIMIZED FORMAT: Structured knowledge recording"
    echo "□ 7️⃣ CHECKLIST-DRIVEN: CDTE framework applied when applicable"
    echo "□ 8️⃣ NO MOCKS: Real API calls only - NO mocking in tests"
    echo "□ 9️⃣ WEB RESEARCH: Unknown items researched via WebSearch"
    echo "□ 🔟 FACT-BASED: No speculation, verified facts only"
    echo ""
    echo "🔒 SECURITY CHECKLIST"
    echo "□ No env.*API, cat.*key, echo.*token, grep.*secret"
    echo "□ No printenv.*KEY, cat .env, export.*SECRET"
    echo ""
    echo "💎 VALUE ASSESSMENT (5-POINT)"
    echo "□ SECURITY: No credential exposure?"
    echo "□ USER VALUE: Serves user not convenience?"
    echo "□ LONG-TERM: Sustainable solution?"
    echo "□ FACT-BASED: Verified information?"
    echo "□ ALTERNATIVES: Better approach evaluated?"
    echo ""
    echo "🌿 WORK MANAGEMENT"
    echo "□ NOT on main/master branch"
    echo "□ Branch pattern: feature/* | docs/* | fix/* | task/*"
    echo ""
    echo "🚀 EXECUTION CHECKLIST"
    echo "□ 1. AI COMPLIANCE: python scripts/pre_action_check.py --strict-mode"
    echo "□ 2. DATE CONTEXT: date command executed"
    echo "□ 3. WORK BRANCH: Verified not on main/master"
    echo "□ 4. KNOWLEDGE LOAD: smart_knowledge_load \"domain\""
    echo "□ 5. TDD: Test written FIRST"
    echo "□ 6. NO SPECULATION: Facts only"
    echo "□ 7. QUALITY GATES: Before commit"
    echo "□ 8. PR CREATION: When done"
    echo ""
    echo "📚 MANDATORY REFERENCES:"
    echo "   • memory-bank/00-core/*mandatory*.md"
    echo "   • memory-bank/11-checklist-driven/checklist_driven_execution_framework.md"
    echo "   • memory-bank/02-organization/tmux_organization_success_patterns.md (for tmux)"
    echo "   • checklists/mandatory_rules_checklist.md (full version)"
    echo ""
    read -p "❓ Confirm ALL mandatory rules verified before starting task (y/N): " confirmation
    if [[ "$confirmation" != "y" && "$confirmation" != "Y" ]]; then
        echo "❌ TASK ABORTED: Mandatory rules must be verified before proceeding"
        return 1
    fi
    echo "✅ MANDATORY RULES VERIFICATION COMPLETED"
    echo ""
    echo "⚡ Quick commands:"
    echo "   smart_knowledge_load \"domain\"  # Load domain knowledge"
    echo "   git checkout -b task/description  # Create task branch"
    echo "   python scripts/pre_action_check.py --strict-mode  # AI compliance"
    echo ""
    return 0
}

# Allow direct execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    display_mandatory_rules_checklist
fi