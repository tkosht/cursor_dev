# Knowledge Loading Functions Implementation

**CRITICAL: These functions MUST be executed before ANY task - NO EXCEPTIONS**

## smart_knowledge_load() - Default for ALL tasks (5-15s)

```bash
function smart_knowledge_load() {
    local domain="$1"
    local task_context="${2:-general}"
    echo "⚡ SMART: Quick Knowledge Loading for: $domain"
    echo "📅 Date: $(date '+%Y-%m-%d %H:%M')"
    
    # Always check session continuity first
    if [ -f "memory-bank/09-meta/session_continuity_task_management.md" ]; then
        echo "📋 Loading session continuity..."
        grep -A 20 "CURRENT.*STATUS" memory-bank/09-meta/session_continuity_task_management.md | head -10
    fi
    
    # Auto-upgrade check for high-risk domains
    case "$domain $task_context" in
        *security*|*architecture*|*new-technology*|*troubleshooting*|*error*|*debug*|*vulnerability*|*performance*|*optimization*)
            echo "🚨 HIGH-RISK DOMAIN DETECTED: Auto-upgrading to comprehensive_knowledge_load"
            comprehensive_knowledge_load "$domain" "$task_context"
            return
            ;;
        *organization*|*team*|*coordination*|*tmux*|*agent*)
            echo "🏆 ORGANIZATION ACTIVITY DETECTED: Loading proven success patterns"
            echo "📚 Proven Success: memory-bank/02-organization/tmux_organization_success_patterns.md"
            echo "🎯 Quick Protocol: Team04 5-step success pattern (100% proven)"
            echo "💡 Use: team04_proven_success_protocol 'your_task_description'"
            ;;
        *hooks*|*hook*|*claude-code*)
            echo "🔧 CLAUDE CODE HOOKS DETECTED: Loading mandatory constraints"
            echo "📚 Critical: memory-bank/00-core/claude_code_hooks_constraints_mandatory.md"
            echo "🚨 CONSTRAINT: All hooks scripts MUST be POSIX sh-compatible"
            echo "💡 Use: /bin/sh syntax only (no bash-specific features)"
            ;;
        *checklist*|*driven*|*execution*|*task*|*completion*)
            echo "📋 CHECKLIST-DRIVEN EXECUTION DETECTED: Loading systematic execution methodology"
            echo "📚 Framework: memory-bank/11-checklist-driven/checklist_driven_execution_framework.md"
            echo "📝 Templates: memory-bank/11-checklist-driven/templates_collection.md"
            echo "🎯 Quick Start: MUST/SHOULD/COULD condition hierarchy + Red-Green-Refactor cycle"
            echo "💡 Use: Create verification checklist FIRST, then execute systematically"
            ;;
    esac
    
    # Fast local search for domain-specific knowledge
    echo "🔍 Domain search: $domain"
    find memory-bank/ -name "*${domain}*.md" -o -name "*mandatory*.md" | head -5
    
    # Essential core rules (always loaded)
    echo "🚨 Core rules check:"
    ls memory-bank/00-core/*mandatory*.md 2>/dev/null | head -5
    
    # Task Completion Integrity (mandatory for all tasks)
    if [ -f "memory-bank/00-core/task_completion_integrity_mandatory.md" ]; then
        echo "✅ Task Completion Integrity Protocol loaded"
    else
        echo "⚠️ WARNING: Task Completion Integrity Protocol missing"
    fi
    
    # AI Cognitive Enhancement (mandatory for analysis tasks)
    if [ -f "memory-bank/00-core/forced_depth_analysis_mandatory.md" ]; then
        echo "🧠 Forced Depth Analysis Protocol loaded"
        echo "💡 Use for complex analysis: enforce_analysis_quality [topic]"
    fi
    
    if [ -f "memory-bank/00-core/ai_strategic_thinking_framework_mandatory.md" ]; then
        echo "🎯 Strategic Thinking Framework loaded"
        echo "💡 Use for strategic decisions: enforce_strategic_completeness [topic]"
    fi
    
    # Optional Cognee if available and fast
    if mcp__cognee__cognify_status >/dev/null 2>&1; then
        echo "🧠 Cognee search: $domain"
        mcp__cognee__search "$domain" CHUNKS | head -5
    fi
    
    echo "✅ Smart Loading Complete (5-15s)"
    echo "💡 Need more comprehensive analysis? Request comprehensive_knowledge_load()"
}
```

## comprehensive_knowledge_load() - Only on explicit user request (30-60s)

```bash
function comprehensive_knowledge_load() {
    local domain="$1"
    local task_context="${2:-general}"
    echo "🚨 MANDATORY: 3-Layer Comprehensive Knowledge Loading"
    echo "📅 Date: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "📋 Domain: $domain | Context: $task_context"
    
    # Layer 1: Local Repository Search (必須)
    echo "📁 Layer 1: Local Repository Knowledge"
    local_files=$(find memory-bank/ -name "*${domain}*.md" -o -name "*mandatory*.md" | 
        xargs grep -l "$domain\|${task_context}\|rules\|patterns" 2>/dev/null | head -10)
    
    for file in $local_files; do
        echo "📚 LOADING: $file"
        # Extract key sections: rules, patterns, examples
        grep -A 5 -B 2 -i "rule\|pattern\|example\|mandatory\|forbidden" "$file" 2>/dev/null
    done
    
    # Layer 2: Cognee Knowledge Graph (必須 if available)
    echo "🧠 Layer 2: Cognee Knowledge Graph"
    if mcp__cognee__cognify_status >/dev/null 2>&1; then
        # Multi-phase strategic search
        echo "  Phase 1: Fast metadata search"
        mcp__cognee__search "$domain $task_context rules" CHUNKS
        
        echo "  Phase 2: Semantic relationship search"  
        mcp__cognee__search "$domain implementation patterns examples" RAG_COMPLETION
        
        echo "  Phase 3: Comprehensive knowledge synthesis"
        mcp__cognee__search "$domain best practices mandatory guidelines" GRAPH_COMPLETION
    else
        echo "⚠️ Cognee unavailable - relying on local + web search"
    fi
    
    # Layer 3: Web Search for External Knowledge (必須)
    echo "🌐 Layer 3: Web Search - External Best Practices"
    
    # Search 1: Current best practices and standards
    echo "📡 Web search: $domain best practices guide" 
    # Use: WebSearch tool with query "$domain best practices 2024 implementation guide standards"
    
    # Search 2: Common issues and solutions
    echo "📡 Web search: $domain troubleshooting"
    # Use: WebSearch tool with query "$domain common mistakes solutions troubleshooting"
    
    # Search 3: Recent updates and breaking changes
    echo "📡 Web search: $domain latest updates"
    # Use: WebSearch tool with query "$domain latest updates breaking changes 2024"
    
    # Search 4: Task-specific guidance
    if [[ "$task_context" != "general" ]]; then
        echo "📡 Web search: $domain $task_context implementation"
        # Use: WebSearch tool with query "$domain $task_context tutorial example"
    fi
    
    echo "✅ 3-Layer Knowledge Loading Complete"
    echo "📊 Sources: Local(${#local_files[@]} files) + Cognee + Web = Comprehensive Understanding"
    echo "🎯 Ready for informed strategy formulation"
}
```

## Usage Examples

```bash
# Default usage for all tasks
smart_knowledge_load "testing" "unit-test-implementation"
smart_knowledge_load "security" "api-key-management"
smart_knowledge_load "performance" "optimization"

# Comprehensive loading only when explicitly requested
comprehensive_knowledge_load "architecture" "microservices-design"
comprehensive_knowledge_load "troubleshooting" "performance-issues"
```