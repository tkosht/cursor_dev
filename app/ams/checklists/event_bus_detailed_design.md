# EventBus 詳細設計チェックリスト

実行日: 2025-01-23
タスク: EventBusの詳細設計

## 🎯 コンポーネントの責務

EventBusは、シミュレーション内の非同期イベント通信を管理し、以下を提供する：
- イベントの発行（publish）とサブスクライブ（subscribe）
- 非同期メッセージ配信
- イベントの優先順位付けとキューイング
- エラーハンドリングとリトライ
- イベント履歴の記録

## 📋 設計チェックリスト

### 1. クラス構造設計

□ **ファイル名**: `src/utils/event_bus.py`
□ **メインクラス**: `EventBus`
□ **補助クラス**: 
  - `Event`: イベントデータクラス
  - `EventHandler`: ハンドラーの基底クラス
  - `EventSubscription`: サブスクリプション管理

### 2. 必要な依存関係

□ **標準ライブラリ**
  - `asyncio` for 非同期処理
  - `typing` for 型ヒント
  - `dataclasses` for イベント定義
  - `weakref` for ハンドラー参照管理
  - `logging` for ログ記録

□ **外部ライブラリ**
  - `priority_queue` or `heapq` for 優先順位付きキュー

□ **内部依存**
  - `SimulationClock` for タイムスタンプ（循環依存に注意）

### 3. イベント設計

□ **基本イベントクラス**
  ```python
  @dataclass
  class Event:
      event_type: str
      source: str  # 発行元のエージェントID
      timestamp: datetime
      data: dict[str, Any]
      priority: int = 0
      correlation_id: str | None = None
  ```

□ **イベントタイプ定義**
  ```python
  class EventType(str, Enum):
      # エージェント関連
      AGENT_STARTED = "agent.started"
      AGENT_COMPLETED = "agent.completed"
      AGENT_FAILED = "agent.failed"
      
      # ペルソナ関連
      PERSONA_CREATED = "persona.created"
      PERSONA_EVALUATED = "persona.evaluated"
      
      # シミュレーション関連
      SIMULATION_STARTED = "simulation.started"
      SIMULATION_PHASE_CHANGED = "simulation.phase_changed"
      SIMULATION_COMPLETED = "simulation.completed"
      
      # データ関連
      DATA_AGGREGATED = "data.aggregated"
      REPORT_GENERATED = "report.generated"
  ```

### 4. メソッド設計

□ **初期化メソッド**
  ```python
  def __init__(self, max_queue_size: int = 1000):
      self._subscribers: dict[str, list[EventHandler]] = {}
      self._event_queue: asyncio.PriorityQueue = asyncio.PriorityQueue(max_queue_size)
      self._running: bool = False
      self._worker_task: asyncio.Task | None = None
      self._event_history: list[Event] = []
  ```

□ **イベント発行メソッド**
  ```python
  async def publish(
      self,
      event_type: str | EventType,
      source: str,
      data: dict[str, Any],
      priority: int = 0
  ) -> None
  ```

□ **サブスクライブメソッド**
  ```python
  def subscribe(
      self,
      event_type: str | EventType,
      handler: EventHandler | Callable[[Event], Awaitable[None]],
      filter_func: Callable[[Event], bool] | None = None
  ) -> EventSubscription
  ```

□ **アンサブスクライブメソッド**
  ```python
  def unsubscribe(
      self,
      subscription: EventSubscription
  ) -> None
  ```

□ **イベント処理ワーカー**
  ```python
  async def _process_events(self) -> None:
      """バックグラウンドでイベントを処理"""
      while self._running:
          try:
              event = await self._event_queue.get()
              await self._dispatch_event(event)
          except Exception as e:
              await self._handle_error(e, event)
  ```

□ **起動・停止メソッド**
  ```python
  async def start(self) -> None
  async def stop(self) -> None
  ```

### 5. 高度な機能

□ **イベントフィルタリング**
  - パターンマッチング
  - 条件付きサブスクリプション
  - データフィルタリング

□ **イベントトランスフォーメーション**
  - イベントの変換
  - データのエンリッチメント
  - イベントの集約

□ **デッドレターキュー**
  - 処理失敗イベントの保存
  - リトライロジック
  - エラー通知

□ **イベントストア**
  - イベント履歴の永続化
  - イベントソーシング対応
  - リプレイ機能

### 6. パフォーマンス最適化

□ **バッチ処理**
  - 同種イベントのバッチング
  - 遅延配信オプション

□ **並列処理**
  - 複数ワーカーでの処理
  - イベントタイプ別の並列化

□ **メモリ管理**
  - イベント履歴のサイズ制限
  - 弱参照によるハンドラー管理

□ **バックプレッシャー**
  - キューサイズの監視
  - 発行レート制限

### 7. エラーハンドリング

□ **ハンドラーエラー**
  - エラーのキャプチャ
  - エラーイベントの発行
  - ハンドラーの隔離

□ **システムエラー**
  - キュー満杯時の処理
  - メモリ不足対応
  - グレースフルシャットダウン

□ **リトライ戦略**
  - 指数バックオフ
  - 最大リトライ回数
  - リトライ可能エラーの判定

### 8. 監視とデバッグ

□ **メトリクス**
  - イベント処理レート
  - キューサイズ
  - エラー率
  - レイテンシ

□ **ロギング**
  - イベントトレース
  - エラーログ
  - パフォーマンスログ

□ **デバッグツール**
  - イベントフロー可視化
  - サブスクリプショングラフ
  - ボトルネック検出

### 9. 統合ポイント

□ **LangGraphとの統合**
  - LangGraphイベントのブリッジング
  - 状態変更の通知

□ **WebSocketとの統合**
  - リアルタイムイベントストリーミング
  - クライアントへの選択的配信

□ **可視化システムとの統合**
  - 可視化用イベントの生成
  - データ変換パイプライン

### 10. テスト計画

□ **単体テスト**
  - 基本的なpub/sub機能
  - エラーハンドリング
  - 並行性テスト

□ **統合テスト**
  - 複数エージェントでの使用
  - 高負荷テスト
  - エラー伝播テスト

□ **パフォーマンステスト**
  - スループット測定
  - レイテンシ測定
  - メモリ使用量

### 11. 実装順序

1. □ 基本的なEvent/EventBusクラス
2. □ シンプルなpub/sub機能
3. □ 非同期イベント処理
4. □ エラーハンドリング基盤
5. □ 優先順位付きキュー実装
6. □ フィルタリング機能
7. □ イベント履歴機能
8. □ 監視・メトリクス機能
9. □ 統合ポイントの実装
10. □ テストの作成
11. □ パフォーマンス最適化

## 🔍 検証項目

□ スレッドセーフ/非同期安全な実装か
□ メモリリークが発生しないか
□ デッドロックが発生しないか
□ 高負荷時の性能劣化が許容範囲内か
□ エラーが適切に伝播・処理されるか

## 📝 備考

- 現在「30%完了（基本構造のみ）」の状態
- LangGraphのイベントシステムとの共存を考慮
- シミュレーションの規模（50-100ペルソナ）に対応できる設計
- WebSocketを通じたリアルタイム配信も考慮