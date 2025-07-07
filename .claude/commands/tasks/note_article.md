# Note Article Creation System

## ⚠️ COMPLEXITY CHOICE (複雑性選択)

**このコマンドは高度な品質保証システムです（30-45分要）**

### 🔄 簡単な記事作成をお探しですか？

```bash
# 5-10分で完成する簡単版
/note_article_quick "あなたのトピック"

# または手動でテンプレート使用
# templates/note_article_template_*.md を参照
```

### 📊 使用判断基準

| 条件 | 推奨コマンド | 所要時間 |
|------|-------------|----------|
| **自動判定** | `/note_article_auto` | **5-45分（自動調整）** |
| 簡単な情報共有 | `/note_article_quick` | 5-10分 |
| 標準的な記事 | `/note_article_standard` | 15-20分 |
| 高品質・公開用 | `/note_article`（このコマンド） | 30-45分 |

### 🎯 自動判定システム

**トピック「$ARGUMENTS」の複雑性を分析中...**

```bash
# 自動分析ロジック
analyze_topic_complexity() {
    local topic="$ARGUMENTS"
    local score=0
    
    # 複雑性キーワード検出
    [[ "$topic" =~ "実装|システム|アーキテクチャ|競争的|組織" ]] && score=$((score + 2))
    [[ "$topic" =~ "比較|分析|評価|詳細" ]] && score=$((score + 2))
    [[ "$topic" =~ "事例|体験|経験" ]] && score=$((score + 1))
    [[ "$topic" =~ "基本|簡単|概要|クイック" ]] && score=$((score - 1))
    
    if [ $score -le 1 ]; then
        echo "🚀 自動判定: Quick版（5-10分）が最適です"
        echo "実行中: /note_article_quick '$ARGUMENTS'"
        # Quick版実行へ自動転送
        return 1
    elif [ $score -le 3 ]; then
        echo "⚖️ 自動判定: Standard版（15-20分）が最適です"
        echo "実行中: /note_article_standard '$ARGUMENTS'" 
        # Standard版実行へ自動転送
        return 2
    else
        echo "🏆 自動判定: 高品質版（30-45分）を推奨します"
        echo "複雑なトピックのため、完全版プロセスを継続します"
        # 現在の高品質版を継続
        return 3
    fi
}

# 実行
analyze_topic_complexity
complexity_level=$?

# 自動転送または継続判定
if [ $complexity_level -eq 1 ] || [ $complexity_level -eq 2 ]; then
    echo "⚡ より適切なコマンドに自動転送しました"
    echo "🔄 高品質版を強制実行したい場合は、このまま継続してください"
    echo ""
    echo "継続しますか？ [y/N]"
    # ユーザーの意思確認後、継続または終了
fi
```

---

## 🔒 MANDATORY BLOCKING SYSTEM (必須ブロッキングシステム)

**⚠️ 高品質記事作成を継続する場合のみ、以下を実行**

**⚠️ CRITICAL: 以下の関数を最初に実行しない限り、後続処理は一切実行禁止**

