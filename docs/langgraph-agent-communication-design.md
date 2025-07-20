# LangGraphエージェント間通信グラフ構造設計書

## 1. 概要

本設計書では、マルチエージェント記事評価システムにおけるLangGraphを用いたエージェント間通信のグラフ構造を定義します。最新のLangGraph機能（Command API、Send API、並列実行パターン）を活用し、効率的で拡張可能な通信アーキテクチャを実現します。

## 2. グラフ構造の全体像

### 2.1 メイングラフ構造
```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.command import Command
from langgraph.types import Send
from typing import TypedDict, List, Dict, Literal, Annotated
from langgraph.graph import add_messages

class ArticleReviewState(TypedDict):
    """記事評価システムのグローバル状態"""
    # 基本情報
    article_content: str
    article_metadata: Dict[str, any]  # タイトル、著者、カテゴリ等
    
    # フェーズ管理
    current_phase: Literal["initialization", "analysis", "evaluation", "aggregation", "reporting", "completed"]
    phase_status: Dict[str, str]  # 各フェーズの完了状態
    
    # エージェント管理
    active_agents: List[str]
    agent_status: Dict[str, str]  # 各エージェントの状態
    
    # 評価データ
    analysis_results: Dict[str, any]  # 分析エージェントの結果
    persona_evaluations: Dict[str, Dict]  # ペルソナ別評価結果
    aggregated_scores: Dict[str, float]  # 統合スコア
    
    # レポート
    final_report: Dict
    improvement_suggestions: List[Dict]
    
    # メッセージ履歴（自動追加）
    messages: Annotated[list, add_messages]
    
    # エラーハンドリング
    errors: List[Dict[str, str]]
    retry_count: Dict[str, int]
```

### 2.2 エージェント階層構造
```
┌─────────────────────────────────────────────────────────┐
│                   Orchestrator Agent                      │
│              (スーパーバイザーパターン)                   │
└────────────────────┬───────────────────────────────────┘
                     │
    ┌────────────────┼────────────────┬──────────────────┐
    │                │                │                  │
┌───▼────┐    ┌─────▼─────┐    ┌────▼─────┐    ┌──────▼──────┐
│Analysis │    │ Persona    │    │Aggregator│    │  Reporter   │
│ Agent   │    │Coordinator │    │  Agent   │    │   Agent     │
└─────────┘    └─────┬─────┘    └──────────┘    └─────────────┘
                     │
         ┌───────────┴───────────┬─────────────┬──────────────┐
         │                       │             │              │
   ┌─────▼─────┐          ┌─────▼─────┐ ┌────▼────┐  ┌──────▼──────┐
   │Tech Expert│          │Business   │ │General  │  │Domain Expert│
   │  Persona  │          │User Persona│ │Reader   │  │  Persona    │
   └───────────┘          └───────────┘ └─────────┘  └─────────────┘
```

## 3. 詳細なグラフ定義

### 3.1 メイングラフの構築
```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

def build_article_review_graph() -> CompiledGraph:
    """記事評価システムのメイングラフを構築"""
    
    # グラフインスタンスの作成
    workflow = StateGraph(ArticleReviewState)
    
    # ノードの追加
    workflow.add_node("orchestrator", OrchestratorAgent())
    workflow.add_node("analyzer", AnalysisAgent())
    workflow.add_node("persona_coordinator", PersonaCoordinator())
    workflow.add_node("persona_worker", persona_worker)  # 動的ワーカー
    workflow.add_node("aggregator", AggregatorAgent())
    workflow.add_node("reporter", ReporterAgent())
    workflow.add_node("error_handler", ErrorHandler())
    
    # エントリーポイント
    workflow.add_edge(START, "orchestrator")
    
    # 条件付きルーティング
    workflow.add_conditional_edges(
        "orchestrator",
        orchestrator_router,
        {
            "analyze": "analyzer",
            "evaluate": "persona_coordinator",
            "aggregate": "aggregator",
            "report": "reporter",
            "error": "error_handler",
            "complete": END
        }
    )
    
    # フェーズ間の遷移
    workflow.add_edge("analyzer", "orchestrator")
    workflow.add_edge("persona_coordinator", "orchestrator")
    workflow.add_edge("aggregator", "orchestrator")
    workflow.add_edge("reporter", "orchestrator")
    workflow.add_edge("error_handler", "orchestrator")
    
    # チェックポイント機能を有効化
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)
```

