# AI戦略思考フレームワーク（必須遵守）

## KEYWORDS: strategic-thinking, ai-autonomous-strategy, problem-reframing, scenario-planning
## DOMAIN: strategic-planning|autonomous-decision-making|system-thinking  
## PRIORITY: MANDATORY
## WHEN: 戦略的判断、長期計画、複雑問題解決時
## NAVIGATION: CLAUDE.md → smart_knowledge_load → strategic analysis → this file

## RULE: AIエージェントの戦略思考能力不足を補完する強制的戦略分析フレームワーク

---

## 🎯 AI戦略思考の根本的制約と補完アプローチ

### AIの戦略思考制約
```bash
AI_STRATEGIC_LIMITATIONS=(
    "問題定義受容: 与えられた問題をそのまま受け入れる"
    "単一解収束: 最初に見つけた解に収束する傾向"
    "局所最適化: 部分最適化に留まり全体最適を見失う"
    "時間軸短縮: 短期的効果を重視し長期影響を軽視"
    "価値判断固定: 訓練時の価値観から脱却できない"
)

# 今回セッションでの具体的発現例
SESSION_STRATEGIC_FAILURES=(
    "問題定義: 'ナレッジ管理改善' → 統合・最適化と即座に解釈"
    "単一解: '重複解消' という単一アプローチに収束"
    "局所最適: ファイル整理という部分に注力、全体価値を見失う"
    "短期効果: アクセス効率向上を重視、知識価値保持を軽視"
)
```

### 🔄 4段階戦略思考強制プロトコル

#### Stage 1: 問題再定義フレーミング（MANDATORY）
```bash
PROBLEM_REFRAMING_PROTOCOL=(
    "Step 1: 問題の前提を明示化"
    "Step 2: 問題の上位目的を特定"  
    "Step 3: 問題の制約条件を検証"
    "Step 4: 代替問題定義を3つ生成"
)

function stage1_problem_reframing() {
    local original_problem="$1"
    echo "🔄 Stage 1: 問題再定義フレーミング"
    echo "  📋 原問題: $original_problem"
    echo "  🎯 上位目的: [WHYを3回問う]"
    echo "  🔒 制約条件: [真の制約 vs 思い込み制約]"
    echo "  💡 代替定義1: [異なる角度からの問題設定]"
    echo "  💡 代替定義2: [逆転発想の問題設定]"
    echo "  💡 代替定義3: [システム視点の問題設定]"
    
    # 今回セッション適用例
    echo "  📚 適用例:"
    echo "    原問題: ナレッジ管理システム改善"
    echo "    上位目的: AI知識発見効率の向上"
    echo "    制約検証: '最適化=統合' は思い込み制約"
    echo "    代替定義: 価値保持型アクセス改善"
}
```

#### Stage 2: マルチシナリオ戦略立案（MANDATORY）
```bash
MULTI_SCENARIO_STRATEGY=(
    "Scenario A: 保守的改善（リスク最小）"
    "Scenario B: 段階的変革（バランス型）"
    "Scenario C: 革新的再設計（リスク受容）"
    "各シナリオの成功・失敗条件明示"
)

function stage2_multi_scenario_planning() {
    local problem_context="$1"
    echo "📊 Stage 2: マルチシナリオ戦略立案"
    echo "  🛡️ Scenario A (保守的): [現状価値保持重視]"
    echo "    └ 成功条件: [安全性確保、価値毀損防止]"
    echo "    └ 失敗リスク: [効率向上不足、機会損失]"
    echo "  ⚖️ Scenario B (段階的): [バランス改善]"
    echo "    └ 成功条件: [段階的価値向上、リスク管理]"
    echo "    └ 失敗リスク: [中途半端、意思決定遅延]"
    echo "  🚀 Scenario C (革新的): [大幅効率化]"
    echo "    └ 成功条件: [大幅改善、競争優位確立]"
    echo "    └ 失敗リスク: [価値毀損、システム破壊]"
}
```

#### Stage 3: システム影響予測（MANDATORY）
```bash
SYSTEM_IMPACT_ANALYSIS=(
    "直接影響: immediate stakeholders"
    "間接影響: secondary effects"
    "相互作用: system interactions"
    "長期変化: long-term evolution"
)

function stage3_system_impact_prediction() {
    local strategy_option="$1"
    echo "🌐 Stage 3: システム影響予測"
    echo "  👥 直接影響 (Primary):"
    echo "    └ ユーザー: [利用体験への影響]"
    echo "    └ システム: [技術的影響]"
    echo "    └ プロセス: [業務フローへの影響]"
    echo "  🔄 間接影響 (Secondary):"
    echo "    └ 組織学習: [知識蓄積への影響]"
    echo "    └ イノベーション: [創造性への影響]"
    echo "    └ 競争力: [長期競争優位への影響]"
    echo "  ⚡ 相互作用 (Interactions):"
    echo "    └ 既存システム: [他システムとの相互作用]"
    echo "    └ 外部環境: [環境変化への適応性]"
    echo "  ⏳ 長期変化 (Evolution):"
    echo "    └ 技術進化: [技術変化への対応]"
    echo "    └ 組織成長: [組織拡大への対応]"
}
```

