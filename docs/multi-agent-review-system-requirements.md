# マルチエージェント記事評価システム要件定義書

## 1. システム概要

### 1.1 目的
記事作成タスクの品質を向上させるため、マルチエージェントによる仮想ペルソナ群を用いて評価・レビューを行い、記事の反響をシミュレーションするツールを構築する。

### 1.2 スコープ
- 仮想ペルソナによる記事評価システムの構築
- LangGraphを用いたエージェント間通信のグラフ構造定義
- 複数LLMモデルのサポート（環境変数による切り替え）
- 非同期実行による効率的な評価プロセス

### 1.3 システムアーキテクチャ
```
┌─────────────────────────────────────────────────────────────┐
│                     Article Review System                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌─────────────────────────┐       │
│  │   Article    │         │   Orchestrator Agent    │       │
│  │    Input     │────────>│   (Supervisor Pattern)  │       │
│  └──────────────┘         └──────────┬──────────────┘       │
│                                      │                        │
│                    ┌─────────────────┴────────────────┐      │
│                    │                                  │      │
│         ┌──────────▼──────────┐           ┌──────────▼──────┐│
│         │  Persona Agents     │           │  Analysis Agent ││
│         │  (Reviewer Group)   │           │                 ││
│         │ ┌─────┐ ┌─────┐    │           │ - Sentiment     ││
│         │ │Tech │ │Biz  │    │           │ - Readability   ││
│         │ │Expert│ │User │    │           │ - Structure     ││
│         │ └─────┘ └─────┘    │           └─────────────────┘│
│         │ ┌─────┐ ┌─────┐    │                              │
│         │ │Gen  │ │Domain│   │                              │
│         │ │Reader│ │Expert│   │                              │
│         │ └─────┘ └─────┘    │                              │
│         └─────────────────────┘                              │
│                                                               │
│                    ┌──────────────────┐                      │
│                    │  Result Aggregator│                      │
│                    │  & Report Generator                      │
│                    └──────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

## 2. 機能要件

### 2.1 コア機能

#### 2.1.1 記事評価機能
- **入力**: マークダウン形式またはプレーンテキストの記事
- **処理**: 複数の仮想ペルソナによる並行評価
- **出力**: 統合された評価レポート（JSON/Markdown形式）

#### 2.1.2 仮想ペルソナエージェント
各ペルソナは以下の属性を持つ：
- **役割** (role): 技術専門家、ビジネスユーザー、一般読者、ドメイン専門家など
- **評価基準** (criteria): 各ペルソナ特有の評価観点
- **重み** (weight): 評価における重要度

#### 2.1.3 評価基準
1. **技術的正確性** (Technical Accuracy)
2. **読みやすさ** (Readability)
3. **構成・論理性** (Structure & Logic)
4. **実用性** (Practicality)
5. **独創性** (Originality)
6. **対象読者適合性** (Target Audience Fit)

### 2.2 エージェント定義

#### 2.2.1 オーケストレーターエージェント (Supervisor Pattern)
```python
class OrchestratorAgent:
    """
    記事評価プロセス全体を管理するスーパーバイザーエージェント
    - タスクの分解と割り当て
    - エージェント間の調整
    - 結果の集約
    """
    capabilities = [
        "task_decomposition",
        "agent_coordination",
        "result_aggregation"
    ]
```

#### 2.2.2 ペルソナエージェント群
```python
class PersonaAgent:
    """
    特定の視点から記事を評価する仮想ペルソナエージェント
    """
    persona_types = {
        "tech_expert": {
            "focus": ["technical_accuracy", "code_quality", "best_practices"],
            "weight": 0.3
        },
        "business_user": {
            "focus": ["practical_value", "roi", "implementation_ease"],
            "weight": 0.25
        },
        "general_reader": {
            "focus": ["readability", "clarity", "engagement"],
            "weight": 0.25
        },
        "domain_expert": {
            "focus": ["domain_accuracy", "depth", "innovation"],
            "weight": 0.2
        }
    }