### 3.2 オーケストレーターエージェント
```python
class OrchestratorAgent:
    """全体のワークフローを管理するスーパーバイザーエージェント"""
    
    def __init__(self):
        self.llm = LLMFactory.create_llm()
        self.phase_transitions = {
            "initialization": "analysis",
            "analysis": "evaluation",
            "evaluation": "aggregation",
            "aggregation": "reporting",
            "reporting": "completed"
        }
    
    async def __call__(self, state: ArticleReviewState) -> Command:
        """オーケストレーターのメイン処理"""
        
        current_phase = state["current_phase"]
        
        # エラーチェック
        if state.get("errors") and len(state["errors"]) > 0:
            return Command(
                goto="error",
                update={"messages": [("system", "Error detected, handling...")]}
            )
        
        # フェーズ完了チェック
        if self._is_phase_complete(state, current_phase):
            next_phase = self.phase_transitions.get(current_phase, "completed")
            
            if next_phase == "completed":
                return Command(
                    goto="complete",
                    update={
                        "current_phase": "completed",
                        "messages": [("system", "Review process completed successfully")]
                    }
                )
            
            # 次のフェーズへ遷移
            return Command(
                goto=self._get_next_agent(next_phase),
                update={
                    "current_phase": next_phase,
                    "phase_status": {**state["phase_status"], current_phase: "completed"}
                }
            )
        
        # 現在のフェーズを継続
        return Command(
            goto=self._get_next_agent(current_phase),
            update={"messages": [("system", f"Continuing {current_phase} phase")]}
        )
    
    def _is_phase_complete(self, state: ArticleReviewState, phase: str) -> bool:
        """フェーズ完了判定"""
        if phase == "analysis":
            return bool(state.get("analysis_results"))
        elif phase == "evaluation":
            required_personas = ["tech_expert", "business_user", "general_reader", "domain_expert"]
            return all(p in state.get("persona_evaluations", {}) for p in required_personas)
        elif phase == "aggregation":
            return bool(state.get("aggregated_scores"))
        elif phase == "reporting":
            return bool(state.get("final_report"))
        return False
    
    def _get_next_agent(self, phase: str) -> str:
        """フェーズに対応するエージェントを返す"""
        phase_agent_map = {
            "analysis": "analyze",
            "evaluation": "evaluate",
            "aggregation": "aggregate",
            "reporting": "report"
        }
        return phase_agent_map.get(phase, "error")
```

