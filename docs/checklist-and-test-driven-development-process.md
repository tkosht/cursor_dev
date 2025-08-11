# チェックリストドリブン＆テストドリブン開発プロセス定義書

## 1. 概要

本文書では、マルチエージェント記事評価システムの開発において、品質と進捗を確実に管理するためのチェックリストドリブン開発（CDD）とテストドリブン開発（TDD）のプロセスを定義します。

## 2. チェックリストドリブン開発（CDD）

### 2.1 マスターチェックリスト

#### 2.1.1 プロジェクト開始時チェックリスト
```markdown
## プロジェクト開始時チェックリスト

### 環境準備
- [ ] Python 3.10以上がインストールされている
- [ ] 仮想環境が作成されている（venv/poetry）
- [ ] .envファイルが作成され、必要な環境変数が設定されている
- [ ] .gitignoreに.envが含まれている
- [ ] requirements.txtとrequirements-dev.txtが準備されている

### プロジェクト構造
- [ ] ディレクトリ構造が仕様書通りに作成されている
- [ ] __init__.pyファイルが各パッケージに配置されている
- [ ] README.mdが作成されている
- [ ] LICENSEファイルが配置されている

### 開発ツール
- [ ] pytest.iniが設定されている
- [ ] Ruff/Black の設定が整備されている（Ruff標準、Flake8は補助）
- [ ] .pre-commit-config.yamlが設定されている
- [ ] logging設定ファイルが準備されている

### APIキー確認
- [ ] 少なくとも1つのLLMプロバイダーのAPIキーが取得されている
- [ ] APIキーが.envファイルに正しく設定されている
- [ ] APIキーの有効性が確認されている（テスト呼び出し成功）
```

#### 2.1.2 機能実装チェックリスト（各機能ごと）
```markdown
## 機能実装チェックリスト: [機能名]

### 実装前
- [ ] 機能の要件が明確に定義されている
- [ ] インターフェース（入力/出力）が定義されている
- [ ] 依存関係が特定されている
- [ ] テストケースが設計されている

### テスト作成（TDD）
- [ ] 単体テストファイルが作成されている
- [ ] 失敗するテストが書かれている（Red）
- [ ] エッジケースのテストが含まれている
- [ ] モックは原則禁止（単体の外部I/O・LLM境界のみ、事前承認がある場合に限る）

### 実装
- [ ] 基本実装が完了している
- [ ] すべてのテストが通る（Green）
- [ ] エラーハンドリングが実装されている
- [ ] ログ出力が適切に配置されている

### リファクタリング
- [ ] コードが読みやすく整理されている（Refactor）
- [ ] 重複コードが除去されている
- [ ] 命名規則に従っている
- [ ] 型ヒントが追加されている

### ドキュメント
- [ ] docstringが記述されている
- [ ] 使用例が含まれている
- [ ] 制限事項が記載されている

### レビュー準備
- [ ] `ruff check .` が通る（必要に応じ `black .`）
- [ ] テストカバレッジが85%以上
- [ ] 実装がベストプラクティスに従っている
```

#### 2.1.3 エージェント実装チェックリスト
```markdown
## エージェント実装チェックリスト: [エージェント名]

### 設計
- [ ] エージェントの役割が明確に定義されている
- [ ] システムプロンプトが作成されている
- [ ] 評価基準が定義されている
- [ ] 必要なツールが特定されている

### 基底クラス継承
- [ ] BaseReviewAgentを継承している
- [ ] 必須メソッドがオーバーライドされている
- [ ] 初期化パラメータが適切に設定されている

### 非同期実装
- [ ] async/awaitが正しく使用されている
- [ ] 並列実行可能な処理が特定されている
- [ ] タイムアウト処理が実装されている

### LLM統合
- [ ] LLMファクトリーを使用している
- [ ] プロンプトテンプレートが定義されている
- [ ] レスポンスパーサーが実装されている

### エラーハンドリング
- [ ] LLM呼び出しエラーがキャッチされている
- [ ] 適切なフォールバック処理がある
- [ ] エラーログが出力される

### テスト
- [ ] 単体テストが作成されている
- [ ] モックLLMレスポンスが準備されている
- [ ] 異常系のテストが含まれている
- [ ] 非同期テストが正しく実装されている
```

### 2.2 日次進捗チェックリスト
```markdown
## 日次進捗チェックリスト

### 開始時
- [ ] 前日の進捗を確認
- [ ] 本日のタスクを特定
- [ ] ブロッカーの有無を確認
- [ ] 必要なリソースが利用可能

### 実装中（2時間ごと）
- [ ] 計画通りに進んでいるか確認
- [ ] テストファーストで実装しているか
- [ ] 定期的にコミットしているか
- [ ] チェックリストを更新しているか

### 終了時
- [ ] 本日の成果をまとめる
- [ ] すべてのテストが通る
- [ ] コードがコミットされている
- [ ] 明日のタスクを整理
- [ ] ブロッカーを記録
```

