# Cognee Strategic Operations (Central Hub)

```bash
# Performance Standards & Assessment  
COGNEE_PERFORMANCE_STANDARD="10 seconds response time threshold"
COGNEE_OPTIMIZATION_TARGET="80% speed improvement, 70% efficiency gain"

# Status & Performance Check
mcp__cognee__cognify_status
start_time=$(date +%s)
mcp__cognee__search "performance test" GRAPH_COMPLETION >/dev/null 2>&1
response_time=$(($(date +%s) - start_time))

if [[ $response_time -gt 10 ]]; then
    echo "⚠️ PERFORMANCE ISSUE: ${response_time}s response time"
    echo "🚀 Apply optimization: search_speed_optimization_and_indexing_strategy.md"
else
    echo "✅ Cognee optimal performance confirmed"
fi

# Strategic Search (3-stage optimization) 
mcp__cognee__search "query" CHUNKS        # Phase 1: Fast metadata (1-3s)
mcp__cognee__search "query" RAG_COMPLETION # Phase 2: Semantic (5-10s)
mcp__cognee__search "query" GRAPH_COMPLETION # Phase 3: Comprehensive (10-20s)

# Knowledge Management
mcp__cognee__cognee_add_developer_rules --base_path /home/devuser/workspace
mcp__cognee__cognify --data "new knowledge content"

# Emergency & Recovery Protocols (Centralized)
COGNEE_EMERGENCY_PROCEDURE="45-minute reconstruction protocol verified"

if ! mcp__cognee__cognify_status > /dev/null 2>&1; then
    echo "🚨 COGNEE EMERGENCY: Database unavailable"
    echo "📋 Complete reconstruction: memory-bank/01-cognee/cognee_reconstruction_successful_procedure.md"
    echo "⚡ Quick restart: mcp__cognee__prune && mcp__cognee__cognee_add_developer_rules"
    echo "⚠️ Fallback: Direct constraint mode"
fi

# Strategic Navigation Hub (All References)
echo "📚 Strategy guide: memory-bank/01-cognee/cognee_effective_utilization_strategy.md"
echo "🚨 Emergency protocol: memory-bank/01-cognee/cognee_reconstruction_successful_procedure.md"
echo "🚀 Performance optimization: memory-bank/01-cognee/search_speed_optimization_and_indexing_strategy.md"
echo "📋 Daily utilization: memory-bank/01-cognee/mandatory_utilization_rules.md"
echo "🎯 ROI Analysis: 64% annual return, 7-month payback period"
```