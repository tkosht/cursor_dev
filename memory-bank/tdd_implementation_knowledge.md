# TDD実装で得られた知識とルール

## 🎯 TDD実践の核心的な学び

### 1. テストファーストの価値

**原則**: テストを書く時点では実装コードは存在しない

**効果**:
- 使いやすいAPIが自然に生まれる
- 実装前に設計の問題に気づける
- 要件の曖昧さが即座に露呈する

**実例**:
```python
# tests/unit/test_core/test_types.py
def test_task_creation_with_required_fields():
    """タスクが必須フィールドで作成できることを確認"""
    # この時点でTaskクラスは存在しない！
    from app.a2a.core.types import Task  # ImportError
    
    task = Task(
        id="task-001",
        title="TDDの記事を書く",
        created_at=datetime.now()
    )
    assert task.completed is False  # デフォルト値も仕様として定義
```

### 2. Red-Green-Refactorサイクルの具体的実装

**実践的なサイクル時間**:
- Red: 5-10分（失敗するテストを書く）
- Green: 10-15分（最小限の実装）
- Refactor: 5-10分（品質向上）
- 合計: 20-35分/サイクル

**重要**: 1日に20-30サイクル回すことで、着実に進歩する

**実装例**: Task型の作成
```python
# Step 1: Red (テストを書く)
def test_task_serialization():
    task = Task(id="1", title="Test", created_at=datetime.now())
    task_dict = task.to_dict()
    assert isinstance(task_dict["created_at"], str)  # ISO形式

# Step 2: Green (最小実装)
@dataclass
class Task:
    id: str
    title: str
    created_at: datetime
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat()
        }

# Step 3: Refactor (改善)
from dataclasses import asdict

def to_dict(self) -> Dict[str, Any]:
    """タスクを辞書形式に変換（JSON変換用）"""
    data = asdict(self)
    # datetimeをISO形式の文字列に変換
    data["created_at"] = self.created_at.isoformat()
    if self.updated_at:
        data["updated_at"] = self.updated_at.isoformat()
    return data
```

### 3. テストの粒度と構成

**推奨される構成**:
- ユニットテスト: 70%
- 統合テスト: 20%
- E2Eテスト: 10%

**カバレッジ目標**:
- 全体: 85%以上
- コアロジック: 95%以上
- ユーティリティ: 80%以上

**実際のテストファイル構成**:
```
tests/
├── unit/
│   ├── test_core/
│   │   ├── test_types.py         # 17 tests
│   │   └── test_exceptions.py    # 5 tests
│   ├── test_storage/
│   │   ├── test_interface.py     # 3 tests
│   │   └── test_memory.py        # 12 tests
│   ├── test_skills/
│   │   └── test_task_skills.py   # 25 tests
│   └── test_agents/
│       └── test_task_agent.py    # 15 tests
└── integration/
    └── test_server/
        └── test_app.py           # 7 tests
```

## 🏗️ アーキテクチャ設計のルール

### 1. 層構造の原則と実装

```
依存関係の方向（単方向のみ）:
core → なし
storage → core
skills → core, storage
agents → core, storage, skills
server → agents
```

**ルール**: 下位層は上位層を知らない

**実装例**: StorageInterfaceの定義
```python
# app/a2a/storage/interface.py
from abc import ABC, abstractmethod
from typing import List
from app.a2a.core.types import Task  # coreのみに依存

class StorageInterface(ABC):
    @abstractmethod
    def create_task(self, task: Task) -> Task:
        pass
    
    @abstractmethod
    def get_task(self, task_id: str) -> Task:
        pass
    
    # skillsやagentsは知らない！
```

### 2. インターフェース駆動設計の実装

**必須事項**:
- 各層の境界にインターフェースを定義
- 実装より先にインターフェースをテスト
- モックを使った独立したテスト

**テスト例**:
```python
# tests/unit/test_storage/test_interface.py
def test_storage_interface_is_abstract():
    """インターフェースが抽象クラスであることを確認"""
    from app.a2a.storage.interface import StorageInterface
    
    # 直接インスタンス化できない
    with pytest.raises(TypeError):
        StorageInterface()
    
    # 必要なメソッドが定義されている
    assert hasattr(StorageInterface, 'create_task')
    assert hasattr(StorageInterface, 'get_task')
```

### 3. エラーハンドリング戦略の実装

**原則**:
- ビジネスロジック層でエラーを処理
- 上位層には成功/失敗の結果型で返す
- 例外は予期しないエラーのみ

