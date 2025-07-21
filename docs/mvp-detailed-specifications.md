# MVP詳細仕様書

## 1. MVP概要

### 1.1 MVPの目的
最小限の機能で、マルチエージェントによる記事評価システムの価値を実証する。

### 1.2 MVPスコープ
- ✅ 基本的な記事評価機能
- ✅ 4つの仮想ペルソナによる評価
- ✅ LLMモデルの環境変数による切り替え
- ✅ 非同期並列実行
- ✅ 基本的なエラーハンドリング
- ❌ Web UI（コマンドラインツールとして実装）
- ❌ 認証機能
- ❌ データベース永続化
- ❌ 詳細なカスタマイズ機能

## 2. LLMモデル切り替え仕様

### 2.1 環境変数設計
```bash
# .env ファイル構成
# ===================
# LLMプロバイダー選択（必須）
LLM_PROVIDER=gemini  # gemini | openai | claude

# 各プロバイダーのAPIキー（使用するプロバイダーのみ必須）
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# モデル指定（オプション：デフォルト値あり）
GEMINI_MODEL=gemini-2.5-flash  # デフォルト
OPENAI_MODEL=gpt-4-turbo       # デフォルト
CLAUDE_MODEL=claude-3-sonnet-20240229  # デフォルト

# 共通パラメータ（オプション）
LLM_TEMPERATURE=0.7    # 0.0-1.0
LLM_MAX_TOKENS=2000    # 最大トークン数
LLM_TIMEOUT=60         # タイムアウト（秒）

# 並列実行設定
MAX_CONCURRENT_AGENTS=4  # 同時実行エージェント数
AGENT_TIMEOUT=60        # 個別エージェントタイムアウト

# ログレベル
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR
```

### 2.2 LLMファクトリー実装
```python
# src/utils/llm_factory.py
import os
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel

class LLMProvider(Enum):
    """サポートされるLLMプロバイダー"""
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"

@dataclass
class LLMConfig:
    """LLM設定のデータクラス"""
    provider: LLMProvider
    model_name: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60
    additional_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}

class LLMFactory:
    """環境変数に基づいてLLMインスタンスを生成するファクトリー"""
    
    # デフォルトモデル設定
    DEFAULT_MODELS = {
        LLMProvider.GEMINI: "gemini-2.5-flash",
        LLMProvider.OPENAI: "gpt-4-turbo",
        LLMProvider.CLAUDE: "claude-3-sonnet-20240229"
    }
    
    @classmethod
    def get_config(cls) -> LLMConfig:
        """環境変数からLLM設定を取得"""
        
        # プロバイダーの取得
        provider_str = os.getenv("LLM_PROVIDER", "gemini").lower()
        try:
            provider = LLMProvider(provider_str)
        except ValueError:
            raise ValueError(
                f"Invalid LLM_PROVIDER: {provider_str}. "
                f"Must be one of: {', '.join([p.value for p in LLMProvider])}"
            )
        
        # APIキーの取得
        api_key_map = {
            LLMProvider.GEMINI: "GOOGLE_API_KEY",
            LLMProvider.OPENAI: "OPENAI_API_KEY",
            LLMProvider.CLAUDE: "ANTHROPIC_API_KEY"
        }
        
        api_key = os.getenv(api_key_map[provider])
        if not api_key:
            raise ValueError(f"API key not found: {api_key_map[provider]}")
        
        # モデル名の取得
        model_env_map = {
            LLMProvider.GEMINI: "GEMINI_MODEL",
            LLMProvider.OPENAI: "OPENAI_MODEL",
            LLMProvider.CLAUDE: "CLAUDE_MODEL"
        }
        
        model_name = os.getenv(
            model_env_map[provider],
            cls.DEFAULT_MODELS[provider]
        )
        
        # 共通パラメータの取得
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
        timeout = int(os.getenv("LLM_TIMEOUT", "60"))
        
        return LLMConfig(
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
    
    @classmethod
    def create_llm(cls, config: Optional[LLMConfig] = None) -> BaseChatModel:
        """LLMインスタンスを生成"""
        
        if config is None:
            config = cls.get_config()
        
        # プロバイダー別のインスタンス生成
        if config.provider == LLMProvider.GEMINI:
            return ChatGoogleGenerativeAI(
                model=config.model_name,
                google_api_key=config.api_key,
                temperature=config.temperature,
                max_output_tokens=config.max_tokens,
                timeout=config.timeout,
                **config.additional_params
            )
        
        elif config.provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                model=config.model_name,
                openai_api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                request_timeout=config.timeout,
                **config.additional_params
            )
        
        elif config.provider == LLMProvider.CLAUDE:
            return ChatAnthropic(
                model=config.model_name,
                anthropic_api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
                **config.additional_params
            )
        
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """現在の設定を検証し、情報を返す"""
        try:
            config = cls.get_config()
            llm = cls.create_llm(config)
            
            # テスト呼び出し
            test_response = llm.invoke("Hello, this is a test.")
            
            return {
                "status": "success",
                "provider": config.provider.value,
                "model": config.model_name,
                "test_response": str(test_response)[:100] + "..."
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
```