## 3. テストドリブン開発（TDD）プロセス

### 3.1 TDDサイクル

#### 3.1.1 Red-Green-Refactorサイクル
```python
# Step 1: Red - 失敗するテストを書く
# tests/test_example_agent.py
import pytest
from src.agents.example_agent import ExampleAgent

class TestExampleAgent:
    def test_agent_initialization(self):
        """エージェントが正しく初期化されることを確認"""
        # この時点ではExampleAgentは存在しない
        agent = ExampleAgent()
        assert agent.name == "example"
        assert agent.llm is not None
```

```python
# Step 2: Green - テストを通す最小限の実装
# src/agents/example_agent.py
from src.agents.base import BaseReviewAgent

class ExampleAgent(BaseReviewAgent):
    def __init__(self):
        super().__init__(name="example", system_prompt="")
```

```python
# Step 3: Refactor - コードを改善
# src/agents/example_agent.py
from src.agents.base import BaseReviewAgent
from typing import Dict, Any

class ExampleAgent(BaseReviewAgent):
    """サンプルエージェントの実装"""
    
    def __init__(self):
        system_prompt = """
        You are an example agent for demonstration purposes.
        Evaluate articles based on clarity and structure.
        """
        super().__init__(
            name="example",
            system_prompt=system_prompt
        )
    
    async def evaluate(self, article: str) -> Dict[str, Any]:
        """記事を評価する"""
        # 実装
        pass
```

### 3.2 テスト戦略

#### 3.2.1 テストピラミッド
```
         /\
        /  \    E2Eテスト（5%）
       /    \   - システム全体の統合テスト
      /------\  
     /        \ 統合テスト（15%）
    /          \- エージェント間連携
   /            \- LangGraphワークフロー
  /              \
 /                \単体テスト（80%）
/                  \- 個別エージェント
                    - ユーティリティ関数
                    - パーサー
```

#### 3.2.2 単体テストテンプレート
```python
# tests/unit/test_agent_template.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime

from src.agents.personas.tech_expert import TechExpertAgent

class TestTechExpertAgent:
    """技術専門家エージェントの単体テスト"""
    
    @pytest.fixture
    def mock_llm(self):
        """モックLLMの作成"""
        mock = AsyncMock()
        mock.ainvoke.return_value = Mock(content='{"score": 85}')
        return mock
    
    @pytest.fixture
    def agent(self, mock_llm):
        """テスト用エージェントの作成"""
        with patch('src.utils.llm_factory.LLMFactory.create_llm', return_value=mock_llm):
            return TechExpertAgent()
    
    @pytest.mark.asyncio
    async def test_evaluate_success(self, agent, mock_llm):
        """正常な評価フローのテスト"""
        # Arrange
        test_article = "# Test Article\nThis is a test."
        expected_response = {
            "overall_score": 85,
            "technical_accuracy": {"score": 90, "comments": "Good"},
            "code_quality": {"score": 80, "comments": "Acceptable"}
        }
        mock_llm.ainvoke.return_value = Mock(
            content=json.dumps(expected_response)
        )
        
        # Act
        result = await agent.evaluate(test_article)
        
        # Assert
        assert result["overall_score"] == 85
        assert "technical_accuracy" in result
        assert mock_llm.ainvoke.called
        assert mock_llm.ainvoke.call_count == 1
    
    @pytest.mark.asyncio
    async def test_evaluate_with_timeout(self, agent, mock_llm):
        """タイムアウト処理のテスト"""
        # Arrange
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(2)
            return Mock(content='{}')
        
        mock_llm.ainvoke = slow_response
        
        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                agent.evaluate("test"),
                timeout=1.0
            )
    
    @pytest.mark.asyncio
    async def test_evaluate_error_handling(self, agent, mock_llm):
        """エラーハンドリングのテスト"""
        # Arrange
        mock_llm.ainvoke.side_effect = Exception("LLM Error")
        
        # Act
        result = await agent.evaluate("test article")
        
        # Assert
        assert result["status"] == "failed"
        assert "error" in result
        assert "LLM Error" in result["error"]
    
    def test_parse_llm_response_valid_json(self, agent):
        """有効なJSONレスポンスのパースのテスト"""
        # Arrange
        valid_json = '{"score": 75, "comments": "Good work"}'
        
        # Act
        result = agent._parse_llm_response(valid_json)
        
        # Assert
        assert result["score"] == 75
        assert result["comments"] == "Good work"
    
    def test_parse_llm_response_invalid_json(self, agent):
        """無効なJSONレスポンスのパースのテスト"""
        # Arrange
        invalid_json = "This is not JSON"
        
        # Act
        result = agent._parse_llm_response(invalid_json)
        
        # Assert
        assert result == {}
        assert agent.last_error is not None
```