**実装例**: TaskSkillのエラーハンドリング
```python
# app/a2a/skills/task_skills.py
def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # バリデーション（ビジネスロジック）
        if 'title' not in data or not data['title'].strip():
            return {"success": False, "error": "Title is required"}
        
        if len(data['title']) > 200:
            return {"success": False, "error": "Title is too long (max 200)"}
        
        # タスク作成
        task = Task(
            id=str(uuid.uuid4()),
            title=data['title'].strip(),
            created_at=datetime.now()
        )
        created_task = self.storage.create_task(task)
        return {"success": True, "task": created_task.to_dict()}
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return {"success": False, "error": str(e)}
```

## 🔧 実装パターン

### 1. アクションマップパターンの実装

**問題**: 複雑な条件分岐（if-elif地獄）でFlake8 C901エラー

**解決策の実装**:
```python
# app/a2a/agents/task_agent.py
class TaskAgent(BaseAgent):
    def __init__(self, storage: StorageInterface):
        self.storage = storage
        self.task_skill = TaskSkill(storage)
        # 起動時にマップを作成（効率的）
        self._action_map = {
            "create": lambda r: self.task_skill.create_task(r.data or {}),
            "get": lambda r: self.task_skill.get_task(r.task_id),
            "list": lambda r: self.task_skill.list_tasks(),
            "update": lambda r: self.task_skill.update_task(
                r.task_id, r.data or {}
            ),
            "delete": lambda r: self.task_skill.delete_task(r.task_id),
            "toggle": lambda r: self.task_skill.toggle_completion(r.task_id),
            "clear": lambda r: self.task_skill.clear_all_tasks(),
        }
    
    def _execute_action(self, request: TaskRequest) -> Dict[str, Any]:
        """アクション実行（複雑度を下げる）"""
        action_func = self._action_map.get(request.action)
        if not action_func:
            return {"success": False, "error": f"Invalid action: {request.action}"}
        return action_func(request)
```

### 2. フィクスチャの活用パターン

**推奨フィクスチャの実装**:
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock
from datetime import datetime

@pytest.fixture
def mock_storage():
    """モックストレージ（全テストで使用）"""
    from app.a2a.storage.interface import StorageInterface
    return Mock(spec=StorageInterface)

@pytest.fixture
def sample_task():
    """サンプルタスク（頻繁に使用）"""
    from app.a2a.core.types import Task
    return Task(
        id="test-001",
        title="テストタスク",
        created_at=datetime.now(),
        description="これはテスト用のタスクです"
    )

@pytest.fixture
def task_agent(mock_storage):
    """エージェントインスタンス（統合テスト用）"""
    from app.a2a.agents.task_agent import TaskAgent
    return TaskAgent(storage=mock_storage)
```

### 3. パラメトリックテストの実装

**エッジケースの網羅**:
```python
# tests/unit/test_skills/test_task_skills.py
@pytest.mark.parametrize("invalid_title,expected_error", [
    (None, "title is required"),
    ("", "title is required"),
    ("  ", "title is required"),
    ("x" * 201, "too long"),
])
def test_create_task_with_invalid_titles(
    task_skill, invalid_title, expected_error
):
    """無効なタイトルのテスト"""
    result = task_skill.create_task({"title": invalid_title})
    assert result["success"] is False
    assert expected_error in result["error"].lower()
```

## 📊 品質管理のルール

### 1. 品質ゲートチェックの実装

**scripts/quality_gate_check.py の実装**:
```python
#!/usr/bin/env python3
import subprocess
import sys

def run_command(cmd):
    """コマンド実行と結果チェック"""
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result.returncode, result.stdout.decode()

