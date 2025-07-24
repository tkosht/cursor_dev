# ReporterAgent 詳細設計チェックリスト

実行日: 2025-01-23
タスク: ReporterAgentの詳細設計

## 🎯 エージェントの責務

ReporterAgentは、シミュレーション全体の結果を包括的なレポートにまとめ、以下を生成する：
- エグゼクティブサマリー
- 詳細な分析結果
- ビジュアル要素の準備（チャート、グラフのデータ）
- 実行可能な推奨事項
- 多様な出力形式（JSON、Markdown、HTML）

## 📋 設計チェックリスト

### 1. クラス構造設計

□ **ファイル名**: `src/agents/reporter.py`
□ **クラス名**: `ReporterAgent`
□ **基底クラス**: `BaseAgent`からの継承
□ **インターフェース**: `IAgent`の実装

### 2. 必要な依存関係

□ **型定義**
  - `ArticleReviewState` from orchestrator
  - `EvaluationResult` from `src.core.types`
  - `PersonaAttributes` from `src.core.types`

□ **ユーティリティ**
  - `create_llm` from `src.utils.llm_factory`
  - `LLMCallTracker` from `src.utils.llm_transparency`

□ **レポート生成ライブラリ**
  - `jinja2` for テンプレートエンジン
  - `markdown` for Markdown処理
  - `plotly` or `matplotlib` for チャートデータ生成

□ **設定**
  - `get_config` from `src.config`

### 3. メソッド設計

□ **初期化メソッド**
  ```python
  def __init__(self):
      self.config = get_config()
      self.llm = create_llm()
      self.call_tracker = LLMCallTracker()
      self.template_engine = self._setup_templates()
  ```

□ **メインレポート生成メソッド**
  ```python
  async def generate_report(
      self,
      state: ArticleReviewState
  ) -> dict[str, Any]
  ```

□ **エグゼクティブサマリー生成**
  ```python
  async def _generate_executive_summary(
      self,
      state: ArticleReviewState
  ) -> dict[str, Any]
  ```

□ **詳細分析セクション生成**
  ```python
  def _generate_detailed_analysis(
      self,
      state: ArticleReviewState
  ) -> dict[str, Any]
  ```

□ **推奨事項生成**
  ```python
  async def _generate_recommendations(
      self,
      aggregated_scores: dict[str, float],
      improvement_suggestions: list[dict[str, Any]]
  ) -> list[dict[str, Any]]
  ```

□ **ビジュアルデータ準備**
  ```python
  def _prepare_visualization_data(
      self,
      state: ArticleReviewState
  ) -> dict[str, Any]
  ```

□ **出力フォーマット変換**
  ```python
  def _format_report(
      self,
      report_data: dict[str, Any],
      format: str = "json"
  ) -> str | dict[str, Any]
  ```

### 4. レポート構造設計

□ **エグゼクティブサマリー**
  - シミュレーション概要
  - 主要な発見事項（3-5点）
  - 全体的な評価スコア
  - 重要な推奨事項（トップ3）

□ **記事分析セクション**
  - 記事の概要
  - ターゲット層の特定
  - 強みと弱みの分析
  - 市場適合性評価

□ **ペルソナ分析セクション**
  - ペルソナ分布の概要
  - セグメント別の反応
  - 特徴的なペルソナの例
  - ペルソナ間の意見の相違点

□ **評価結果セクション**
  - 各メトリクスの詳細スコア
  - スコア分布の可視化
  - センチメント分析結果
  - エンゲージメント予測

□ **改善提案セクション**
  - 優先順位付けされた提案
  - 実装の難易度
  - 期待される効果
  - 具体的なアクション項目

□ **技術的詳細セクション**
  - シミュレーション設定
  - 使用したLLMモデル
  - 処理時間とコスト
  - データ品質メトリクス

### 5. ビジュアル要素設計

□ **チャートタイプ**
  - スコア分布ヒストグラム
  - レーダーチャート（多次元評価）
  - センチメント円グラフ
  - 時系列グラフ（該当する場合）
  - ヒートマップ（セグメント×メトリクス）

□ **データ構造**
  ```python
  {
      "charts": {
          "score_distribution": {
              "type": "histogram",
              "data": {...},
              "layout": {...}
          },
          "metric_radar": {
              "type": "radar",
              "data": {...},
              "layout": {...}
          },
          ...
      }
  }
  ```

### 6. テンプレート設計

□ **Markdownテンプレート**
  - report_template.md
  - executive_summary.md
  - detailed_analysis.md

□ **HTMLテンプレート**
  - report_template.html
  - スタイルシート定義

□ **変数バインディング**
  - Jinja2変数マッピング
  - 条件付きセクション
  - ループ処理

### 7. LLM活用ポイント

□ **洞察の生成**
  - データから意味のある洞察を抽出
  - パターンの説明
  - 予期しない発見の強調

□ **文章の生成**
  - 自然な文章での説明
  - 専門用語の適切な使用
  - 読み手に応じたトーン調整

□ **推奨事項の具体化**
  - 抽象的な提案を具体的なアクションに変換
  - 実装手順の提案
  - リスクと機会の評価

### 8. 出力形式

□ **JSON形式**
  - 構造化された完全なデータ
  - API応答として使用可能
  - プログラマティックな処理が容易

□ **Markdown形式**
  - 人間が読みやすい形式
  - GitHubやドキュメントツールで表示可能
  - 印刷用にも変換可能

□ **HTML形式**
  - インタラクティブな要素
  - 埋め込みチャート
  - スタイリング済み

### 9. エラーハンドリング

□ **データ不足時の対応**
  - 必須データの確認
  - デフォルト値の使用
  - 警告メッセージの追加

□ **LLM生成エラー**
  - フォールバックテキスト
  - 部分的な成功の処理

□ **フォーマット変換エラー**
  - エラーログの記録
  - 基本形式への フォールバック

### 10. パフォーマンス考慮

□ **大規模データ対応**
  - ペルソナ数が多い場合の要約戦略
  - サンプリングによる代表例の選択

□ **生成時間の最適化**
  - 並列処理可能な部分の特定
  - キャッシュの活用

### 11. テスト計画

□ **単体テスト**
  - 各セクション生成のテスト
  - テンプレート処理のテスト
  - データ変換のテスト

□ **統合テスト**
  - 完全なレポート生成テスト
  - 各種フォーマットの検証
  - エッジケースの処理

□ **視覚的検証**
  - 生成されたレポートの手動確認
  - チャートの正確性確認

### 12. 実装順序

1. □ 基本クラス構造の実装
2. □ レポートデータ構造の定義
3. □ 基本的なJSON出力の実装
4. □ テンプレートエンジンの設定
5. □ 各セクション生成メソッドの実装
6. □ LLM洞察生成の統合
7. □ ビジュアルデータ生成
8. □ Markdown/HTML出力の実装
9. □ エラーハンドリング
10. □ テストの作成
11. □ パフォーマンス最適化

## 🔍 検証項目

□ すべての重要な情報が含まれているか
□ レポートが論理的な構造を持っているか
□ 実行可能な推奨事項が含まれているか
□ 技術者と非技術者の両方が理解できるか
□ ビジュアル要素が効果的に使われているか

## 📝 備考

- orchestrator.pyではfinal_reportという辞書型の出力が期待されている
- レポートは記事の改善に直接役立つ内容である必要がある
- WebSocketを通じてリアルタイムで部分的な結果を送信する可能性も考慮