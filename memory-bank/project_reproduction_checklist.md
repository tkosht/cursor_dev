# プロジェクト再現チェックリスト

## 🎯 目的
このチェックリストは、ゼロベースから現在のプロジェクト（91.77%カバレッジ、84テスト）と同等品質のシステムを再現するための完全ガイドです。

## 📋 再現手順

### Phase 1: 環境構築（30分）

#### 1.1 プロジェクト初期化
```bash
# プロジェクトディレクトリ作成
mkdir a2a-mvp && cd a2a-mvp

# Poetry初期化
poetry init --name a2a-mvp --python "^3.10"

# 依存関係追加
poetry add pytest pytest-cov pytest-mock black flake8 isort mypy
poetry add fastapi uvicorn pydantic
```

#### 1.2 プロジェクト構造作成
```bash
# ディレクトリ構造作成
mkdir -p app/a2a_mvp/{core,storage,skills,agents,server}
mkdir -p tests/{unit/{test_core,test_storage,test_skills,test_agents},integration/test_server}
mkdir -p scripts docs memory-bank .github/workflows

# __init__.pyファイル作成
touch app/__init__.py
touch app/a2a_mvp/__init__.py
touch app/a2a_mvp/{core,storage,skills,agents,server}/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/unit/{test_core,test_storage,test_skills,test_agents}/__init__.py
```

#### 1.3 設定ファイル作成

**.flake8**:
```ini
[flake8]
max-line-length = 79
max-complexity = 10
exclude = .git,__pycache__,.venv,build,dist
per-file-ignores = __init__.py:F401
```

**pyproject.toml**:
```toml
[tool.black]
line-length = 79

[tool.isort]
profile = "black"
line_length = 79

[tool.coverage.run]
source = ["app"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
fail_under = 85
show_missing = true
```

### Phase 2: Core層実装（1時間）

#### 2.1 型定義（TDD: Red → Green → Refactor）

**Step 1: テスト作成** (`tests/unit/test_core/test_types.py`)
```python
import pytest
from datetime import datetime

def test_task_creation_with_required_fields():
    """Task作成テスト - この時点でTaskは存在しない"""
    from app.a2a_mvp.core.types import Task  # ImportError!
    
    task = Task(
        id="task-001",
        title="TDDタスク",
        created_at=datetime.now()
    )
    assert task.id == "task-001"
    assert task.title == "TDDタスク"
    assert task.completed is False  # デフォルト値
```

**Step 2: 最小実装** (`app/a2a_mvp/core/types.py`)
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    id: str
    title: str
    created_at: datetime
    completed: bool = False
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
```

**Step 3: リファクタリング**
```python
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, Optional

@dataclass
class Task:
    """タスクエンティティ"""
    id: str
    title: str
    created_at: datetime
    completed: bool = False
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """JSON変換用"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            data["updated_at"] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """JSONから復元"""
        if isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at") and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)
```

#### 2.2 リクエスト/レスポンス型

**テスト** (`tests/unit/test_core/test_types.py` に追加):
```python
def test_task_request_creation():
    from app.a2a_mvp.core.types import TaskRequest
    
    request = TaskRequest(action="create", data={"title": "Test"})
    assert request.action == "create"
    assert request.data == {"title": "Test"}
    assert request.task_id is None
```

**実装** (`app/a2a_mvp/core/types.py` に追加):
```python
@dataclass
class TaskRequest:
    """A2Aリクエスト"""
    action: str
    data: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None

@dataclass
class TaskResponse:
    """A2Aレスポンス"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

#### 2.3 例外定義

**実装** (`app/a2a_mvp/core/exceptions.py`):
```python
class TaskNotFoundException(Exception):
    """タスクが見つからない"""
    pass

class TaskAlreadyExistsException(Exception):
    """タスクが既に存在する"""
    pass
```

### Phase 3: Storage層実装（1時間）

#### 3.1 インターフェース定義

**テスト** (`tests/unit/test_storage/test_interface.py`):
```python
import pytest

def test_storage_interface_is_abstract():
    from app.a2a_mvp.storage.interface import StorageInterface
    
    with pytest.raises(TypeError):
        StorageInterface()
    
    assert hasattr(StorageInterface, 'create_task')
    assert hasattr(StorageInterface, 'get_task')
    assert hasattr(StorageInterface, 'get_all_tasks')
    assert hasattr(StorageInterface, 'update_task')
    assert hasattr(StorageInterface, 'delete_task')
```

