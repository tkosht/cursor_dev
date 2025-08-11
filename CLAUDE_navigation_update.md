# CLAUDE.md Navigation Update Proposal
## 新規知識ファイルへの導線追加提案

---

## 🎯 追加すべき導線（CLAUDE.md への挿入箇所）

### 1. Navigation Guide セクション（318行目付近）への追加

```markdown
| **Session Start** | Run initialization | `source memory-bank/00-core/session_initialization_script.md` |
| **MCP Strategy** | Select optimal MCP | `mcp__serena__read_memory("serena_cognee_mcp_usage_strategy")` |
| **Project Knowledge** | Get project structure | `mcp__serena__read_memory("serena_project_knowledge")` |  # 追加
| **Dynamic Prompts** | Load command templates | `mcp__serena__read_memory("serena_memory_dynamic_prompt_loading")` |  # 追加
| **Project Hierarchy** | Repository structure | `mcp__serena__read_memory("serena_memory_project_hierarchy")` |  # 追加
| **Core Patterns** | Cognee patterns access | `cognee.search("cognee_core_patterns", "GRAPH_COMPLETION")` |  # 追加
| **Essential Patterns** | Development patterns | `cognee.search("essential_patterns", "INSIGHTS")` |  # 追加
| **Command Templates** | Meta-prompt library | `cognee.search("command_templates", "CHUNKS")` |  # 追加
```

### 2. MCP選択プロトコル セクション（330行目付近）への追加

```bash
# 🚨 MANDATORY ACCESS POINTS
MCP_STRATEGY_GUIDE="mcp__serena__read_memory('serena_cognee_mcp_usage_strategy')"
PROJECT_KNOWLEDGE="mcp__serena__read_memory('serena_project_knowledge')"  # 追加
DYNAMIC_PROMPT_SYSTEM="mcp__serena__read_memory('serena_memory_dynamic_prompt_loading')"  # 追加
PROJECT_HIERARCHY="mcp__serena__read_memory('serena_memory_project_hierarchy')"  # 追加

# Cognee Knowledge Access  # 新規セクション追加
CORE_PATTERNS="cognee.search('cognee_core_patterns', 'GRAPH_COMPLETION')"
ESSENTIAL_PATTERNS="cognee.search('essential_patterns_cognee', 'INSIGHTS')"
COMMAND_TEMPLATES="cognee.search('command_templates_cognee', 'CHUNKS')"
EXTRACTED_KNOWLEDGE="cognee.search('extracted_knowledge_cognee', 'RAG_COMPLETION')"
```

### 3. Quick Start Implementation セクション（230行目付近）への追加

```bash
# ⚡ IMMEDIATE SESSION START
source memory-bank/00-core/session_initialization_script.md

# 🆕 KNOWLEDGE LOADING PRIORITY  # 新規追加
echo "📚 Loading Serena Project Knowledge..."
mcp__serena__read_memory serena_project_knowledge
echo "🎯 Loading MCP Usage Strategy..."
mcp__serena__read_memory serena_cognee_mcp_usage_strategy
echo "🔄 Loading Dynamic Prompt System..."
mcp__serena__read_memory serena_memory_dynamic_prompt_loading

# 🚨 CRITICAL REMINDERS (既存)
echo "⚠️ DEFAULT: smart_knowledge_load() for ALL tasks (5-15s)"
```

### 4. Pre-Task Knowledge Protocol への追加（0️⃣セクション）

```bash
# 📚 IMPLEMENTATION: memory-bank/00-core/knowledge_loading_functions.md
source memory-bank/00-core/knowledge_loading_functions.md

# 🆕 KNOWLEDGE SOURCES REFERENCE  # 新規追加
KNOWLEDGE_SOURCES=(
    "SERENA_PROJECT: mcp__serena__read_memory('serena_project_knowledge')"
    "SERENA_HIERARCHY: mcp__serena__read_memory('serena_memory_project_hierarchy')"
    "COGNEE_PATTERNS: cognee.search('cognee_core_patterns', 'GRAPH_COMPLETION')"
    "COMMAND_TEMPLATES: cognee.search('command_templates_cognee', 'CHUNKS')"
    "EXTRACTION_SYSTEM: docs/knowledge_extraction_design.md"
    "DYNAMIC_PROMPTS: docs/dynamic_prompt_system_guide.md"
)
```

---

## 📋 起動時チェックリスト（提案）

### AIエージェント起動時の知識確認フロー

```bash
# 1. セッション初期化
source memory-bank/00-core/session_initialization_script.md

# 2. MCP利用可能性確認
if mcp__serena__list_memories; then
    echo "✅ Serena MCP available"
    # 重要メモリをロード
    mcp__serena__read_memory serena_project_knowledge
    mcp__serena__read_memory serena_cognee_mcp_usage_strategy
fi

if cognee.get_developer_rules; then
    echo "✅ Cognee MCP available"
    # コアパターンを確認
    cognee.search "cognee_core_patterns" "INSIGHTS"
fi

# 3. フォールバック
if [ "$MCP_UNAVAILABLE" ]; then
    echo "⚠️ Using file-based knowledge loading"
    # 直接ファイルから読み込み
    cat cognee_core_patterns.md
    cat serena_project_knowledge.md
fi
```

---

## 🚀 実装優先度

### HIGH Priority（即座に実装）
1. Navigation Guide への主要ファイル参照追加
2. MCP選択プロトコルへのアクセスポイント追加

### MEDIUM Priority（次回更新時）
3. Quick Start への知識ロード優先順位追加
4. 起動時チェックリストの実装

### LOW Priority（将来的改善）
5. 知識ソース自動検出機能
6. 動的導線更新システム

---

## 📝 変更の影響

### 改善される点
- ✅ 起動時に全ての重要知識へアクセス可能
- ✅ Serena/Cogneeの使い分けが明確化
- ✅ 動的プロンプトシステムへの導線確立
- ✅ Knowledge Extraction システムの活用促進

### 必要な作業
- CLAUDE.md への上記セクション追加（約50行）
- 起動時スクリプトの更新（オプション）
- 既存のSerenaメモリへの登録確認

---

この提案により、今回整理した知識ファイルが起動時から適切にアクセス可能になり、AIエージェントの効率的な動作を支援します。