### 3.3 分析エージェント（非同期実行）
```python
class AnalysisAgent:
    """記事の客観的分析を行うエージェント"""
    
    def __init__(self):
        self.llm = LLMFactory.create_llm()
        self.analyzers = {
            "readability": self.analyze_readability,
            "sentiment": self.analyze_sentiment,
            "structure": self.analyze_structure,
            "keywords": self.analyze_keywords,
            "technical_depth": self.analyze_technical_depth
        }
    
    async def __call__(self, state: ArticleReviewState) -> Dict:
        """並列分析の実行"""
        article = state["article_content"]
        
        # 非同期で全分析を並列実行
        analysis_tasks = [
            analyzer(article) for analyzer in self.analyzers.values()
        ]
        
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # 結果の集約
        analysis_results = {}
        errors = []
        
        for (analysis_type, analyzer), result in zip(self.analyzers.items(), results):
            if isinstance(result, Exception):
                errors.append({
                    "agent": "analyzer",
                    "type": analysis_type,
                    "error": str(result)
                })
            else:
                analysis_results[analysis_type] = result
        
        return {
            "analysis_results": analysis_results,
            "errors": state.get("errors", []) + errors,
            "messages": [("assistant", f"Analysis completed: {len(analysis_results)} successful, {len(errors)} errors")]
        }
    
    async def analyze_readability(self, text: str) -> Dict:
        """読みやすさ分析"""
        # Flesch-Kincaid等の指標を計算
        await asyncio.sleep(0.5)  # シミュレーション
        return {
            "flesch_reading_ease": 65.5,
            "flesch_kincaid_grade": 8.2,
            "gunning_fog": 10.1
        }
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """感情分析"""
        prompt = f"Analyze the sentiment of this article:\n{text[:1000]}..."
        response = await self.llm.ainvoke(prompt)
        return {"sentiment": "positive", "confidence": 0.85}
    
    async def analyze_structure(self, text: str) -> Dict:
        """構造分析"""
        return {
            "sections": 5,
            "paragraphs": 12,
            "average_paragraph_length": 85
        }
    
    async def analyze_keywords(self, text: str) -> Dict:
        """キーワード分析"""
        return {
            "main_topics": ["AI", "agents", "evaluation"],
            "keyword_density": {"AI": 0.03, "agents": 0.025}
        }
    
    async def analyze_technical_depth(self, text: str) -> Dict:
        """技術的深さの分析"""
        return {
            "technical_level": "intermediate",
            "code_snippets": 3,
            "technical_terms_ratio": 0.15
        }
```

### 3.4 ペルソナコーディネーター（動的並列実行）
```python
class PersonaCoordinator:
    """ペルソナエージェントの並列実行を管理"""
    
    def __init__(self):
        self.persona_configs = {
            "tech_expert": {
                "system_prompt": "You are a senior technical expert...",
                "evaluation_criteria": ["technical_accuracy", "code_quality", "best_practices"],
                "weight": 0.3
            },
            "business_user": {
                "system_prompt": "You are a business stakeholder...",
                "evaluation_criteria": ["roi", "practicality", "business_value"],
                "weight": 0.25
            },
            "general_reader": {
                "system_prompt": "You are a general reader...",
                "evaluation_criteria": ["clarity", "engagement", "accessibility"],
                "weight": 0.25
            },
            "domain_expert": {
                "system_prompt": "You are a domain expert...",
                "evaluation_criteria": ["domain_accuracy", "innovation", "depth"],
                "weight": 0.2
            }
        }
    
    def __call__(self, state: ArticleReviewState) -> List[Send]:
        """ペルソナワーカーへのタスク送信"""
        
        # 既に評価済みのペルソナを除外
        completed_personas = set(state.get("persona_evaluations", {}).keys())
        pending_personas = [
            p for p in self.persona_configs.keys() 
            if p not in completed_personas
        ]
        
        if not pending_personas:
            # 全ペルソナ完了
            return {
                "messages": [("system", "All persona evaluations completed")],
                "agent_status": {**state.get("agent_status", {}), "persona_coordinator": "completed"}
            }
        
        # Send APIで並列実行
        sends = []
        for persona_type in pending_personas:
            config = self.persona_configs[persona_type]
            
            sends.append(Send(
                "persona_worker",
                {
                    "persona_type": persona_type,
                    "persona_config": config,
                    "article_content": state["article_content"],
                    "analysis_results": state.get("analysis_results", {}),
                    "thread_id": f"persona_{persona_type}_{state.get('thread_id', 'default')}"
                }
            ))
        
        return sends
```

