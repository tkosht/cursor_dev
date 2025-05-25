# TDD実践ガイドライン

このドキュメントは、A2A実機調査での反省を踏まえ、今後のプロジェクトで**Test Driven Development（TDD）を確実に実践する**ためのガイドラインです。

## 📋 TDD実践の必須要件

### 🎯 TDDの基本原則

1. **Red**: まず失敗するテストを書く
2. **Green**: テストを通すために最小限のコードを書く  
3. **Refactor**: コードを改善しつつテストが通ることを確認

**重要**: 実装コードを書く前に**必ずテストを先に書く**

---

## 🏗️ プロジェクト構造

### テストディレクトリ構造

```
tests/
├── unit/                    # 単体テスト（高速・独立）
│   ├── test_types/              # a2a.types モジュールテスト
│   │   ├── test_agent_card.py      # AgentCard単体テスト
│   │   ├── test_agent_skill.py     # AgentSkill単体テスト
│   │   ├── test_task_state.py      # TaskState単体テスト
│   │   └── test_event_queue.py     # EventQueue単体テスト
│   ├── test_agents/             # エージェント単体テスト
│   │   ├── test_base_agent.py      # BaseA2AAgent単体テスト
│   │   └── test_simple_agent.py    # SimpleTestAgent単体テスト
│   └── test_utils/              # ユーティリティ単体テスト
│       └── test_config.py          # AgentConfig単体テスト
├── integration/             # 統合テスト（中速・依存あり）
│   ├── test_agent_communication.py  # エージェント間通信
│   ├── test_sdk_integration.py      # a2a-sdk統合テスト
│   └── test_server_integration.py   # サーバー統合テスト
├── e2e/                     # E2Eテスト（低速・完全シナリオ）
│   ├── test_full_agent_workflow.py  # 完全ワークフロー
│   └── test_real_communication.py   # 実通信テスト
├── fixtures/                # テスト用データ・設定
│   ├── sample_agents.py         # サンプルエージェント定義
│   ├── test_configurations.py   # テスト用設定
│   └── mock_responses.py        # モックレスポンス
└── conftest.py              # pytest設定・共通フィクスチャ
```

### pyproject.toml テスト設定

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-fail-under=90",
]
markers = [
    "unit: 単体テスト",
    "integration: 統合テスト", 
    "e2e: E2Eテスト",
    "slow: 実行時間の長いテスト",
]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

---

## 🧪 TDDサイクルの実践

### 1. Red フェーズ: 失敗するテストを書く

```python
# tests/unit/test_types/test_agent_skill.py
import pytest
from pydantic import ValidationError
from a2a.types import AgentSkill

class TestAgentSkillCreation:
    """AgentSkill作成のTDDテスト"""
    
    def test_create_with_all_required_fields(self):
        """Red: 必須フィールドでの正常作成テスト"""
        # Given: 有効な必須フィールド
        skill_data = {
            "id": "test_skill",
            "name": "Test Skill", 
            "description": "A test skill for validation",
            "tags": ["test", "validation"]
        }
        
        # When: AgentSkillを作成
        skill = AgentSkill(**skill_data)
        
        # Then: 期待される値で正確に作成される
        assert skill.id == "test_skill"
        assert skill.name == "Test Skill"
        assert skill.description == "A test skill for validation"
        assert skill.tags == ["test", "validation"]
        assert isinstance(skill.tags, list)
        assert len(skill.tags) == 2
    
    def test_create_missing_id_field_raises_validation_error(self):
        """Red: id フィールド不足時のバリデーションエラー"""
        # Given: id フィールドが不足したデータ
        skill_data = {
            "name": "Test Skill",
            "description": "A test skill",
            "tags": ["test"]
        }
        
        # When/Then: ValidationErrorが発生する
        with pytest.raises(ValidationError) as exc_info:
            AgentSkill(**skill_data)
        
        # Then: エラーメッセージに「id」「Field required」が含まれる
        error_str = str(exc_info.value)
        assert "id" in error_str
        assert "Field required" in error_str
```

### 2. Green フェーズ: テストを通すための最小実装

```python
# 最初はテストが失敗することを確認
$ poetry run pytest tests/unit/test_types/test_agent_skill.py::TestAgentSkillCreation::test_create_with_all_required_fields -v

# テストが通るまで実装を行う（この場合は既存実装で通る）
```

### 3. Refactor フェーズ: コード改善

テストが通った後、コードの改善を行う：
- 重複除去
- 可読性向上
- パフォーマンス改善

**重要**: リファクタリング後もテストが通ることを必ず確認

---

## 📝 テストケース設計パターン

### AAA（Arrange-Act-Assert）パターン

```python
def test_event_queue_lifecycle():
    """EventQueueのライフサイクルテスト"""
    # Arrange: 前提条件の準備
    queue = EventQueue()
    
    # Act: 実際の動作
    initial_state = queue.is_closed()
    await queue.close()
    final_state = queue.is_closed()
    
    # Assert: 結果の検証
    assert initial_state is False
    assert final_state is True
```

