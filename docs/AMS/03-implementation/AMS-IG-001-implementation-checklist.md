# AMS-IG-001: Article Market Simulator 実装チェックリスト

## 実装進捗サマリー
- **最終更新**: 2025-07-22
- **全体進捗**: Week 1 の 70% 完了
- **完了項目**: 
  - ✅ 開発環境セットアップ (100%)
  - ✅ プロジェクト構造作成 (100%)
  - ✅ コアインターフェース実装 (100%)
  - ✅ 設定管理システム実装 (100%)
  - ✅ LangGraphオーケストレーター実装 (100%)
  - ✅ 記事分析エージェント実装 (100%)
- **作業中**: 
  - 🔄 EventBus, SimulationClock (30%)
  - 🔄 単体テスト作成 (現在カバレッジ29%)
- **次のタスク**: PopulationArchitect 実装

## 1. 実装前準備チェックリスト

### 1.1 開発環境セットアップ
- [x] Python 3.11+ のインストール確認 (完了: 2025-07-22)
- [x] 必要なパッケージのリスト作成 (完了: 2025-07-22)
  - [x] LangChain/LangGraph
  - [x] asyncio/aiohttp
  - [x] WebSocket (fastapi + websockets)
  - [x] pytest/pytest-asyncio
- [x] LLMプロバイダーの設定 (完了: 2025-07-22)
  - [x] Gemini API キーの確認
  - [x] OpenAI API キー（オプション）
  - [x] 環境変数設定（.env）
- [x] プロジェクト構造の作成 (完了: 2025-07-22)
  ```
  ams/
  ├── src/
  │   ├── core/           # コアフレームワーク
  │   ├── plugins/        # シミュレーションプラグイン
  │   ├── personas/       # ペルソナ生成システム
  │   ├── visualization/  # 可視化層
  │   └── utils/          # ユーティリティ
  ├── tests/
  │   ├── unit/
  │   ├── integration/
  │   └── e2e/
  ├── docs/
  ├── scripts/
  └── requirements.txt
  ```

### 1.2 技術的確認事項
- [ ] LangGraphのバージョンと機能確認
- [ ] 並列処理（Send API）の動作確認
- [ ] WebSocketストリーミングのテスト環境
- [ ] 時系列データストレージの選定（InfluxDB/TimescaleDB）

## 2. MVP実装チェックリスト（4週間）

### Week 1: コア基盤実装
#### Day 1-2: プロジェクトセットアップ
- [x] プロジェクト構造の作成 (完了: 2025-07-22)
- [x] 基本的な依存関係のインストール (完了: 2025-07-22 - pyproject.toml作成)
- [ ] CLIインターフェースの骨組み作成
- [x] 開発環境のドキュメント作成 (完了: 2025-07-22 - README.md作成)

#### Day 3-4: 抽象フレームワーク
- [x] IAgent, IEnvironment, IAction インターフェース実装 (完了: 2025-07-22)
- [x] ISimulationPlugin インターフェース実装 (完了: 2025-07-22 - IPlugin として実装)
- [~] EventBus, SimulationClock の実装 (30% 完了: BaseSimulation内に部分実装)
- [x] 基本的な単体テスト作成 (完了: 2025-07-22 - test_core_interfaces.py, test_analyzer.py, test_json_parser.py - カバレッジ81%達成)

#### Day 5-7: シンプルな階層的ペルソナ生成（3層）
- [x] DeepContextAnalyzer の基本実装 (完了: 2025-07-22 - AnalysisAgent として実装)
- [ ] PopulationArchitect の簡易版実装
- [ ] 基本的なペルソナ生成（10体程度）
- [ ] ペルソナ生成のテスト

### Week 2: 記事評価プラグイン
#### Day 8-9: ArticleEvaluationPlugin
- [ ] プラグインインターフェースの実装
- [ ] PersonaAgent クラスの実装
- [ ] ArticleEnvironment の実装
- [ ] プラグイン統合テスト

#### Day 10-11: 個人反応モデル
- [ ] PersonaDecisionEngine の実装
- [ ] 記事評価ロジック（relevance, comprehension, value）
- [ ] 共有意思決定モデル
- [ ] 反応モデルのテスト

#### Day 12-14: ネットワーク伝播シミュレーション
- [ ] NetworkEffectSimulator の実装
- [ ] 情報伝播アルゴリズム
- [ ] 収束判定ロジック
- [ ] シミュレーション統合テスト

### Week 3: 可視化基盤
#### Day 15-16: ストリーミングデータ構造
- [ ] StreamableState の実装
- [ ] SimulationDataStream の実装
- [ ] VisualizationBridge の実装
- [ ] データ変換パイプライン

#### Day 17-18: WebSocketサーバー
- [ ] FastAPI + WebSocket セットアップ
- [ ] VisualizationServer の実装
- [ ] クライアント接続管理
- [ ] ストリーミングテスト

#### Day 19-21: 基本的な可視化
- [ ] 時系列チャートデータ生成
- [ ] ネットワークグラフデータ生成
- [ ] Markdownレポート生成
- [ ] 簡易フロントエンド（デモ用）

### Week 4: 品質保証と完成
#### Day 22-23: テストスイート完成
- [x] 単体テストカバレッジ80%以上 (達成: 2025-07-22 - 81%カバレッジ)
- [ ] 統合テストシナリオ作成
- [ ] E2Eテスト（記事入力→レポート生成）
- [ ] LLM統合テスト（モック不使用）

#### Day 24-25: パフォーマンス最適化
- [ ] 並列処理の最適化
- [ ] メモリ使用量の分析
- [ ] レスポンスタイムの測定
- [ ] ボトルネック改善