### 2.3 モデル切り替えのテスト
```python
# tests/test_llm_factory.py
import pytest
import os
from unittest.mock import patch, MagicMock
from src.utils.llm_factory import LLMFactory, LLMProvider, LLMConfig

class TestLLMFactory:
    """LLMファクトリーのテストスイート"""
    
    @pytest.fixture
    def mock_env_gemini(self):
        """Gemini用の環境変数モック"""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "gemini",
            "GOOGLE_API_KEY": "test_google_key",
            "GEMINI_MODEL": "gemini-2.5-flash",
            "LLM_TEMPERATURE": "0.5",
            "LLM_MAX_TOKENS": "1500"
        }):
            yield
    
    @pytest.fixture
    def mock_env_openai(self):
        """OpenAI用の環境変数モック"""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "test_openai_key",
            "OPENAI_MODEL": "gpt-4-turbo",
            "LLM_TEMPERATURE": "0.8"
        }):
            yield
    
    def test_get_config_gemini(self, mock_env_gemini):
        """Gemini設定の取得テスト"""
        config = LLMFactory.get_config()
        
        assert config.provider == LLMProvider.GEMINI
        assert config.model_name == "gemini-2.5-flash"
        assert config.api_key == "test_google_key"
        assert config.temperature == 0.5
        assert config.max_tokens == 1500
    
    def test_get_config_openai(self, mock_env_openai):
        """OpenAI設定の取得テスト"""
        config = LLMFactory.get_config()
        
        assert config.provider == LLMProvider.OPENAI
        assert config.model_name == "gpt-4-turbo"
        assert config.api_key == "test_openai_key"
        assert config.temperature == 0.8
    
    def test_create_llm_gemini(self, mock_env_gemini):
        """Gemini LLMインスタンス作成テスト"""
        llm = LLMFactory.create_llm()
        
        assert llm.__class__.__name__ == "ChatGoogleGenerativeAI"
        assert llm.model == "gemini-2.5-flash"
    
    def test_invalid_provider(self):
        """無効なプロバイダーのテスト"""
        with patch.dict(os.environ, {"LLM_PROVIDER": "invalid"}):
            with pytest.raises(ValueError, match="Invalid LLM_PROVIDER"):
                LLMFactory.get_config()
    
    def test_missing_api_key(self):
        """APIキー未設定のテスト"""
        with patch.dict(os.environ, {"LLM_PROVIDER": "gemini"}, clear=True):
            with pytest.raises(ValueError, match="API key not found"):
                LLMFactory.get_config()
```

## 3. 非同期実行仕様