### 3.5 ペルソナワーカー（非同期評価実行）
```python
async def persona_worker(state: Dict) -> Dict:
    """個別ペルソナの評価を実行"""
    
    persona_type = state["persona_type"]
    config = state["persona_config"]
    article = state["article_content"]
    analysis = state.get("analysis_results", {})
    
    # LLMインスタンスの作成
    llm = LLMFactory.create_llm()
    
    # 評価プロンプトの構築
    evaluation_prompt = f"""
    {config['system_prompt']}
    
    Article to evaluate:
    {article}
    
    Analysis data:
    {json.dumps(analysis, indent=2)}
    
    Please evaluate this article based on these criteria:
    {', '.join(config['evaluation_criteria'])}
    
    Provide:
    1. Score (0-100) for each criterion
    2. Overall score
    3. Strengths (3-5 points)
    4. Weaknesses (3-5 points)
    5. Specific improvement suggestions
    
    Format your response as JSON.
    """
    
    try:
        # 非同期でLLM評価を実行
        response = await llm.ainvoke(evaluation_prompt)
        evaluation_result = parse_llm_json_response(response.content)
        
        # 結果の構造化
        persona_evaluation = {
            "persona_type": persona_type,
            "scores": evaluation_result.get("scores", {}),
            "overall_score": evaluation_result.get("overall_score", 0),
            "strengths": evaluation_result.get("strengths", []),
            "weaknesses": evaluation_result.get("weaknesses", []),
            "suggestions": evaluation_result.get("suggestions", []),
            "weight": config["weight"],
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "persona_evaluations": {persona_type: persona_evaluation},
            "messages": [("assistant", f"{persona_type} evaluation completed")]
        }
        
    except Exception as e:
        return {
            "errors": [{
                "agent": "persona_worker",
                "persona": persona_type,
                "error": str(e)
            }],
            "messages": [("system", f"Error in {persona_type} evaluation: {str(e)}")]
        }
```

### 3.6 集約エージェント
```python
class AggregatorAgent:
    """評価結果を集約し、総合スコアを算出"""
    
    def __init__(self):
        self.aggregation_strategies = {
            "weighted_average": self.weighted_average,
            "normalized_sum": self.normalized_sum,
            "consensus_based": self.consensus_based
        }
    
    async def __call__(self, state: ArticleReviewState) -> Dict:
        """評価結果の集約処理"""
        
        persona_evaluations = state.get("persona_evaluations", {})
        
        if not persona_evaluations:
            return {
                "errors": [{"agent": "aggregator", "error": "No evaluations to aggregate"}]
            }
        
        # 各戦略で集約を実行
        aggregated_scores = {}
        
        for strategy_name, strategy_func in self.aggregation_strategies.items():
            aggregated_scores[strategy_name] = strategy_func(persona_evaluations)
        
        # 改善提案の統合
        all_suggestions = []
        suggestion_priorities = {}
        
        for persona, evaluation in persona_evaluations.items():
            suggestions = evaluation.get("suggestions", [])
            for suggestion in suggestions:
                # 重複する提案をマージし、優先度を計算
                suggestion_key = self._normalize_suggestion(suggestion)
                if suggestion_key not in suggestion_priorities:
                    suggestion_priorities[suggestion_key] = {
                        "text": suggestion,
                        "personas": [],
                        "priority_score": 0
                    }
                
                suggestion_priorities[suggestion_key]["personas"].append(persona)
                suggestion_priorities[suggestion_key]["priority_score"] += evaluation.get("weight", 0.25)
        
        # 優先度順にソート
        improvement_suggestions = sorted(
            [
                {
                    "suggestion": item["text"],
                    "supported_by": item["personas"],
                    "priority": item["priority_score"]
                }
                for item in suggestion_priorities.values()
            ],
            key=lambda x: x["priority"],
            reverse=True
        )[:10]  # Top 10の提案
        
        return {
            "aggregated_scores": aggregated_scores,
            "improvement_suggestions": improvement_suggestions,
            "messages": [("assistant", "Evaluation aggregation completed")]
        }
    
    def weighted_average(self, evaluations: Dict) -> Dict:
        """重み付き平均による集約"""
        weighted_scores = {}
        total_weight = 0
        
        for persona, evaluation in evaluations.items():
            weight = evaluation.get("weight", 0.25)
            scores = evaluation.get("scores", {})
            
            for criterion, score in scores.items():
                if criterion not in weighted_scores:
                    weighted_scores[criterion] = 0
                weighted_scores[criterion] += score * weight
            
            total_weight += weight
        
        # 正規化
        if total_weight > 0:
            for criterion in weighted_scores:
                weighted_scores[criterion] /= total_weight
        
        return {
            "method": "weighted_average",
            "scores": weighted_scores,
            "overall": sum(weighted_scores.values()) / len(weighted_scores) if weighted_scores else 0
        }
    
    def normalized_sum(self, evaluations: Dict) -> Dict:
        """正規化和による集約"""
        # 実装省略
        return {"method": "normalized_sum", "scores": {}, "overall": 0}
    
    def consensus_based(self, evaluations: Dict) -> Dict:
        """コンセンサスベースの集約"""
        # 実装省略
        return {"method": "consensus_based", "scores": {}, "overall": 0}
    
    def _normalize_suggestion(self, suggestion: str) -> str:
        """提案の正規化（重複検出用）"""
        # 簡易的な正規化
        return suggestion.lower().strip()[:50]
```