#### 3.2.3 統合テストテンプレート
```python
# tests/integration/test_workflow_integration.py
import pytest
from langgraph.checkpoint.memory import MemorySaver
import asyncio

from src.graph.builder import build_article_review_graph
from src.agents.agent_registry import register_all_agents

class TestWorkflowIntegration:
    """ワークフロー統合テスト"""
    
    @pytest.fixture
    async def review_graph(self):
        """テスト用グラフの作成"""
        # エージェントの登録
        register_all_agents()
        
        # グラフの構築
        checkpointer = MemorySaver()
        graph = build_article_review_graph()
        compiled = graph.compile(checkpointer=checkpointer)
        
        return compiled
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_simple_article_review(self, review_graph):
        """シンプルな記事レビューのエンドツーエンドテスト"""
        # Arrange
        test_article = """
        # Introduction to Python Async
        
        Python's async/await syntax provides powerful concurrency.
        
        ```python
        async def hello():
            await asyncio.sleep(1)
            return "Hello, World!"
        ```
        """
        
        initial_state = {
            "article_content": test_article,
            "article_metadata": {
                "title": "Introduction to Python Async",
                "word_count": len(test_article.split())
            },
            "current_phase": "initialization"
        }
        
        # Act
        config = {"configurable": {"thread_id": "test_001"}}
        result = await review_graph.ainvoke(initial_state, config)
        
        # Assert
        assert result["current_phase"] == "completed"
        assert "final_report" in result
        assert len(result["persona_evaluations"]) >= 4
        assert result["final_report"]["overall_score"] > 0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_parallel_persona_execution(self, review_graph):
        """ペルソナの並列実行テスト"""
        # Arrange
        test_article = "Test article for parallel execution"
        initial_state = {
            "article_content": test_article,
            "current_phase": "evaluation"
        }
        
        # Act
        start_time = asyncio.get_event_loop().time()
        config = {"configurable": {"thread_id": "test_parallel"}}
        
        # ストリーミングで進捗を監視
        events = []
        async for event in review_graph.astream(initial_state, config):
            events.append(event)
            if "persona_evaluations" in event:
                print(f"Persona completed: {list(event['persona_evaluations'].keys())}")
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        
        # Assert
        # 4つのペルソナが並列実行されるので、順次実行より速いはず
        assert execution_time < 10  # 仮定：各ペルソナ3秒×4＝12秒の順次実行より速い
        assert len(events) > 0
```

### 3.3 テスト実行と品質管理

#### 3.3.1 テスト実行コマンド
```bash
# 全テスト実行
pytest

# カバレッジ付き実行（相対パス原則）
pytest --cov=app --cov-report=html

# 特定のマーカーのみ実行
pytest -m "not integration"  # 統合テスト以外
pytest -m asyncio           # 非同期テストのみ

# 並列実行（高速化）
pytest -n auto

# 詳細出力
pytest -v -s

# 失敗時に停止
pytest -x

# 最後に失敗したテストのみ再実行
pytest --lf
```

#### 3.3.2 pytest設定
```ini
# pytest.ini
[tool:pytest]
minversion = 6.0
addopts = -ra -q --strict-markers
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    asyncio: marks tests as async (deselect with '-m "not asyncio"')
    integration: marks tests as integration tests
    slow: marks tests as slow
    unit: marks tests as unit tests

asyncio_mode = auto

# カバレッジ設定
[coverage:run]
source = src
omit = 
    */tests/*
    */test_*
    */__init__.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

### 3.4 継続的品質改善

#### 3.4.1 コード品質チェックリスト
```markdown
## コード品質チェックリスト

### スタイル
- [ ] PEP 8に準拠している
- [ ] 一貫した命名規則
- [ ] 適切なインデント（4スペース）
- [ ] 行長は88文字以内（Black基準）

### 構造
- [ ] 関数は単一責任原則に従う
- [ ] クラスは適切に設計されている
- [ ] 循環インポートがない
- [ ] 依存関係が明確

### ドキュメント
- [ ] すべての公開関数にdocstring
- [ ] 複雑なロジックにコメント
- [ ] 型ヒントが完全
- [ ] 使用例が含まれている

### テスト
- [ ] テストカバレッジ80%以上
- [ ] エッジケースがテストされている
- [ ] モックが適切に使用されている
- [ ] テストが独立している

