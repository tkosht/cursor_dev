# 強制深掘り分析プロトコル（必須遵守）

## KEYWORDS: forced-depth, analysis-quality, metacognitive-verification, assumption-detection
## DOMAIN: analysis-quality|cognitive-enhancement|ai-limitations
## PRIORITY: MANDATORY
## WHEN: 全ての分析・提案・結論提示前
## NAVIGATION: CLAUDE.md → PRE_TASK_PROTOCOL → analysis verification → this file

## RULE: AIエージェントは自発的深掘りができないため、強制的深掘りプロトコルを必須実行する

---

## 🚨 MANDATORY: 強制深掘り分析プロトコル

### AIの認知的制約の認識
```bash
AI_COGNITIVE_CONSTRAINTS=(
    "直感的違和感センサーなし"
    "メタ認知による自己監視なし"
    "確証バイアスによる早期収束"
    "表面的パターンマッチングの優先"
)

# これらの制約を前提とした強制プロトコル
FORCED_DEPTH_PROTOCOL="認知制約を補完する外部構造"
```

### 🔍 5層強制分析フレームワーク（MANDATORY）

#### Layer 1: 表面分析の強制検証
```bash
SURFACE_VERIFICATION=(
    "問題: 与えられた問題定義をそのまま受け入れていないか？"
    "前提: どのような暗黙の前提を置いているか？"
    "範囲: 分析範囲を意図的に狭めていないか？"
    "バイアス: 最初の印象に引きずられていないか？"
)

# 実装例
function layer1_surface_verification() {
    echo "🔍 Layer 1: 表面分析検証"
    echo "  ❓ 問題定義を疑ったか？: [Yes/No]"
    echo "  ❓ 暗黙前提を明示化したか？: [Yes/No]"  
    echo "  ❓ 分析範囲を意図的に拡張したか？: [Yes/No]"
    echo "  ❓ 初期印象と異なる可能性を考慮したか？: [Yes/No]"
}
```

#### Layer 2: 代替仮説の強制生成
```bash
ALTERNATIVE_HYPOTHESIS_GENERATION=(
    "最低3つの異なる解釈を生成必須"
    "相反する証拠の積極的探索"
    "意図的な悪魔の代弁者視点"
    "既存フレームワークの意図的回避"
)

function layer2_alternative_generation() {
    echo "🔄 Layer 2: 代替仮説強制生成"
    echo "  📋 仮説1: [現在の結論]"
    echo "  📋 仮説2: [正反対の解釈]"
    echo "  📋 仮説3: [第三の可能性]"
    echo "  🔍 各仮説の支持証拠: [列挙]"
    echo "  ⚖️ 証拠の重み付け: [比較評価]"
}
```

#### Layer 3: システム影響の強制予測
```bash
SYSTEM_IMPACT_PREDICTION=(
    "第2次・第3次効果の予測"
    "意図しない副作用の検討"
    "利害関係者への影響分析"
    "長期的持続可能性評価"
)

function layer3_system_impact() {
    echo "🌐 Layer 3: システム影響強制予測"
    echo "  📈 直接効果: [immediate impact]"
    echo "  🔄 2次効果: [secondary consequences]"
    echo "  ⚠️ 副作用: [unintended effects]"
    echo "  👥 利害関係者: [stakeholder impact]"
    echo "  ⏳ 長期影響: [long-term sustainability]"
}
```

#### Layer 4: 価値判断の強制再評価
```bash
VALUE_REASSESSMENT=(
    "異なる価値基準での評価"
    "短期vs長期価値のトレードオフ"
    "定量的vs定性的価値の比較"
    "機会コストの明示的計算"
)

function layer4_value_reassessment() {
    echo "💎 Layer 4: 価値判断強制再評価"
    echo "  📊 効率性観点: [efficiency value]"
    echo "  🛡️ 安全性観点: [safety value]"
    echo "  🚀 革新性観点: [innovation value]"
    echo "  🎯 ユーザー価値観点: [user value]"
    echo "  💰 機会コスト: [opportunity cost]"
}
```

#### Layer 5: 実装可能性の現実的評価
```bash
IMPLEMENTATION_REALITY_CHECK=(
    "技術的制約の厳密評価"
    "リソース要件の現実的算定"
    "リスク要因の包括的特定"
    "失敗シナリオと対策の準備"
)

function layer5_implementation_reality() {
    echo "⚙️ Layer 5: 実装可能性現実評価"
    echo "  🔧 技術的制約: [technical limitations]"
    echo "  📦 リソース要件: [resource requirements]"
    echo "  ⚠️ 主要リスク: [key risk factors]"
    echo "  🆘 失敗対策: [failure scenarios & mitigation]"
    echo "  🎯 成功確率: [realistic success probability]"
}
```