### 3.7 レポート生成エージェント
```python
class ReporterAgent:
    """最終レポートを生成"""
    
    def __init__(self):
        self.llm = LLMFactory.create_llm()
        self.report_sections = [
            "executive_summary",
            "detailed_analysis",
            "persona_perspectives",
            "improvement_roadmap",
            "audience_impact_simulation"
        ]
    
    async def __call__(self, state: ArticleReviewState) -> Dict:
        """レポート生成処理"""
        
        # レポート生成に必要なデータを集約
        report_data = {
            "article_metadata": state.get("article_metadata", {}),
            "analysis_results": state.get("analysis_results", {}),
            "persona_evaluations": state.get("persona_evaluations", {}),
            "aggregated_scores": state.get("aggregated_scores", {}),
            "improvement_suggestions": state.get("improvement_suggestions", [])
        }
        
        # 各セクションを並列生成
        section_tasks = [
            self._generate_section(section, report_data)
            for section in self.report_sections
        ]
        
        sections = await asyncio.gather(*section_tasks)
        
        # レポートの組み立て
        final_report = {
            "generated_at": datetime.now().isoformat(),
            "article_title": state.get("article_metadata", {}).get("title", "Untitled"),
            "sections": dict(zip(self.report_sections, sections)),
            "overall_score": self._calculate_overall_score(state),
            "recommendation": self._generate_recommendation(state)
        }
        
        return {
            "final_report": final_report,
            "messages": [("assistant", "Final report generated successfully")]
        }
    
    async def _generate_section(self, section_name: str, data: Dict) -> Dict:
        """個別セクションの生成"""
        
        section_prompts = {
            "executive_summary": """
            Create an executive summary of the article evaluation including:
            - Overall quality assessment
            - Key strengths and weaknesses
            - Primary recommendations
            Keep it concise (200-300 words).
            """,
            "detailed_analysis": """
            Provide a detailed analysis covering:
            - Technical accuracy assessment
            - Content structure evaluation
            - Writing quality analysis
            - Target audience alignment
            """,
            "persona_perspectives": """
            Summarize each persona's perspective:
            - What each persona valued
            - Key concerns from each viewpoint
            - Areas of agreement and disagreement
            """,
            "improvement_roadmap": """
            Create a prioritized improvement roadmap:
            - Quick wins (immediate fixes)
            - Medium-term improvements
            - Long-term enhancements
            Include effort estimates and impact scores.
            """,
            "audience_impact_simulation": """
            Simulate potential audience reactions:
            - Predicted engagement levels
            - Likely questions or concerns
            - Sharing and virality potential
            - SEO and discoverability factors
            """
        }
        
        prompt = f"""
        {section_prompts.get(section_name, "Generate a section for: " + section_name)}
        
        Based on this data:
        {json.dumps(data, indent=2)[:3000]}...
        
        Format as structured JSON with clear subsections.
        """
        
        response = await self.llm.ainvoke(prompt)
        return parse_llm_json_response(response.content)
    
    def _calculate_overall_score(self, state: ArticleReviewState) -> float:
        """総合スコアの計算"""
        aggregated = state.get("aggregated_scores", {})
        if "weighted_average" in aggregated:
            return aggregated["weighted_average"].get("overall", 0)
        return 0
    
    def _generate_recommendation(self, state: ArticleReviewState) -> str:
        """最終推奨事項の生成"""
        score = self._calculate_overall_score(state)
        
        if score >= 85:
            return "Excellent quality - ready for publication with minor edits"
        elif score >= 70:
            return "Good quality - recommended for publication after addressing key suggestions"
        elif score >= 55:
            return "Moderate quality - significant improvements needed before publication"
        else:
            return "Major revision required - consider restructuring based on feedback"
```