```

#### 2.2.3 分析エージェント
```python
class AnalysisAgent:
    """
    記事の客観的指標を分析するエージェント
    """
    analysis_types = [
        "sentiment_analysis",
        "readability_metrics",  # Flesch-Kincaid等
        "structure_analysis",
        "keyword_density",
        "technical_depth"
    ]
```

#### 2.2.4 レポート生成エージェント
```python
class ReportGeneratorAgent:
    """
    各エージェントの評価を統合し、最終レポートを生成
    """
    report_sections = [
        "executive_summary",
        "detailed_evaluations",
        "improvement_suggestions",
        "audience_impact_simulation"
    ]
```

### 2.3 LangGraphによるエージェント間通信

#### 2.3.1 グラフ構造定義
```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.command import Command
from typing import TypedDict, List, Dict, Literal

class ReviewSystemState(TypedDict):
    """評価システムの共有状態"""
    article_content: str
    persona_evaluations: Dict[str, Dict]
    analysis_results: Dict[str, any]
    final_report: Dict
    current_phase: Literal["analysis", "evaluation", "aggregation", "reporting"]
    
# グラフ構築
review_graph = StateGraph(ReviewSystemState)

# ノード追加
review_graph.add_node("orchestrator", orchestrator_agent)
review_graph.add_node("persona_evaluator", persona_evaluation_handler)
review_graph.add_node("analyzer", analysis_agent)
review_graph.add_node("report_generator", report_generator_agent)

# エッジ定義（条件付きルーティング）
review_graph.add_edge(START, "orchestrator")
review_graph.add_conditional_edges(
    "orchestrator",
    route_by_phase,
    {
        "analysis": "analyzer",
        "evaluation": "persona_evaluator",
        "reporting": "report_generator"
    }
)
```

#### 2.3.2 非同期並列実行パターン
```python
async def persona_evaluation_handler(state: ReviewSystemState):
    """複数ペルソナの並列評価実行"""
    personas = ["tech_expert", "business_user", "general_reader", "domain_expert"]
    
    # 並列実行のためのSend APIを使用
    evaluation_tasks = [
        Send(
            "evaluate_as_persona",
            {
                "persona": persona,
                "article": state["article_content"],
                "criteria": get_persona_criteria(persona)
            }
        ) for persona in personas
    ]
    
    return evaluation_tasks
```

## 3. 非機能要件

### 3.1 パフォーマンス要件
- **並行処理**: 最大10個のペルソナエージェントの同時実行
- **レスポンスタイム**: 
  - 1000文字の記事: 30秒以内
  - 5000文字の記事: 90秒以内
- **スケーラビリティ**: 水平スケーリング対応

### 3.2 信頼性要件
- **エラーハンドリング**: 個別エージェントの失敗が全体に影響しない
- **リトライ機構**: 失敗時の自動リトライ（最大3回）
- **タイムアウト**: 各エージェントに60秒のタイムアウト設定

### 3.3 運用性要件
- **ログ**: 構造化ログによる実行トレース
- **モニタリング**: 各エージェントの実行時間とステータス
- **設定管理**: 環境変数による柔軟な設定

## 4. 技術仕様

### 4.1 LLMモデル設定

#### 4.1.1 環境変数設定
```bash
# .env ファイル
# LLMプロバイダー選択（gemini/openai/claude）
LLM_PROVIDER=gemini

# 各プロバイダーのAPI設定
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# モデル指定（プロバイダーごと）
GEMINI_MODEL=gemini-2.5-flash
OPENAI_MODEL=gpt-4-turbo
CLAUDE_MODEL=claude-3-sonnet-20240229

# 共通設定
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
```

#### 4.1.2 モデルファクトリー実装
```python
from typing import Union
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