def main():
    print("🚀 Running quality gate checks...\n")
    
    # 1. Tests with coverage
    print("🧪 Running tests...")
    code, output = run_command(
        "pytest --cov=app --cov-fail-under=85 -v"
    )
    if code != 0:
        print("❌ Tests failed!")
        return 1
    print("✅ Tests passed with coverage >= 85%")
    
    # 2. Flake8
    print("\n🔍 Checking code quality...")
    code, output = run_command("flake8 app/ tests/")
    if code != 0:
        print("❌ Flake8 violations found!")
        return 1
    print("✅ Flake8: No violations")
    
    # 3. Black
    code, output = run_command("black --check app/ tests/")
    if code != 0:
        print("❌ Black formatting issues!")
        return 1
    print("✅ Black: Properly formatted")
    
    print("\n✅ All quality gates passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 2. CI/CDのベストプラクティス実装

**.github/workflows/ci.yml**:
```yaml
name: CI
on:
  push:
    branches: [main, develop, feature/*]
    paths:
      - 'app/**'
      - 'tests/**'
      - 'pyproject.toml'
      - '.github/workflows/ci.yml'

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pypoetry
            ~/.cache/pip
          key: ${{ runner.os }}-poetry-${{ hashFiles('**/poetry.lock') }}
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Run quality checks
        run: |
          poetry run flake8 app/ tests/
          poetry run black --check app/ tests/
          poetry run pytest --cov=app --cov-fail-under=85
```

### 3. コード複雑度の管理

**Flake8設定 (.flake8)**:
```ini
[flake8]
max-line-length = 79
max-complexity = 10
exclude = 
    .git,
    __pycache__,
    .venv,
    build,
    dist
per-file-ignores =
    __init__.py:F401
```

## 🚀 パフォーマンス最適化の実装

### 1. 事前計算とキャッシュ

**実装例**:
```python
class TaskAgent(BaseAgent):
    def __init__(self, storage: StorageInterface):
        # 起動時に一度だけ作成
        self._action_map = self._create_action_map()
        self._validators = self._create_validators()
        self._cache = {}
        
    def _create_action_map(self):
        """アクションマップを事前作成"""
        return {
            "create": self._handle_create,
            "get": self._handle_get,
            # ...
        }
```

### 2. 非同期処理の活用

**実装予定のパターン**:
```python
import asyncio
from typing import List

async def handle_multiple_agents(messages: List[Dict]):
    """複数エージェントへの同時リクエスト"""
    tasks = [
        agent.handle_message_async(msg) 
        for agent, msg in messages
    ]
    return await asyncio.gather(*tasks)
```

## 🔒 セキュリティルールの実装

### 1. 入力検証の実装

**Pydanticを使った検証（将来実装）**:
```python
from pydantic import BaseModel, Field, validator

class TaskCreateModel(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        # SQLインジェクション対策
        if re.search(r'[;\'"\\]', v):
            raise ValueError('Title contains invalid characters')
        return v.strip()
```

### 2. エラー情報の制限

**実装済みのパターン**:
```python
try:
    # 詳細な処理
    result = self.storage.create_task(task)
except TaskAlreadyExistsException as e:
    logger.error(f"Task already exists: {task.id}")  # ログには詳細
    return {"success": False, "error": "Task already exists"}  # ユーザーには最小限
except Exception as e:
    logger.exception("Unexpected error in create_task")  # スタックトレース
    return {"success": False, "error": "Internal error"}  # 一般的なエラー
```

### 3. レート制限（将来実装）

**実装予定**:
```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=100, window=timedelta(minutes=1)):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = datetime.now()
        # ウィンドウ外のリクエストを削除
        self.requests[client_id] = [
            req for req in self.requests[client_id]
            if now - req < self.window
        ]
        
        if len(self.requests[client_id]) >= self.max_requests:
            return False
            
        self.requests[client_id].append(now)
        return True
```

## 📝 ドキュメンテーション

### 1. テストがドキュメント

**原則**: テスト名で仕様を表現

```python
class TestTaskSkills:
    def test_create_task_with_valid_data_returns_success(self):
        """有効なデータでタスク作成すると成功を返す"""
        
    def test_create_task_without_title_returns_error(self):
        """タイトルなしでタスク作成するとエラーを返す"""
        
    def test_toggle_completion_changes_task_state(self):
        """完了状態の切り替えがタスクの状態を変更する"""
```

### 2. コメントの最小化

**ルール**:
- コードで意図を表現
- コメントは「なぜ」を説明（「何を」ではない）
- 複雑なビジネスロジックのみコメント

## 🎓 チーム開発への適用

### 1. ペアプログラミング推奨

**TDDとの相性**:
- 1人がテストを書き、もう1人が実装
- 役割を交代しながら進める
- レビューが自然に組み込まれる

### 2. 継続的な改善

**メトリクス収集**:
```bash
# カバレッジレポート生成
pytest --cov=app --cov-report=html --cov-report=term-missing

# 複雑度チェック
flake8 app/ --max-complexity=10 --show-source

# 実行時間測定
pytest --durations=10
```

### 3. 知識共有

**推奨事項**:
- 週次でTDD勉強会
- 失敗事例の共有
- ベストプラクティスの更新

## 🔄 継続的な学習

### 次のステップ

1. **プロパティベーステスト**: hypothesis導入
   ```python
   from hypothesis import given, strategies as st
   
   @given(st.text(min_size=1, max_size=200))
   def test_create_task_with_any_valid_title(title):
       result = create_task({"title": title})
       assert result["success"] is True
   ```

2. **ミューテーションテスト**: テストの品質確認
3. **パフォーマンステスト**: 自動化された性能測定
4. **カオステスト**: 障害注入による堅牢性確認

---

*このドキュメントは、A2A MVP実装プロジェクトでの実践経験に基づいています。実際のコード例とともに、再現可能な形で記録しています。*