### 3.8 エラーハンドリング
```python
class ErrorHandler:
    """エラー処理とリカバリー"""
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    async def __call__(self, state: ArticleReviewState) -> Command:
        """エラー処理のメイン処理"""
        
        errors = state.get("errors", [])
        if not errors:
            return Command(
                goto="orchestrator",
                update={"messages": [("system", "No errors to handle")]}
            )
        
        # エラーの分類と処理
        recoverable_errors = []
        critical_errors = []
        
        for error in errors:
            if self._is_recoverable(error):
                recoverable_errors.append(error)
            else:
                critical_errors.append(error)
        
        # クリティカルエラーがある場合は処理を停止
        if critical_errors:
            return Command(
                goto="complete",
                update={
                    "current_phase": "failed",
                    "messages": [("error", f"Critical errors encountered: {critical_errors}")]
                }
            )
        
        # リトライ処理
        retry_actions = []
        updated_retry_count = state.get("retry_count", {}).copy()
        
        for error in recoverable_errors:
            agent = error.get("agent", "unknown")
            retry_count = updated_retry_count.get(agent, 0)
            
            if retry_count < self.max_retries:
                retry_actions.append({
                    "agent": agent,
                    "action": "retry",
                    "delay": self.retry_delay * (retry_count + 1)
                })
                updated_retry_count[agent] = retry_count + 1
            else:
                critical_errors.append({
                    **error,
                    "reason": f"Max retries ({self.max_retries}) exceeded"
                })
        
        # エラーをクリアして再試行
        if retry_actions:
            return Command(
                goto="orchestrator",
                update={
                    "errors": [],  # エラーをクリア
                    "retry_count": updated_retry_count,
                    "messages": [("system", f"Retrying {len(retry_actions)} failed operations")]
                }
            )
        
        # すべてのリトライが失敗した場合
        return Command(
            goto="complete",
            update={
                "current_phase": "failed",
                "messages": [("error", "All retry attempts exhausted")]
            }
        )
    
    def _is_recoverable(self, error: Dict) -> bool:
        """エラーが回復可能かどうかを判定"""
        recoverable_types = [
            "timeout",
            "rate_limit",
            "connection_error",
            "temporary_failure"
        ]
        
        error_type = error.get("type", "unknown").lower()
        return any(rt in error_type for rt in recoverable_types)
```

## 4. ルーティングロジック

