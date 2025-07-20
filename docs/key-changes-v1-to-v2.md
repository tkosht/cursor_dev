# 要件定義 v1 → v2 主要変更点

## 1. パラダイムシフト：役割ベース → 個人ベース

### v1: 役割ベース評価
```
技術専門家として評価 → スコア
ビジネスユーザーとして評価 → スコア
一般読者として評価 → スコア
→ 重み付き平均で最終スコア
```

### v2: 個人ベースシミュレーション
```
田中太郎（32歳、エンジニア、早期採用者）が記事を読む
→ 個人的な評価（興味、理解度、価値認識）
→ SNSでシェアするか決定
→ フォロワー850人に露出
→ その中の山田花子が読んで更にシェア
→ ネットワーク効果で拡散
```

## 2. 静的 → 動的

### v1: 静的な評価
- 固定された4つのペルソナ
- 一度きりの評価
- 個別の評価を集約

### v2: 動的なシミュレーション
- 記事に応じて20-50体のペルソナを動的生成
- 時系列での行動変化
- ペルソナ間の相互作用

## 3. 評価 → 市場反応予測

### v1の出力
```json
{
  "tech_expert_score": 85,
  "business_user_score": 80,
  "general_reader_score": 75,
  "overall_score": 80,
  "improvement_suggestions": [...]
}
```

### v2の出力
```json
{
  "market_response": {
    "expected_reach": 15420,
    "viral_coefficient": 1.3,
    "peak_timing": "3-4 days",
    "primary_sharers": ["early_adopters", "thought_leaders"],
    "sentiment_evolution": {
      "day_1": "curious",
      "day_3": "excited",
      "day_7": "mainstream_adoption"
    }
  },
  "segment_performance": {
    "tech_professionals": {
      "adoption_rate": 0.72,
      "share_rate": 0.31,
      "influential_nodes": ["CTO_persona_3", "dev_lead_persona_7"]
    }
  }
}
```

## 4. 新しいコア機能

### 階層化ペルソナ生成システム
```
記事分析
  ↓
想定読者層の特定
  ↓
市場セグメンテーション
  ↓
各セグメントに対して：
  - デモグラフィック設計
  - サイコグラフィック設計
  - 行動パターン設計
  - ソーシャルネットワーク設計
  ↓
統計的に妥当なペルソナ群
```

### ネットワーク効果シミュレーション
- **初期拡散**: アーリーアダプターから開始
- **ソーシャルプルーフ**: 友人の行動に影響される
- **インフルエンサー効果**: 影響力のあるノードを特定
- **飽和点予測**: いつ拡散が止まるか

## 5. 実装上の主要な違い

### v1: シンプルな並列評価
```python
async def evaluate_article(article):
    results = await asyncio.gather(
        tech_expert.evaluate(article),
        business_user.evaluate(article),
        general_reader.evaluate(article),
        domain_expert.evaluate(article)
    )
    return aggregate_results(results)
```

### v2: 複雑な時系列シミュレーション
```python
async def simulate_market_response(article):
    # 1. ペルソナ群を動的生成
    personas = await generate_persona_population(article)
    
    # 2. ネットワーク構築
    network = build_social_network(personas)
    
    # 3. 時系列シミュレーション
    for t in range(time_steps):
        # 各ペルソナの行動を並列シミュレート
        actions = await simulate_timestep(personas, network, t)
        
        # ネットワーク効果を適用
        apply_network_effects(actions, network)
        
        # 収束チェック
        if is_converged(actions):
            break
    
    # 4. 市場反応分析
    return analyze_market_response(simulation_history)
```

## 6. ビジネス価値の違い

### v1: 品質改善フォーカス
- 記事の弱点を特定
- 改善提案を生成
- 品質スコアを提供

### v2: 市場インパクト予測フォーカス
- どれだけの人に届くか
- どのように拡散するか
- どのセグメントが反応するか
- いつバズるか（またはバズらないか）
- ROIの予測

## 7. 技術的チャレンジ

### v1の技術的チャレンジ
- LLMの品質
- 評価基準の一貫性
- 並列処理の効率

### v2の技術的チャレンジ
- 統計的に妥当なペルソナ生成
- リアリスティックなネットワーク構造
- 行動モデルの精度
- 計算量の増大（O(n²)のネットワーク効果）
- 時系列データの管理

## 8. MVP実装の違い

### v1 MVP（3週間）
- Week 1: 基本機能
- Week 2: 4エージェント実装
- Week 3: 統合とテスト

### v2 MVP（3週間）
- Week 1: 基本的なペルソナ生成（5-10体）
- Week 2: 個人の意思決定モデル
- Week 3: 簡易ネットワーク伝播

## まとめ

v2は単なる「評価ツール」から「市場シミュレーター」への進化です。記事の品質を評価するだけでなく、実際の市場でどのような反応が起きるかを予測することで、より戦略的なコンテンツマーケティングを可能にします。