### Given-When-Then パターン

```python
def test_simple_agent_echo_command():
    """SimpleTestAgentのechoコマンドテスト"""
    # Given: 設定済みのSimpleTestAgent
    config = AgentConfig(name="test-agent", url="http://localhost:8001")
    agent = SimpleTestAgent(config)
    
    # When: echoコマンドを実行
    result = await agent.process_user_input("echo Hello World")
    
    # Then: メッセージがエコーされる
    assert result == "Echo: Hello World"
    assert "Echo:" in result
    assert "Hello World" in result
```

### パラメータ化テスト

```python
@pytest.mark.parametrize("invalid_id", [
    None,           # None値
    "",             # 空文字
    123,            # 数値
    [],             # リスト
    {},             # 辞書
])
def test_agent_skill_invalid_id_types(invalid_id):
    """AgentSkill: 無効なidの型でバリデーションエラー"""
    skill_data = {
        "id": invalid_id,
        "name": "Test",
        "description": "Test",
        "tags": ["test"]
    }
    
    with pytest.raises(ValidationError):
        AgentSkill(**skill_data)
```

---

## 🏃‍♂️ テスト実行戦略

### 階層別実行コマンド

```bash
# 1. 高速フィードバック: 単体テストのみ
poetry run pytest tests/unit/ -v

# 2. 中程度フィードバック: 単体+統合テスト
poetry run pytest tests/unit/ tests/integration/ -v

# 3. 完全テスト: すべてのテスト
poetry run pytest tests/ -v

# 4. カバレッジ付き実行
poetry run pytest tests/ --cov=src --cov-report=html

# 5. 並列実行（pytest-xdist使用）
poetry run pytest tests/ -n auto
```

### TDDサイクル実行スクリプト

```bash
#!/bin/bash
# scripts/tdd_cycle.sh

echo "=== TDD Cycle: Red → Green → Refactor ==="

echo "📍 Step 1: Running failing test (Red)"
poetry run pytest tests/unit/ -v --tb=short
if [ $? -eq 0 ]; then
    echo "⚠️  Warning: Tests are passing. Write a failing test first!"
    exit 1
fi

echo "📍 Step 2: Implement minimal code (Green)" 
echo "Write code to make the test pass, then press Enter..."
read

echo "📍 Step 3: Verify tests pass"
poetry run pytest tests/unit/ -v
if [ $? -ne 0 ]; then
    echo "❌ Tests still failing. Continue implementation."
    exit 1
fi

echo "📍 Step 4: Run full test suite"
poetry run pytest tests/ -v

echo "📍 Step 5: Check coverage"
poetry run pytest tests/ --cov=src --cov-report=term

echo "✅ TDD Cycle completed successfully!"
```

---

## 🔧 モック・フィクスチャ活用

### pytest フィクスチャ

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from a2a.types import EventQueue, AgentCard
from app.a2a_prototype.utils.config import AgentConfig

@pytest.fixture
def sample_agent_config():
    """テスト用のAgentConfig"""
    return AgentConfig(
        name="test-agent",
        description="Test agent for TDD",
        url="http://localhost:8001",
        port=8001
    )

@pytest.fixture
def sample_agent_skill():
    """テスト用のAgentSkill"""
    return {
        "id": "test_skill",
        "name": "Test Skill",
        "description": "A skill for testing",
        "tags": ["test", "unit"]
    }

@pytest.fixture
def mock_event_queue():
    """EventQueueのモック"""
    queue = AsyncMock(spec=EventQueue)
    queue.is_closed.return_value = False
    return queue

@pytest.fixture
async def async_mock_event_queue():
    """非同期テスト用EventQueueモック"""
    queue = AsyncMock(spec=EventQueue)
    queue.is_closed.return_value = False
    
    # ライフサイクルシミュレーション
    async def mock_close():
        queue.is_closed.return_value = True
    
    queue.close.side_effect = mock_close
    return queue
```

### モック活用例

```python
# tests/unit/test_agents/test_simple_agent.py
import pytest
from unittest.mock import patch, MagicMock
from app.a2a_prototype.agents.simple_agent import SimpleTestAgent