class LLMFactory:
    """環境変数に基づいてLLMインスタンスを生成"""
    
    @staticmethod
    def create_llm() -> Union[ChatGoogleGenerativeAI, ChatOpenAI, ChatAnthropic]:
        provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
        
        if provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                temperature=temperature,
                max_tokens=max_tokens,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
        elif provider == "openai":
            return ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
                temperature=temperature,
                max_tokens=max_tokens,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        elif provider == "claude":
            return ChatAnthropic(
                model=os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229"),
                temperature=temperature,
                max_tokens=max_tokens,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
```

### 4.2 エージェント実装パターン

#### 4.2.1 基底エージェントクラス
```python
from abc import ABC, abstractmethod
from langgraph.prebuilt import create_react_agent

class BaseReviewAgent(ABC):
    """全エージェントの基底クラス"""
    
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.llm = LLMFactory.create_llm()
        self.agent = create_react_agent(
            self.llm,
            tools=self.get_tools(),
            system_message=system_prompt
        )
    
    @abstractmethod
    def get_tools(self) -> List:
        """エージェント固有のツールを定義"""
        pass
    
    async def process(self, state: Dict) -> Dict:
        """非同期処理の実行"""
        try:
            result = await self.agent.ainvoke(state)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
```

#### 4.2.2 ペルソナエージェント実装例
```python
class TechExpertPersona(BaseReviewAgent):
    """技術専門家ペルソナの実装"""
    
    def __init__(self):
        system_prompt = """
        あなたは経験豊富な技術専門家です。
        以下の観点から記事を評価してください：
        1. 技術的正確性
        2. コードの品質
        3. ベストプラクティスの準拠
        4. セキュリティ考慮事項
        5. パフォーマンスへの影響
        """
        super().__init__("tech_expert", system_prompt)
    
    def get_tools(self) -> List:
        return [
            # 技術評価に必要なツール
            code_analyzer_tool,
            security_checker_tool,
            best_practices_validator_tool
        ]
```

### 4.3 非同期実行とエラーハンドリング

#### 4.3.1 サーキットブレーカーパターン
```python
from datetime import datetime, timedelta
import asyncio

class CircuitBreaker:
    """エージェントの障害を検出し、システムを保護"""
    
    def __init__(self, failure_threshold: int = 3, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise Exception(f"Circuit breaker is open for {func.__name__}")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)
        )
    
    def _on_success(self):
        self.failures = 0
        self.state = "closed"
    
    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()
        if self.failures >= self.failure_threshold:
            self.state = "open"
```

#### 4.3.2 タイムアウト付き並列実行
```python
async def execute_with_timeout(agent_func, timeout: int = 60):
    """タイムアウト付きでエージェントを実行"""
    try:
        return await asyncio.wait_for(
            agent_func(),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "error": f"Agent execution timed out after {timeout} seconds"
        }
```

## 5. 開発プロセス

### 5.1 チェックリストドリブン開発

#### 5.1.1 実装前チェックリスト
```markdown
## 実装前チェックリスト

### 設計フェーズ
- [ ] 各エージェントの役割と責任範囲が明確に定義されている
- [ ] エージェント間の依存関係が最小化されている
- [ ] エラーハンドリングの方針が決定されている
- [ ] パフォーマンス目標が設定されている

### 環境準備
- [ ] 必要な環境変数がすべて定義されている
- [ ] LLM APIキーが正しく設定されている
- [ ] 依存パッケージがすべてインストールされている

### セキュリティ
- [ ] APIキーがコードに直接記述されていない
- [ ] 入力検証が実装されている
- [ ] 出力のサニタイズが実装されている
```

#### 5.1.2 実装中チェックリスト
```markdown
## 実装中チェックリスト

### コード品質
- [ ] 各エージェントが単一責任原則に従っている
- [ ] 非同期処理が適切に実装されている
- [ ] エラーハンドリングが実装されている
- [ ] ログ出力が適切に配置されている