### 3.1 非同期実行アーキテクチャ
```python
# src/core/async_executor.py
import asyncio
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class AsyncTask:
    """非同期タスクの定義"""
    id: str
    name: str
    func: Callable
    args: tuple = ()
    kwargs: dict = None
    dependencies: List[str] = None
    timeout: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class TaskResult:
    """タスク実行結果"""
    task_id: str
    status: str  # success, failed, timeout
    result: Any = None
    error: Optional[str] = None
    start_time: datetime = None
    end_time: datetime = None
    duration: float = None

class AsyncExecutor:
    """非同期タスク実行エンジン"""
    
    def __init__(self, max_concurrent: int = 4):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.results: Dict[str, TaskResult] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
    
    async def execute_task(self, task: AsyncTask) -> TaskResult:
        """個別タスクの実行"""
        async with self.semaphore:
            start_time = datetime.now()
            result = TaskResult(
                task_id=task.id,
                status="running",
                start_time=start_time
            )
            
            try:
                logger.info(f"Starting task: {task.name} (ID: {task.id})")
                
                # タイムアウト付き実行
                if task.timeout:
                    task_result = await asyncio.wait_for(
                        self._run_task(task),
                        timeout=task.timeout
                    )
                else:
                    task_result = await self._run_task(task)
                
                end_time = datetime.now()
                result.status = "success"
                result.result = task_result
                result.end_time = end_time
                result.duration = (end_time - start_time).total_seconds()
                
                logger.info(
                    f"Task completed: {task.name} "
                    f"(Duration: {result.duration:.2f}s)"
                )
                
            except asyncio.TimeoutError:
                result.status = "timeout"
                result.error = f"Task timed out after {task.timeout}s"
                logger.error(f"Task timeout: {task.name}")
                
            except Exception as e:
                result.status = "failed"
                result.error = str(e)
                logger.error(f"Task failed: {task.name} - {str(e)}")
            
            self.results[task.id] = result
            return result
    
    async def _run_task(self, task: AsyncTask) -> Any:
        """タスク関数の実行（同期/非同期両対応）"""
        if asyncio.iscoroutinefunction(task.func):
            # 非同期関数
            return await task.func(*task.args, **task.kwargs)
        else:
            # 同期関数を非同期で実行
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.executor,
                task.func,
                *task.args
            )
    
    async def execute_parallel(self, tasks: List[AsyncTask]) -> List[TaskResult]:
        """複数タスクの並列実行"""
        logger.info(f"Starting parallel execution of {len(tasks)} tasks")
        
        # 依存関係のないタスクから実行
        execution_order = self._resolve_dependencies(tasks)
        all_results = []
        
        for batch in execution_order:
            batch_tasks = [
                self.execute_task(task) for task in batch
            ]
            batch_results = await asyncio.gather(*batch_tasks)
            all_results.extend(batch_results)
            
            # 失敗したタスクのリトライ
            for i, result in enumerate(batch_results):
                if result.status == "failed" and batch[i].retry_count < batch[i].max_retries:
                    logger.info(f"Retrying task: {batch[i].name}")
                    batch[i].retry_count += 1
                    retry_result = await self.execute_task(batch[i])
                    all_results[all_results.index(result)] = retry_result
        
        return all_results
    
    def _resolve_dependencies(self, tasks: List[AsyncTask]) -> List[List[AsyncTask]]:
        """依存関係を解決してバッチに分割"""
        task_dict = {task.id: task for task in tasks}
        completed = set()
        batches = []
        
        while len(completed) < len(tasks):
            current_batch = []
            
            for task in tasks:
                if task.id not in completed:
                    # 依存関係がすべて完了しているか確認
                    if all(dep in completed for dep in task.dependencies):
                        current_batch.append(task)
            
            if not current_batch:
                # 循環依存の検出
                remaining = [t.id for t in tasks if t.id not in completed]
                raise ValueError(f"Circular dependency detected: {remaining}")
            
            batches.append(current_batch)
            completed.update(task.id for task in current_batch)
        
        return batches
    
    async def execute_with_progress(
        self,
        tasks: List[AsyncTask],
        progress_callback: Optional[Callable] = None
    ) -> List[TaskResult]:
        """進捗コールバック付き実行"""
        total_tasks = len(tasks)
        completed_tasks = 0
        
        async def task_with_progress(task: AsyncTask) -> TaskResult:
            result = await self.execute_task(task)
            
            nonlocal completed_tasks
            completed_tasks += 1
            
            if progress_callback:
                await progress_callback({
                    "completed": completed_tasks,
                    "total": total_tasks,
                    "percentage": (completed_tasks / total_tasks) * 100,
                    "current_task": task.name,
                    "status": result.status
                })
            
            return result
        
        # 並列実行
        results = await asyncio.gather(*[
            task_with_progress(task) for task in tasks
        ])
        
        return results
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        self.executor.shutdown(wait=True)
```

