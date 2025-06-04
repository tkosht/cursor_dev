# A2A MVP実装 - TDDアプローチによる実践的サンプル

## 概要

本ドキュメントは、Google A2A (Agent-to-Agent) プロトコルの実践的なサンプル実装を、TDD（テスト駆動開発）アプローチで開発したプロセスと成果物をまとめたものです。

## プロジェクト構成

```
app/a2a/
├── core/               # コアプロトコル層
│   ├── types.py       # 型定義（Task, TaskRequest, TaskResponse, A2A types）
│   └── exceptions.py  # カスタム例外
├── storage/           # ストレージ層
│   ├── interface.py   # 抽象インターフェース
│   └── memory.py      # インメモリ実装
├── skills/            # スキル層
│   ├── base.py        # 基底スキルクラス
│   └── task_skills.py # タスク管理スキル
├── agents/            # エージェント層
│   ├── base.py        # 基底エージェントクラス
│   └── task_agent.py  # タスク管理エージェント
├── server/            # サーバー層
│   └── app.py         # FastAPIサーバー
└── client/            # クライアント層
    └── cli.py         # CLIクライアント
```

## TDD実装プロセス

### 1. テストファースト

各モジュールの実装前に、以下の順序でテストを作成：

1. **Core層テスト** (`test_types.py`, `test_exceptions.py`)
   - 型定義の振る舞い
   - 例外処理の確認

2. **Storage層テスト** (`test_interface.py`)
   - インターフェース定義
   - CRUD操作の検証

3. **Skills層テスト** (`test_task_skills.py`)
   - ビジネスロジックの検証
   - エラーハンドリング

4. **Agents層テスト** (`test_task_agent.py`)
   - A2Aプロトコル処理
   - リクエスト/レスポンス変換

### 2. 実装の特徴

#### データモデル（Task）
```python
@dataclass
class Task:
    id: str
    title: str
    created_at: datetime
    description: Optional[str] = None
    completed: bool = False
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式への変換（ISO形式の日時）"""
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """辞書形式からの復元"""
```

#### ストレージインターフェース
```python
class StorageInterface(ABC):
    @abstractmethod
    def create_task(self, task: Task) -> Task:
    @abstractmethod
    def get_task(self, task_id: str) -> Task:
    @abstractmethod
    def get_all_tasks(self) -> List[Task]:
    @abstractmethod
    def update_task(self, task: Task) -> Task:
    @abstractmethod
    def delete_task(self, task_id: str) -> None:
    @abstractmethod
    def clear_all(self) -> None:
```

#### A2Aエージェント実装
```python
class TaskAgent(BaseAgent):
    def get_agent_card(self) -> A2AAgentCard:
        """エージェント能力の定義"""
        
    def process_request(self, request: TaskRequest) -> TaskResponse:
        """タスクリクエストの処理"""
        
    def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """A2Aプロトコルメッセージの処理"""
```

## 使用方法

### サーバーの起動

```bash
# Python環境のセットアップ
cd /home/devuser/workspace
poetry shell

# サーバーの起動
python -m app.a2a.server.app
```

### CLIクライアントの使用

```bash
# エージェント情報の取得
python -m app.a2a.client.cli info

# タスクの作成
python -m app.a2a.client.cli create "買い物に行く" -d "牛乳とパンを買う"

# タスク一覧の表示
python -m app.a2a.client.cli list

# タスクの完了切り替え
python -m app.a2a.client.cli toggle <task_id>

# タスクの削除
python -m app.a2a.client.cli delete <task_id>
```

### APIエンドポイント

#### GET /
エージェントカード情報を返す

#### POST /task
タスク操作を実行
```json
{
  "action": "create|get|list|update|delete|toggle|clear",
  "task_id": "optional-task-id",
  "data": {
    "title": "タスクタイトル",
    "description": "説明",
    "completed": false
  }
}
```

#### POST /a2a/message
A2Aプロトコルメッセージを処理

## テスト実行とカバレッジ

```bash
# 全テストの実行
pytest tests/unit/ -v

# カバレッジレポート付き
pytest tests/unit/ --cov=app.a2a --cov-report=html

# 特定のテストのみ
pytest tests/unit/test_agents/ -v
```

### 現在のカバレッジ: 81%
- core/types.py: 100%
- core/exceptions.py: 100%
- storage/memory.py: 100%
- agents/task_agent.py: 92%
- skills/task_skills.py: 63%

## MVP開発への活用

### 1. モジュール性
各層が独立しているため、必要に応じて拡張・置換が可能：
- Storage層: PostgreSQL、MongoDB等への置換
- Skills層: 新しいビジネスロジックの追加
- Agents層: 複数エージェントの実装

### 2. 拡張ポイント
- 認証・認可の追加
- WebSocketによるリアルタイム通信
- タスクの優先度・期限管理
- マルチテナント対応

### 3. プロダクション対応
- 環境変数による設定管理
- ロギングの強化
- エラーモニタリング
- パフォーマンス最適化

## 学んだ教訓

### TDDの利点
1. **設計の明確化**: テストを先に書くことで、インターフェースが明確に
2. **リファクタリングの安心感**: テストがセーフティネットとして機能
3. **ドキュメントとしての役割**: テストが仕様書として機能

### A2A実装のポイント
1. **型安全性**: Pythonでも型ヒントを活用し、安全性を向上
2. **層の分離**: ビジネスロジックとプロトコル処理を分離
3. **エラーハンドリング**: 各層で適切な例外処理

## 次のステップ

1. **統合テストの追加**: サーバー・クライアント間の統合テスト
2. **E2Eテストの実装**: 実際のワークフローのテスト
3. **パフォーマンステスト**: 負荷テストとボトルネック分析
4. **セキュリティ強化**: 認証・認可・入力検証の実装

## まとめ

TDDアプローチにより、A2Aプロトコルの実践的なサンプルを体系的に実装できました。このサンプルは、MVP開発の基盤として活用でき、必要に応じて拡張・カスタマイズが可能な設計となっています。