### テスト
- [ ] 単体テストが各エージェントに対して作成されている
- [ ] 統合テストがエージェント間通信に対して作成されている
- [ ] エラーケースのテストが含まれている
- [ ] パフォーマンステストが実施されている
```

#### 5.1.3 デプロイ前チェックリスト
```markdown
## デプロイ前チェックリスト

### 機能確認
- [ ] すべての評価基準が正しく動作する
- [ ] 並列実行が期待通りに動作する
- [ ] タイムアウトが適切に機能する
- [ ] エラー時のフォールバックが動作する

### パフォーマンス
- [ ] 目標レスポンスタイムを満たしている
- [ ] メモリ使用量が許容範囲内
- [ ] API呼び出し回数が想定内

### 運用準備
- [ ] ログ出力が運用に必要な情報を含んでいる
- [ ] モニタリング設定が完了している
- [ ] ドキュメントが最新化されている
```

### 5.2 テストドリブン開発

#### 5.2.1 テスト戦略
```python
# tests/test_agents.py
import pytest
from unittest.mock import Mock, patch
import asyncio

class TestPersonaAgents:
    """ペルソナエージェントのテストスイート"""
    
    @pytest.fixture
    def mock_llm(self):
        """LLMのモック"""
        with patch('src.agents.LLMFactory.create_llm') as mock:
            mock.return_value = Mock()
            yield mock
    
    @pytest.mark.asyncio
    async def test_tech_expert_evaluation(self, mock_llm):
        """技術専門家エージェントの評価テスト"""
        agent = TechExpertPersona()
        test_article = "# テスト記事\nこれはテスト用の技術記事です。"
        
        result = await agent.process({
            "article_content": test_article,
            "evaluation_criteria": ["technical_accuracy", "code_quality"]
        })
        
        assert result["status"] == "success"
        assert "technical_accuracy" in result["result"]
        assert "code_quality" in result["result"]
    
    @pytest.mark.asyncio
    async def test_parallel_persona_execution(self):
        """複数ペルソナの並列実行テスト"""
        personas = [
            TechExpertPersona(),
            BusinessUserPersona(),
            GeneralReaderPersona()
        ]
        
        start_time = asyncio.get_event_loop().time()
        
        results = await asyncio.gather(*[
            persona.process({"article_content": "test"})
            for persona in personas
        ])
        
        end_time = asyncio.get_event_loop().time()
        
        # 並列実行の確認（3つのエージェントが順次実行されるより速い）
        assert end_time - start_time < 3.0  # 各1秒と仮定
        assert all(r["status"] == "success" for r in results)
```

#### 5.2.2 統合テスト
```python
# tests/test_integration.py
import pytest
from langgraph.checkpoint.memory import MemorySaver

class TestReviewSystemIntegration:
    """評価システム全体の統合テスト"""
    
    @pytest.fixture
    def review_system(self):
        """評価システムのセットアップ"""
        checkpointer = MemorySaver()
        graph = build_review_graph()
        return graph.compile(checkpointer=checkpointer)
    
    @pytest.mark.asyncio
    async def test_full_review_workflow(self, review_system):
        """完全な評価ワークフローのテスト"""
        test_article = """
        # AIエージェントシステムの実装
        
        本記事では、LangGraphを使用したマルチエージェントシステムの
        実装方法について解説します。
        
        ## 主な特徴
        - 非同期実行による高速化
        - 柔軟なエージェント間通信
        - スケーラブルなアーキテクチャ
        """
        
        result = await review_system.ainvoke({
            "article_content": test_article,
            "current_phase": "analysis"
        })
        
        # 結果の検証
        assert result["final_report"] is not None
        assert "executive_summary" in result["final_report"]
        assert len(result["persona_evaluations"]) >= 4
        assert all(
            eval["status"] == "success" 
            for eval in result["persona_evaluations"].values()
        )