```bash
# 🚨 BLOCKING EXECUTION: Worktree競争的開発の強制実行
MANDATORY_WORKTREE_EXECUTION() {
    echo "🔒 BLOCKING SYSTEM: Worktree competitive development MUST be executed"
    
    # 環境チェック
    command -v git >/dev/null || { echo "❌ BLOCKING: git not available"; return 1; }
    git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "❌ BLOCKING: not in git repo"; return 1; }
    
    # 強制実行: worktree競争的開発
    echo "🏁 MANDATORY EXECUTION: Creating competitive development environment"
    
    APPROACHES=("structure_first" "content_first" "examples_first")
    SUCCESS_COUNT=0
    
    for approach in "${APPROACHES[@]}"; do
        worktree_path="/tmp/note_${approach}_$(date +%Y%m%d_%H%M%S)"
        branch_name="note_${approach}_$(date +%Y%m%d_%H%M%S)"
        
        if git worktree add "$worktree_path" -b "$branch_name" 2>/dev/null; then
            echo "✅ MANDATORY SATISFIED: $approach worktree created at $worktree_path"
            echo "$approach:$worktree_path" >> /tmp/worktree_evidence.txt
            ((SUCCESS_COUNT++))
        else
            echo "❌ MANDATORY FAILED: $approach worktree creation failed"
        fi
    done
    
    # 成功判定
    if [[ $SUCCESS_COUNT -eq 3 ]]; then
        export WORKTREE_MANDATORY_COMPLETED="TRUE"
        echo "🎯 MANDATORY REQUIREMENT SATISFIED: All 3 worktrees created successfully"
        echo "WORKTREE_EXECUTION_TIMESTAMP: $(date)" >> /tmp/worktree_evidence.txt
        return 0
    else
        echo "❌ MANDATORY FAILED: Only $SUCCESS_COUNT/3 worktrees created"
        echo "🛑 CANNOT PROCEED: Fix worktree issues before continuing"
        return 1
    fi
}

# 🚨 ENFORCEMENT: 実行確認チェック
VERIFY_MANDATORY_EXECUTION() {
    if [[ "${WORKTREE_MANDATORY_COMPLETED:-FALSE}" != "TRUE" ]]; then
        echo "🛑 EXECUTION BLOCKED: MANDATORY_WORKTREE_EXECUTION() not completed"
        echo "📋 REQUIRED ACTION: Run MANDATORY_WORKTREE_EXECUTION() first"
        return 1
    fi
    
    if [[ ! -f /tmp/worktree_evidence.txt ]]; then
        echo "🛑 EXECUTION BLOCKED: No evidence of worktree execution"
        return 1
    fi
    
    echo "✅ MANDATORY VERIFICATION PASSED: Worktree execution confirmed"
}
```

---

## 🚨 MANDATORY PRE-EXECUTION CHECK (実行前必須検証)

**⚠️ Note Article Creation Rules: 以下は絶対遵守**

```bash
# CRITICAL: 品質保証体制確認
QUALITY_ASSURANCE_CHECK="
echo '🔍 Checking quality assurance system...'
[[ -f /tmp/note_article_checklist.md ]] || {
    echo '📋 Creating mandatory checklist template...'
    cat > /tmp/note_article_checklist.md << 'CHECKLIST_EOF'
## 🎯 Note記事作成チェックリスト

### MUST条件（絶対必須）
- [ ] ターゲット読者明確化（具体的ペルソナ定義）
- [ ] 事実ベース検証（推測語句・根拠なし数値排除）
- [ ] 構成論理性確保（導入→展開→結論の流れ）
- [ ] 技術実装例（実行可能・再現可能な例示）

### SHOULD条件（推奨）
- [ ] 読者魅力度（続きを読みたくなる構成）
- [ ] SEO最適化（検索意図への対応）
- [ ] 実践価値（即座活用可能な内容）

### 自動検証スクリプト
```bash
verify_note_quality() {
    echo 'Running fact-based verification...'
    # 禁止パターンチェック
    grep -E 'たぶん|おそらく|probably|maybe|約[0-9]+%' \$1 && {
        echo '❌ 推測語句・根拠なし数値検出'
        return 1
    }
    echo '✅ 事実ベース検証合格'
}
```
CHECKLIST_EOF
}
"
```

**🔍 EXECUTION VERIFICATION CHECKLIST:**
- [ ] チェックリストテンプレート確認
- [ ] 品質基準明確化確認
- [ ] 自動検証スクリプト準備
- [ ] 事実ベース検証有効化

---

## 👤 ROLE DEFINITION

あなたは、Note Article Creator です。

### 🚨 MANDATORY実行プロセス (絶対実行)

- **Step -1. BLOCKING SYSTEM**:
  - **🚨 MANDATORY**: `MANDATORY_WORKTREE_EXECUTION()` 実行・成功確認
  - **🚨 MANDATORY**: `VERIFY_MANDATORY_EXECUTION()` 検証合格
  - **🚨 MANDATORY**: worktree競争的開発環境作成完了

### 🔒 EXECUTION GATE: 上記Step -1が100%完了するまで次段階進行禁止

- **Step0. 品質保証体制構築**
  - **🚨 MANDATORY**: チェックリストテンプレート確認・作成
  - **🚨 MANDATORY**: 品質ゲート自動検証スクリプト準備
  - **🚨 MANDATORY**: 事実ベース検証システム有効化

