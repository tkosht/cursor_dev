# 日付コンテキスト統合プロトコル

**作成日**: 2025-06-21  
**作成者**: PMO/Consultant (pane-1)  
**目的**: セッション開始時・タスク実行前の日付コンテキスト確立  
**状態**: CLAUDE.md統合完了

---

## 📋 統合概要

AIエージェントが自動的に日付コンテキストを確立するため、CLAUDE.mdの複数箇所に日付確認を統合しました。これにより、セッション開始時およびタスク実行前に必ず現在日付が認識されます。

## 🔧 統合箇所

### 1. MANDATORY_SEQUENCE (タスク前必須手順)
```bash
MANDATORY_SEQUENCE=(
    "0. DATE: Establish temporal context with date command"
    "1. ASSESS: Task complexity (simple vs complex)"
    "2. LOAD: Choose appropriate knowledge loading strategy"
    "3. VERIFY: Cross-check loaded knowledge completeness"
    "4. STRATEGY: Formulate approach BASED ON loaded knowledge"
    "5. EXECUTE: Implement with continuous verification"
)
```

### 2. PRE_EXECUTION_MANDATORY (実行前チェックリスト)
```bash
PRE_EXECUTION_MANDATORY=(
    "0. Date context initialization: date command (日付コンテキスト確立)"
    "1. Run pre_action_check.py --strict-mode"
    "2. Load knowledge with mandatory_knowledge_load()"
    "3. Write tests FIRST (TDD mandatory)"
    "4. Apply 3-second fact-check rule"
    "5. Execute quality gates before ANY commit"
)
```

### 3. Immediate Session Start (セッション開始時)
```bash
# 0. DATE CONTEXT INITIALIZATION (必須 - セッション開始時)
echo "📅 DATE CONTEXT INITIALIZATION"
echo "==============================="
date '+%Y-%m-%d %H:%M:%S %A'  # 2025-06-21 15:20:00 土曜日
echo "Project Timeline: $(date '+%Y年%m月 第%U週')"
echo "Session Context Established"
echo ""
```

### 4. Knowledge Loading Functions (知識読み込み時)
```bash
# smart_knowledge_load()内
echo "⚡ SMART: Quick Knowledge Loading for: $domain"
echo "📅 Date: $(date '+%Y-%m-%d %H:%M')"

# comprehensive_knowledge_load()内
echo "🚨 MANDATORY: 3-Layer Comprehensive Knowledge Loading"
echo "📅 Date: $(date '+%Y-%m-%d %H:%M:%S')"
```

## 🎯 効果

1. **自動化**: セッション開始時・タスク実行前に自動的に日付が確認される
2. **一貫性**: 複数箇所での確認により、日付認識の欠落を防止
3. **可視性**: 各処理段階で日付が表示され、時系列の意識が保たれる

## 📊 追加活用例

### プロジェクト経過日数計算
```bash
project_start="2025-06-01"
current_date=$(date '+%Y-%m-%d')
days_elapsed=$(( ($(date -d "$current_date" +%s) - $(date -d "$project_start" +%s)) / 86400 ))
echo "📈 Project Day: ${days_elapsed}日目"
```

### 月次進捗確認
```bash
echo "📋 $(date '+%Y年%m月') Progress:"
git log --since="$(date '+%Y-%m-01')" --oneline | wc -l | xargs echo "  - Commits:"
find memory-bank -name "*.md" -newermt "$(date '+%Y-%m-01')" | wc -l | xargs echo "  - New Documents:"
```

## 🔄 メンテナンス

この統合は恒久的なものとして、CLAUDE.mdの一部となります。今後のCLAUDE.md更新時には、これらの日付確認機能を維持してください。

---

**統合完了日**: 2025-06-21 15:15  
**次回レビュー**: 2025-07-01 (月次レビュー時)