# Session Initialization Script (Copy-Paste Ready)

```bash
# 0. DATE CONTEXT INITIALIZATION (必須 - セッション開始時)
echo "📅 DATE CONTEXT INITIALIZATION"
echo "==============================="
date '+%Y-%m-%d %H:%M:%S %A'  # 2025-06-21 15:20:00 土曜日
echo "Project Timeline: $(date '+%Y年%m月 第%U週')"
echo "Session Context Established"
echo ""

# 1. AI COMPLIANCE VERIFICATION (ALWAYS FIRST)
echo "🤖 AI Compliance Check..."
python scripts/pre_action_check.py --strict-mode || exit 1

# 2. WORK MANAGEMENT VERIFICATION  
echo "🔧 Work Management Check..."
current_branch=$(git branch --show-current)
if [[ "$current_branch" == "main" ]] || [[ "$current_branch" == "master" ]]; then
    echo "⚠️ WARNING: Currently on main branch"
    echo "🎯 Reminder: Create task branch before starting any work"
    echo "📋 Pattern: git checkout -b docs/[content] or task/[type] or feature/[function]"
else
    echo "✅ Work management ready: Active on branch '$current_branch'"
fi

# 3. Load essential constraints (minimum required)
echo "Loading core constraints..."
[ -f memory-bank/00-core/knowledge_access_principles_mandatory.md ] && echo "✅ Knowledge access principles found"
[ -f memory-bank/00-core/user_authorization_mandatory.md ] && echo "✅ User auth rules found"
[ -f memory-bank/00-core/testing_mandatory.md ] && echo "✅ Testing rules found"
[ -f memory-bank/00-core/code_quality_anti_hacking.md ] && echo "✅ Quality rules found"
[ -f memory-bank/00-core/claude_code_hooks_constraints_mandatory.md ] && echo "✅ Claude Code hooks constraints found"
[ -f memory-bank/09-meta/progress_recording_mandatory_rules.md ] && echo "✅ Progress recording rules found"

# 4. Cognee strategic integration (knowledge management optimization)
if mcp__cognee__cognify_status > /dev/null 2>&1; then
    mcp__cognee__cognee_add_developer_rules --base_path /home/devuser/workspace
    echo "✅ Cognee enhanced mode active"
    
    # Performance check (detailed analysis: see Cognee Strategic Operations)
    if ! mcp__cognee__search "test" GRAPH_COMPLETION >/dev/null 2>&1; then
        echo "⚠️ COGNEE PERFORMANCE: Check 'Cognee Strategic Operations (Central Hub)' for optimization"
    else
        echo "🎯 Cognee optimal performance confirmed"
    fi
else
    echo "🚨 COGNEE CRITICAL: Database unavailable"
    echo "🔧 Full protocols: See 'Cognee Strategic Operations (Central Hub)' in Reference section"
    echo "⚡ Quick restart: mcp__cognee__prune && mcp__cognee__cognee_add_developer_rules"
    echo "⚠️ Fallback: Direct constraint mode only"
fi

echo "🎯 Session ready! You can now start development."

# 🚨 CRITICAL: Pre-Task Knowledge Protocol  
echo "⚠️ REMINDER: Smart knowledge loading is DEFAULT for all tasks"
echo "🔍 Usage: smart_knowledge_load 'domain' 'task_context' (5-15s)"
echo "📋 Layers: Local→Cognee (fast) = Efficient understanding"
echo "🎯 Upgrade: Use comprehensive_knowledge_load only on explicit user request"

# 📋 CHECKLIST-DRIVEN EXECUTION FRAMEWORK
echo "🎯 CHECKLIST-DRIVEN EXECUTION AVAILABLE:"
echo "📚 Framework: memory-bank/11-checklist-driven/checklist_driven_execution_framework.md"
echo "📝 Templates: memory-bank/11-checklist-driven/templates_collection.md"
echo "🛠️ Implementation: memory-bank/11-checklist-driven/implementation_examples.md"
echo "💡 Use for: Complex tasks, quality assurance, systematic execution"

# 📋 SESSION CONTINUITY CHECK
if [ -f "memory-bank/09-meta/session_continuity_task_management.md" ]; then
    echo "🔄 Session continuity available - check previous tasks"
    echo "💡 Use: cat memory-bank/09-meta/session_continuity_task_management.md"
fi
```