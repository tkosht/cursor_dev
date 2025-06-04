# A2A実装実践記録：TDD手法による本格的なエージェント開発

## はじめに

前回の記事でA2Aプロトコルの概要を説明しましたが、今回は実際にTDD（Test-Driven Development）手法を用いてA2A MVPを開発した過程を詳しく解説します。

単なる技術解説ではなく、**実際のコードと直面した課題**、そして**TDDがもたらした開発体験の変化**に焦点を当てた実践記録です。

## プロジェクト概要

### 開発したシステム
タスク管理エージェント（TODO管理）を中核とするA2A MVP

### 技術スタック
- **言語**: Python 3.12
- **フレームワーク**: FastAPI (サーバー)
- **テスト**: pytest + coverage
- **A2Aライブラリ**: Google公式 a2a-sdk v0.2.4

### アーキテクチャ設計
```
app/a2a/
├── core/         # 型定義・例外処理
├── storage/      # データストレージ抽象化
├── skills/       # ビジネスロジック
├── agents/       # A2Aエージェント実装
├── server/       # API サーバー
└── client/       # CLI クライアント
```

## TDD実装プロセスの実際

### Phase 1: 型システムの設計（Red → Green → Refactor）

**Red Phase（失敗テスト作成）**
```python
def test_task_creation_with_required_fields():
    """タスク作成: 必須フィールド指定テスト"""
    # Given: 有効なタスクデータ
    task_data = {
        "title": "買い物に行く",
        "description": "牛乳とパンを買う"
    }
    
    # When: Taskを作成
    task = Task(
        id="test-123",
        title=task_data["title"],
        description=task_data["description"],
        created_at=datetime.now()
    )
    
    # Then: 期待される値で作成される
    assert task.title == "買い物に行く"
    assert task.description == "牛乳とパンを買う"
    assert task.completed is False  # デフォルト値
    assert isinstance(task.created_at, datetime)
```

**Green Phase（最小実装）**
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
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """辞書形式からの復元"""
        created_at = datetime.fromisoformat(data["created_at"])
        updated_at = None
        if data.get("updated_at"):
            updated_at = datetime.fromisoformat(data["updated_at"])
        
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description"),
            completed=data.get("completed", False),
            created_at=created_at,
            updated_at=updated_at
        )
```

**Refactor Phase（設計改善）**
日時処理のユーティリティメソッド追加、バリデーション強化など

### Phase 2: ストレージ層の抽象化

**インターフェース駆動設計の実践**

```python
# テストファースト: インターフェース仕様の定義
def test_storage_interface_crud_operations():
    """ストレージインターフェース: CRUD操作テスト"""
    storage = InMemoryStorage()
    
    # Create
    task = Task(id="test-1", title="テスト", created_at=datetime.now())
    created_task = storage.create_task(task)
    assert created_task.id == "test-1"
    
    # Read
    retrieved_task = storage.get_task("test-1")
    assert retrieved_task.title == "テスト"
    
    # Update
    retrieved_task.title = "更新されたテスト"
    updated_task = storage.update_task(retrieved_task)
    assert updated_task.title == "更新されたテスト"
    
    # Delete
    storage.delete_task("test-1")
    with pytest.raises(TaskNotFoundException):
        storage.get_task("test-1")
```

**抽象インターフェースの実装**
```python
class StorageInterface(ABC):
    """タスクストレージの抽象インターフェース"""
    
    @abstractmethod
    def create_task(self, task: Task) -> Task:
        """新しいタスクを作成"""
        pass
    
    @abstractmethod
    def get_task(self, task_id: str) -> Task:
        """IDでタスクを取得"""
        pass
    
    @abstractmethod
    def get_all_tasks(self) -> List[Task]:
        """全タスクを取得"""
        pass
    
    @abstractmethod
    def update_task(self, task: Task) -> Task:
        """既存タスクを更新"""
        pass
    
    @abstractmethod
    def delete_task(self, task_id: str) -> None:
        """タスクを削除"""
        pass