### パフォーマンス
- [ ] 不要なループがない
- [ ] 適切なデータ構造を使用
- [ ] 非同期処理が活用されている
- [ ] メモリリークがない
```

#### 3.4.2 CI/CDパイプライン設定
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with Ruff
      run: |
        ruff check .
    
    - name: Type check with mypy
      run: |
        mypy app --ignore-missing-imports
    
    - name: Test with pytest
      run: |
        pytest tests/unit -v --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

## 4. 実装例：TDDでのLLMファクトリー開発

### 4.1 Step 1: 失敗するテストを書く
```python
# tests/unit/test_llm_factory_tdd.py
import pytest
import os
from unittest.mock import patch

# この時点でLLMFactoryはまだ存在しない
from src.utils.llm_factory import LLMFactory, LLMProvider

class TestLLMFactoryTDD:
    def test_get_provider_from_env(self):
        """環境変数からプロバイダーを取得できる"""
        with patch.dict(os.environ, {"LLM_PROVIDER": "gemini"}):
            provider = LLMFactory.get_provider()
            assert provider == LLMProvider.GEMINI
    
    def test_create_gemini_llm(self):
        """Gemini LLMを作成できる"""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "gemini",
            "GOOGLE_API_KEY": "test_key"
        }):
            llm = LLMFactory.create_llm()
            assert llm is not None
            assert hasattr(llm, 'invoke')
```

### 4.2 Step 2: 最小限の実装
```python
# src/utils/llm_factory.py
import os
from enum import Enum

class LLMProvider(Enum):
    GEMINI = "gemini"

class LLMFactory:
    @classmethod
    def get_provider(cls):
        provider_str = os.getenv("LLM_PROVIDER", "gemini")
        return LLMProvider(provider_str)
    
    @classmethod
    def create_llm(cls):
        # 最小限の実装
        class MockLLM:
            def invoke(self, prompt):
                return "response"
        return MockLLM()
```

### 4.3 Step 3: リファクタリング
```python
# src/utils/llm_factory.py (改善版)
import os
from enum import Enum
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI

class LLMProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"

class LLMFactory:
    """LLMインスタンスを生成するファクトリークラス"""
    
    @classmethod
    def get_provider(cls) -> LLMProvider:
        """環境変数からプロバイダーを取得"""
        provider_str = os.getenv("LLM_PROVIDER", "gemini").lower()
        try:
            return LLMProvider(provider_str)
        except ValueError:
            raise ValueError(f"Invalid LLM provider: {provider_str}")
    
    @classmethod
    def create_llm(cls):
        """設定に基づいてLLMインスタンスを生成"""
        provider = cls.get_provider()
        
        if provider == LLMProvider.GEMINI:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found")
            
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=api_key
            )
        
        # 他のプロバイダーは後で実装
        raise NotImplementedError(f"Provider {provider} not implemented yet")
```

## 5. 実装スケジュール例

### 5.1 Week 1: 基盤構築
```markdown
## Week 1 チェックリスト

### Day 1-2: プロジェクトセットアップ
- [ ] リポジトリ作成
- [ ] ディレクトリ構造作成
- [ ] 依存関係定義
- [ ] 開発環境設定
- [ ] 基本的なCI設定

### Day 3-4: LLMファクトリー
- [ ] LLMFactory設計
- [ ] テスト作成（TDD）
- [ ] 実装
- [ ] 3プロバイダー対応
- [ ] 統合テスト

### Day 5: 非同期実行基盤
- [ ] AsyncExecutor設計
- [ ] テスト作成
- [ ] 基本実装
- [ ] エラーハンドリング
```

### 5.2 Week 2: エージェント実装
```markdown
## Week 2 チェックリスト

### Day 1-2: 基底クラスとオーケストレーター
- [ ] BaseReviewAgent設計
- [ ] テスト作成
- [ ] 実装
- [ ] Orchestrator設計と実装

### Day 3-5: ペルソナエージェント
- [ ] 各ペルソナの設計
- [ ] テスト作成（各ペルソナ）
- [ ] 実装（TDD）
- [ ] 非同期対応
- [ ] 統合テスト
```

### 5.3 Week 3: 統合とリリース
```markdown
## Week 3 チェックリスト

### Day 1-2: LangGraph統合
- [ ] グラフ設計
- [ ] ノード実装
- [ ] ルーティング実装
- [ ] 状態管理

### Day 3-4: CLI実装
- [ ] CLIインターフェース設計
- [ ] 実装
- [ ] エラーハンドリング
- [ ] ヘルプドキュメント

### Day 5: 最終テストとドキュメント
- [ ] E2Eテスト
- [ ] パフォーマンステスト
- [ ] ドキュメント更新
- [ ] デモ準備
```

## 6. まとめ

本プロセス定義により：

1. **品質保証**: チェックリストによる漏れ防止
2. **進捗管理**: 明確なマイルストーン
3. **テスト駆動**: 高品質なコード
4. **継続的改善**: フィードバックループ

これらのプロセスに従うことで、高品質なマルチエージェントシステムを効率的に開発できます。