**実装** (`app/a2a_mvp/storage/interface.py`):
```python
from abc import ABC, abstractmethod
from typing import List
from app.a2a_mvp.core.types import Task

class StorageInterface(ABC):
    @abstractmethod
    def create_task(self, task: Task) -> Task:
        pass
    
    @abstractmethod
    def get_task(self, task_id: str) -> Task:
        pass
    
    @abstractmethod
    def get_all_tasks(self) -> List[Task]:
        pass
    
    @abstractmethod
    def update_task(self, task: Task) -> Task:
        pass
    
    @abstractmethod
    def delete_task(self, task_id: str) -> None:
        pass
```

#### 3.2 InMemoryStorage実装

**包括的テスト** (`tests/unit/test_storage/test_memory.py`):
```python
import pytest
from datetime import datetime

class TestInMemoryStorage:
    @pytest.fixture
    def storage(self):
        from app.a2a_mvp.storage.memory import InMemoryStorage
        return InMemoryStorage()
    
    @pytest.fixture
    def sample_task(self):
        from app.a2a_mvp.core.types import Task
        return Task(
            id="test-001",
            title="テストタスク",
            created_at=datetime.now()
        )
    
    def test_create_and_retrieve_task(self, storage, sample_task):
        created = storage.create_task(sample_task)
        assert created.id == sample_task.id
        
        retrieved = storage.get_task(sample_task.id)
        assert retrieved == created
    
    def test_create_duplicate_raises_error(self, storage, sample_task):
        storage.create_task(sample_task)
        
        with pytest.raises(ValueError, match="already exists"):
            storage.create_task(sample_task)
    
    def test_get_nonexistent_raises_error(self, storage):
        from app.a2a_mvp.core.exceptions import TaskNotFoundException
        
        with pytest.raises(TaskNotFoundException):
            storage.get_task("nonexistent")
    
    def test_update_task(self, storage, sample_task):
        storage.create_task(sample_task)
        
        sample_task.title = "更新済み"
        updated = storage.update_task(sample_task)
        
        assert updated.title == "更新済み"
        assert storage.get_task(sample_task.id).title == "更新済み"
    
    def test_delete_task(self, storage, sample_task):
        storage.create_task(sample_task)
        storage.delete_task(sample_task.id)
        
        from app.a2a_mvp.core.exceptions import TaskNotFoundException
        with pytest.raises(TaskNotFoundException):
            storage.get_task(sample_task.id)
    
    def test_get_all_tasks(self, storage):
        from app.a2a_mvp.core.types import Task
        
        tasks = [
            Task(id=f"task-{i}", title=f"タスク{i}", created_at=datetime.now())
            for i in range(3)
        ]
        
        for task in tasks:
            storage.create_task(task)
        
        all_tasks = storage.get_all_tasks()
        assert len(all_tasks) == 3
        assert all(t in all_tasks for t in tasks)
```

**実装** (`app/a2a_mvp/storage/memory.py`):
```python
from typing import Dict, List
from app.a2a_mvp.core.exceptions import TaskNotFoundException
from app.a2a_mvp.core.types import Task
from app.a2a_mvp.storage.interface import StorageInterface

class InMemoryStorage(StorageInterface):
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
    
    def create_task(self, task: Task) -> Task:
        if task.id in self._tasks:
            raise ValueError(f"Task with id {task.id} already exists")
        self._tasks[task.id] = task
        return task
    
    def get_task(self, task_id: str) -> Task:
        if task_id not in self._tasks:
            raise TaskNotFoundException(f"Task not found: {task_id}")
        return self._tasks[task_id]
    
    def get_all_tasks(self) -> List[Task]:
        return list(self._tasks.values())
    
    def update_task(self, task: Task) -> Task:
        if task.id not in self._tasks:
            raise TaskNotFoundException(f"Task not found: {task.id}")
        self._tasks[task.id] = task
        return task
    
    def delete_task(self, task_id: str) -> None:
        if task_id not in self._tasks:
            raise TaskNotFoundException(f"Task not found: {task_id}")
        del self._tasks[task_id]
```