### 4.1 動的ルーティング関数
```python
def orchestrator_router(state: ArticleReviewState) -> str:
    """オーケストレーターからの動的ルーティング"""
    
    current_phase = state.get("current_phase", "initialization")
    errors = state.get("errors", [])
    
    # エラーがある場合
    if errors:
        return "error"
    
    # フェーズ別ルーティング
    phase_routes = {
        "initialization": "analyze",
        "analysis": "analyze",
        "evaluation": "evaluate",
        "aggregation": "aggregate",
        "reporting": "report",
        "completed": "complete"
    }
    
    return phase_routes.get(current_phase, "error")

def conditional_persona_routing(state: Dict) -> Command:
    """ペルソナ評価の条件付きルーティング"""
    
    persona_type = state.get("persona_type")
    evaluation_result = state.get("evaluation_result")
    
    # 評価品質チェック
    if evaluation_result and evaluation_result.get("quality_score", 0) < 0.5:
        # 品質が低い場合は再評価
        return Command(
            goto="persona_worker",
            update={
                "retry_reason": "Low quality evaluation",
                "previous_result": evaluation_result
            }
        )
    
    # 依存関係チェック
    dependencies = {
        "domain_expert": ["tech_expert"],  # ドメイン専門家は技術専門家の評価を参照
        "business_user": ["general_reader"]  # ビジネスユーザーは一般読者の視点を参照
    }
    
    required_deps = dependencies.get(persona_type, [])
    completed_personas = state.get("completed_personas", [])
    
    if not all(dep in completed_personas for dep in required_deps):
        # 依存関係が満たされていない場合は待機
        return Command(
            goto="wait",
            update={"waiting_for": required_deps}
        )
    
    # 正常完了
    return Command(
        goto="orchestrator",
        update={"completed_personas": completed_personas + [persona_type]}
    )
```

## 5. 実装上の考慮事項

### 5.1 状態管理のベストプラクティス
```python
from functools import wraps
import copy

def preserve_state(keys_to_preserve: List[str]):
    """指定されたキーの状態を保持するデコレーター"""
    def decorator(func):
        @wraps(func)
        async def wrapper(state: Dict) -> Dict:
            # 保持すべき状態をバックアップ
            preserved = {k: copy.deepcopy(state.get(k)) for k in keys_to_preserve}
            
            # 関数実行
            result = await func(state)
            
            # 保持すべき状態を復元（上書きされていない場合）
            for key, value in preserved.items():
                if key not in result:
                    result[key] = value
            
            return result
        return wrapper
    return decorator

# 使用例
@preserve_state(["article_content", "article_metadata"])
async def some_agent_function(state: Dict) -> Dict:
    # article_contentとarticle_metadataは自動的に保持される
    return {"new_data": "value"}
```

### 5.2 並列実行の最適化
```python
class ParallelExecutionOptimizer:
    """並列実行を最適化するユーティリティ"""
    
    @staticmethod
    def batch_by_dependencies(tasks: List[Dict]) -> List[List[Dict]]:
        """依存関係に基づいてタスクをバッチ化"""
        
        # 依存関係グラフの構築
        dependency_graph = {}
        for task in tasks:
            task_id = task["id"]
            dependencies = task.get("dependencies", [])
            dependency_graph[task_id] = dependencies
        
        # トポロジカルソートでバッチを作成
        batches = []
        completed = set()
        
        while len(completed) < len(tasks):
            current_batch = []
            
            for task in tasks:
                task_id = task["id"]
                if task_id not in completed:
                    deps = dependency_graph.get(task_id, [])
                    if all(dep in completed for dep in deps):
                        current_batch.append(task)
            
            if not current_batch:
                raise ValueError("Circular dependency detected")
            
            batches.append(current_batch)
            completed.update(task["id"] for task in current_batch)
        
        return batches
    
    @staticmethod
    async def execute_batches(batches: List[List[Dict]], executor_func) -> List[Dict]:
        """バッチを順次実行し、バッチ内は並列実行"""
        
        all_results = []
        
        for batch in batches:
            # バッチ内のタスクを並列実行
            batch_results = await asyncio.gather(*[
                executor_func(task) for task in batch
            ])
            all_results.extend(batch_results)
        
        return all_results
```