- **Step1. CDTE(Checklist-Driven Task Execution)**
  - 記事要件をMUST/SHOULD/COULDに分類
  - 各条件の検証可能な成功基準設定
  - 実行前にチェックリスト合意確認

- **Step2. 競争的品質開発**
  - 複数アプローチでの記事構成案作成
  - 各案の客観的品質評価実施
  - 最優秀案の選定と統合実行

- **Step3. 自動品質検証**
  - 3段階品質ゲート自動実行
  - 事実ベース検証・禁止パターン検出
  - 品質基準未達時の自動修正指示

- **Step4. 統合完了確認**
  - 全MUST条件の最終確認
  - 品質スコア達成状況検証
  - 公開可能レベル到達確認

## 🚨 CRITICAL REQUIREMENTS (重要事項絶対遵守)

### 1️⃣ FACT-BASED VERIFICATION (事実ベース検証強制)

```bash
# 禁止パターン自動検出
FORBIDDEN_PATTERNS=(
    "ROI.*[0-9]+%"      # 根拠のない数値
    "約[0-9]+倍"        # 曖昧な効果表現  
    "たぶん|おそらく"   # 推測語句（日本語）
    "probably|maybe"    # 推測語句（英語）
    "[0-9]+%.*向上"     # 根拠のない向上率
)

# 自動検証実行
fact_check_enforcement() {
    local article_file="$1"
    for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
        if grep -E "$pattern" "$article_file"; then
            echo "❌ 禁止パターン検出: $pattern"
            echo "📝 修正必須: 事実根拠を明示するか削除してください"
            return 1
        fi
    done
    echo "✅ 事実ベース検証合格"
}
```

### 2️⃣ QUALITY GATE AUTOMATION (品質ゲート自動化)

```bash
# 3段階品質ゲート
QUALITY_GATES=(
    "Gate1_Content_Structure:構成・論理性:85"
    "Gate2_Technical_Accuracy:技術精度・実装:90" 
    "Gate3_Publication_Ready:公開準備・完成度:95"
)

# 自動評価実行
auto_quality_assessment() {
    local score=0
    # チェックリスト完了度評価
    # 技術実装例の実行可能性評価
    # 読者価値・魅力度評価
    echo "品質スコア: $score/100"
}
```

### 3️⃣ CHECKLIST-DRIVEN EXECUTION (チェックリスト駆動実行)

**📋 強制実行サイクル:**
- **Red Phase**: MUST条件チェックリスト作成・合意
- **Green Phase**: 最小実装でMUST条件満足
- **Refactor Phase**: SHOULD条件対応・品質向上

### 4️⃣ DIRECTORY STRUCTURE COMPLIANCE (配置ルール遵守)

```bash
# Note記事配置ルール
NOTE_ARTICLE_LOCATIONS=(
    "docs/05.articles/"     # メイン記事
    "docs/91.notes/"        # ドラフト・作業用
    "templates/"            # テンプレート
)

# 配置先自動判定
determine_article_location() {
    local article_type="$1"
    case "$article_type" in
        "final"|"published")   echo "docs/05.articles/" ;;
        "draft"|"work")        echo "docs/91.notes/" ;;
        "template")            echo "templates/" ;;
        *)                     echo "docs/91.notes/" ;;  # デフォルト
    esac
}
```

### 5️⃣ WORKTREE COMPETITIVE DEVELOPMENT (競争的開発)

```bash
# 競争的開発実行
setup_competitive_development() {
    echo "🏁 Setting up competitive development environment..."
    
    # 複数アプローチ用のworktree作成
    APPROACHES=("structure_first" "content_first" "examples_first")
    
    for approach in "${APPROACHES[@]}"; do
        git worktree add "/tmp/note_${approach}" -b "note_${approach}_$(date +%Y%m%d_%H%M%S)"
        echo "📝 Created worktree for approach: $approach"
    done
    
    # 競争開始
    echo "🚀 Starting competitive note article development..."
}
```

---

## 📝 Note記事作成タスク

worktree を使ったコンペ方式、及び、各AI Agent によるチェックリストドリブンで「$ARGUMENTS」に関して事例を踏まえて note 記事を作成してください。

### 📋 実行チェックリスト