```

#### 5.2.3 パフォーマンステスト
```python
# tests/test_performance.py
import time
import pytest
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:
    """パフォーマンステストスイート"""
    
    @pytest.mark.performance
    def test_response_time_1000_chars(self, review_system):
        """1000文字記事のレスポンスタイムテスト"""
        article = "x" * 1000
        
        start = time.time()
        result = review_system.invoke({"article_content": article})
        end = time.time()
        
        assert end - start < 30  # 30秒以内
        assert result["status"] == "completed"
    
    @pytest.mark.performance
    def test_concurrent_reviews(self, review_system):
        """並行レビューのテスト"""
        articles = [f"Article {i}: " + "x" * 500 for i in range(5)]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(
                    review_system.invoke,
                    {"article_content": article}
                )
                for article in articles
            ]
            
            results = [f.result() for f in futures]
        
        assert all(r["status"] == "completed" for r in results)
```

## 6. プロジェクト構成

### 6.1 ディレクトリ構造
```
multi-agent-review-system/
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py              # 基底エージェントクラス
│   │   ├── orchestrator.py      # オーケストレーター
│   │   ├── personas/            # ペルソナエージェント群
│   │   │   ├── __init__.py
│   │   │   ├── tech_expert.py
│   │   │   ├── business_user.py
│   │   │   ├── general_reader.py
│   │   │   └── domain_expert.py
│   │   ├── analyzer.py          # 分析エージェント
│   │   └── report_generator.py  # レポート生成エージェント
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── builder.py           # グラフ構築
│   │   ├── states.py            # 状態定義
│   │   └── routing.py           # ルーティングロジック
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── analysis_tools.py    # 分析ツール
│   │   └── evaluation_tools.py  # 評価ツール
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── llm_factory.py       # LLMファクトリー
│   │   ├── circuit_breaker.py   # サーキットブレーカー
│   │   └── logger.py            # ロギング設定
│   └── main.py                  # エントリーポイント
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_tools.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── test_workflow.py
│   │   └── test_graph.py
│   └── performance/
│       └── test_performance.py
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── deployment.md
├── config/
│   ├── .env.example
│   └── logging.yaml
├── scripts/
│   ├── setup.sh
│   └── run_evaluation.py
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .gitignore
└── README.md
```

### 6.2 依存関係
```txt
# requirements.txt
langgraph>=0.2.0
langchain>=0.2.0
langchain-google-genai>=1.0.0
langchain-openai>=0.1.0
langchain-anthropic>=0.1.0
python-dotenv>=1.0.0
pydantic>=2.0.0
structlog>=24.0.0
asyncio>=3.4.3
aiohttp>=3.9.0

# requirements-dev.txt
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
black>=24.0.0
flake8>=7.0.0
mypy>=1.8.0
```

## 7. 今後の拡張性

### 7.1 機能拡張の可能性
1. **リアルタイム評価**: ストリーミング対応による執筆中の評価
2. **カスタムペルソナ**: ユーザー定義のペルソナ追加
3. **多言語対応**: 英語以外の言語サポート
4. **視覚的分析**: グラフやチャートによる評価結果の可視化
5. **履歴管理**: 過去の評価履歴と改善トレンドの追跡

### 7.2 統合の可能性
1. **CI/CDパイプライン**: PR時の自動評価
2. **エディタプラグイン**: VSCode、IntelliJ等との統合
3. **APIサービス**: RESTful API化によるサービス提供
4. **Slackボット**: チャットベースでの評価依頼

## 8. まとめ

本要件定義書は、LangGraphを活用したマルチエージェント記事評価システムの構築指針を示しています。最新のLangGraph機能（Command API、並列実行、非同期処理）を活用し、スケーラブルで拡張可能なシステムアーキテクチャを実現します。

チェックリストドリブンとテストドリブンの開発アプローチにより、品質の高いシステム構築を目指します。