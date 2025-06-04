# 【完全ガイド】AIエージェント開発の始め方 - 環境構築から初回デプロイまで全手順

> **この記事を読むとできるようになること**
> - AIエージェント開発環境の構築
> - 基本的なエージェントの実装
> - テスト・デバッグ・デプロイの流れ
> - 実用的なトラブルシューティング

## はじめに - この記事の対象読者

【導入文 - 読者の現状確認】
- プログラミング経験: 初級〜中級
- AIエージェントへの興味: あり
- 実際に手を動かしたい方
- 実用的なシステムを作りたい方

## 🎯 この記事で作るもの

### 完成形のイメージ
- シンプルなタスク管理エージェント
- REST API経由での操作
- 基本的なCRUD機能
- ローカル環境での動作

### 技術スタック
- **言語**: Python 3.10+
- **フレームワーク**: FastAPI
- **AI**: [使用するAIライブラリ]
- **テスト**: pytest
- **その他**: Docker（オプション）

## 📋 事前準備

### 必要なソフトウェア
- [ ] Python 3.10以上
- [ ] Git
- [ ] テキストエディタ（VSCode推奨）
- [ ] ターミナル/コマンドプロンプト

### スキル前提
- [ ] 基本的なPythonの読み書き
- [ ] コマンドライン操作の基礎
- [ ] Git の基本操作

## 🛠 Step 1: 開発環境構築

### 1-1. プロジェクトディレクトリ作成
```bash
# プロジェクトディレクトリ作成
mkdir ai-agent-tutorial
cd ai-agent-tutorial

# 仮想環境作成
python -m venv venv

# 仮想環境アクティベート
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 1-2. 必要なライブラリインストール
```bash
# requirements.txt作成
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
pytest==7.4.3
requests==2.31.0
EOF

# インストール実行
pip install -r requirements.txt
```

### 1-3. プロジェクト構造作成
```bash
# ディレクトリ構造作成
mkdir -p src/{core,agents,api}
mkdir -p tests/{unit,integration}
mkdir -p docs

# 基本ファイル作成
touch src/__init__.py
touch src/core/__init__.py
touch src/agents/__init__.py  
touch src/api/__init__.py
touch tests/__init__.py
```

**✅ チェックポイント**: `ls -la` でディレクトリ構造を確認

## 🔧 Step 2: 基本コンポーネント実装

### 2-1. データモデル定義
`src/core/models.py`を作成:
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Task(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TaskRequest(BaseModel):
    action: str
    task_id: Optional[str] = None
    data: Optional[dict] = None

class TaskResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
```

**✅ チェックポイント**: `python -c "from src.core.models import Task; print('OK')"` でインポート確認

### 2-2. ストレージ層実装
`src/core/storage.py`を作成:
```python
from typing import Dict, List, Optional
from .models import Task
import uuid
from datetime import datetime

class InMemoryStorage:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
    
    def create_task(self, task: Task) -> Task:
        task.id = str(uuid.uuid4())
        task.created_at = datetime.now()
        task.updated_at = datetime.now()
        self.tasks[task.id] = task
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    def list_tasks(self) -> List[Task]:
        return list(self.tasks.values())
    
    def update_task(self, task_id: str, updates: dict) -> Optional[Task]:
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        task.updated_at = datetime.now()
        return task
    
    def delete_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
```

**✅ チェックポイント**: ストレージのユニットテストを実行

### 2-3. エージェント実装
`src/agents/task_agent.py`を作成:
```python
from ..core.models import Task, TaskRequest, TaskResponse, TaskStatus
from ..core.storage import InMemoryStorage
from typing import Dict, Any

class TaskAgent:
    def __init__(self, storage: InMemoryStorage):
        self.storage = storage
    
    def process_request(self, request: TaskRequest) -> TaskResponse:
        try:
            if request.action == "create":
                return self._create_task(request.data)
            elif request.action == "get":
                return self._get_task(request.task_id)
            elif request.action == "list":
                return self._list_tasks()
            elif request.action == "update":
                return self._update_task(request.task_id, request.data)
            elif request.action == "delete":
                return self._delete_task(request.task_id)
            else:
                return TaskResponse(
                    success=False, 
                    error=f"Unknown action: {request.action}"
                )
        except Exception as e:
            return TaskResponse(success=False, error=str(e))
    
    def _create_task(self, data: dict) -> TaskResponse:
        task = Task(**data)
        created_task = self.storage.create_task(task)
        return TaskResponse(
            success=True, 
            data=created_task.model_dump()
        )
    
    def _get_task(self, task_id: str) -> TaskResponse:
        task = self.storage.get_task(task_id)
        if task:
            return TaskResponse(success=True, data=task.model_dump())
        return TaskResponse(success=False, error="Task not found")
    
    def _list_tasks(self) -> TaskResponse:
        tasks = self.storage.list_tasks()
        return TaskResponse(
            success=True, 
            data={"tasks": [t.model_dump() for t in tasks]}
        )
    
    def _update_task(self, task_id: str, data: dict) -> TaskResponse:
        updated_task = self.storage.update_task(task_id, data)
        if updated_task:
            return TaskResponse(success=True, data=updated_task.model_dump())
        return TaskResponse(success=False, error="Task not found")
    
    def _delete_task(self, task_id: str) -> TaskResponse:
        if self.storage.delete_task(task_id):
            return TaskResponse(success=True, data={"deleted": True})
        return TaskResponse(success=False, error="Task not found")
```