```

**TDDの効果**: インターフェースを先に定義することで、実装の方向性が明確になり、将来のデータベース切り替えが容易な設計となった。

### Phase 3: ビジネスロジック層（Skills）の実装

**複雑なビジネスロジックのテスト駆動開発**

```python
def test_create_task_with_validation():
    """タスク作成スキル: バリデーション付きテスト"""
    storage = InMemoryStorage()
    skill = TaskSkill(storage)
    
    # 正常ケース
    result = skill.create_task({
        "title": "有効なタスク",
        "description": "説明文"
    })
    assert result["success"] is True
    assert result["task"]["title"] == "有効なタスク"
    
    # エラーケース: タイトル不足
    result = skill.create_task({})
    assert result["success"] is False
    assert "title" in result["error"].lower()
    
    # エラーケース: 空のタイトル
    result = skill.create_task({"title": ""})
    assert result["success"] is False
    assert "title" in result["error"].lower()
```

**実装されたTaskSkillクラス**
```python
class TaskSkill(BaseSkill):
    """タスク管理スキルの実装"""
    
    def __init__(self, storage: StorageInterface):
        self.storage = storage
    
    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """タスク作成処理"""
        try:
            # バリデーション
            if 'title' not in data or not data['title'].strip():
                return {"success": False, "error": "Title is required"}
            
            # タスク作成
            task = Task(
                id=str(uuid.uuid4()),
                title=data['title'].strip(),
                description=data.get('description', '').strip() or None,
                created_at=datetime.now()
            )
            
            created_task = self.storage.create_task(task)
            return {"success": True, "task": created_task.to_dict()}
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return {"success": False, "error": str(e)}
    
    def toggle_task_completion(self, task_id: str) -> Dict[str, Any]:
        """タスク完了状態の切り替え"""
        try:
            task = self.storage.get_task(task_id)
            task.completed = not task.completed
            task.updated_at = datetime.now()
            
            updated_task = self.storage.update_task(task)
            return {"success": True, "task": updated_task.to_dict()}
            
        except TaskNotFoundException:
            return {"success": False, "error": f"Task not found: {task_id}"}
        except Exception as e:
            logger.error(f"Error toggling task completion: {e}")
            return {"success": False, "error": str(e)}
```

### Phase 4: A2Aエージェント層の実装

**プロトコル準拠エージェントのTDD実装**

```python
def test_task_agent_a2a_message_handling():
    """TaskAgent: A2Aメッセージハンドリングテスト"""
    storage = InMemoryStorage()
    agent = TaskAgent(storage)
    
    # タスク作成メッセージ
    message = {
        "action": "create",
        "data": {"title": "A2Aタスク", "description": "A2A経由で作成"}
    }
    
    response = agent.handle_a2a_message(message)
    assert response["success"] is True
    assert response["data"]["title"] == "A2Aタスク"
    
    # 不正メッセージ
    invalid_message = {"invalid": "message"}
    response = agent.handle_a2a_message(invalid_message)
    assert response["success"] is False
    assert "action" in response["error"]