### Phase 4: Skills層実装（2時間）

#### 4.1 BaseSkill定義

**実装** (`app/a2a_mvp/skills/base.py`):
```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseSkill(ABC):
    @abstractmethod
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        pass
```

#### 4.2 TaskSkill実装

**包括的テスト** (`tests/unit/test_skills/test_task_skills.py`):
```python
import pytest
from unittest.mock import Mock
from datetime import datetime

class TestTaskSkills:
    @pytest.fixture
    def mock_storage(self):
        from app.a2a_mvp.storage.interface import StorageInterface
        return Mock(spec=StorageInterface)
    
    @pytest.fixture
    def task_skill(self, mock_storage):
        from app.a2a_mvp.skills.task_skills import TaskSkill
        return TaskSkill(mock_storage)
    
    def test_create_task_success(self, task_skill, mock_storage):
        from app.a2a_mvp.core.types import Task
        
        # モック設定
        mock_task = Task(
            id="generated-id",
            title="テスト",
            created_at=datetime.now()
        )
        mock_storage.create_task.return_value = mock_task
        
        # 実行
        result = task_skill.create_task({"title": "テスト"})
        
        # 検証
        assert result["success"] is True
        assert result["task"]["title"] == "テスト"
        mock_storage.create_task.assert_called_once()
    
    def test_create_task_validation_errors(self, task_skill, mock_storage):
        # タイトルなし
        result = task_skill.create_task({})
        assert result["success"] is False
        assert "title" in result["error"].lower()
        
        # 空タイトル
        result = task_skill.create_task({"title": "  "})
        assert result["success"] is False
        
        # 長すぎるタイトル
        result = task_skill.create_task({"title": "x" * 201})
        assert result["success"] is False
        assert "too long" in result["error"].lower()
    
    def test_toggle_completion(self, task_skill, mock_storage):
        from app.a2a_mvp.core.types import Task
        
        task = Task(
            id="task-123",
            title="既存タスク",
            created_at=datetime.now(),
            completed=False
        )
        mock_storage.get_task.return_value = task
        mock_storage.update_task.return_value = task
        
        result = task_skill.toggle_completion("task-123")
        
        assert result["success"] is True
        assert mock_storage.update_task.called
        updated_task = mock_storage.update_task.call_args[0][0]
        assert updated_task.completed is True
        assert updated_task.updated_at is not None
    
    def test_error_handling(self, task_skill, mock_storage):
        mock_storage.create_task.side_effect = Exception("DB error")
        
        result = task_skill.create_task({"title": "エラーテスト"})
        
        assert result["success"] is False
        assert "DB error" in result["error"]
    
    # execute メソッドのテスト（カバレッジ向上）
    @pytest.mark.parametrize("action,expected_method", [
        ("create", "create_task"),
        ("get", "get_task"),
        ("list", "list_tasks"),
        ("update", "update_task"),
        ("delete", "delete_task"),
        ("toggle", "toggle_completion"),
        ("clear", "clear_all_tasks"),
    ])
    def test_execute_routes_to_correct_method(
        self, task_skill, action, expected_method
    ):
        # メソッドをモック
        setattr(task_skill, expected_method, Mock(return_value={"success": True}))
        
        request = {"action": action}
        if action in ["get", "update", "delete", "toggle"]:
            request["task_id"] = "test-id"
        if action in ["create", "update"]:
            request["data"] = {"title": "Test"}
        
        result = task_skill.execute(request)
        
        assert result["success"] is True
        getattr(task_skill, expected_method).assert_called_once()
```

