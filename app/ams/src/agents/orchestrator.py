"""
Main orchestrator agent using LangGraph
"""

import logging
from datetime import datetime
from typing import Annotated, Any, Literal, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, Send

from ..config import get_config
from ..core.types import EvaluationResult, PersonaAttributes
from ..utils.llm_factory import create_llm

logger = logging.getLogger(__name__)


class ArticleReviewState(TypedDict):
    """Global state for article review system"""

    # Basic information
    article_content: str
    article_metadata: dict[str, Any]

    # Phase management
    current_phase: Literal[
        "initialization",
        "analysis",
        "persona_generation",
        "evaluation",
        "aggregation",
        "reporting",
        "completed",
    ]
    phase_status: dict[str, str]

    # Agent management
    active_agents: list[str]
    agent_status: dict[str, str]

    # Analysis data
    analysis_results: dict[str, Any]

    # Persona data
    persona_count: int
    generated_personas: list[PersonaAttributes]
    persona_generation_complete: bool

    # Evaluation data
    persona_evaluations: dict[str, EvaluationResult]
    evaluation_complete: bool

    # Aggregation data
    aggregated_scores: dict[str, float]
    improvement_suggestions: list[dict[str, Any]]

    # Final report
    final_report: dict[str, Any]

    # Message history
    messages: Annotated[list, add_messages]

    # Error handling
    errors: list[dict[str, str]]
    retry_count: dict[str, int]

    # Metadata
    simulation_id: str
    start_time: datetime
    end_time: Annotated[datetime, None]