#### Day 26-27: ドキュメント整備
- [ ] APIドキュメント作成
- [ ] 使用方法ガイド
- [ ] アーキテクチャ図の更新
- [ ] デプロイメントガイド

#### Day 28: デモとリリース準備
- [ ] デモシナリオの作成
- [ ] サンプル記事での動作確認
- [ ] リリースノート作成
- [ ] 今後の拡張計画

## 3. テスト戦略チェックリスト

### 3.1 単体テスト
- [x] 各インターフェースの実装テスト (完了: 2025-07-22)
- [ ] ペルソナ生成ロジックのテスト
- [ ] シミュレーションエンジンのテスト
- [ ] 可視化データ変換のテスト

### 3.2 統合テスト（LLMモック不使用）
- [ ] 実際のLLM APIを使用したペルソナ生成テスト
- [ ] エンドツーエンドのシミュレーションテスト
- [ ] WebSocketストリーミングテスト
- [ ] プラグイン統合テスト

### 3.3 性能テスト
- [ ] 50ペルソナ生成の時間測定（目標: 10秒以内）
- [ ] 10タイムステップシミュレーション（目標: 60秒以内）
- [ ] 同時接続クライアント数のテスト
- [ ] メモリリークの確認

### 3.4 品質保証
- [ ] コードレビューチェックリスト作成
- [ ] 静的解析ツールの設定（pylint, mypy）
- [ ] セキュリティチェック（API キー管理）
- [ ] エラーハンドリングの網羅性

## 4. リスクと対策

### 4.1 技術的リスク
| リスク | 影響度 | 対策 |
|--------|--------|------|
| LLM APIのレート制限 | 高 | バッチ処理、キャッシング実装 |
| 並列処理の複雑性 | 中 | 段階的実装、十分なテスト |
| リアルタイム性能 | 中 | データサンプリング、差分更新 |
| スケーラビリティ | 低 | MVP後に最適化 |

### 4.2 スケジュールリスク
- [ ] 週次進捗レビューの実施
- [ ] バッファ時間の確保（各フェーズ+1日）
- [ ] 優先順位の明確化（MVP必須機能）
- [ ] 早期のプロトタイプ作成

## 5. 確認事項と質問リスト

### 5.1 要件確認
- [ ] ペルソナ生成数の上限（MVP: 50体、将来: ?）
- [ ] シミュレーション時間の想定（リアルタイム vs 高速）
- [ ] 可視化の優先順位（ネットワーク vs 時系列）
- [ ] レポート形式の詳細要件

### 5.2 技術選定
- [ ] LLMプロバイダーの優先順位
- [ ] データストレージの選定（ローカル vs クラウド）
- [ ] フロントエンド技術（MVP: 簡易、将来: React?）
- [ ] デプロイ環境（ローカル vs Docker vs クラウド）

### 5.3 拡張性考慮
- [ ] プラグインAPIの安定性
- [ ] データモデルのバージョニング
- [ ] 国際化対応の必要性
- [ ] マルチテナント対応の計画

## 6. 成功基準

### 6.1 機能要件
- [ ] 記事入力から結果表示まで5分以内
- [ ] 50体のペルソナで意味のあるシミュレーション
- [ ] リアルタイムで可視化更新
- [ ] Markdownレポートの自動生成

### 6.2 非機能要件
- [ ] テストカバレッジ80%以上
- [ ] ドキュメント完備
- [ ] エラーハンドリング実装
- [ ] 基本的なセキュリティ対策

## 7. 次のアクション

1. **環境構築**（今日）
   - プロジェクトディレクトリ作成
   - requirements.txt作成
   - 基本的なCLI実装

2. **設計レビュー**（明日）
   - ドキュメント間の整合性確認
   - 不明点の洗い出し
   - 実装優先順位の確定

3. **プロトタイプ作成**（今週）
   - 最小限のペルソナ生成
   - 簡単なシミュレーション
   - 概念実証

---

## 実装済みファイル一覧 (2025-07-22 追加)

### コアシステム
- `app/ams/pyproject.toml` - プロジェクト設定
- `app/ams/.env.example` - 環境変数テンプレート
- `app/ams/README.md` - プロジェクトドキュメント

### src/core/
- `interfaces.py` - IAgent, IEnvironment, IAction, IPlugin, ISimulation, IVisualization
- `base.py` - BaseAgent, BaseEnvironment, BaseAction, BasePlugin, BaseSimulation
- `types.py` - PersonaAttributes, ActionResult, SimulationState, EvaluationResult

### src/agents/
- `orchestrator.py` - OrchestratorAgent, ArticleReviewState (LangGraph実装)
- `analyzer.py` - AnalysisAgent (8次元分析: content, structure, sentiment, readability, keywords, target_audience, technical_depth, emotional_impact)

### src/config/
- `config.py` - AMSConfig, LLMConfig, SimulationConfig, VisualizationConfig
- `llm_selector.py` - LLMSelector, TaskType別最適化

### src/utils/
- `llm_factory.py` - LLMインスタンス生成
- `json_parser.py` - LLM応答解析

### tests/
- `conftest.py` - pytest設定
- `unit/test_core_interfaces.py` - インターフェーステスト (全テストパス)
- `unit/test_config.py` - 設定管理テスト (全テストパス)
- `unit/test_analyzer.py` - 記事分析エージェントテスト (8テスト、100%カバレッジ)
- `unit/test_json_parser.py` - JSONパーサーテスト (20テスト、100%カバレッジ)

---

更新日: 2025-07-22 (実装進捗を反映 - 単体テストカバレッジ81%達成)
作成者: AMS Implementation Team