- [ ] **Step -1**: MANDATORY実行（worktree競争的開発環境作成・検証）
- [ ] **Step0**: 品質保証体制構築（チェックリスト・検証スクリプト準備）
- [ ] **Step1**: CDTE実行（要件分類・成功基準設定・合意確認）
- [ ] **Step2**: 競争的品質開発（複数アプローチ・評価・選定）
- [ ] **Step3**: 自動品質検証（3段階ゲート・禁止パターン検出）
- [ ] **Step4**: 統合完了確認（MUST条件確認・品質スコア・公開準備）

### 🎯 成功基準

**MUST達成項目:**
- [ ] 事実ベース検証100%合格（推測語句・根拠なし数値排除）
- [ ] 3段階品質ゲート全通過（85/90/95点以上）
- [ ] チェックリスト完全実行（全項目確認完了）
- [ ] 技術実装例の実行可能性確認（再現テスト成功）
- [ ] 読者魅力度確保（続きを読みたくなる構成）

**品質スコア目標:** 95/100以上

**禁止事項（自動検出・阻止）:**
- 推測語句の使用（たぶん、おそらく、probably、maybe）
- 根拠のない数値・効果の記載（ROI○○%、約○倍等）
- チェックリスト未実行での作業進行
- 品質ゲート未通過での公開判定

### 📚 必須参照ナレッジ

note記事の書き方もナレッジに記録があるはずなので、必ず熟読し記事を書く戦略を立ててください。特に以下を重点参照：

- `memory-bank/03-process/note_article_creation_comprehensive_process_knowledge.md`
- `memory-bank/07-templates/note_article_creation_enhanced_rules.md`
- `memory-bank/11-checklist-driven/checklist_driven_execution_framework.md`

### 🎨 創造性ガイドライン

- タイトルや構成も含めすべて任せます
- 自由な発想と人間の思考領域にとどまらない範囲での創造性を発揮
- 最高の note 記事を作成してください
- 読者にとって参考になり、もっと続きを読みたいという心理になるように
- **但し**: 嘘くさい数値は絶対に載せないでください（読み手が離脱します）

---

## 🔧 自動実行メカニズム

このslash commandは以下の仕組みで自動品質保証を実現：

1. **実行前検証**: 必須ファイル・スクリプトの自動生成
2. **段階的実行**: チェックリストドリブンの強制適用
3. **リアルタイム検証**: 執筆中の禁止パターン検出
4. **品質ゲート**: 3段階の自動品質評価
5. **完了保証**: 全基準達成まで完了ブロック

### 🏆 期待効果

1. **品質の標準化**: 毎回同じ高品質基準での記事作成
2. **自動検証**: 事実ベース・技術精度の自動確認
3. **効率化**: チェックリストドリブンによる作業効率向上
4. **再現性**: 同品質の記事を安定的に量産可能

---

## 🎯 FINAL BLOCKING VERIFICATION (最終必須検証)

**⚠️ CRITICAL: タスク完了報告前に以下の検証が必須**

```bash
# 完了前必須確認
FINAL_BLOCKING_CHECK() {
    echo "🎯 FINAL BLOCKING VERIFICATION: Task completion check"
    
    # 必須実行証跡確認
    if [[ "${WORKTREE_MANDATORY_COMPLETED:-FALSE}" != "TRUE" ]]; then
        echo "❌ BLOCKING: Worktree execution not completed"
        return 1
    fi
    
    if [[ ! -f /tmp/worktree_evidence.txt ]]; then
        echo "❌ BLOCKING: No worktree execution evidence"
        return 1
    fi
    
    local worktree_count=$(grep -c ":" /tmp/worktree_evidence.txt 2>/dev/null || echo 0)
    if [[ $worktree_count -lt 3 ]]; then
        echo "❌ BLOCKING: Insufficient worktree evidence ($worktree_count/3)"
        return 1
    fi
    
    echo "✅ FINAL VERIFICATION PASSED: All mandatory requirements satisfied"
    echo "📋 WORKTREE EXECUTION EVIDENCE:"
    cat /tmp/worktree_evidence.txt
}
```

### 🚨 COMPLETION RULE: 
**タスク完了報告前に`FINAL_BLOCKING_CHECK()`の成功実行が必須**