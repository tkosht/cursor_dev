# エラー解析プロトコル（必須遵守）- AIエージェント専用

## KEYWORDS: error-analysis, deep-investigation, root-cause, complete-resolution, debugging-protocol
## DOMAIN: debugging|problem-solving|quality-assurance
## PRIORITY: MANDATORY
## WHEN: Error reports, script failures, test failures, accuracy issues, any problem investigation

**🤖 AI Agent Exclusive Knowledge**: このファイルはAIエージェント用に最適化されています。

## 🚨 ABSOLUTE MANDATORY RULES

### 0️⃣ **認知バイアス防止原則**
```bash
COGNITIVE_BIAS_PREVENTION=(
    "❌ 表面読み禁止: エラーレポートの部分的解釈"
    "❌ 選択的注意禁止: 都合の良い情報のみの採用"
    "❌ 確証バイアス禁止: 先入観による問題判断"
    "❌ 早期満足禁止: '大体解決した'での作業停止"
)

REQUIRED_MINDSET=(
    "✅ 全体分析: エラーレポート全項目の個別検証"
    "✅ 複合問題意識: 複数の異なる問題が混在する可能性"
    "✅ 根本追跡: 表面症状ではなく根本原因の特定"
    "✅ 完全解決: 100%問題解決まで継続"
)
```

### 1️⃣ **段階的問題分析プロトコル**

#### **Phase 1: 問題の完全把握（必須）**
```bash
COMPLETE_PROBLEM_UNDERSTANDING=(
    "1. 全エラーメッセージの収集・分類"
    "2. 各エラーの独立性・関連性の分析"
    "3. 誤検出 vs 真の問題の分離"
    "4. 影響範囲・重要度の評価"
)

# 実行例
echo "=== PHASE 1: COMPLETE PROBLEM ANALYSIS ==="
echo "🔍 All error messages:"
[全エラーメッセージのリスト化]
echo "🎯 Error classification:"
[HIGH/MEDIUM/LOW + TRUE_ISSUE/FALSE_POSITIVE の分類]
echo "📊 Impact assessment:"
[各エラーの影響範囲と重要度の評価]
```

#### **Phase 2: 根本原因追跡（必須）**
```bash
ROOT_CAUSE_INVESTIGATION=(
    "1. 技術的原因の特定（コード・設定・環境）"
    "2. プロセス原因の特定（手順・確認不備）"
    "3. 認知原因の特定（判断ミス・思い込み）"
    "4. システム原因の特定（ツール・フレームワーク）"
)

# Deep Dive Investigation Protocol
function deep_investigate() {
    local error_type="$1"
    echo "🧠 Deep Investigation: $error_type"
    
    # Technical Layer
    echo "  🔧 Technical: Code/Config/Environment analysis"
    
    # Process Layer  
    echo "  📋 Process: Procedure/Verification analysis"
    
    # Cognitive Layer
    echo "  🎯 Cognitive: Decision/Assumption analysis"
    
    # System Layer
    echo "  ⚙️ System: Tool/Framework analysis"
}
```

#### **Phase 3: 完全解決実装（必須）**
```bash
COMPLETE_RESOLUTION_PROTOCOL=(
    "1. 根本原因に対する直接的修正"
    "2. 再発防止のための予防的修正"
    "3. 関連問題の予測・対処"
    "4. 修正効果の定量的検証"
)

# Resolution Verification
function verify_complete_resolution() {
    echo "=== RESOLUTION VERIFICATION ==="
    echo "✅ Primary issue resolved:"
    [主要問題の解決確認]
    echo "✅ Secondary issues addressed:"
    [関連問題の対処確認]
    echo "✅ Prevention measures implemented:"
    [再発防止策の実装確認]
    echo "✅ Quantitative improvement verified:"
    [定量的改善の確認]
}
```

### 2️⃣ **品質基準（妥協禁止）**

#### **完全解決基準**
```bash
COMPLETION_CRITERIA=(
    "❌ 部分解決: 主要問題のみの解決"
    "❌ 症状改善: 根本原因を残した表面的改善"
    "❌ 暫定対処: 一時的な回避策のみ"
    "✅ 根本解決: 原因レベルでの完全解決"
    "✅ 再発防止: 同種問題の予防策実装"
    "✅ 関連改善: 関連する潜在問題の改善"
)
```

#### **検証要件**
```bash
VERIFICATION_REQUIREMENTS=(
    "1. Before/After比較: 定量的改善の確認"
    "2. Full scenario test: 完全シナリオでの動作確認" 
    "3. Edge case test: 境界条件での動作確認"
    "4. Regression test: 既存機能の非破壊確認"
)
```