```

**TaskAgentの実装**
```python
class TaskAgent(BaseAgent):
    """タスク管理A2Aエージェント"""
    
    def __init__(self, storage: StorageInterface):
        self.storage = storage
        self.task_skill = TaskSkill(storage)
    
    def get_agent_card(self) -> A2AAgentCard:
        """エージェント能力カードの生成"""
        skills = [
            A2ASkill(
                id="create_task",
                name="Create Task",
                description="Create a new TODO task with title and optional description",
                tags=["task", "create", "todo", "productivity"],
                examples=["Create a task to buy groceries", "Add a reminder to call mom"]
            ),
            A2ASkill(
                id="list_tasks",
                name="List Tasks",
                description="Get all tasks with their completion status",
                tags=["task", "list", "todo", "view"],
                examples=["Show me all my tasks", "What tasks do I have?"]
            ),
            # ... 他のスキル定義
        ]
        
        return A2AAgentCard(
            id="task_agent",
            name="Task Management Agent",
            description="An agent for managing TODO tasks with full CRUD operations",
            skills=skills,
            tags=["productivity", "task-management", "todo"],
            version="1.0.0"
        )
    
    def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """A2Aプロトコルメッセージの処理"""
        try:
            # メッセージ検証
            if "action" not in message:
                return {"success": False, "error": "Missing required field: action"}
            
            # TaskRequestに変換
            request = TaskRequest(
                action=message["action"],
                data=message.get("data"),
                task_id=message.get("task_id")
            )
            
            # リクエスト処理
            response = self.process_request(request)
            
            return {
                "success": response.success,
                "data": response.data,
                "error": response.error
            }
            
        except Exception as e:
            logger.error(f"Error handling A2A message: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}
```

## TDD実践で直面した課題と解決策

### 課題1: テスト設計の複雑性

**問題**: 非同期処理とストレージの状態管理が複雑

**解決策**: フィクスチャとモックの活用
```python
@pytest.fixture
def task_agent():
    """テスト用TaskAgentインスタンス"""
    storage = InMemoryStorage()
    return TaskAgent(storage=storage)

@pytest.fixture
def sample_tasks():
    """テスト用サンプルタスク"""
    return [
        Task(id="1", title="タスク1", created_at=datetime.now()),
        Task(id="2", title="タスク2", created_at=datetime.now(), completed=True)
    ]
```

### 課題2: エラーハンドリングのテスト

**問題**: 例外ケースの網羅的テストが困難

**解決策**: 例外専用テストクラスとパラメータ化テスト
```python
class TestTaskAgentErrorHandling:
    """TaskAgent エラーハンドリングテスト"""
    
    @pytest.mark.parametrize("invalid_action", [None, "", "invalid", 123])
    def test_invalid_action_handling(self, task_agent, invalid_action):
        """無効なアクションのエラーハンドリング"""
        message = {"action": invalid_action}
        response = task_agent.handle_a2a_message(message)
        assert response["success"] is False
        assert "error" in response
    
    def test_storage_exception_handling(self, task_agent):
        """ストレージ例外のハンドリング"""
        # ストレージエラーをシミュレート
        with patch.object(task_agent.storage, 'create_task', 
                          side_effect=StorageException("Database error")):
            message = {"action": "create", "data": {"title": "Test"}}
            response = task_agent.handle_a2a_message(message)
            assert response["success"] is False
            assert "error" in response
```

### 課題3: 統合テストの実装

**問題**: サーバー・クライアント間のE2Eテストが複雑

**解決策**: TestClientを使った統合テスト
```python
def test_full_workflow_via_api():
    """完全ワークフローのAPIテスト"""
    from fastapi.testclient import TestClient
    from app.a2a.server.app import app
    
    client = TestClient(app)
    
    # タスク作成
    create_response = client.post("/task", json={
        "action": "create",
        "data": {"title": "API経由タスク"}
    })
    assert create_response.status_code == 200
    task_data = create_response.json()
    task_id = task_data["task"]["id"]
    
    # タスク取得
    get_response = client.post("/task", json={
        "action": "get",
        "task_id": task_id
    })
    assert get_response.status_code == 200
    assert get_response.json()["task"]["title"] == "API経由タスク"
```

## TDDがもたらした開発体験の変化

### 1. 設計の明確化

**Before TDD**:
```python
# 曖昧な要件のままコーディング開始
def create_task(data):
    # とりあえず実装...
    pass
```

**After TDD**:
```python
# テストが仕様書として機能
def test_create_task_validates_title_requirement():
    """タスク作成時のタイトル必須バリデーション"""
    # この時点で要件が明確化される
    pass
```

### 2. リファクタリングの安心感

**実例**: ストレージ層のインターフェース変更

```python
# 変更前
class InMemoryStorage:
    def save_task(self, task): pass

# 変更後（メソッド名統一）
class InMemoryStorage(StorageInterface):
    def create_task(self, task): pass
    def update_task(self, task): pass
```

テストがあることで、インターフェース変更による影響範囲が即座に把握でき、安心してリファクタリングを実行できました。

### 3. バグの早期発見

**実例**: 日時シリアライゼーションのバグ

```python
def test_task_serialization_with_none_updated_at():
    """updated_atがNoneの場合のシリアライゼーション"""
    task = Task(id="1", title="Test", created_at=datetime.now())
    # updated_at=None の場合の処理をテスト
    task_dict = task.to_dict()
    assert task_dict["updated_at"] is None  # バグ発見！
```

このテストにより、`updated_at`がNoneの場合にシリアライゼーションエラーが発生するバグを開発初期で発見できました。

## 実装成果とメトリクス

### テストカバレッジ結果
```
app/a2a/core/types.py          100%
app/a2a/core/exceptions.py     100%
app/a2a/storage/memory.py      100%
app/a2a/agents/task_agent.py    92%
app/a2a/skills/task_skills.py   63%
-------------------------------------------
TOTAL                               81%
```

### テスト実行結果
- **総テスト数**: 55個
- **成功率**: 100%（全テスト合格）
- **実行時間**: 0.8秒（高速フィードバック）

### 実装規模
- **コード行数**: 約1,200行
- **テストコード行数**: 約800行
- **テスト/コード比**: 約1:1.5

## 使用例とデモンストレーション

### CLIクライアント操作例

```bash
# サーバー起動
python -m app.a2a.server.app

# タスク作成
python -m app.a2a.client.cli create "買い物に行く" -d "牛乳とパンを買う"
# 出力: Task created successfully: 1a2b3c4d-...

# タスク一覧表示
python -m app.a2a.client.cli list
# 出力:
# Tasks (1 total):
# □ 1a2b3c4d | 買い物に行く | 牛乳とパンを買う

# タスク完了
python -m app.a2a.client.cli toggle 1a2b3c4d
# 出力: Task completion toggled: 1a2b3c4d

# 完了状態確認
python -m app.a2a.client.cli list
# 出力:
# Tasks (1 total):
# ✓ 1a2b3c4d | 買い物に行く | 牛乳とパンを買う
```

### A2AプロトコルAPIの使用例

```python
import requests

# エージェント情報取得
response = requests.get("http://localhost:8000/")
agent_card = response.json()
print(f"Agent: {agent_card['name']}")
print(f"Skills: {[skill['name'] for skill in agent_card['skills']]}")

# A2Aメッセージでタスク作成
a2a_message = {
    "action": "create",
    "data": {"title": "A2A経由タスク", "description": "プロトコル経由で作成"}
}
response = requests.post("http://localhost:8000/a2a/message", json=a2a_message)
result = response.json()
print(f"Created task: {result['data']['task']['title']}")
```

## レッスンラーンドと今後の展望

### TDD実践の教訓

**1. テストファーストの威力**
- 要件の曖昧さが即座に露呈する
- インターフェース設計が自然と洗練される
- コードの結合度が下がり、保守性が向上する

**2. 段階的開発の重要性**
- Core → Storage → Skills → Agents の順序が効果的
- 各層の独立性により、問題の局所化が可能
- 統合時の問題が最小限に抑えられる

**3. テストの品質 = プロダクトの品質**
- テストケースの網羅性がプロダクトの信頼性に直結
- エラーケースのテストが本番環境での安定性を保証
- パフォーマンステストの重要性

### 技術的発見

**1. A2Aプロトコルの実装ポイント**
- エージェントカードの詳細な記述が重要
- スキル定義の構造化が相互運用性を向上させる
- エラーハンドリングの一貫性がプロトコル準拠に必要

**2. Pythonでの型安全プログラミング**
- dataclassと型ヒントの組み合わせが効果的
- Pydanticによるランタイム型検証の価値
- 抽象基底クラス（ABC）による契約プログラミング

### 次のステップ

**短期的改善項目**
1. **テストカバレッジ向上**: 目標95%以上
2. **パフォーマンステスト**: 負荷テストとボトルネック分析
3. **セキュリティ強化**: 認証・認可・入力検証の実装

**中期的発展計画**
1. **マルチエージェント連携**: 複数エージェント間のワークフロー
2. **永続化ストレージ**: PostgreSQL・Redis統合
3. **WebUI実装**: React/Vue.jsによるフロントエンド

**長期的ビジョン**
1. **エージェントマーケットプレイス**: スキル共有プラットフォーム
2. **AI支援開発**: コード生成・テスト自動作成
3. **エンタープライズ対応**: 大規模システム統合

## まとめ

TDD手法によるA2A実装は、技術的な学習だけでなく、**開発プロセス自体の質的変化**をもたらしました。

**テストファーストの文化**は、コードの品質向上だけでなく、**要件定義の明確化**、**設計の洗練**、**チーム内コミュニケーションの向上**といった副次的効果も生み出しています。

A2Aプロトコルという新しい技術領域において、TDDアプローチは**リスクを最小化**しながら**確実に学習を積み重ねる**ための強力な手法であることが実証されました。

今後、このMVPを基盤として、より複雑で実用的なマルチエージェントシステムの開発に取り組んでいく予定です。

---

**次回予告**
次回の記事では、A2A MVPの技術検証結果と実用性評価について詳しく解説します。プロトコルの制約、パフォーマンス特性、セキュリティ考慮事項など、実際の運用を想定した評価結果をお届けします。

---

*本記事のサンプルコードは、GitHubリポジトリで公開予定です。TDD実践の参考資料として、テストコードと併せてご活用ください。*