### 3.2 エージェント非同期実行マネージャー
```python
# src/agents/async_agent_manager.py
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import logging

from src.core.async_executor import AsyncExecutor, AsyncTask, TaskResult
from src.utils.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

class AsyncAgentManager:
    """エージェントの非同期実行を管理"""
    
    def __init__(self, max_concurrent_agents: int = 4):
        self.max_concurrent = max_concurrent_agents
        self.executor = AsyncExecutor(max_concurrent)
        self.agent_registry = {}
        self.execution_history = []
    
    def register_agent(self, agent_id: str, agent_instance: Any):
        """エージェントの登録"""
        self.agent_registry[agent_id] = agent_instance
        logger.info(f"Registered agent: {agent_id}")
    
    async def execute_persona_evaluations(
        self,
        article_content: str,
        personas: List[str]
    ) -> Dict[str, Any]:
        """ペルソナ評価の並列実行"""
        
        # ペルソナタスクの作成
        tasks = []
        for persona in personas:
            agent = self.agent_registry.get(f"{persona}_agent")
            if not agent:
                logger.warning(f"Agent not found: {persona}_agent")
                continue
            
            task = AsyncTask(
                id=f"eval_{persona}_{datetime.now().timestamp()}",
                name=f"{persona}_evaluation",
                func=agent.evaluate,
                kwargs={"article": article_content},
                timeout=60  # 60秒のタイムアウト
            )
            tasks.append(task)
        
        # 並列実行
        start_time = datetime.now()
        results = await self.executor.execute_parallel(tasks)
        end_time = datetime.now()
        
        # 結果の集約
        evaluations = {}
        errors = []
        
        for result in results:
            persona_name = result.task_id.split('_')[1]
            
            if result.status == "success":
                evaluations[persona_name] = result.result
            else:
                errors.append({
                    "persona": persona_name,
                    "error": result.error,
                    "status": result.status
                })
        
        execution_summary = {
            "evaluations": evaluations,
            "errors": errors,
            "execution_time": (end_time - start_time).total_seconds(),
            "success_rate": len(evaluations) / len(tasks) if tasks else 0
        }
        
        self.execution_history.append(execution_summary)
        return execution_summary
    
    async def execute_with_dependencies(
        self,
        agent_tasks: List[Dict[str, Any]]
    ) -> List[TaskResult]:
        """依存関係を持つエージェントタスクの実行"""
        
        # タスクオブジェクトの作成
        tasks = []
        for task_config in agent_tasks:
            agent = self.agent_registry.get(task_config["agent_id"])
            if not agent:
                continue
            
            task = AsyncTask(
                id=task_config["id"],
                name=task_config["name"],
                func=agent.process,
                kwargs=task_config.get("kwargs", {}),
                dependencies=task_config.get("dependencies", []),
                timeout=task_config.get("timeout", 60)
            )
            tasks.append(task)
        
        # 依存関係を考慮した実行
        results = await self.executor.execute_parallel(tasks)
        return results
    
    async def stream_agent_execution(
        self,
        agent_id: str,
        input_data: Dict[str, Any]
    ):
        """エージェント実行のストリーミング"""
        
        agent = self.agent_registry.get(agent_id)
        if not agent:
            yield {"error": f"Agent not found: {agent_id}"}
            return
        
        try:
            # ストリーミング対応エージェントの場合
            if hasattr(agent, 'stream_process'):
                async for chunk in agent.stream_process(input_data):
                    yield {
                        "type": "stream",
                        "agent_id": agent_id,
                        "data": chunk,
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                # 通常の実行
                result = await agent.process(input_data)
                yield {
                    "type": "complete",
                    "agent_id": agent_id,
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            yield {
                "type": "error",
                "agent_id": agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """実行統計の取得"""
        if not self.execution_history:
            return {"message": "No executions yet"}
        
        total_executions = len(self.execution_history)
        total_time = sum(e["execution_time"] for e in self.execution_history)
        avg_time = total_time / total_executions
        success_rates = [e["success_rate"] for e in self.execution_history]
        
        return {
            "total_executions": total_executions,
            "total_execution_time": total_time,
            "average_execution_time": avg_time,
            "average_success_rate": sum(success_rates) / len(success_rates),
            "max_execution_time": max(e["execution_time"] for e in self.execution_history),
            "min_execution_time": min(e["execution_time"] for e in self.execution_history)
        }
```

