# SimulationClock 詳細設計チェックリスト

実行日: 2025-01-23
タスク: SimulationClockの詳細設計

## 🎯 コンポーネントの責務

SimulationClockは、シミュレーション内の時間管理を担当し、以下を提供する：
- 仮想時間の管理（実時間とは独立）
- タイムステップの制御
- スケジュールされたイベントの管理
- 時間関連のイベント発火
- 時間の加速・減速・一時停止

## 📋 設計チェックリスト

### 1. クラス構造設計

□ **ファイル名**: `src/utils/simulation_clock.py`
□ **メインクラス**: `SimulationClock`
□ **補助クラス**:
  - `ScheduledEvent`: スケジュールされたイベント
  - `TimeScale`: 時間スケール設定
  - `ClockState`: クロックの状態

### 2. 必要な依存関係

□ **標準ライブラリ**
  - `asyncio` for 非同期タイマー
  - `datetime` for 時刻表現
  - `heapq` for イベントスケジューリング
  - `typing` for 型ヒント
  - `dataclasses` for データ構造

□ **内部依存**
  - `EventBus` for イベント発行（オプション）
  - 型定義 from `src.core.types`

### 3. 時間モデル設計

□ **時間表現**
  ```python
  @dataclass
  class SimulationTime:
      step: int  # シミュレーションステップ
      virtual_time: datetime  # 仮想時間
      real_start_time: datetime  # 実時間の開始時刻
      time_scale: float  # 時間スケール（1.0 = リアルタイム）
  ```

□ **クロック状態**
  ```python
  class ClockState(Enum):
      STOPPED = "stopped"
      RUNNING = "running"
      PAUSED = "paused"
      STEPPING = "stepping"  # ステップ実行中
  ```

### 4. メソッド設計

□ **初期化メソッド**
  ```python
  def __init__(
      self,
      start_time: datetime | None = None,
      time_scale: float = 1.0,
      step_duration: float = 1.0,  # 1ステップの仮想時間（秒）
      event_bus: EventBus | None = None
  ):
      self._current_step: int = 0
      self._virtual_time: datetime = start_time or datetime.now()
      self._time_scale: float = time_scale
      self._step_duration: float = step_duration
      self._state: ClockState = ClockState.STOPPED
      self._scheduled_events: list[ScheduledEvent] = []
      self._event_bus = event_bus
  ```

□ **時間進行メソッド**
  ```python
  async def advance(self, steps: int = 1) -> None:
      """指定ステップ数だけ時間を進める"""
  
  async def advance_to(self, target_time: datetime) -> None:
      """指定時刻まで時間を進める"""
  
  async def run(self) -> None:
      """連続的に時間を進める"""
  ```

□ **制御メソッド**
  ```python
  async def start(self) -> None
  async def pause(self) -> None
  async def resume(self) -> None
  async def stop(self) -> None
  async def reset(self, start_time: datetime | None = None) -> None
  ```

□ **スケジューリングメソッド**
  ```python
  def schedule_event(
      self,
      callback: Callable[[], Awaitable[None]],
      delay: float | None = None,
      at_time: datetime | None = None,
      at_step: int | None = None,
      recurring: bool = False,
      interval: float | None = None
  ) -> str:  # Returns event_id
  
  def cancel_event(self, event_id: str) -> bool
  ```

□ **時間取得メソッド**
  ```python
  def current_time(self) -> datetime
  def current_step(self) -> int
  def elapsed_virtual_time(self) -> timedelta
  def elapsed_real_time(self) -> timedelta
  ```

□ **時間スケール操作**
  ```python
  def set_time_scale(self, scale: float) -> None
  def get_time_scale(self) -> float
  ```

### 5. イベントスケジューリング

□ **スケジュールイベントクラス**
  ```python
  @dataclass
  class ScheduledEvent:
      event_id: str
      callback: Callable[[], Awaitable[None]]
      scheduled_time: datetime
      scheduled_step: int
      recurring: bool = False
      interval: float | None = None
      cancelled: bool = False
  ```

□ **イベント管理**
  - 優先度付きキューでの管理
  - 効率的な挿入・削除
  - 定期イベントの再スケジューリング

### 6. 高度な機能

□ **時間同期**
  - 複数のシミュレーションコンポーネント間の同期
  - バリア同期ポイント
  - 分散シミュレーション対応

□ **時間トラベル**
  - 過去の状態へのロールバック（オプション）
  - チェックポイント機能
  - 状態の保存・復元

□ **適応的時間ステップ**
  - イベント密度に基づく時間ステップ調整
  - 重要なイベント前後での細かい時間制御

□ **時間統計**
  - ステップ実行時間の計測
  - ボトルネック検出
  - パフォーマンスメトリクス

### 7. EventBusとの統合

□ **発行イベント**
  ```python
  # 時間関連イベント
  CLOCK_STARTED = "clock.started"
  CLOCK_STOPPED = "clock.stopped"
  CLOCK_PAUSED = "clock.paused"
  CLOCK_RESUMED = "clock.resumed"
  CLOCK_STEP_COMPLETED = "clock.step_completed"
  CLOCK_TIME_CHANGED = "clock.time_changed"
  ```

□ **イベントデータ**
  ```python
  {
      "current_step": int,
      "current_time": datetime,
      "time_scale": float,
      "state": ClockState
  }
  ```

### 8. パフォーマンス考慮

□ **効率的なイベント処理**
  - O(log n)のイベント挿入・削除
  - バッチイベント処理
  - 不要なイベントの早期削除

□ **メモリ管理**
  - 完了イベントの削除
  - 弱参照の使用（適切な場所で）

□ **並行性**
  - スレッドセーフな実装
  - 非同期操作の適切な管理

### 9. エラーハンドリング

□ **コールバックエラー**
  - エラーのキャプチャとログ
  - クロックの継続動作保証
  - エラーイベントの発行

□ **時間の不整合**
  - 負の時間進行の防止
  - オーバーフローの処理
  - 無効な時間スケールの拒否

### 10. テスト計画

□ **単体テスト**
  - 基本的な時間進行
  - イベントスケジューリング
  - 状態遷移
  - エラー処理

□ **統合テスト**
  - EventBusとの連携
  - 複数コンポーネントの同期
  - 長時間実行テスト

□ **パフォーマンステスト**
  - 大量イベントの処理
  - 時間精度の検証
  - メモリ使用量の監視

### 11. 実装順序

1. □ 基本的なクロッククラス構造
2. □ 時間進行ロジック
3. □ 状態管理（start/stop/pause）
4. □ シンプルなイベントスケジューリング
5. □ EventBus統合（オプション）
6. □ 定期イベント機能
7. □ 時間スケール機能
8. □ エラーハンドリング
9. □ 高度な同期機能
10. □ テストの作成
11. □ パフォーマンス最適化

## 🔍 検証項目

□ 時間の一貫性が保たれているか
□ イベントが正確なタイミングで発火するか
□ 一時停止・再開が正しく動作するか
□ 時間スケールが正しく適用されるか
□ 並行アクセスに対して安全か

## 📝 備考

- 現在「30%完了（基本構造のみ）」の状態
- シミュレーションステップ数は10程度を想定
- リアルタイム可視化との連携も考慮
- LangGraphのワークフロー実行と協調する必要がある