**実装** (`app/a2a_mvp/skills/task_skills.py`):
```python
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

from app.a2a_mvp.core.types import Task
from app.a2a_mvp.core.exceptions import TaskNotFoundException
from app.a2a_mvp.storage.interface import StorageInterface
from app.a2a_mvp.skills.base import BaseSkill

logger = logging.getLogger(__name__)

class TaskSkill(BaseSkill):
    def __init__(self, storage: StorageInterface):
        self.storage = storage
    
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """リクエストを適切なメソッドにルーティング"""
        action = request.get("action")
        
        action_map = {
            "create": lambda: self.create_task(request.get("data", {})),
            "get": lambda: self.get_task(request.get("task_id")),
            "list": lambda: self.list_tasks(),
            "update": lambda: self.update_task(
                request.get("task_id"), request.get("data", {})
            ),
            "delete": lambda: self.delete_task(request.get("task_id")),
            "toggle": lambda: self.toggle_completion(request.get("task_id")),
            "clear": lambda: self.clear_all_tasks(),
        }
        
        handler = action_map.get(action)
        if not handler:
            return {"success": False, "error": f"Unknown action: {action}"}
        
        return handler()
    
    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # バリデーション
            if 'title' not in data or not data['title'].strip():
                return {"success": False, "error": "Title is required"}
            
            title = data['title'].strip()
            if len(title) > 200:
                return {"success": False, "error": "Title is too long (max 200)"}
            
            # タスク作成
            task = Task(
                id=str(uuid.uuid4()),
                title=title,
                description=data.get('description', '').strip() or None,
                created_at=datetime.now()
            )
            
            created_task = self.storage.create_task(task)
            return {"success": True, "task": created_task.to_dict()}
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return {"success": False, "error": str(e)}
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        try:
            if not task_id:
                return {"success": False, "error": "Task ID is required"}
            
            task = self.storage.get_task(task_id)
            return {"success": True, "task": task.to_dict()}
            
        except TaskNotFoundException:
            return {"success": False, "error": f"Task not found: {task_id}"}
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return {"success": False, "error": str(e)}
    
    def list_tasks(self) -> Dict[str, Any]:
        try:
            tasks = self.storage.get_all_tasks()
            return {
                "success": True,
                "tasks": [task.to_dict() for task in tasks],
                "count": len(tasks)
            }
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return {"success": False, "error": str(e)}
    
    def update_task(self, task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not task_id:
                return {"success": False, "error": "Task ID is required"}
            
            task = self.storage.get_task(task_id)
            
            # 更新
            if 'title' in data:
                title = data['title'].strip()
                if not title:
                    return {"success": False, "error": "Title cannot be empty"}
                if len(title) > 200:
                    return {"success": False, "error": "Title is too long"}
                task.title = title
            
            if 'description' in data:
                task.description = data['description'].strip() or None
            
            if 'completed' in data:
                task.completed = bool(data['completed'])
            
            task.updated_at = datetime.now()
            
            updated_task = self.storage.update_task(task)
            return {"success": True, "task": updated_task.to_dict()}
            
        except TaskNotFoundException:
            return {"success": False, "error": f"Task not found: {task_id}"}
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        try:
            if not task_id:
                return {"success": False, "error": "Task ID is required"}
            
            self.storage.delete_task(task_id)
            return {"success": True, "message": "Task deleted successfully"}
            
        except TaskNotFoundException:
            return {"success": False, "error": f"Task not found: {task_id}"}
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return {"success": False, "error": str(e)}
    
    def toggle_completion(self, task_id: str) -> Dict[str, Any]:
        try:
            if not task_id:
                return {"success": False, "error": "Task ID is required"}
            
            task = self.storage.get_task(task_id)
            task.completed = not task.completed
            task.updated_at = datetime.now()
            
            updated_task = self.storage.update_task(task)
            return {"success": True, "task": updated_task.to_dict()}
            
        except TaskNotFoundException:
            return {"success": False, "error": f"Task not found: {task_id}"}
        except Exception as e:
            logger.error(f"Error toggling task: {e}")
            return {"success": False, "error": str(e)}
    
    def clear_all_tasks(self) -> Dict[str, Any]:
        try:
            tasks = self.storage.get_all_tasks()
            for task in tasks:
                self.storage.delete_task(task.id)
            
            return {
                "success": True,
                "message": f"Cleared {len(tasks)} tasks"
            }
        except Exception as e:
            logger.error(f"Error clearing tasks: {e}")
            return {"success": False, "error": str(e)}
```

### Phase 5: Agent層実装（1.5時間）

#### 5.1 BaseAgent定義