### 3.3 非同期エージェントの実装例
```python
# src/agents/personas/async_tech_expert.py
import asyncio
from typing import Dict, Any
import json
from datetime import datetime

from src.agents.base import BaseReviewAgent
from src.utils.llm_factory import LLMFactory

class AsyncTechExpertAgent(BaseReviewAgent):
    """非同期実行対応の技術専門家エージェント"""
    
    def __init__(self):
        super().__init__(
            name="tech_expert",
            system_prompt="""
            あなたは経験豊富な技術専門家です。
            以下の観点から記事を評価してください：
            1. 技術的正確性
            2. コードの品質とベストプラクティス
            3. セキュリティ考慮事項
            4. パフォーマンスへの影響
            5. 最新技術トレンドとの整合性
            """
        )
        self.sub_analyzers = {
            "code_quality": self._analyze_code_quality,
            "security": self._analyze_security,
            "performance": self._analyze_performance,
            "best_practices": self._analyze_best_practices
        }
    
    async def evaluate(self, article: str) -> Dict[str, Any]:
        """記事の非同期評価"""
        
        # サブ分析を並列実行
        sub_analysis_tasks = [
            analyzer(article) for analyzer in self.sub_analyzers.values()
        ]
        
        sub_results = await asyncio.gather(*sub_analysis_tasks)
        
        # LLMによる総合評価
        evaluation_prompt = self._build_evaluation_prompt(article, sub_results)
        
        try:
            # 非同期LLM呼び出し
            llm_response = await self.llm.ainvoke(evaluation_prompt)
            evaluation = self._parse_llm_response(llm_response.content)
            
            # サブ分析結果を統合
            evaluation["sub_analysis"] = dict(
                zip(self.sub_analyzers.keys(), sub_results)
            )
            evaluation["evaluated_at"] = datetime.now().isoformat()
            
            return evaluation
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "evaluated_at": datetime.now().isoformat()
            }
    
    async def _analyze_code_quality(self, article: str) -> Dict[str, Any]:
        """コード品質の分析"""
        await asyncio.sleep(0.5)  # シミュレーション
        
        # コードブロックの抽出と分析
        code_blocks = self._extract_code_blocks(article)
        
        return {
            "code_blocks_count": len(code_blocks),
            "has_syntax_errors": False,
            "follows_conventions": True,
            "readability_score": 0.85
        }
    
    async def _analyze_security(self, article: str) -> Dict[str, Any]:
        """セキュリティの分析"""
        await asyncio.sleep(0.3)
        
        security_issues = []
        
        # 簡易的なセキュリティチェック
        if "eval(" in article or "exec(" in article:
            security_issues.append("Dangerous function usage detected")
        
        if "password" in article.lower() and "=" in article:
            security_issues.append("Potential hardcoded credentials")
        
        return {
            "security_score": 0.9 if not security_issues else 0.6,
            "issues": security_issues,
            "recommendations": ["Use environment variables for sensitive data"]
        }
    
    async def _analyze_performance(self, article: str) -> Dict[str, Any]:
        """パフォーマンスの分析"""
        await asyncio.sleep(0.4)
        
        return {
            "has_performance_considerations": True,
            "optimization_suggestions": [
                "Consider using async/await for I/O operations",
                "Implement caching for repeated calculations"
            ],
            "complexity_analysis": "O(n log n)"
        }
    
    async def _analyze_best_practices(self, article: str) -> Dict[str, Any]:
        """ベストプラクティスの分析"""
        await asyncio.sleep(0.3)
        
        return {
            "follows_solid_principles": True,
            "has_error_handling": True,
            "has_documentation": True,
            "test_coverage_mentioned": False
        }
    
    def _extract_code_blocks(self, article: str) -> List[str]:
        """コードブロックの抽出"""
        import re
        pattern = r'```[\w]*\n(.*?)\n```'
        return re.findall(pattern, article, re.DOTALL)
    
    def _build_evaluation_prompt(
        self,
        article: str,
        sub_results: List[Dict]
    ) -> str:
        """評価プロンプトの構築"""
        return f"""
        技術記事の評価を行ってください。
        
        記事内容:
        {article[:2000]}...
        
        サブ分析結果:
        {json.dumps(sub_results, indent=2)}
        
        以下の形式でJSON形式で評価を提供してください：
        {{
            "overall_score": 0-100,
            "technical_accuracy": {{
                "score": 0-100,
                "comments": "詳細なコメント"
            }},
            "code_quality": {{
                "score": 0-100,
                "comments": "詳細なコメント"
            }},
            "strengths": ["強み1", "強み2", ...],
            "weaknesses": ["弱み1", "弱み2", ...],
            "improvement_suggestions": ["提案1", "提案2", ...]
        }}
        """
    
    async def stream_process(self, input_data: Dict[str, Any]):
        """ストリーミング処理（オプション）"""
        
        article = input_data.get("article", "")
        
        # 進捗をストリーミング
        yield {"status": "starting", "progress": 0}
        
        # サブ分析を順次実行してストリーミング
        for i, (name, analyzer) in enumerate(self.sub_analyzers.items()):
            yield {
                "status": "analyzing",
                "current_analysis": name,
                "progress": (i / len(self.sub_analyzers)) * 50
            }
            
            result = await analyzer(article)
            
            yield {
                "status": "analysis_complete",
                "analysis_type": name,
                "result": result,
                "progress": ((i + 1) / len(self.sub_analyzers)) * 50
            }
        
        # LLM評価
        yield {"status": "evaluating", "progress": 75}
        
        evaluation = await self.evaluate(article)
        
        yield {
            "status": "complete",
            "progress": 100,
            "evaluation": evaluation
        }
```

