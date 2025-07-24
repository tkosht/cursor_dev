# AggregatorAgent 詳細設計チェックリスト

実行日: 2025-01-23
タスク: AggregatorAgentの詳細設計

## 🎯 エージェントの責務

AggregatorAgentは、複数のペルソナからの評価結果を集約し、以下を生成する：
- 統合されたスコア（各メトリクスの集約）
- 改善提案の優先順位付け
- センチメント分布の分析
- 統計的サマリー

## 📋 設計チェックリスト

### 1. クラス構造設計

□ **ファイル名**: `src/agents/aggregator.py`
□ **クラス名**: `AggregatorAgent`
□ **基底クラス**: `BaseAgent`からの継承
□ **インターフェース**: `IAgent`の実装

### 2. 必要な依存関係

□ **型定義**
  - `EvaluationResult` from `src.core.types`
  - `AgentID` from `src.core.types`

□ **ユーティリティ**
  - `create_llm` from `src.utils.llm_factory`
  - `parse_llm_json_response` from `src.utils.json_parser`
  - `LLMCallTracker` from `src.utils.llm_transparency`

□ **統計ライブラリ**
  - `numpy` for 統計計算
  - `pandas` for データ操作（オプション）

□ **設定**
  - `get_config` from `src.config`

### 3. メソッド設計

□ **初期化メソッド**
  ```python
  def __init__(self):
      self.config = get_config()
      self.llm = create_llm()
      self.call_tracker = LLMCallTracker()
  ```

□ **メイン集約メソッド**
  ```python
  async def aggregate(
      self,
      persona_evaluations: dict[str, EvaluationResult]
  ) -> dict[str, Any]:
      # Return: {"scores": {...}, "suggestions": [...]}
  ```

□ **統計集約メソッド**
  ```python
  def _aggregate_metrics(
      self,
      evaluations: list[EvaluationResult]
  ) -> dict[str, dict[str, float]]
  ```

□ **提案優先順位付けメソッド**
  ```python
  def _prioritize_suggestions(
      self,
      evaluations: list[EvaluationResult]
  ) -> list[dict[str, Any]]
  ```

□ **センチメント分析メソッド**
  ```python
  def _analyze_sentiment_distribution(
      self,
      evaluations: list[EvaluationResult]
  ) -> dict[str, Any]
  ```

□ **LLMサマリー生成メソッド**
  ```python
  async def _generate_insights_summary(
      self,
      aggregated_data: dict[str, Any]
  ) -> dict[str, Any]
  ```

### 4. 集約ロジック設計

□ **メトリクス集約方法**
  - 平均値（mean）
  - 中央値（median）
  - 標準偏差（std）
  - 最小値・最大値
  - パーセンタイル（25%, 75%）
  - 加重平均（ペルソナの影響度による）

□ **セグメント別集約**
  - ペルソナタイプ別
  - 年齢層別
  - 興味カテゴリ別
  - センチメント別

□ **外れ値処理**
  - 外れ値の検出
  - トリミング戦略
  - ロバスト統計量の使用

### 5. 提案の優先順位付け

□ **優先順位基準**
  - 言及頻度
  - 影響を受けるペルソナの数
  - 改善によるスコア向上の期待値
  - 実装の容易さ（LLM判断）

□ **提案のカテゴリ分類**
  - コンテンツの改善
  - 構造の改善
  - トーンの調整
  - 追加情報の必要性

□ **実行可能性評価**
  - 短期的改善
  - 中期的改善
  - 長期的改善

### 6. 統計的分析機能

□ **分布分析**
  - スコア分布のヒストグラム
  - 正規性検定
  - 歪度・尖度

□ **相関分析**
  - メトリクス間の相関
  - ペルソナ属性とスコアの相関

□ **クラスタリング**
  - 類似評価のグループ化
  - 特徴的なセグメントの発見

### 7. データ構造設計

□ **入力データ構造**
  ```python
  {
      "persona_id": EvaluationResult,
      ...
  }
  ```

□ **出力データ構造**
  ```python
  {
      "scores": {
          "overall": {"mean": 75.5, "median": 76.0, ...},
          "relevance": {"mean": 80.2, ...},
          ...
      },
      "suggestions": [
          {
              "suggestion": "...",
              "priority": "high",
              "impact": 15.5,
              "affected_personas": 25,
              "category": "content"
          },
          ...
      ],
      "sentiment": {
          "distribution": {"positive": 45, "neutral": 30, "negative": 25},
          "trends": {...}
      },
      "segments": {
          "by_age": {...},
          "by_interest": {...}
      },
      "insights": "LLM生成の洞察サマリー"
  }
  ```

### 8. エラーハンドリング

□ **データ不足**
  - 最小評価数のチェック
  - 部分的な集約の処理

□ **計算エラー**
  - ゼロ除算の防止
  - NaN/Inf値の処理

□ **LLMエラー**
  - インサイト生成の失敗時の対処
  - フォールバック戦略

### 9. パフォーマンス最適化

□ **大規模データ対応**
  - ストリーミング集約
  - メモリ効率的な計算

□ **並列処理**
  - セグメント別集約の並列化
  - 非同期処理の活用

□ **キャッシング**
  - 中間結果のキャッシュ
  - 再計算の最小化

### 10. テスト計画

□ **単体テスト**
  - 各集約メソッドのテスト
  - エッジケースのテスト
  - 統計計算の正確性

□ **統合テスト**
  - 様々な評価データセットでのテスト
  - LLMインサイト生成のテスト
  - パフォーマンステスト

### 11. 実装順序

1. □ 基本クラス構造の実装
2. □ 統計集約ロジックの実装
3. □ 提案優先順位付けロジック
4. □ センチメント分析機能
5. □ セグメント別集約機能
6. □ LLMインサイト生成
7. □ エラーハンドリング
8. □ 単体テストの作成
9. □ 統合テストの実装
10. □ パフォーマンス最適化

## 🔍 検証項目

□ すべての評価メトリクスが適切に集約されているか
□ 統計的手法が適切に選択されているか
□ 提案の優先順位付けが論理的か
□ セグメント分析が有用な洞察を提供しているか
□ 出力形式がReporterAgentで利用しやすいか

## 📝 備考

- orchestrator.pyではaggregated_scoresとimprovement_suggestionsが期待されている
- 大規模なペルソナ数（50-100）に対応できる設計が必要
- ReporterAgentが使いやすい形式で出力する必要がある