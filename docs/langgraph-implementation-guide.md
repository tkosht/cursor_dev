# LangGraph 実装ガイド：動的エージェント階層生成とエージェント間連携

## 目次
1. [LangGraphの基礎概念](#1-langgraphの基礎概念)
2. [基本的な実装パターン](#2-基本的な実装パターン)
3. [動的エージェント階層生成](#3-動的エージェント階層生成)
4. [エージェント間連携とワークフロー](#4-エージェント間連携とワークフロー)
5. [実践的な実装例](#5-実践的な実装例)
6. [ベストプラクティス](#6-ベストプラクティス)
7. [トラブルシューティング](#7-トラブルシューティング)

## 1. LangGraphの基礎概念

### 1.1 コアコンポーネント

LangGraphは、複雑なマルチエージェントシステムを構築するための低レベルオーケストレーションフレームワークです。

#### State（状態管理）
```python
from typing import TypedDict, Annotated
from langgraph.graph import add_messages

# 基本的な状態定義
class State(TypedDict):
    messages: list
    current_task: str
    results: dict

# メッセージ自動追加のReducer付き状態
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]  # 自動的にメッセージを追加
    agent_history: dict
    task_queue: list
```

#### Node（ノード）
```python
# 同期ノード
def process_node(state: State) -> dict:
    """ノードは状態を受け取り、更新を返す"""
    result = analyze_task(state["current_task"])
    return {"results": {**state["results"], "analysis": result}}

# 非同期ノード
async def async_node(state: State) -> dict:
    """非同期処理にも対応"""
    result = await fetch_external_data(state["messages"][-1])
    return {"messages": [("assistant", f"Data fetched: {result}")]}
```

#### Edge（エッジ）
```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)

# 通常のエッジ
builder.add_edge("analyze", "process")

# 条件付きエッジ
def routing_logic(state: State) -> str:
    if state["results"].get("complexity", 0) > 0.7:
        return "complex_handler"
    return "simple_handler"

builder.add_conditional_edges(
    "router",
    routing_logic,
    {
        "complex_handler": "complex_processing",
        "simple_handler": "simple_processing"
    }
)
```

### 1.2 Graph（グラフ）の構築と実行

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

class WorkflowState(TypedDict):
    query: str
    analysis: dict
    response: str

def analyze(state: WorkflowState) -> dict:
    # 分析ロジック
    analysis = {"complexity": 0.8, "domain": "technical"}
    return {"analysis": analysis}

def generate_response(state: WorkflowState) -> dict:
    # レスポンス生成
    response = f"Based on analysis: {state['analysis']}"
    return {"response": response}

# グラフの構築
builder = StateGraph(WorkflowState)
builder.add_node("analyze", analyze)
builder.add_node("respond", generate_response)

builder.add_edge(START, "analyze")
builder.add_edge("analyze", "respond")
builder.add_edge("respond", END)

# チェックポイント付きでコンパイル
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# 実行
result = graph.invoke(
    {"query": "Explain quantum computing"},
    config={"configurable": {"thread_id": "session-123"}}
)
```

## 2. 基本的な実装パターン

### 2.1 シンプルなエージェントチェーン

```python
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# エージェントの作成
research_agent = create_react_agent(
    ChatOpenAI(model="gpt-4"),
    tools=[web_search_tool, arxiv_tool],
    system_message="You are a research specialist."
)

writer_agent = create_react_agent(
    ChatOpenAI(model="gpt-4"),
    tools=[format_tool, grammar_check_tool],
    system_message="You are a technical writer."
)

# ワークフローの構築
workflow = StateGraph(MessagesState)
workflow.add_node("research", research_agent)
workflow.add_node("write", writer_agent)

workflow.add_edge(START, "research")
workflow.add_edge("research", "write")
workflow.add_edge("write", END)

app = workflow.compile()
```

### 2.2 条件分岐を含むワークフロー

```python
class RouterState(TypedDict):
    messages: list
    task_type: str
    results: dict

def task_classifier(state: RouterState) -> dict:
    """タスクの種類を分類"""
    last_message = state["messages"][-1].content
    
    if "code" in last_message.lower():
        task_type = "coding"
    elif "research" in last_message.lower():
        task_type = "research"
    else:
        task_type = "general"
    
    return {"task_type": task_type}

def route_task(state: RouterState) -> str:
    """タスクタイプに基づいてルーティング"""
    return state["task_type"]

# グラフ構築
workflow = StateGraph(RouterState)
workflow.add_node("classify", task_classifier)
workflow.add_node("coding", coding_agent)
workflow.add_node("research", research_agent)
workflow.add_node("general", general_agent)

workflow.add_edge(START, "classify")
workflow.add_conditional_edges(
    "classify",
    route_task,
    {
        "coding": "coding",
        "research": "research",
        "general": "general"
    }
)

# 各エージェントからENDへ
workflow.add_edge("coding", END)
workflow.add_edge("research", END)
workflow.add_edge("general", END)
```

## 3. 動的エージェント階層生成

### 3.1 ランタイムグラフ生成パターン

```python
from langgraph.types import Send
from typing import List, Dict

class DynamicOrchestratorState(TypedDict):
    query: str
    subtasks: List[Dict]
    results: Dict[str, any]
    
def task_analyzer(state: DynamicOrchestratorState) -> dict:
    """クエリを分析してサブタスクに分解"""
    # LLMを使用してタスクを動的に分解
    subtasks = [
        {"id": "task1", "type": "research", "query": "Find latest papers"},
        {"id": "task2", "type": "code", "query": "Implement algorithm"},
        {"id": "task3", "type": "review", "query": "Review implementation"}
    ]
    return {"subtasks": subtasks}

def orchestrator(state: DynamicOrchestratorState):
    """動的にワーカーエージェントを生成して送信"""
    # Send APIを使用して並列実行
    return [
        Send("worker", {"task": task, "parent_context": state["query"]}) 
        for task in state["subtasks"]
    ]

def worker(state: dict) -> dict:
    """個別タスクを処理"""
    task = state["task"]
    
    # タスクタイプに基づいて適切な処理を実行
    if task["type"] == "research":
        result = perform_research(task["query"])
    elif task["type"] == "code":
        result = generate_code(task["query"])
    else:
        result = perform_review(task["query"])
    
    return {"results": {task["id"]: result}}

# 動的ワークフロー構築
dynamic_workflow = StateGraph(DynamicOrchestratorState)
dynamic_workflow.add_node("analyze", task_analyzer)
dynamic_workflow.add_node("orchestrate", orchestrator)
dynamic_workflow.add_node("worker", worker)

dynamic_workflow.add_edge(START, "analyze")
dynamic_workflow.add_edge("analyze", "orchestrate")
```

### 3.2 階層的エージェントチーム

```python
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent

def create_research_team():
    """研究チームのサブグラフを作成"""
    class ResearchState(TypedDict):
        query: str
        papers: list
        summary: str
    
    team = StateGraph(ResearchState)
    
    # チームメンバー
    paper_finder = create_react_agent(
        ChatOpenAI(model="gpt-4"),
        tools=[arxiv_search, google_scholar],
        name="paper_finder"
    )
    
    summarizer = create_react_agent(
        ChatOpenAI(model="gpt-4"),
        tools=[text_summarization],
        name="summarizer"
    )
    
    team.add_node("find_papers", paper_finder)
    team.add_node("summarize", summarizer)
    
    team.add_edge(START, "find_papers")
    team.add_edge("find_papers", "summarize")
    team.add_edge("summarize", END)
    
    return team.compile()

def create_engineering_team():
    """エンジニアリングチームのサブグラフを作成"""
    class EngineeringState(TypedDict):
        requirements: str
        code: str
        tests: str
        
    team = StateGraph(EngineeringState)
    
    # チームメンバー
    architect = create_react_agent(
        ChatOpenAI(model="gpt-4"),
        tools=[design_pattern_db],
        name="architect"
    )
    
    developer = create_react_agent(
        ChatOpenAI(model="gpt-4"),
        tools=[code_generator, syntax_checker],
        name="developer"
    )
    
    tester = create_react_agent(
        ChatOpenAI(model="gpt-4"),
        tools=[test_generator, test_runner],
        name="tester"
    )
    
    team.add_node("design", architect)
    team.add_node("develop", developer)
    team.add_node("test", tester)
    
    team.add_edge(START, "design")
    team.add_edge("design", "develop")
    team.add_edge("develop", "test")
    team.add_edge("test", END)
    
    return team.compile()

# メインスーパーバイザーグラフ
class SupervisorState(TypedDict):
    task: str
    team_assignment: str
    final_result: dict

def team_supervisor(state: SupervisorState) -> dict:
    """タスクを適切なチームに割り当て"""
    task = state["task"]
    
    if "research" in task or "papers" in task:
        assignment = "research_team"
    elif "implement" in task or "code" in task:
        assignment = "engineering_team"
    else:
        assignment = "general_team"
        
    return {"team_assignment": assignment}

# 階層的システムの構築
main_workflow = StateGraph(SupervisorState)
main_workflow.add_node("supervisor", team_supervisor)
main_workflow.add_node("research_team", create_research_team())
main_workflow.add_node("engineering_team", create_engineering_team())

main_workflow.add_edge(START, "supervisor")
main_workflow.add_conditional_edges(
    "supervisor",
    lambda x: x["team_assignment"],
    {
        "research_team": "research_team",
        "engineering_team": "engineering_team"
    }
)
```

### 3.3 動的エージェント生成ファクトリーパターン

```python
from typing import Type, Callable

class AgentFactory:
    """動的にエージェントを生成するファクトリー"""
    
    @staticmethod
    def create_specialist_agent(
        specialty: str,
        tools: list,
        model: str = "gpt-4"
    ) -> Callable:
        """特定の専門性を持つエージェントを動的に生成"""
        
        system_message = f"You are a {specialty} specialist. Your expertise includes: {', '.join([t.name for t in tools])}"
        
        return create_react_agent(
            ChatOpenAI(model=model),
            tools=tools,
            system_message=system_message,
            name=f"{specialty}_agent"
        )
    
    @staticmethod
    def create_dynamic_team(requirements: dict) -> StateGraph:
        """要件に基づいて動的にチームを構成"""
        
        team = StateGraph(MessagesState)
        
        # 必要な専門性に基づいてエージェントを生成
        for role, config in requirements.items():
            agent = AgentFactory.create_specialist_agent(
                specialty=role,
                tools=config["tools"],
                model=config.get("model", "gpt-4")
            )
            team.add_node(role, agent)
        
        # ワークフローを動的に構築
        nodes = list(requirements.keys())
        team.add_edge(START, nodes[0])
        
        for i in range(len(nodes) - 1):
            team.add_edge(nodes[i], nodes[i + 1])
        
        team.add_edge(nodes[-1], END)
        
        return team.compile()

# 使用例
team_requirements = {
    "data_analyst": {
        "tools": [sql_query_tool, data_viz_tool],
        "model": "gpt-4"
    },
    "ml_engineer": {
        "tools": [model_training_tool, hyperparameter_tuning_tool],
        "model": "gpt-4"
    },
    "report_writer": {
        "tools": [document_formatter, chart_generator],
        "model": "gpt-3.5-turbo"
    }
}

dynamic_team = AgentFactory.create_dynamic_team(team_requirements)
```

## 4. エージェント間連携とワークフロー

### 4.1 Command APIを使用した高度な連携

```python
from langgraph.types import Command
from typing import Literal

class CollaborativeState(TypedDict):
    messages: list
    current_agent: str
    shared_knowledge: dict
    task_status: dict

def create_handoff_tool(agent_name: str, description: str = None):
    """エージェント間のハンドオフツールを作成"""
    @tool(name=f"transfer_to_{agent_name}")
    def handoff(request: str) -> Command:
        """別のエージェントに制御を移譲"""
        return Command(
            goto=agent_name,
            update={
                "messages": [("user", request)],
                "current_agent": agent_name
            },
            graph=Command.PARENT  # 親グラフでのナビゲーション
        )
    
    return handoff

# 協調的なエージェントシステム
class CooperativeAgentSystem:
    def __init__(self):
        self.workflow = StateGraph(CollaborativeState)
        
    def add_cooperative_agent(self, name: str, tools: list, other_agents: list):
        """他のエージェントと協調できるエージェントを追加"""
        
        # 他のエージェントへのハンドオフツールを追加
        handoff_tools = [
            create_handoff_tool(agent) 
            for agent in other_agents
        ]
        
        agent = create_react_agent(
            ChatOpenAI(model="gpt-4"),
            tools=tools + handoff_tools,
            system_message=f"You are {name}. You can collaborate with: {', '.join(other_agents)}"
        )
        
        self.workflow.add_node(name, agent)
        
    def build(self):
        """協調システムを構築"""
        # 全てのエージェントを相互接続
        agents = list(self.workflow.nodes.keys())
        
        for agent in agents:
            for other in agents:
                if agent != other:
                    self.workflow.add_edge(agent, other)
        
        return self.workflow.compile()

# 使用例
system = CooperativeAgentSystem()
system.add_cooperative_agent(
    "researcher",
    tools=[web_search, paper_search],
    other_agents=["analyst", "writer"]
)
system.add_cooperative_agent(
    "analyst",
    tools=[data_analysis, visualization],
    other_agents=["researcher", "writer"]
)
system.add_cooperative_agent(
    "writer",
    tools=[text_generation, formatting],
    other_agents=["researcher", "analyst"]
)

collaborative_app = system.build()
```

### 4.2 双方向通信パターン

```python
class BidirectionalState(TypedDict):
    messages: list
    agent_states: dict
    feedback_queue: list
    
def create_bidirectional_agent(name: str, peer_agents: list):
    """双方向通信可能なエージェントを作成"""
    
    def agent_node(state: BidirectionalState) -> Command:
        # 自身の状態を更新
        my_state = state["agent_states"].get(name, {})
        
        # フィードバックキューをチェック
        feedback = [
            msg for msg in state["feedback_queue"] 
            if msg["to"] == name
        ]
        
        if feedback:
            # フィードバックに基づいて処理
            response = process_feedback(feedback)
            next_agent = determine_next_agent(response)
            
            return Command(
                goto=next_agent,
                update={
                    "agent_states": {
                        **state["agent_states"],
                        name: {"last_action": "processed_feedback"}
                    },
                    "feedback_queue": [
                        msg for msg in state["feedback_queue"]
                        if msg["to"] != name
                    ]
                }
            )
        else:
            # 通常の処理
            result = perform_task(state["messages"][-1])
            
            # 必要に応じて他のエージェントにフィードバックを送信
            if result.needs_clarification:
                return Command(
                    goto=result.clarification_agent,
                    update={
                        "feedback_queue": state["feedback_queue"] + [{
                            "from": name,
                            "to": result.clarification_agent,
                            "message": result.clarification_request
                        }]
                    }
                )
            
            return Command(
                goto=result.next_agent,
                update={
                    "messages": state["messages"] + [result.message],
                    "agent_states": {
                        **state["agent_states"],
                        name: {"last_action": result.action}
                    }
                }
            )
    
    return agent_node

# 双方向通信ワークフローの構築
bidirectional_workflow = StateGraph(BidirectionalState)

agents = ["planner", "executor", "validator"]
for agent in agents:
    peer_agents = [a for a in agents if a != agent]
    bidirectional_workflow.add_node(
        agent, 
        create_bidirectional_agent(agent, peer_agents)
    )

# 全エージェント間の双方向接続
for source in agents:
    for target in agents:
        if source != target:
            bidirectional_workflow.add_edge(source, target)

bidirectional_app = bidirectional_workflow.compile()
```

### 4.3 イベント駆動型連携パターン

```python
from typing import Any, Dict
from dataclasses import dataclass

@dataclass
class Event:
    type: str
    source: str
    data: Dict[str, Any]
    
class EventDrivenState(TypedDict):
    events: list[Event]
    agent_responses: dict
    processing_complete: bool

class EventDrivenOrchestrator:
    """イベント駆動型のオーケストレーター"""
    
    def __init__(self):
        self.workflow = StateGraph(EventDrivenState)
        self.event_handlers = {}
        
    def register_event_handler(self, event_type: str, handler_agent: str):
        """イベントタイプに対するハンドラーを登録"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler_agent)
        
    def event_dispatcher(self, state: EventDrivenState) -> list:
        """イベントを適切なハンドラーにディスパッチ"""
        sends = []
        
        for event in state["events"]:
            handlers = self.event_handlers.get(event.type, [])
            for handler in handlers:
                sends.append(
                    Send(handler, {
                        "event": event,
                        "context": state["agent_responses"]
                    })
                )
        
        return sends
    
    def create_event_handler(self, agent_name: str, handle_types: list[str]):
        """イベントハンドラーエージェントを作成"""
        
        def handler(state: dict) -> dict:
            event = state["event"]
            context = state["context"]
            
            # イベントタイプに基づいて処理
            if event.type == "data_ready":
                result = process_data(event.data)
            elif event.type == "error_occurred":
                result = handle_error(event.data)
            elif event.type == "task_completed":
                result = finalize_task(event.data, context)
            else:
                result = {"status": "unhandled"}
            
            # 新しいイベントを生成することも可能
            new_events = []
            if result.get("trigger_next"):
                new_events.append(Event(
                    type="next_phase",
                    source=agent_name,
                    data=result
                ))
            
            return {
                "agent_responses": {agent_name: result},
                "events": new_events
            }
        
        # ハンドラーを登録
        for event_type in handle_types:
            self.register_event_handler(event_type, agent_name)
        
        self.workflow.add_node(agent_name, handler)
        
    def build(self):
        """イベント駆動システムを構築"""
        self.workflow.add_node("dispatcher", self.event_dispatcher)
        self.workflow.add_edge(START, "dispatcher")
        
        # 条件付きでディスパッチャーに戻る
        def check_completion(state):
            if state.get("processing_complete"):
                return END
            return "dispatcher"
        
        for node in self.workflow.nodes:
            if node != "dispatcher" and node != START and node != END:
                self.workflow.add_conditional_edges(
                    node,
                    check_completion,
                    {
                        "dispatcher": "dispatcher",
                        END: END
                    }
                )
        
        return self.workflow.compile()

# 使用例
orchestrator = EventDrivenOrchestrator()
orchestrator.create_event_handler(
    "data_processor",
    handle_types=["data_ready", "data_update"]
)
orchestrator.create_event_handler(
    "error_handler",
    handle_types=["error_occurred", "validation_failed"]
)
orchestrator.create_event_handler(
    "reporter",
    handle_types=["task_completed", "milestone_reached"]
)

event_driven_app = orchestrator.build()
```

## 5. 実践的な実装例

### 5.1 完全な動的マルチエージェントシステム

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command, Send
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from typing import Literal, List, Dict, Any
import json

class ProjectManagementState(TypedDict):
    """プロジェクト管理システムの状態"""
    messages: list
    project_requirements: dict
    task_breakdown: list[dict]
    agent_assignments: dict
    results: dict
    project_status: Literal["planning", "executing", "reviewing", "completed"]

class DynamicProjectManager:
    """動的にチームを編成してプロジェクトを管理するシステム"""
    
    def __init__(self, available_tools: dict):
        self.available_tools = available_tools
        self.workflow = StateGraph(ProjectManagementState)
        self._build_core_system()
        
    def _build_core_system(self):
        """コアシステムを構築"""
        # プロジェクトマネージャー
        self.workflow.add_node("project_manager", self._create_project_manager())
        
        # タスクアナライザー
        self.workflow.add_node("task_analyzer", self._task_analyzer)
        
        # 動的ワーカー
        self.workflow.add_node("dynamic_worker", self._dynamic_worker)
        
        # レビュアー
        self.workflow.add_node("reviewer", self._create_reviewer())
        
        # フロー定義
        self.workflow.add_edge(START, "project_manager")
        self.workflow.add_conditional_edges(
            "project_manager",
            self._route_from_pm,
            {
                "analyze": "task_analyzer",
                "review": "reviewer",
                "complete": END
            }
        )
        self.workflow.add_edge("task_analyzer", "dynamic_worker")
        self.workflow.add_edge("dynamic_worker", "project_manager")
        self.workflow.add_edge("reviewer", "project_manager")
        
    def _create_project_manager(self):
        """プロジェクトマネージャーエージェントを作成"""
        return create_react_agent(
            ChatOpenAI(model="gpt-4"),
            tools=[],
            system_message="""You are a project manager responsible for:
            1. Understanding project requirements
            2. Coordinating task execution
            3. Monitoring progress
            4. Ensuring quality through reviews
            Make decisions about project flow and status."""
        )
    
    def _task_analyzer(self, state: ProjectManagementState) -> dict:
        """タスクを分析して、必要なエージェントを決定"""
        requirements = state["project_requirements"]
        
        # LLMを使用してタスクを分解
        llm = ChatOpenAI(model="gpt-4")
        
        # タスク分解プロンプト
        breakdown_prompt = f"""
        Analyze the following project requirements and break them down into specific tasks:
        {json.dumps(requirements, indent=2)}
        
        For each task, specify:
        1. task_id
        2. description
        3. required_skills (e.g., 'research', 'coding', 'analysis', 'writing')
        4. dependencies (other task_ids)
        5. estimated_complexity (low, medium, high)
        
        Return as JSON array.
        """
        
        response = llm.invoke(breakdown_prompt)
        task_breakdown = json.loads(response.content)
        
        # 各タスクに適切なツールを割り当て
        agent_assignments = {}
        for task in task_breakdown:
            required_skills = task["required_skills"]
            assigned_tools = []
            
            for skill in required_skills:
                if skill in self.available_tools:
                    assigned_tools.extend(self.available_tools[skill])
            
            agent_assignments[task["task_id"]] = {
                "tools": assigned_tools,
                "skills": required_skills
            }
        
        return {
            "task_breakdown": task_breakdown,
            "agent_assignments": agent_assignments,
            "project_status": "executing"
        }
    
    def _dynamic_worker(self, state: ProjectManagementState):
        """動的にワーカーエージェントを生成して実行"""
        task_breakdown = state["task_breakdown"]
        agent_assignments = state["agent_assignments"]
        
        # Send APIを使用して並列実行
        sends = []
        for task in task_breakdown:
            # 依存関係をチェック
            dependencies = task.get("dependencies", [])
            if all(dep in state.get("results", {}) for dep in dependencies):
                sends.append(Send(
                    "execute_task",
                    {
                        "task": task,
                        "tools": agent_assignments[task["task_id"]]["tools"],
                        "context": state["results"]
                    }
                ))
        
        return sends
    
    def execute_task(self, state: dict) -> dict:
        """個別タスクを実行"""
        task = state["task"]
        tools = state["tools"]
        context = state["context"]
        
        # 動的にエージェントを作成
        task_agent = create_react_agent(
            ChatOpenAI(model="gpt-4"),
            tools=tools,
            system_message=f"Execute the following task: {task['description']}"
        )
        
        # タスクを実行
        result = task_agent.invoke({
            "messages": [("user", f"Task: {task['description']}\nContext: {json.dumps(context)}")]
        })
        
        return {
            "results": {task["task_id"]: result}
        }
    
    def _create_reviewer(self):
        """レビュアーエージェントを作成"""
        return create_react_agent(
            ChatOpenAI(model="gpt-4"),
            tools=[],
            system_message="""You are a quality reviewer. Review completed tasks and provide feedback.
            Ensure all requirements are met and suggest improvements if needed."""
        )
    
    def _route_from_pm(self, state: ProjectManagementState) -> str:
        """プロジェクトマネージャーからのルーティング"""
        status = state["project_status"]
        
        if status == "planning":
            return "analyze"
        elif status == "executing":
            # 全タスク完了チェック
            if self._all_tasks_completed(state):
                return "review"
            return "analyze"  # 継続実行
        elif status == "reviewing":
            return "review"
        else:
            return "complete"
    
    def _all_tasks_completed(self, state: ProjectManagementState) -> bool:
        """全タスクが完了したかチェック"""
        task_breakdown = state.get("task_breakdown", [])
        results = state.get("results", {})
        
        return all(task["task_id"] in results for task in task_breakdown)
    
    def compile(self, checkpointer=None):
        """ワークフローをコンパイル"""
        if checkpointer is None:
            checkpointer = MemorySaver()
        
        # execute_taskノードを追加
        self.workflow.add_node("execute_task", self.execute_task)
        
        return self.workflow.compile(checkpointer=checkpointer)

# 使用例
available_tools = {
    "research": [web_search_tool, arxiv_tool, wikipedia_tool],
    "coding": [python_repl, code_formatter, syntax_checker],
    "analysis": [data_analyzer, statistical_tool, visualization_tool],
    "writing": [text_generator, grammar_checker, citation_tool]
}

project_manager = DynamicProjectManager(available_tools)
app = project_manager.compile()

# プロジェクト実行
result = app.invoke(
    {
        "messages": [("user", "Create a machine learning model for sentiment analysis")],
        "project_requirements": {
            "goal": "sentiment analysis model",
            "dataset": "twitter data",
            "performance_target": "90% accuracy",
            "deliverables": ["model", "documentation", "API"]
        },
        "project_status": "planning"
    },
    config={"configurable": {"thread_id": "project-001"}}
)
```

### 5.2 自己組織化エージェントネットワーク

```python
class SelfOrganizingNetwork:
    """自己組織化するエージェントネットワーク"""
    
    def __init__(self):
        self.workflow = StateGraph(NetworkState)
        self.agent_registry = {}
        self.capability_map = {}
        
    def register_agent_template(self, agent_type: str, capabilities: list, tools: list):
        """エージェントテンプレートを登録"""
        self.agent_registry[agent_type] = {
            "capabilities": capabilities,
            "tools": tools,
            "instances": 0
        }
        
        # 能力マップを更新
        for capability in capabilities:
            if capability not in self.capability_map:
                self.capability_map[capability] = []
            self.capability_map[capability].append(agent_type)
    
    def spawn_agent(self, agent_type: str) -> str:
        """新しいエージェントインスタンスを生成"""
        if agent_type not in self.agent_registry:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        template = self.agent_registry[agent_type]
        instance_id = f"{agent_type}_{template['instances']}"
        template['instances'] += 1
        
        # エージェントノードを作成
        agent = create_react_agent(
            ChatOpenAI(model="gpt-4"),
            tools=template['tools'],
            system_message=f"You are a {agent_type} agent with capabilities: {template['capabilities']}"
        )
        
        self.workflow.add_node(instance_id, agent)
        
        return instance_id
    
    def self_organize(self, state: NetworkState) -> list:
        """ネットワークが自己組織化して必要なエージェントを生成"""
        required_capabilities = state["required_capabilities"]
        current_agents = state["active_agents"]
        
        sends = []
        
        for capability in required_capabilities:
            # 能力を持つエージェントタイプを検索
            agent_types = self.capability_map.get(capability, [])
            
            if agent_types:
                # 最適なエージェントタイプを選択
                selected_type = self._select_optimal_agent(agent_types, state)
                
                # エージェントをスポーン
                agent_id = self.spawn_agent(selected_type)
                
                # タスクを送信
                sends.append(Send(
                    agent_id,
                    {
                        "task": state["tasks"][capability],
                        "network_state": state["shared_knowledge"]
                    }
                ))
        
        return sends
    
    def _select_optimal_agent(self, agent_types: list, state: NetworkState) -> str:
        """状態に基づいて最適なエージェントタイプを選択"""
        # ここでは単純な選択ロジック
        # 実際には、負荷分散、過去のパフォーマンスなどを考慮
        return agent_types[0]
```

## 6. ベストプラクティス

### 6.1 状態管理のベストプラクティス

```python
# 1. 状態スキーマは明確で型安全に
from typing import TypedDict, Literal, Optional
from pydantic import BaseModel, Field

class TaskStatus(BaseModel):
    """タスクステータスの詳細な定義"""
    id: str
    status: Literal["pending", "in_progress", "completed", "failed"]
    assigned_agent: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    
class WellDefinedState(TypedDict):
    """明確に定義された状態"""
    messages: list
    tasks: list[TaskStatus]
    agent_metrics: dict[str, dict]
    global_context: dict

# 2. 状態の分離とカプセル化
class AgentPrivateState(TypedDict):
    """エージェント固有のプライベート状態"""
    internal_memory: list
    working_data: dict
    
class SharedState(TypedDict):
    """共有状態"""
    public_messages: list
    shared_results: dict

# 3. 状態変換関数の使用
def transform_to_agent_state(shared: SharedState) -> AgentPrivateState:
    """共有状態をエージェント状態に変換"""
    return {
        "internal_memory": filter_relevant_messages(shared["public_messages"]),
        "working_data": extract_relevant_data(shared["shared_results"])
    }
```

### 6.2 エラーハンドリングとリカバリー

```python
from langgraph.types import RetryPolicy
from functools import wraps
import logging

# 1. リトライポリシーの設定
def create_robust_agent(name: str, tools: list):
    """堅牢なエージェントを作成"""
    
    def agent_with_error_handling(state: dict) -> dict:
        try:
            # メイン処理
            result = process_task(state)
            
            # 結果の検証
            if not validate_result(result):
                raise ValueError("Invalid result")
                
            return {"status": "success", "result": result}
            
        except ConnectionError as e:
            logging.error(f"Connection error in {name}: {e}")
            return {"status": "retry", "error": str(e)}
            
        except Exception as e:
            logging.error(f"Unexpected error in {name}: {e}")
            return {"status": "failed", "error": str(e)}
    
    return agent_with_error_handling

# 2. サーキットブレーカーパターン
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        
    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        self.failures = 0
        self.state = "closed"
        
    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "open"

# 3. 状態ロールバック
class StateManager:
    def __init__(self):
        self.checkpoints = []
        
    def save_checkpoint(self, state: dict):
        """チェックポイントを保存"""
        self.checkpoints.append(copy.deepcopy(state))
        
    def rollback(self, steps: int = 1):
        """指定したステップ数だけロールバック"""
        if len(self.checkpoints) >= steps:
            return self.checkpoints[-steps]
        return self.checkpoints[0] if self.checkpoints else {}
```

### 6.3 パフォーマンス最適化

```python
# 1. 並列実行の最適化
def optimize_parallel_execution(tasks: list[dict]) -> list[Send]:
    """タスクを最適に並列実行"""
    # 依存関係を分析
    dependency_graph = build_dependency_graph(tasks)
    
    # 実行可能なタスクをバッチ化
    execution_batches = topological_sort_with_batching(dependency_graph)
    
    sends = []
    for batch in execution_batches:
        for task in batch:
            sends.append(Send("worker", task))
    
    return sends

# 2. キャッシング戦略
from functools import lru_cache
import hashlib

class CachedAgent:
    def __init__(self, cache_size: int = 100):
        self.cache = {}
        self.cache_size = cache_size
        
    def get_cache_key(self, state: dict) -> str:
        """状態からキャッシュキーを生成"""
        # 重要な部分のみをキーに含める
        key_parts = {
            "query": state.get("messages", [])[-1],
            "context": state.get("context", {})
        }
        return hashlib.md5(
            json.dumps(key_parts, sort_keys=True).encode()
        ).hexdigest()
    
    def process_with_cache(self, state: dict) -> dict:
        """キャッシュを使用して処理"""
        cache_key = self.get_cache_key(state)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self.expensive_operation(state)
        
        # キャッシュに保存
        if len(self.cache) >= self.cache_size:
            # LRU eviction
            oldest = min(self.cache.items(), key=lambda x: x[1]["timestamp"])
            del self.cache[oldest[0]]
        
        self.cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
        
        return result

# 3. 状態サイズの最適化
def optimize_state_size(state: dict) -> dict:
    """状態サイズを最適化"""
    optimized = {}
    
    # メッセージ履歴を制限
    if "messages" in state:
        optimized["messages"] = state["messages"][-50:]  # 最新50件のみ保持
    
    # 大きな結果をIDで参照
    if "results" in state:
        optimized["result_ids"] = store_and_get_ids(state["results"])
    
    # 不要なデータを削除
    for key, value in state.items():
        if key not in ["messages", "results"] and sys.getsizeof(value) < 1000:
            optimized[key] = value
    
    return optimized
```

## 7. トラブルシューティング

### 7.1 一般的な問題と解決策

#### 問題1: 無限ループ
```python
# 解決策: 再帰制限とループ検出
config = {
    "recursion_limit": 25,
    "configurable": {"thread_id": "session-123"}
}

# カスタムループ検出
class LoopDetector:
    def __init__(self, window_size: int = 10):
        self.history = []
        self.window_size = window_size
        
    def check_loop(self, state_hash: str) -> bool:
        """ループを検出"""
        if state_hash in self.history[-self.window_size:]:
            return True
        self.history.append(state_hash)
        return False
```

#### 問題2: メモリリーク
```python
# 解決策: 適切なリソース管理
class ResourceManagedAgent:
    def __init__(self):
        self.resources = []
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # リソースをクリーンアップ
        for resource in self.resources:
            resource.close()
    
    def add_resource(self, resource):
        self.resources.append(resource)
```

#### 問題3: デバッグの困難さ
```python
# 解決策: 包括的なロギングとトレーシング
import structlog
from opentelemetry import trace

logger = structlog.get_logger()
tracer = trace.get_tracer(__name__)

def traced_node(name: str):
    """トレーシング付きノードデコレーター"""
    def decorator(func):
        @wraps(func)
        def wrapper(state: dict) -> dict:
            with tracer.start_as_current_span(f"node_{name}") as span:
                span.set_attribute("node.name", name)
                span.set_attribute("state.size", len(str(state)))
                
                logger.info(
                    "node_execution_start",
                    node=name,
                    state_keys=list(state.keys())
                )
                
                try:
                    result = func(state)
                    
                    logger.info(
                        "node_execution_success",
                        node=name,
                        result_keys=list(result.keys())
                    )
                    
                    return result
                    
                except Exception as e:
                    logger.error(
                        "node_execution_error",
                        node=name,
                        error=str(e),
                        exc_info=True
                    )
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator

# 使用例
@traced_node("analyzer")
def analyze_task(state: dict) -> dict:
    # 処理ロジック
    return {"analysis": "completed"}
```

### 7.2 パフォーマンスプロファイリング

```python
import cProfile
import pstats
from memory_profiler import profile

class PerformanceMonitor:
    """パフォーマンス監視ユーティリティ"""
    
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.memory_snapshots = []
        
    def start_profiling(self):
        """プロファイリング開始"""
        self.profiler.enable()
        
    def stop_profiling(self, top_n: int = 10):
        """プロファイリング停止と結果表示"""
        self.profiler.disable()
        
        stats = pstats.Stats(self.profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(top_n)
        
    @profile
    def memory_profile_node(self, node_func):
        """メモリプロファイリング付きノード実行"""
        def wrapper(state: dict) -> dict:
            # メモリ使用量を記録
            import tracemalloc
            tracemalloc.start()
            
            result = node_func(state)
            
            current, peak = tracemalloc.get_traced_memory()
            self.memory_snapshots.append({
                "node": node_func.__name__,
                "current": current,
                "peak": peak
            })
            
            tracemalloc.stop()
            
            return result
        
        return wrapper
```

### まとめ

LangGraphは、動的で階層的なマルチエージェントシステムを構築するための強力なフレームワークです。主な利点：

1. **柔軟な状態管理**: TypedDictとReducerによる型安全な状態管理
2. **動的な制御フロー**: 条件付きエッジとSend APIによる動的ルーティング
3. **階層的アーキテクチャ**: サブグラフとCommand APIによる階層構造
4. **並列実行**: Send APIによる効率的な並列タスク実行
5. **永続性とチェックポイント**: 本番環境対応の状態管理
6. **統合性**: 他のフレームワーク（CrewAI、AutoGen）との連携

これらの機能を活用することで、複雑な要件に対応できる柔軟で拡張可能なAIシステムを構築できます。