class OrchestratorAgent:
    """Main orchestrator agent that controls the article review workflow"""

    def __init__(self):
        self.config = get_config()
        self.llm = create_llm()
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the main workflow graph"""
        workflow = StateGraph(ArticleReviewState)

        # Add nodes
        workflow.add_node("orchestrator", self._orchestrator_node)
        workflow.add_node("analyzer", self._analyzer_node)
        workflow.add_node("persona_generator", self._persona_generator_node)
        workflow.add_node("persona_evaluator", self._persona_evaluator_node)
        workflow.add_node("aggregator", self._aggregator_node)
        workflow.add_node("reporter", self._reporter_node)
        workflow.add_node("error_handler", self._error_handler_node)

        # Entry point
        workflow.add_edge(START, "orchestrator")

        # Conditional routing from orchestrator
        workflow.add_conditional_edges(
            "orchestrator",
            self._route_from_orchestrator,
            {
                "analyze": "analyzer",
                "generate_personas": "persona_generator",
                "evaluate": "persona_evaluator",
                "aggregate": "aggregator",
                "report": "reporter",
                "error": "error_handler",
                "complete": END,
            },
        )

        # Return to orchestrator after each phase
        workflow.add_edge("analyzer", "orchestrator")
        workflow.add_edge("persona_generator", "orchestrator")
        workflow.add_edge("persona_evaluator", "orchestrator")
        workflow.add_edge("aggregator", "orchestrator")
        workflow.add_edge("reporter", "orchestrator")
        workflow.add_edge("error_handler", "orchestrator")

        return workflow

    async def _orchestrator_node(self, state: ArticleReviewState) -> Command:
        """Main orchestrator logic"""
        current_phase = state["current_phase"]

        # Check for errors
        if state.get("errors"):
            logger.warning(f"Errors detected: {state['errors']}")
            return Command(
                goto="error",
                update={
                    "messages": [("system", "Errors detected, handling...")],
                },
            )

        # Phase transition logic
        phase_transitions = {
            "initialization": self._check_initialization,
            "analysis": self._check_analysis,
            "persona_generation": self._check_persona_generation,
            "evaluation": self._check_evaluation,
            "aggregation": self._check_aggregation,
            "reporting": self._check_reporting,
        }

        if current_phase in phase_transitions:
            next_phase = phase_transitions[current_phase](state)

            if next_phase == "completed":
                return Command(
                    goto="complete",
                    update={
                        "current_phase": "completed",
                        "end_time": datetime.now(),
                        "messages": [
                            ("system", "Review process completed successfully")
                        ],
                    },
                )

            return Command(
                goto=self._get_node_for_phase(next_phase),
                update={
                    "current_phase": next_phase,
                    "phase_status": {
                        **state.get("phase_status", {}),
                        current_phase: "completed",
                    },
                    "messages": [
                        ("system", f"Transitioning to {next_phase} phase")
                    ],
                },
            )

        # Default: complete
        return Command(goto="complete")

    def _check_initialization(self, state: ArticleReviewState) -> str:
        """Check initialization and determine next phase"""
        if state.get("article_content"):
            return "analysis"
        return "initialization"  # Stay in initialization

    def _check_analysis(self, state: ArticleReviewState) -> str:
        """Check analysis completion"""
        if state.get("analysis_results"):
            return "persona_generation"
        return "analysis"

    def _check_persona_generation(self, state: ArticleReviewState) -> str:
        """Check persona generation completion"""
        if state.get("persona_generation_complete"):
            return "evaluation"
        return "persona_generation"

    def _check_evaluation(self, state: ArticleReviewState) -> str:
        """Check evaluation completion"""
        if state.get("evaluation_complete"):
            return "aggregation"
        return "evaluation"

    def _check_aggregation(self, state: ArticleReviewState) -> str:
        """Check aggregation completion"""
        if state.get("aggregated_scores"):
            return "reporting"
        return "aggregation"

    def _check_reporting(self, state: ArticleReviewState) -> str:
        """Check reporting completion"""
        if state.get("final_report"):
            return "completed"
        return "reporting"

    def _get_node_for_phase(self, phase: str) -> str:
        """Map phase to node name"""
        phase_node_map = {
            "analysis": "analyze",
            "persona_generation": "generate_personas",
            "evaluation": "evaluate",
            "aggregation": "aggregate",
            "reporting": "report",
        }
        return phase_node_map.get(phase, "error")

    def _route_from_orchestrator(self, state: ArticleReviewState) -> str:
        """Route from orchestrator based on state"""
        # This is called by the conditional edge
        # The actual routing decision is made in _orchestrator_node
        # which returns a Command with goto
        return "analyze"  # Default fallback

    async def _analyzer_node(self, state: ArticleReviewState) -> dict:
        """Run article analysis"""
        from .analyzer import AnalysisAgent

        agent = AnalysisAgent()
        result = await agent.analyze(state["article_content"])

        return {
            "analysis_results": result,
            "messages": [("assistant", "Article analysis completed")],
        }

    async def _persona_generator_node(self, state: ArticleReviewState) -> dict:
        """Generate personas"""
        from .persona_generator import PersonaGenerator

        generator = PersonaGenerator()
        personas = await generator.generate_personas(
            article_content=state["article_content"],
            analysis_results=state["analysis_results"],
            count=state.get(
                "persona_count", self.config.simulation.population_size
            ),
        )

        return {
            "generated_personas": personas,
            "persona_generation_complete": True,
            "messages": [("assistant", f"Generated {len(personas)} personas")],
        }

    def _persona_evaluator_node(self, state: ArticleReviewState) -> list[Send]:
        """Send personas for parallel evaluation"""
        personas = state.get("generated_personas", [])

        # Use Send API for parallel evaluation
        sends = []
        for i, persona in enumerate(personas):
            sends.append(
                Send(
                    "evaluate_single_persona",
                    {
                        "persona": persona,
                        "persona_id": f"persona_{i}",
                        "article_content": state["article_content"],
                        "analysis_results": state["analysis_results"],
                    },
                )
            )

        return sends

    async def _aggregator_node(self, state: ArticleReviewState) -> dict:
        """Aggregate evaluation results"""
        from .aggregator import AggregatorAgent

        aggregator = AggregatorAgent()
        result = await aggregator.aggregate(state["persona_evaluations"])

        return {
            "aggregated_scores": result["scores"],
            "improvement_suggestions": result["suggestions"],
            "messages": [("assistant", "Evaluation results aggregated")],
        }

    async def _reporter_node(self, state: ArticleReviewState) -> dict:
        """Generate final report"""
        from .reporter import ReporterAgent

        reporter = ReporterAgent()
        report = await reporter.generate_report(state)

        return {
            "final_report": report,
            "messages": [("assistant", "Final report generated")],
        }

    async def _error_handler_node(self, state: ArticleReviewState) -> Command:
        """Handle errors with retry logic"""
        errors = state.get("errors", [])
        retry_count = state.get("retry_count", {})

        # Simple retry logic
        for error in errors:
            agent = error.get("agent", "unknown")
            current_retries = retry_count.get(agent, 0)

            if current_retries < 3:
                # Retry
                retry_count[agent] = current_retries + 1
                return Command(
                    goto="orchestrator",
                    update={
                        "errors": [],  # Clear errors
                        "retry_count": retry_count,
                        "messages": [
                            (
                                "system",
                                f"Retrying {agent} (attempt {current_retries + 1})",
                            )
                        ],
                    },
                )

        # Max retries exceeded
        return Command(
            goto="complete",
            update={
                "current_phase": "failed",
                "messages": [("error", "Max retries exceeded")],
            },
        )

    def compile(self, checkpointer=None):
        """Compile the workflow with optional checkpointing"""
        if checkpointer is None:
            checkpointer = MemorySaver()

        # Add the single persona evaluation node
        self.workflow.add_node(
            "evaluate_single_persona", self._evaluate_single_persona
        )

        return self.workflow.compile(checkpointer=checkpointer)

    async def _evaluate_single_persona(self, state: dict) -> dict:
        """Evaluate a single persona"""
        from .evaluator import EvaluationAgent

        evaluator = EvaluationAgent()
        result = await evaluator.evaluate_persona(
            persona=state["persona"],
            article_content=state["article_content"],
            analysis_results=state["analysis_results"],
        )

        return {"persona_evaluations": {state["persona_id"]: result}}