**実装** (`app/a2a_mvp/agents/base.py`):
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    @abstractmethod
    def get_agent_card(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def process_request(self, request: Any) -> Any:
        pass
```

#### 5.2 TaskAgent実装

**テスト** (`tests/unit/test_agents/test_task_agent.py`):
```python
import pytest
from unittest.mock import Mock

class TestTaskAgent:
    @pytest.fixture
    def mock_storage(self):
        from app.a2a_mvp.storage.interface import StorageInterface
        return Mock(spec=StorageInterface)
    
    @pytest.fixture
    def task_agent(self, mock_storage):
        from app.a2a_mvp.agents.task_agent import TaskAgent
        return TaskAgent(mock_storage)
    
    def test_get_agent_card(self, task_agent):
        card = task_agent.get_agent_card()
        
        assert card["name"] == "Task Manager Agent"
        assert card["version"] == "1.0.0"
        assert len(card["skills"]) > 0
        
        create_skill = next(
            s for s in card["skills"] if s["id"] == "create_task"
        )
        assert create_skill["name"] == "Create Task"
        assert "task" in create_skill["tags"]
    
    def test_process_request_create(self, task_agent):
        from app.a2a_mvp.core.types import TaskRequest
        
        request = TaskRequest(
            action="create",
            data={"title": "テストタスク"}
        )
        
        response = task_agent.process_request(request)
        
        assert response.success is True
        assert response.data is not None
    
    def test_process_request_invalid_action(self, task_agent):
        from app.a2a_mvp.core.types import TaskRequest
        
        request = TaskRequest(action="invalid")
        response = task_agent.process_request(request)
        
        assert response.success is False
        assert "Invalid action" in response.error
    
    def test_process_request_error_handling(self, task_agent):
        from app.a2a_mvp.core.types import TaskRequest
        
        # エラーを発生させる
        task_agent.task_skill.create_task = Mock(
            side_effect=Exception("Test error")
        )
        
        request = TaskRequest(
            action="create",
            data={"title": "エラーテスト"}
        )
        
        response = task_agent.process_request(request)
        
        assert response.success is False
        assert "Internal error" in response.error
```

**実装** (`app/a2a_mvp/agents/task_agent.py`):
```python
import logging
from typing import Dict, Any

from app.a2a_mvp.core.types import TaskRequest, TaskResponse
from app.a2a_mvp.skills.task_skills import TaskSkill
from app.a2a_mvp.storage.interface import StorageInterface
from app.a2a_mvp.agents.base import BaseAgent

logger = logging.getLogger(__name__)

class TaskAgent(BaseAgent):
    def __init__(self, storage: StorageInterface):
        self.storage = storage
        self.task_skill = TaskSkill(storage)
        
        # アクションマップ（複雑度削減）
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
    
    def get_agent_card(self) -> Dict[str, Any]:
        return {
            "name": "Task Manager Agent",
            "version": "1.0.0",
            "description": "Manages TODO tasks with full CRUD operations",
            "capabilities": {
                "request_response": True,
                "streaming": False,
                "batch": True
            },
            "skills": [
                {
                    "id": "create_task",
                    "name": "Create Task",
                    "description": "Create a new TODO task",
                    "tags": ["task", "create", "todo", "productivity"],
                    "examples": [
                        "Create a task to buy groceries",
                        "Add a reminder to call mom"
                    ]
                },
                {
                    "id": "list_tasks",
                    "name": "List Tasks",
                    "description": "Get all tasks with their status",
                    "tags": ["task", "list", "todo", "view"],
                    "examples": [
                        "Show me all my tasks",
                        "What tasks do I have?"
                    ]
                },
                {
                    "id": "update_task",
                    "name": "Update Task",
                    "description": "Update task details",
                    "tags": ["task", "update", "edit", "modify"],
                    "examples": ["Update task title", "Change task description"]
                },
                {
                    "id": "delete_task",
                    "name": "Delete Task",
                    "description": "Remove a task permanently",
                    "tags": ["task", "delete", "remove"],
                    "examples": ["Delete completed task", "Remove task"]
                },
                {
                    "id": "toggle_completion",
                    "name": "Toggle Task Completion",
                    "description": "Mark task as complete/incomplete",
                    "tags": ["task", "complete", "toggle", "done"],
                    "examples": ["Mark task as done", "Toggle task completion"]
                },
                {
                    "id": "get_task",
                    "name": "Get Task Details",
                    "description": "Get specific task information",
                    "tags": ["task", "get", "details", "info"],
                    "examples": ["Get task details", "Show task information"]
                },
                {
                    "id": "clear_tasks",
                    "name": "Clear All Tasks",
                    "description": "Remove all tasks at once",
                    "tags": ["task", "clear", "remove", "all"],
                    "examples": ["Clear all tasks", "Delete everything"]
                }
            ]
        }
    
    def process_request(self, request: TaskRequest) -> TaskResponse:
        try:
            # アクション実行
            result = self._execute_action(request)
            
            if not result["success"]:
                return TaskResponse(
                    success=False,
                    error=result.get("error", "Unknown error")
                )
            
            return TaskResponse(
                success=True,
                data=self._format_response_data(result, request.action)
            )
            
        except Exception as e:
            logger.exception("Error processing request")
            return TaskResponse(
                success=False,
                error=f"Internal error: {str(e)}"
            )
    
    def _execute_action(self, request: TaskRequest) -> Dict[str, Any]:
        """アクション実行（複雑度削減）"""
        action_func = self._action_map.get(request.action)
        if not action_func:
            return {"success": False, "error": f"Invalid action: {request.action}"}
        return action_func(request)
    
    def _format_response_data(
        self, result: Dict[str, Any], action: str
    ) -> Dict[str, Any]:
        """レスポンスデータのフォーマット"""
        if action == "list":
            return {
                "tasks": result.get("tasks", []),
                "count": result.get("count", 0)
            }
        elif action in ["delete", "clear"]:
            return {"message": result.get("message", "Operation completed")}
        else:
            return {"task": result.get("task", {})}
```

### Phase 6: Server層実装（1時間）

#### 6.1 FastAPIサーバー

**テスト** (`tests/integration/test_server/test_app.py`):
```python
import pytest
from fastapi.testclient import TestClient

class TestFastAPIServer:
    @pytest.fixture
    def client(self):
        from app.a2a_mvp.server.app import app
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Task Manager Agent"
        assert "skills" in data
    
    def test_task_endpoint_create(self, client):
        response = client.post("/task", json={
            "action": "create",
            "data": {"title": "APIテスト"}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["task"]["title"] == "APIテスト"
    
    def test_complete_lifecycle(self, client):
        # 作成
        create_resp = client.post("/task", json={
            "action": "create",
            "data": {"title": "ライフサイクルテスト"}
        })
        task_id = create_resp.json()["data"]["task"]["id"]
        
        # 取得
        get_resp = client.post("/task", json={
            "action": "get",
            "task_id": task_id
        })
        assert get_resp.json()["data"]["task"]["completed"] is False
        
        # 完了切り替え
        toggle_resp = client.post("/task", json={
            "action": "toggle",
            "task_id": task_id
        })
        assert toggle_resp.json()["data"]["task"]["completed"] is True
        
        # 削除
        delete_resp = client.post("/task", json={
            "action": "delete",
            "task_id": task_id
        })
        assert delete_resp.json()["success"] is True
    
    def test_error_handling(self, client):
        response = client.post("/task", json={
            "action": "invalid_action"
        })
        
        assert response.status_code == 500
        assert "Invalid action" in response.json()["detail"]
```

**実装** (`app/a2a_mvp/server/app.py`):
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.a2a_mvp.agents.task_agent import TaskAgent
from app.a2a_mvp.storage.memory import InMemoryStorage
from app.a2a_mvp.core.types import TaskRequest

app = FastAPI(
    title="A2A Task Manager",
    version="1.0.0",
    description="Task management agent following A2A protocol"
)

# グローバルインスタンス（シンプルさのため）
storage = InMemoryStorage()
agent = TaskAgent(storage)

class TaskRequestModel(BaseModel):
    action: str
    data: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None

@app.get("/")
async def get_agent_card():
    """エージェントカードを返す"""
    return agent.get_agent_card()

@app.post("/task")
async def handle_task_request(request: TaskRequestModel):
    """タスクリクエストを処理"""
    task_request = TaskRequest(
        action=request.action,
        data=request.data,
        task_id=request.task_id
    )
    
    response = agent.process_request(task_request)
    
    if not response.success:
        raise HTTPException(status_code=500, detail=response.error)
    
    return {
        "success": response.success,
        "data": response.data,
        "error": response.error
    }

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "service": "A2A Task Manager"}
```

### Phase 7: 品質管理設定（30分）

#### 7.1 品質ゲートスクリプト

**実装** (`scripts/quality_gate_check.py`):
```python
#!/usr/bin/env python3
import subprocess
import sys

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result.returncode, result.stdout.decode()

def main():
    print("🚀 Running quality gate checks...\n")
    
    # Tests
    print("🧪 Running tests...")
    code, _ = run_command("pytest --cov=app --cov-fail-under=85 -v")
    if code != 0:
        print("❌ Tests failed!")
        return 1
    print("✅ Tests passed with coverage >= 85%")
    
    # Flake8
    print("\n🔍 Checking code quality...")
    code, _ = run_command("flake8 app/ tests/")
    if code != 0:
        print("❌ Flake8 violations found!")
        return 1
    print("✅ Flake8: No violations")
    
    # Black
    code, _ = run_command("black --check app/ tests/")
    if code != 0:
        print("❌ Black formatting issues!")
        return 1
    print("✅ Black: Properly formatted")
    
    # isort
    code, _ = run_command("isort --check app/ tests/")
    if code != 0:
        print("❌ Import sorting issues!")
        return 1
    print("✅ isort: Properly sorted")
    
    print("\n✅ All quality gates passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

#### 7.2 CI/CD設定

**実装** (`.github/workflows/ci.yml`):
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
  pull_request:
    branches: [main]

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
      
      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH
      
      - name: Install dependencies
        run: poetry install --no-interaction
      
      - name: Run linters
        run: |
          poetry run flake8 app/ tests/
          poetry run black --check app/ tests/
          poetry run isort --check app/ tests/
      
      - name: Type checking
        run: poetry run mypy app/ --ignore-missing-imports
      
      - name: Run tests with coverage
        run: |
          poetry run pytest tests/ \
            --cov=app \
            --cov-report=xml \
            --cov-report=term-missing \
            --cov-fail-under=85 \
            -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

#### 7.3 Conftest設定

**実装** (`tests/conftest.py`):
```python
import pytest
from unittest.mock import Mock
from datetime import datetime

@pytest.fixture
def mock_storage():
    """共通モックストレージ"""
    from app.a2a_mvp.storage.interface import StorageInterface
    return Mock(spec=StorageInterface)

@pytest.fixture
def sample_task():
    """共通サンプルタスク"""
    from app.a2a_mvp.core.types import Task
    return Task(
        id="test-001",
        title="テストタスク",
        created_at=datetime.now(),
        description="これはテスト用のタスクです"
    )

@pytest.fixture
def task_skill(mock_storage):
    """TaskSkillインスタンス"""
    from app.a2a_mvp.skills.task_skills import TaskSkill
    return TaskSkill(mock_storage)

@pytest.fixture
def task_agent(mock_storage):
    """TaskAgentインスタンス"""
    from app.a2a_mvp.agents.task_agent import TaskAgent
    return TaskAgent(mock_storage)
```

## 🎯 確認ポイント

### 品質チェック
```bash
# 全体チェック
python scripts/quality_gate_check.py

# 個別確認
pytest --cov=app --cov-report=term-missing
flake8 app/ tests/ --show-source
black --check app/ tests/
mypy app/ --ignore-missing-imports
```

### 期待される結果
- テスト数: 84個以上
- カバレッジ: 91%以上
- Flake8違反: 0
- ビルド時間: 1分以内

## 📝 トラブルシューティング

### ImportError
- PYTHONPATHにプロジェクトルートが含まれているか確認
- `__init__.py`が全ディレクトリに存在するか確認

### カバレッジ不足
- `pytest --cov=app --cov-report=html`でHTMLレポート生成
- カバーされていない行を確認し、テスト追加

### Flake8エラー
- 複雑度エラー: メソッドを分割
- 行長エラー: 79文字以内に調整

---

*このチェックリストに従えば、ゼロから91.77%カバレッジのA2A MVPを再現できます。*