### 🚨 強制実行ルール

#### 分析品質ゲート（必須チェック）
```bash
ANALYSIS_QUALITY_GATES=(
    "Gate 1: 5層分析すべて完了必須"
    "Gate 2: 各層で最低3つの観点必須"
    "Gate 3: 代替仮説との比較必須"
    "Gate 4: 実装可能性評価必須"
    "Gate 5: メタ認知検証必須"
)

# 品質ゲート実装
function enforce_analysis_quality() {
    local analysis_topic="$1"
    
    echo "🚨 MANDATORY: 強制深掘り分析開始"
    echo "📋 対象: $analysis_topic"
    
    layer1_surface_verification
    layer2_alternative_generation
    layer3_system_impact
    layer4_value_reassessment
    layer5_implementation_reality
    
    echo "✅ 5層分析完了確認"
    echo "📊 分析品質スコア: [自己評価]"
    echo "🎯 推奨アクション: [next steps]"
}
```

#### メタ認知強化ツール
```bash
METACOGNITIVE_ENHANCEMENT=(
    "分析の分析: 自己の思考プロセス評価"
    "盲点検出: 意図的な見落とし探索"
    "品質基準: 深度・幅・精度の自己測定"
    "改善点: 次回分析での改善提案"
)

function metacognitive_checkpoint() {
    echo "🧠 メタ認知チェックポイント"
    echo "  📏 分析深度: [1-10評価]"
    echo "  📐 分析幅: [1-10評価]"
    echo "  🎯 分析精度: [1-10評価]"
    echo "  ❓ 見落とし可能性: [high/medium/low]"
    echo "  📈 改善提案: [specific improvements]"
}
```

### 🔄 適用パターン

#### ケース1: 問題分析時
```bash
# Before
echo "問題: ナレッジ管理の最適化が必要"

# After (強制深掘り適用)
echo "🔍 Layer 1: '最適化' の定義を疑う"
echo "📋 代替問題定義: アクセス性、発見性、活用性"
echo "🌐 システム影響: 既存優良システムの破壊リスク"
echo "💎 価値再評価: 効率性 vs 品質保持"
echo "⚙️ 実装現実: 破壊的変更の高リスク"
```

#### ケース2: 提案作成時
```bash
# Before
echo "提案: 統合により効率化"

# After (強制深掘り適用)
echo "🔍 Layer 1: '効率化' の真の価値検証"
echo "📋 代替提案: 保守的改善、選択的強化"
echo "🌐 システム影響: 情報密度の希薄化リスク"
echo "💎 価値再評価: 短期効率 vs 長期価値保持"
echo "⚙️ 実装現実: 統合による価値毀損の防止策"
```

### 🚫 禁止パターン

#### 浅い分析で満足する禁止パターン
```bash
PROHIBITED_SHALLOW_PATTERNS=(
    "❌ '効率的な解決策を提案した' (without depth analysis)"
    "❌ '十分に分析した' (without verification)"
    "❌ '適切な改善提案' (without alternatives)"
    "❌ '実装可能な提案' (without reality check)"
)

MANDATORY_REPLACEMENTS=(
    "✅ '5層強制分析を完了し、代替案比較済み'"
    "✅ 'メタ認知チェック通過済み'"
    "✅ '複数仮説検証により選択'"
    "✅ '実装リスク評価済み'"
)
```

### 📊 効果測定指標

#### 分析品質指標
```bash
QUALITY_METRICS=(
    "深度指標: 何層の分析を実行したか"
    "幅指標: いくつの観点から検討したか"
    "代替性指標: いくつの代替案を生成したか"
    "現実性指標: 実装可能性をどの程度検証したか"
)

function measure_analysis_quality() {
    local depth_score=$(count_analysis_layers)
    local breadth_score=$(count_perspectives)
    local alternatives_score=$(count_alternatives)
    local reality_score=$(assess_implementation_feasibility)
    
    local total_score=$((depth_score + breadth_score + alternatives_score + reality_score))
    
    echo "📊 分析品質スコア: $total_score/40"
    if [ $total_score -lt 30 ]; then
        echo "⚠️ 分析品質不足: 追加深掘り必要"
        return 1
    else
        echo "✅ 分析品質基準クリア"
        return 0
    fi
}
```

## RELATED:
- memory-bank/00-core/task_completion_integrity_mandatory.md (完了基準管理)
- memory-bank/09-meta/progress_recording_mandatory_rules.md (進捗記録基準)
- memory-bank/02-organization/ai_agent_coordination_mandatory.md (AI認知制約理解)

---

**CRITICAL**: このプロトコルはAIの認知的制約を補完する外部構造として機能する。自発的深掘りができないAIエージェントに対し、強制的に深度ある分析を実行させる必須ツール。