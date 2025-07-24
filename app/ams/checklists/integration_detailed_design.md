# 統合設計チェックリスト - AMSコンポーネント間連携

実行日: 2025-01-23
タスク: 全コンポーネント間の統合設計

## 🎯 統合の目的

AMSの未実装コンポーネントを既存システムと統合し、以下を実現する：
- LangGraphワークフローとの完全な統合
- 非同期イベント駆動アーキテクチャの実装
- リアルタイム可視化システムとの連携
- スケーラブルで保守可能なシステム設計

## 📋 統合設計チェックリスト

### 1. コンポーネント間の依存関係

□ **依存関係グラフ**
  ```
  OrchestratorAgent (既存)
      ├── AnalysisAgent (既存)
      ├── PersonaGenerator (既存)
      ├── PersonaEvaluationAgent (新規)
      ├── AggregatorAgent (新規)
      └── ReporterAgent (新規)
  
  EventBus (新規)
      ├── 全エージェント
      ├── SimulationClock
      └── WebSocket Server
  
  SimulationClock (新規)
      └── EventBus
  ```

□ **循環依存の確認**
  - EventBusとSimulationClockの双方向依存を回避
  - インターフェースを使用した疎結合設計

### 2. データフロー設計

□ **メインワークフロー**
  ```
  1. Article → OrchestratorAgent
  2. → AnalysisAgent → analysis_results
  3. → PersonaGenerator → personas[]
  4. → PersonaEvaluationAgent (並列) → evaluations[]
  5. → AggregatorAgent → aggregated_scores
  6. → ReporterAgent → final_report
  ```

□ **イベントフロー**
  ```
  各フェーズ完了時:
  - Agent → EventBus → SimulationClock
  - EventBus → WebSocket → Client
  - EventBus → Logging/Monitoring
  ```

### 3. LangGraphとの統合ポイント

□ **新規エージェントのノード登録**
  ```python
  # orchestrator.pyの修正箇所
  - _persona_evaluator_node: EvaluationAgentの統合
  - _aggregator_node: AggregatorAgentの統合
  - _reporter_node: ReporterAgentの統合
  ```

□ **Send APIの活用**
  - PersonaEvaluationAgentの並列実行
  - 評価結果の収集メカニズム

□ **状態管理**
  - ArticleReviewStateへの新規フィールド追加
  - 状態の一貫性保証

### 4. EventBus統合設計

□ **エージェントイベント発行**
  ```python
  # 各エージェントでの実装
  async def execute(self, ...):
      await self.event_bus.publish(
          EventType.AGENT_STARTED,
          source=self.agent_id,
          data={"phase": self.phase_name}
      )
      # 処理実行
      result = await self._process()
      
      await self.event_bus.publish(
          EventType.AGENT_COMPLETED,
          source=self.agent_id,
          data={"result": result.to_dict()}
      )
  ```

□ **イベントサブスクリプション**
  - OrchestratorAgentがフェーズ完了イベントを監視
  - WebSocketサーバーが可視化イベントを監視
  - ロギングシステムが全イベントを監視

### 5. SimulationClock統合設計

□ **時間管理の統合**
  ```python
  # OrchestratorAgentでの使用
  self.clock = SimulationClock(event_bus=self.event_bus)
  await self.clock.start()
  
  # 各フェーズでの時間進行
  await self.clock.advance()  # 次のステップへ
  ```

□ **タイムアウト管理**
  - 各エージェントの実行時間制限
  - グローバルシミュレーション時間制限

### 6. エラーハンドリング統合

□ **エラー伝播パス**
  ```
  Agent Error → EventBus → OrchestratorAgent
              → ErrorHandler → Retry/Abort
              → EventBus → Client Notification
  ```

□ **リカバリー戦略**
  - エージェントレベルのリトライ
  - フェーズレベルのフォールバック
  - シミュレーション全体の中断判断

### 7. パフォーマンス最適化統合

□ **並列処理の調整**
  - PersonaEvaluationAgentの並列度制御
  - EventBusのワーカー数調整
  - リソースプールの共有

□ **メモリ管理**
  - 大規模ペルソナデータの効率的な受け渡し
  - イベント履歴のサイズ制限
  - 完了データのガベージコレクション

### 8. 設定管理統合

□ **統一設定スキーマ**
  ```python
  # config.pyへの追加
  class EventBusConfig(BaseModel):
      max_queue_size: int = 1000
      worker_count: int = 4
      
  class SimulationClockConfig(BaseModel):
      time_scale: float = 1.0
      step_duration: float = 1.0
  
  class EvaluationConfig(BaseModel):
      max_parallel_evaluations: int = 10
      evaluation_timeout: float = 30.0
  ```

□ **環境変数マッピング**
  - EVENT_BUS_MAX_QUEUE_SIZE
  - SIMULATION_TIME_SCALE
  - MAX_PARALLEL_EVALUATIONS

### 9. テスト統合戦略

□ **統合テストシナリオ**
  - エンドツーエンドワークフロー
  - イベント発行・受信の検証
  - エラー状況でのシステム動作

□ **モックとスタブ**
  - EventBusのテストモード
  - SimulationClockの高速実行モード
  - LLMレスポンスの固定化オプション

### 10. 段階的統合計画

□ **フェーズ1: 基本統合**
  1. PersonaEvaluationAgentの実装と統合
  2. 既存ワークフローでの動作確認
  3. 基本的なエラーハンドリング

□ **フェーズ2: イベント駆動化**
  1. EventBusの実装
  2. 各エージェントへのイベント発行追加
  3. 基本的なイベントフローの確立

□ **フェーズ3: 時間管理追加**
  1. SimulationClockの実装
  2. EventBusとの統合
  3. タイムステップベースの実行

□ **フェーズ4: 完全統合**
  1. AggregatorAgentの実装と統合
  2. ReporterAgentの実装と統合
  3. 全体的な最適化とチューニング

### 11. 移行戦略

□ **既存コードへの影響最小化**
  - インターフェースの後方互換性維持
  - 段階的なEventBus移行
  - フィーチャーフラグによる切り替え

□ **ロールバック計画**
  - 各フェーズでのチェックポイント
  - 問題発生時の切り戻し手順
  - データ整合性の保証

### 12. 監視とデバッグ

□ **統合ログ戦略**
  - 相関IDによるトレース
  - 分散ログの集約
  - パフォーマンスメトリクス

□ **デバッグツール**
  - イベントフローの可視化
  - ワークフロー実行のトレース
  - ボトルネック分析

## 🔍 検証項目

□ 全コンポーネントが正しく連携しているか
□ データの一貫性が保たれているか
□ エラーが適切に処理されているか
□ パフォーマンス要件を満たしているか
□ スケーラビリティが確保されているか

## 📝 リスクと対策

### リスク1: LangGraphとEventBusの競合
- **対策**: 明確な責任分離とイベントのブリッジング

### リスク2: パフォーマンスボトルネック
- **対策**: 非同期処理の徹底と適切なバッファリング

### リスク3: 複雑性の増大
- **対策**: 明確なインターフェース定義と段階的実装

## 🚀 次のステップ

1. PersonaEvaluationAgentの実装開始
2. 基本的な統合テストの作成
3. EventBusの基本実装
4. 段階的な統合の実施

---

この統合設計に基づいて、各コンポーネントの実装を進めることで、スケーラブルで保守可能なAMSシステムを構築する。