class TestSimpleTestAgent:
    """SimpleTestAgentの包括的テスト"""
    
    def test_get_skills_returns_expected_skills(self, sample_agent_config):
        """get_skills: 期待されるスキル一覧を返す"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)
        
        # When: スキル一覧を取得
        skills = agent.get_skills()
        
        # Then: 期待されるスキルが含まれる
        assert len(skills) == 2
        skill_ids = [skill.id for skill in skills]
        assert "echo" in skill_ids
        assert "greet" in skill_ids
    
    @pytest.mark.asyncio
    async def test_process_user_input_echo_command(self, sample_agent_config):
        """process_user_input: echoコマンドの処理"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)
        
        # When: echoコマンドを実行
        result = await agent.process_user_input("echo Test Message")
        
        # Then: メッセージがエコーされる
        assert result == "Echo: Test Message"
    
    @pytest.mark.asyncio
    async def test_process_user_input_empty_echo(self, sample_agent_config):
        """process_user_input: 空のechoコマンド"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)
        
        # When: 空のechoコマンドを実行
        result = await agent.process_user_input("echo")
        
        # Then: 空メッセージの通知
        assert result == "Echo: (empty message)"
```

---

## 🤖 CI/CD統合

### GitHub Actions設定

```yaml
# .github/workflows/tdd.yml
name: TDD Test Suite

on:
  push:
    branches: [ main, develop, feature/* ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: latest
        virtualenvs-create: true
        virtualenvs-in-project: true
    
    - name: Load cached venv
      id: cached-poetry-dependencies
      uses: actions/cache@v3
      with:
        path: .venv
        key: venv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}
    
    - name: Install dependencies
      if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
      run: poetry install --no-interaction --no-root
    
    - name: Install project
      run: poetry install --no-interaction
    
    - name: Run unit tests
      run: |
        poetry run pytest tests/unit/ -v \
          --cov=src \
          --cov-report=xml \
          --cov-report=term-missing \
          --cov-fail-under=90
    
    - name: Run integration tests
      run: |
        poetry run pytest tests/integration/ -v
    
    - name: Run E2E tests
      run: |
        poetry run pytest tests/e2e/ -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true

  quality-gate:
    runs-on: ubuntu-latest
    needs: test
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Quality Gate Check
      run: |
        echo "✅ All tests passed"
        echo "✅ Coverage requirement met"
        echo "✅ Ready for merge"
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: unit-tests
        name: Run Unit Tests
        entry: poetry run pytest tests/unit/ -v
        language: system
        pass_filenames: false
        always_run: true
      
      - id: test-coverage
        name: Check Test Coverage
        entry: poetry run pytest tests/unit/ --cov=src --cov-fail-under=90
        language: system
        pass_filenames: false
        always_run: true
```

---

## 📊 品質指標・メトリクス

### カバレッジ目標

- **単体テスト**: 最低90%、目標95%
- **統合テスト**: 主要パス100%
- **E2Eテスト**: クリティカルパス100%

### テスト実行時間目標

- **単体テスト**: 10秒以内
- **統合テスト**: 30秒以内  
- **E2Eテスト**: 120秒以内

### 品質ゲート

```bash
# 品質チェックスクリプト
#!/bin/bash
# scripts/quality_gate.sh

echo "=== Quality Gate Check ==="

# 1. 単体テスト実行
echo "📋 Running unit tests..."
poetry run pytest tests/unit/ -q
if [ $? -ne 0 ]; then
    echo "❌ Unit tests failed"
    exit 1
fi

# 2. カバレッジチェック
echo "📊 Checking coverage..."
poetry run pytest tests/unit/ --cov=src --cov-fail-under=90 -q
if [ $? -ne 0 ]; then
    echo "❌ Coverage below 90%"
    exit 1
fi

# 3. 統合テスト実行
echo "🔗 Running integration tests..."
poetry run pytest tests/integration/ -q
if [ $? -ne 0 ]; then
    echo "❌ Integration tests failed"
    exit 1
fi

echo "✅ All quality gates passed!"
```

---

## 📚 TDD教育・実践プロセス

### チーム実践ルール

1. **新機能開発**: 必ずテストファーストで実装
2. **バグ修正**: 再現テストを先に書く
3. **リファクタリング**: テストが通ることを確認しながら実施
4. **コードレビュー**: TDD実践の確認を必須項目にする

### ペアプログラミング推奨

```
Driver（実装者）とNavigator（レビュアー）でTDDサイクルを実践：
1. Navigator: 失敗するテストを提案
2. Driver: テストを実装
3. Driver: テストを通すためのコードを実装
4. 両者: リファクタリングの検討・実施
5. 役割交代して次のサイクル
```

### TDDレビューチェックリスト

**プルリクエストレビュー時の確認項目**:
- [ ] テストが実装より先に書かれているか
- [ ] 失敗ケース・境界値がテストされているか
- [ ] テストコードは理解しやすいか
- [ ] モック・フィクスチャが適切に使われているか
- [ ] カバレッジが基準を満たしているか
- [ ] 命名が明確か（何をテストしているか分かる）

---

## 🎯 成功指標

### プロジェクトレベル

- **テストファースト実践率**: 100%
- **カバレッジ**: 単体テスト90%以上
- **テスト実行頻度**: 1日複数回
- **品質ゲート通過率**: 100%

### チームレベル

- **TDD理解度**: 全メンバーが基本実践可能
- **実践浸透度**: 新機能開発でのTDD適用率100%
- **継続改善**: 月次でのTDD実践レビュー・改善

---

**このガイドラインに従って、今後のすべてのプロジェクトでTDDを徹底実践します。**

---

**作成日**: A2A実機調査でのテスト設計不足を受けて  
**対象**: 全プロジェクトメンバー  
**更新**: TDD実践状況に応じて継続的に改善 