## 4. MVPの実装優先順位

### 4.1 フェーズ1：基本機能（Week 1）
1. **環境設定とプロジェクト構造**
   - プロジェクトディレクトリ構造の作成
   - 依存関係のセットアップ
   - 環境変数設定

2. **LLMファクトリーの実装**
   - 環境変数からの設定読み込み
   - 3つのプロバイダー対応
   - 基本的なテスト

3. **非同期実行基盤**
   - AsyncExecutorクラス
   - 基本的な並列実行
   - タイムアウト処理

### 4.2 フェーズ2：エージェント実装（Week 2）
1. **基底エージェントクラス**
   - 共通インターフェース定義
   - LLM統合

2. **4つのペルソナエージェント**
   - 技術専門家
   - ビジネスユーザー
   - 一般読者
   - ドメイン専門家

3. **オーケストレーター**
   - 基本的なワークフロー管理
   - エージェント間の調整

### 4.3 フェーズ3：統合とテスト（Week 3）
1. **LangGraphグラフ構築**
   - ノードとエッジの定義
   - 状態管理

2. **エラーハンドリング**
   - 基本的なリトライ機構
   - エラーログ

3. **CLIツール**
   - コマンドラインインターフェース
   - 結果の表示

4. **統合テスト**
   - エンドツーエンドテスト
   - パフォーマンステスト

## 5. MVPの制限事項と今後の拡張

### 5.1 MVPの制限事項
- Web UIなし（CLIのみ）
- 固定の4ペルソナのみ
- 英語と日本語のみ対応
- ローカル実行のみ
- 結果の永続化なし

### 5.2 将来の拡張可能性
- Web API化
- カスタムペルソナの追加
- 多言語対応
- クラウドデプロイ
- 結果のデータベース保存
- リアルタイムストリーミング
- 複数記事のバッチ処理

## 6. まとめ

本MVP詳細仕様書では、以下を定義しました：

1. **LLMモデル切り替え**: 環境変数による柔軟な設定
2. **非同期実行**: 効率的な並列処理とエラーハンドリング
3. **実装優先順位**: 3週間でのMVP完成計画

これにより、実用的で拡張可能なマルチエージェント評価システムのMVPを構築できます。