### 3️⃣ **具体的実装パターン**

#### **エラーレポート分析テンプレート**
```bash
function analyze_error_report() {
    echo "🔍 ERROR REPORT ANALYSIS"
    echo "========================"
    
    # Step 1: Complete error inventory
    echo "1. COMPLETE ERROR INVENTORY:"
    echo "   HIGH: [数] - [カテゴリ別リスト]"
    echo "   MEDIUM: [数] - [カテゴリ別リスト]"  
    echo "   LOW: [数] - [カテゴリ別リスト]"
    
    # Step 2: True vs False classification
    echo "2. TRUE vs FALSE CLASSIFICATION:"
    echo "   TRUE_ISSUES: [実際の問題リスト]"
    echo "   FALSE_POSITIVES: [誤検出リスト]"
    echo "   UNCLEAR: [要調査リスト]"
    
    # Step 3: Root cause analysis for each true issue
    echo "3. ROOT CAUSE ANALYSIS:"
    for issue in "${TRUE_ISSUES[@]}"; do
        echo "   Issue: $issue"
        echo "     Technical: [技術的原因]"
        echo "     Process: [プロセス原因]"
        echo "     Tool: [ツール原因]"
    done
    
    # Step 4: Resolution plan
    echo "4. RESOLUTION PLAN:"
    echo "   Primary fixes: [主要修正]"
    echo "   Prevention measures: [予防策]"
    echo "   Verification plan: [検証計画]"
}
```

#### **段階的修正実装**
```bash
function implement_complete_fix() {
    local problem_domain="$1"
    
    echo "🔧 COMPLETE FIX IMPLEMENTATION"
    echo "=============================="
    
    # Phase 1: Immediate fix
    echo "Phase 1: IMMEDIATE FIX"
    [根本原因に対する直接修正]
    
    # Phase 2: Prevention
    echo "Phase 2: PREVENTION"
    [再発防止策の実装]
    
    # Phase 3: Related improvements  
    echo "Phase 3: RELATED IMPROVEMENTS"
    [関連する潜在問題の改善]
    
    # Phase 4: Verification
    echo "Phase 4: VERIFICATION"
    [修正効果の確認]
    
    echo "✅ Complete fix implemented for: $problem_domain"
}
```

### 4️⃣ **今回の事例から学ぶ具体的教訓**

#### **Critical Documentation Review Bug事例**
```bash
CASE_STUDY_LESSONS=(
    "🐛 PROBLEM: r'(docs/[^\\s]+\\.md)' pattern captured ](docs/... incorrectly"
    "🔍 INVESTIGATION: Multiple error types mixed in single report"
    "💡 SOLUTION: Markdown link exclusion + pattern refinement"
    "📊 RESULT: HIGH Issues 3→0, complete resolution confirmed"
)

SPECIFIC_IMPROVEMENTS=(
    "1. Error report multi-layered analysis (true vs false issues)"
    "2. Regex pattern debugging with concrete test cases"
    "3. Solution verification through quantitative measurement"
    "4. Complete workflow testing before final commit"
)
```

## 📋 **実行チェックリスト**

### **問題発生時の必須手順**
```bash
MANDATORY_ERROR_ANALYSIS_CHECKLIST=(
    "□ 全エラーメッセージを収集・分類した"
    "□ 真の問題と誤検出を分離した"
    "□ 各問題の根本原因を技術レベルで特定した"
    "□ 根本原因に対する直接的修正を実装した"
    "□ 再発防止策を実装した"
    "□ 修正効果を定量的に検証した"
    "□ 関連する潜在問題を改善した"
    "□ 完全なシナリオテストを実行した"
)

# 一つでも未完了なら作業継続必須
COMPLETION_RULE="全項目✅まで作業停止禁止"
```

### **品質ゲート**
```bash
QUALITY_GATES=(
    "Gate 1: Problem understanding completeness (100%)"
    "Gate 2: Root cause identification accuracy (100%)"  
    "Gate 3: Solution implementation completeness (100%)"
    "Gate 4: Verification success rate (100%)"
)

GATE_PASS_CRITERIA="全ゲート100%通過まで次工程移行禁止"
```

---

## 🚨 **違反時の対処**

### **即座実行事項**
1. 作業の即座停止
2. 完全な問題分析の再実行
3. 根本原因レベルまでの調査継続
4. 100%解決まで作業継続

### **学習・改善**
1. 失敗原因の詳細分析・記録
2. 防止策の強化・ルール追加
3. チェックリスト・プロトコルの更新

---

**重要**: このプロトコルは例外なく適用される。「時間不足」「部分解決で十分」等を理由とした例外は一切認めない。