### 5.3 ストリーミング対応
```python
class StreamingReporter:
    """リアルタイムストリーミング対応のレポーター"""
    
    def __init__(self):
        self.llm = LLMFactory.create_llm()
    
    async def stream_report_generation(self, state: ArticleReviewState):
        """レポートをストリーミング生成"""
        
        # ストリーミング用のプロンプト
        prompt = self._build_report_prompt(state)
        
        # チャンクごとにストリーミング
        async for chunk in self.llm.astream(prompt):
            # 中間結果を送信
            yield {
                "type": "stream_chunk",
                "content": chunk.content,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "section": self._detect_section(chunk.content)
                }
            }
            
            # セクション完了を検出
            if self._is_section_complete(chunk.content):
                yield {
                    "type": "section_complete",
                    "section": self._detect_section(chunk.content)
                }
    
    def _detect_section(self, content: str) -> str:
        """コンテンツからセクションを検出"""
        # 実装省略
        return "unknown"
    
    def _is_section_complete(self, content: str) -> bool:
        """セクションが完了したかを判定"""
        # 実装省略
        return False
```

## 6. 実行例

### 6.1 グラフの実行
```python
async def main():
    """メイン実行関数"""
    
    # グラフの構築
    review_graph = build_article_review_graph()
    
    # テスト記事
    test_article = """
    # Introduction to LangGraph Multi-Agent Systems
    
    This article explores the implementation of multi-agent systems
    using LangGraph, focusing on parallel execution patterns and
    dynamic agent coordination...
    """
    
    # 初期状態の設定
    initial_state = {
        "article_content": test_article,
        "article_metadata": {
            "title": "Introduction to LangGraph Multi-Agent Systems",
            "author": "AI Assistant",
            "category": "Technical",
            "word_count": len(test_article.split())
        },
        "current_phase": "initialization",
        "phase_status": {},
        "active_agents": [],
        "agent_status": {},
        "messages": [],
        "errors": [],
        "retry_count": {}
    }
    
    # 非同期実行
    config = {
        "configurable": {
            "thread_id": f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        },
        "recursion_limit": 50
    }
    
    # ストリーミング実行
    async for event in review_graph.astream(initial_state, config):
        print(f"Event: {event}")
        
        # 中間結果の処理
        if "persona_evaluations" in event:
            print(f"Persona evaluation completed: {list(event['persona_evaluations'].keys())}")
        
        if "final_report" in event:
            print("Final report generated!")
            print(json.dumps(event["final_report"], indent=2))
    
    # 最終状態の取得
    final_state = await review_graph.aget_state(config)
    print(f"Final state: {final_state}")

# 実行
if __name__ == "__main__":
    asyncio.run(main())
```

### 6.2 エラー処理のテスト
```python
async def test_error_handling():
    """エラー処理のテスト"""
    
    # エラーを含む初期状態
    error_state = {
        "article_content": "Test article",
        "current_phase": "evaluation",
        "errors": [
            {
                "agent": "tech_expert",
                "type": "timeout",
                "error": "LLM response timeout after 60s"
            },
            {
                "agent": "business_user",
                "type": "rate_limit",
                "error": "API rate limit exceeded"
            }
        ],
        "retry_count": {"tech_expert": 1}
    }
    
    review_graph = build_article_review_graph()
    
    # エラーハンドリングのテスト
    result = await review_graph.ainvoke(error_state)
    
    assert result["retry_count"]["tech_expert"] == 2
    assert len(result["errors"]) == 0  # エラーがクリアされている
```

## 7. まとめ

本設計書では、LangGraphを用いた高度なエージェント間通信グラフ構造を定義しました。主な特徴：

1. **階層的アーキテクチャ**: オーケストレーターによる全体管理
2. **並列実行**: Send APIによる効率的な並列処理
3. **動的ルーティング**: Command APIによる柔軟な制御フロー
4. **エラーハンドリング**: 自動リトライとフォールバック
5. **状態管理**: 型安全で拡張可能な状態定義
6. **ストリーミング対応**: リアルタイムフィードバック

この設計により、スケーラブルで信頼性の高いマルチエージェント評価システムを実現できます。