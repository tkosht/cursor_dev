# PersonaEvaluationAgent 詳細設計チェックリスト

実行日: 2025-01-23
タスク: PersonaEvaluationAgentの詳細設計

## 🎯 エージェントの責務

PersonaEvaluationAgentは、生成されたペルソナの視点から記事を評価し、以下を生成する：
- 複数の評価メトリクスとスコア
- 定性的フィードバック（強み、弱み、提案）
- 予測される行動（共有確率、エンゲージメントレベル、センチメント）
- 評価の理由と信頼度

## 📋 設計チェックリスト

### 1. クラス構造設計

□ **ファイル名**: `src/agents/evaluator.py`
□ **クラス名**: `EvaluationAgent`
□ **基底クラス**: `BaseAgent`からの継承
□ **インターフェース**: `IAgent`の実装

### 2. 必要な依存関係

□ **型定義**
  - `PersonaAttributes` from `src.core.types`
  - `EvaluationResult` from `src.core.types`
  - `EvaluationMetric` from `src.core.types`

□ **ユーティリティ**
  - `create_llm` from `src.utils.llm_factory`
  - `parse_llm_json_response` from `src.utils.json_parser`
  - `LLMCallTracker` from `src.utils.llm_transparency`

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

□ **メイン評価メソッド**
  ```python
  async def evaluate_persona(
      self,
      persona: PersonaAttributes,
      article_content: str,
      analysis_results: dict[str, Any]
  ) -> EvaluationResult
  ```

□ **プロンプト生成メソッド**
  ```python
  def _generate_evaluation_prompt(
      self,
      persona: PersonaAttributes,
      article_content: str,
      analysis_results: dict[str, Any]
  ) -> str
  ```

□ **レスポンス解析メソッド**
  ```python
  def _parse_evaluation_response(
      self,
      response: str,
      persona_id: str,
      article_id: str
  ) -> EvaluationResult
  ```

### 4. LLMプロンプト設計

□ **ペルソナコンテキスト**
  - 人口統計情報の要約
  - サイコグラフィック特性
  - 行動パターン
  - 認知バイアスと感情的トリガー

□ **評価指示**
  - 記事の関連性評価
  - 情報の信頼性評価
  - 感情的インパクト評価
  - 行動喚起の強さ評価

□ **出力フォーマット**
  - JSON形式での構造化出力
  - 評価メトリクスの明確な定義
  - 定性的フィードバックの具体性

### 5. 評価メトリクス設計

□ **基本メトリクス**
  - relevance_score: 記事の関連性（0-100）
  - clarity_score: 情報の明確さ（0-100）
  - credibility_score: 信頼性（0-100）
  - emotional_impact_score: 感情的影響（0-100）
  - action_potential_score: 行動喚起力（0-100）

□ **ペルソナ固有メトリクス**
  - interest_alignment: 興味との一致度
  - value_alignment: 価値観との一致度
  - bias_resonance: 認知バイアスとの共鳴

### 6. エラーハンドリング

□ **LLM呼び出しエラー**
  - リトライロジック（最大3回）
  - エラーログ記録
  - デフォルト評価の生成

□ **JSONパースエラー**
  - フォールバック解析ロジック
  - 部分的な結果の回復
  - エラー詳細の記録

□ **タイムアウト処理**
  - 設定可能なタイムアウト値
  - 部分結果の返却
  - タイムアウト警告

### 7. パフォーマンス最適化

□ **並列処理対応**
  - 非同期実行のサポート
  - バッチ処理の考慮
  - リソース管理

□ **キャッシング戦略**
  - 類似ペルソナの結果再利用
  - プロンプトテンプレートのキャッシュ

### 8. テスト計画

□ **単体テスト**
  - プロンプト生成のテスト
  - レスポンス解析のテスト
  - エラーハンドリングのテスト

□ **統合テスト**
  - 実際のLLM呼び出しテスト
  - 各種ペルソナタイプでのテスト
  - タイムアウトシナリオのテスト

### 9. ドキュメント要件

□ **クラスドキュメント**
  - 評価プロセスの説明
  - メトリクスの詳細定義
  - 使用例

□ **設定ドキュメント**
  - 調整可能なパラメータ
  - パフォーマンスチューニング

### 10. 実装順序

1. □ 基本クラス構造の実装
2. □ プロンプト生成ロジックの実装
3. □ LLM呼び出しとレスポンス解析
4. □ エラーハンドリングの追加
5. □ 単体テストの作成
6. □ 統合テストの実装
7. □ パフォーマンス最適化
8. □ ドキュメントの作成

## 🔍 検証項目

□ PersonaAttributesのすべての属性が評価に反映されているか
□ EvaluationResultのすべてのフィールドが適切に設定されているか
□ LLMプロンプトが明確で構造化されているか
□ エラーハンドリングが包括的か
□ パフォーマンス要件を満たしているか

## 📝 備考

- orchestrator.pyではEvaluationAgentとして参照されている
- Send APIを使用した並列評価に対応する必要がある
- 評価結果はAggregatorAgentで集約される