**✅ チェックポイント**: エージェントの基本動作確認

## 🌐 Step 3: REST API実装

### 3-1. FastAPIアプリケーション
`src/api/app.py`を作成:
```python
from fastapi import FastAPI, HTTPException
from ..core.models import TaskRequest, TaskResponse
from ..core.storage import InMemoryStorage
from ..agents.task_agent import TaskAgent

# アプリケーション初期化
app = FastAPI(title="AI Task Agent", version="1.0.0")
storage = InMemoryStorage()
agent = TaskAgent(storage)

@app.get("/")
async def root():
    return {
        "message": "AI Task Agent API",
        "version": "1.0.0",
        "endpoints": ["/tasks"]
    }

@app.post("/tasks", response_model=TaskResponse)
async def handle_task_request(request: TaskRequest):
    response = agent.process_request(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return response

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 3-2. サーバー起動スクリプト
`run_server.py`を作成:
```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

**✅ チェックポイント**: `python run_server.py` でサーバー起動確認

## 🧪 Step 4: テスト実装

### 4-1. ユニットテスト
`tests/unit/test_task_agent.py`を作成:
```python
import pytest
from src.core.models import TaskRequest, TaskStatus
from src.core.storage import InMemoryStorage
from src.agents.task_agent import TaskAgent

@pytest.fixture
def agent():
    storage = InMemoryStorage()
    return TaskAgent(storage)

def test_create_task(agent):
    request = TaskRequest(
        action="create",
        data={"title": "Test Task", "description": "Test Description"}
    )
    response = agent.process_request(request)
    assert response.success
    assert response.data["title"] == "Test Task"

def test_list_tasks(agent):
    # タスクを作成
    create_request = TaskRequest(
        action="create",
        data={"title": "Test Task"}
    )
    agent.process_request(create_request)
    
    # リスト取得
    list_request = TaskRequest(action="list")
    response = agent.process_request(list_request)
    
    assert response.success
    assert len(response.data["tasks"]) == 1

def test_invalid_action(agent):
    request = TaskRequest(action="invalid_action")
    response = agent.process_request(request)
    assert not response.success
    assert "Unknown action" in response.error
```

### 4-2. 統合テスト
`tests/integration/test_api.py`を作成:
```python
import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Task Agent API" in response.json()["message"]

def test_create_task_api():
    response = client.post("/tasks", json={
        "action": "create",
        "data": {"title": "API Test Task"}
    })
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

**✅ チェックポイント**: `pytest tests/ -v` でテスト実行

## 🚀 Step 5: 動作確認とデプロイ

### 5-1. 手動テスト
```bash
# サーバー起動
python run_server.py

# 別ターミナルでAPIテスト
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{"action": "create", "data": {"title": "Test Task"}}'

curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{"action": "list"}'
```

### 5-2. Docker化（オプション）
`Dockerfile`を作成:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run_server.py"]
```

`docker-compose.yml`を作成:
```yaml
version: '3.8'
services:
  ai-agent:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
```

**✅ チェックポイント**: `docker-compose up` で起動確認

## 🔧 トラブルシューティング

### よくある問題と解決策

#### 問題1: モジュールインポートエラー
```
ModuleNotFoundError: No module named 'src'
```
**解決策**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# または
python -m pytest  # pytestの場合
```

#### 問題2: ポートが使用中
```
OSError: [Errno 48] Address already in use
```
**解決策**:
```bash
# プロセス確認
lsof -i :8000
# プロセス終了
kill -9 <PID>
```

#### 問題3: Pydanticバリデーションエラー
**解決策**: モデル定義の型チェック、必須フィールドの確認

## 🎯 次のステップ

### 基本機能の拡張
- [ ] データベース連携（SQLite → PostgreSQL）
- [ ] 認証・認可機能
- [ ] WebSocket対応
- [ ] ログ機能強化

### AI機能の追加
- [ ] 自然言語処理
- [ ] タスク自動分類
- [ ] 優先度自動設定
- [ ] スケジューリング機能

### 運用面の改善
- [ ] CI/CD パイプライン
- [ ] モニタリング
- [ ] エラー追跡
- [ ] パフォーマンス測定

## 📚 参考リソース

### 公式ドキュメント
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [Pydantic公式ガイド](https://pydantic-docs.helpmanual.io/)
- [pytest公式チュートリアル](https://docs.pytest.org/)

### 追加学習リソース
- AIエージェント設計パターン
- REST API設計のベストプラクティス
- Pythonの非同期プログラミング

## まとめ

【達成したこと】
- 基本的なAIエージェントの実装
- REST APIによる操作
- テスト駆動開発の実践
- Docker化による環境構築

**次回予告**: この基盤を使って、より高度なAI機能を実装する方法を解説予定です。

---

## ハッシュタグ
#AIエージェント #Python #FastAPI #チュートリアル #プログラミング #初心者向け #ハンズオン

---

**📋 執筆チェックリスト**
- [ ] 手順が明確で追随可能
- [ ] コード例が動作する
- [ ] チェックポイントを設置
- [ ] トラブルシューティングを含む
- [ ] 初心者にも理解しやすい説明
- [ ] 実用的な完成品を作成
- [ ] 次のステップを提示
- [ ] 読了時間: 15-20分程度
- [ ] 実際に手を動かせる内容