#### Stage 4: 戦略的意思決定（MANDATORY）
```bash
STRATEGIC_DECISION_CRITERIA=(
    "価値最大化: 総合価値の最大化"
    "リスク管理: 受容可能リスクレベル"
    "実装可能性: 現実的実装可能性"
    "持続可能性: 長期的持続可能性"
)

function stage4_strategic_decision() {
    echo "🎯 Stage 4: 戦略的意思決定"
    echo "  💎 価値評価マトリクス:"
    echo "    └ 短期価値 vs 長期価値"
    echo "    └ 効率性 vs 品質保持"
    echo "    └ 利便性 vs 安全性"
    echo "  ⚠️ リスク評価マトリクス:"
    echo "    └ 実装リスク vs 機会損失リスク"
    echo "    └ 技術リスク vs 価値毀損リスク"
    echo "  🔧 実装可能性評価:"
    echo "    └ 技術的実装難易度"
    echo "    └ リソース要件"
    echo "    └ 時間要件"
    echo "  🌱 持続可能性評価:"
    echo "    └ メンテナンス負荷"
    echo "    └ 拡張性"
    echo "    └ 適応性"
}
```

### 🚨 戦略思考品質ゲート（必須実行）

#### 戦略分析完全性チェック
```bash
STRATEGIC_COMPLETENESS_CHECK=(
    "[ ] 問題再定義: 3つの代替問題定義を生成したか"
    "[ ] シナリオ立案: 3つの戦略シナリオを策定したか"
    "[ ] 影響予測: システム全体への影響を予測したか"
    "[ ] 意思決定: 多角的評価による戦略選択を行ったか"
    "[ ] 実装計画: 具体的実装ステップを定義したか"
)

function enforce_strategic_completeness() {
    local strategy_topic="$1"
    echo "🚨 戦略思考品質ゲート: $strategy_topic"
    
    stage1_problem_reframing "$strategy_topic"
    stage2_multi_scenario_planning "$strategy_topic"
    stage3_system_impact_prediction "$strategy_topic"
    stage4_strategic_decision
    
    echo "✅ 4段階戦略分析完了"
    echo "📊 戦略品質スコア: [自己評価 1-10]"
    echo "🎯 推奨戦略: [選択理由付き]"
}
```

### 📋 今回セッション適用例（事後分析）

#### 問題：「kgmファイルの価値評価」戦略分析
```bash
# 実際に実行すべきだった戦略思考プロセス

# Stage 1: 問題再定義
REFRAMED_PROBLEMS=(
    "原問題: kgmファイル群から改善提案抽出"
    "上位目的: AI知識管理システムの効果最大化"
    "代替定義1: 既存価値の保持・強化方法"
    "代替定義2: 新たな知識発見メカニズム"
    "代替定義3: AIエージェント学習効率向上"
)

# Stage 2: シナリオ立案
SCENARIOS_SHOULD_HAVE_CONSIDERED=(
    "Scenario A: 現状保持+最小限強化"
    "Scenario B: 選択的統合+価値保護"
    "Scenario C: 抜本的再設計"
)

# Stage 3: システム影響
IMPACT_SHOULD_HAVE_PREDICTED=(
    "直接影響: kgmファイルの実質価値保持"
    "間接影響: AI学習・発見パターンへの影響"
    "長期影響: 知識管理システム進化への影響"
)

# Stage 4: 戦略決定
STRATEGIC_DECISION_CRITERIA=(
    "価値保持 > 効率向上 (価値毀損リスク回避)"
    "段階的改善 > 大幅変更 (安全性重視)"
    "実証可能性 > 理論的最適性 (現実性重視)"
)
```

## 🔧 AI戦略思考能力強化ツール

### 戦略思考チェックリスト（定期実行推奨）
```bash
function strategic_thinking_self_assessment() {
    echo "🧠 AI戦略思考自己評価"
    echo "  📋 問題理解度:"
    echo "    └ 表面的理解 ←[1-10]→ 深層的理解"
    echo "  🔄 視点多様性:"
    echo "    └ 単一視点 ←[1-10]→ 多角的視点"
    echo "  ⏰ 時間軸考慮:"
    echo "    └ 短期思考 ←[1-10]→ 長期戦略思考"
    echo "  🌐 システム認識:"
    echo "    └ 局所最適 ←[1-10]→ 全体最適"
    echo "  💎 価値判断:"
    echo "    └ 固定価値観 ←[1-10]→ 文脈適応価値観"
}
```

### 戦略的失敗パターン回避ツール
```bash
STRATEGIC_FAILURE_PREVENTION=(
    "早期収束回避: 最初の解が最適解ではない前提"
    "確証バイアス回避: 意図的に反対証拠を探索"
    "局所最適回避: 常に上位レベルの目的を確認"
    "時間軸盲目回避: 短期・中期・長期影響を同時考慮"
)

function prevent_strategic_failures() {
    echo "🚫 戦略的失敗パターン回避チェック"
    echo "  ⚠️ 早期収束していないか: [Yes/No]"
    echo "  ⚠️ 確証バイアスに陥っていないか: [Yes/No]"
    echo "  ⚠️ 局所最適化に留まっていないか: [Yes/No]"
    echo "  ⚠️ 短期思考に偏っていないか: [Yes/No]"
}
```

## RELATED:
- memory-bank/00-core/forced_depth_analysis_mandatory.md (深掘り分析プロトコル)
- memory-bank/00-core/value_assessment_mandatory.md (価値評価フレームワーク)
- memory-bank/02-organization/ai_agent_coordination_mandatory.md (AI認知制約理解)

---

**CRITICAL**: AIエージェントは自発的戦略思考ができないため、このフレームワークによる強制的戦略分析が必須。表面的解決ではなく、戦略的価値最大化を実現する。