"""Integration tests for OrchestratorAgent with AggregatorAgent and ReporterAgent."""

import pytest
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.orchestrator import OrchestratorAgent, ArticleReviewState
from src.agents.aggregator import AggregatorAgent
from src.agents.reporter import ReporterAgent
from src.core.types import EvaluationResult, EvaluationMetric, PersonaAttributes


class TestOrchestratorIntegration:
    """Integration tests for orchestrator with aggregator and reporter agents."""

    @pytest.fixture
    def sample_article_review_state(self) -> ArticleReviewState:
        """Create a sample ArticleReviewState for testing."""
        return ArticleReviewState(
            article_content="This is a test article about AI and technology.",
            article_metadata={
                "title": "AI in Modern Technology",
                "author": "Test Author",
                "category": "Technology"
            },
            current_phase="aggregation",
            phase_status={
                "initialization": "completed",
                "analysis": "completed",
                "persona_generation": "completed",
                "evaluation": "completed",
                "aggregation": "in_progress"
            },
            active_agents=["aggregator"],
            agent_status={"aggregator": "active"},
            analysis_results={
                "topics": ["AI", "Technology", "Innovation"],
                "tone": "informative",
                "target_audience": "tech professionals",
                "complexity": "intermediate"
            },
            persona_count=3,
            generated_personas=[
                PersonaAttributes(
                    age=30,
                    occupation="Software Engineer",
                    interests=["AI", "Programming"],
                    values=["Innovation", "Efficiency"]
                ),
                PersonaAttributes(
                    age=35,
                    occupation="Data Scientist",
                    interests=["Machine Learning", "Statistics"],
                    values=["Accuracy", "Research"]
                ),
                PersonaAttributes(
                    age=28,
                    occupation="Product Manager",
                    interests=["Technology", "Business"],
                    values=["User Experience", "Growth"]
                )
            ],
            persona_generation_complete=True,
            persona_evaluations={
                "persona_0": EvaluationResult(
                    persona_id="persona_0",
                    persona_type="tech_enthusiast",
                    article_id="test_001",
                    overall_score=85,
                    metrics=[
                        EvaluationMetric(name="relevance", score=90),
                        EvaluationMetric(name="clarity", score=80),
                        EvaluationMetric(name="engagement", score=85)
                    ],
                    sentiment="positive",
                    suggestions=["Add more code examples", "Include real-world use cases"],
                    strengths=["Clear explanation", "Good structure"],
                    weaknesses=["Lacks practical examples"],
                    sharing_probability=0.8,
                    engagement_level="high"
                ),
                "persona_1": EvaluationResult(
                    persona_id="persona_1",
                    persona_type="data_professional",
                    article_id="test_001",
                    overall_score=78,
                    metrics=[
                        EvaluationMetric(name="relevance", score=85),
                        EvaluationMetric(name="clarity", score=70),
                        EvaluationMetric(name="engagement", score=75)
                    ],
                    sentiment="neutral",
                    suggestions=["Add more technical depth", "Include benchmarks"],
                    strengths=["Good overview"],
                    weaknesses=["Too high-level"],
                    sharing_probability=0.6,
                    engagement_level="medium"
                ),
                "persona_2": EvaluationResult(
                    persona_id="persona_2",
                    persona_type="business_focused",
                    article_id="test_001",
                    overall_score=82,
                    metrics=[
                        EvaluationMetric(name="relevance", score=80),
                        EvaluationMetric(name="clarity", score=85),
                        EvaluationMetric(name="engagement", score=80)
                    ],
                    sentiment="positive",
                    suggestions=["Add ROI analysis", "Include case studies"],
                    strengths=["Business relevance"],
                    weaknesses=["Needs business metrics"],
                    sharing_probability=0.75,
                    engagement_level="high"
                )
            },
            evaluation_complete=True,
            aggregated_scores={},
            improvement_suggestions=[],
            final_report={},
            messages=[],
            errors=[],
            retry_count={},
            simulation_id="test_sim_001",
            start_time=datetime.now(),
            end_time=None
        )

    @pytest.mark.asyncio
    async def test_aggregator_integration_with_orchestrator(self, sample_article_review_state):
        """Test AggregatorAgent integration with OrchestratorAgent."""
        orchestrator = OrchestratorAgent()
        
        # Test the aggregator node
        result = await orchestrator._aggregator_node(sample_article_review_state)
        
        # Verify the result structure
        assert "aggregated_scores" in result
        assert "improvement_suggestions" in result
        assert "messages" in result
        
        # Verify aggregated scores
        scores = result["aggregated_scores"]
        assert "overall_score" in scores
        assert scores["overall_score"]["mean"] == pytest.approx(81.67, 0.01)
        assert scores["overall_score"]["median"] == 82.0
        
        # Verify improvement suggestions
        suggestions = result["improvement_suggestions"]
        assert len(suggestions) > 0
        assert suggestions[0]["suggestion"] in [
            "Add more code examples",
            "Add more technical depth",
            "Add ROI analysis"
        ]
        
        # Verify messages
        assert result["messages"][0] == ("assistant", "Evaluation results aggregated")

    @pytest.mark.asyncio
    async def test_reporter_integration_with_orchestrator(self, sample_article_review_state):
        """Test ReporterAgent integration with OrchestratorAgent."""
        # First populate aggregated scores and suggestions
        sample_article_review_state["aggregated_scores"] = {
            "overall": 81.67,
            "relevance": 85.0,
            "clarity": 78.33,
            "engagement": 80.0
        }
        sample_article_review_state["improvement_suggestions"] = [
            {
                "suggestion": "Add more code examples",
                "priority": "high",
                "affected_personas": 1,
                "impact": 33.3,
                "category": "content"
            },
            {
                "suggestion": "Add more technical depth",
                "priority": "medium",
                "affected_personas": 1,
                "impact": 33.3,
                "category": "content"
            }
        ]
        sample_article_review_state["current_phase"] = "reporting"
        
        orchestrator = OrchestratorAgent()
        
        # Test the reporter node
        result = await orchestrator._reporter_node(sample_article_review_state)
        
        # Verify the result structure
        assert "final_report" in result
        assert "messages" in result
        
        # Verify final report structure
        report = result["final_report"]
        assert "executive_summary" in report
        assert "detailed_analysis" in report
        assert "recommendations" in report
        assert "visualization_data" in report
        assert "metadata" in report
        
        # Verify executive summary
        exec_summary = report["executive_summary"]
        assert "overview" in exec_summary
        assert "key_findings" in exec_summary
        assert "overall_score" in exec_summary
        assert exec_summary["overall_score"] == 81.67
        
        # Verify messages
        assert result["messages"][0] == ("assistant", "Final report generated")

    @pytest.mark.asyncio
    async def test_full_aggregation_to_reporting_flow(self, sample_article_review_state):
        """Test complete flow from aggregation to reporting phase."""
        orchestrator = OrchestratorAgent()
        
        # Phase 1: Aggregation
        aggregation_result = await orchestrator._aggregator_node(sample_article_review_state)
        
        # Update state with aggregation results
        sample_article_review_state["aggregated_scores"] = aggregation_result["aggregated_scores"]
        sample_article_review_state["improvement_suggestions"] = aggregation_result["improvement_suggestions"]
        sample_article_review_state["current_phase"] = "reporting"
        
        # Phase 2: Reporting
        reporting_result = await orchestrator._reporter_node(sample_article_review_state)
        
        # Verify complete flow
        assert reporting_result["final_report"] is not None
        report = reporting_result["final_report"]
        
        # Verify report uses aggregated data
        assert report["executive_summary"]["overall_score"] == aggregation_result["aggregated_scores"]["overall_score"]["mean"]
        assert len(report["executive_summary"]["top_recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_orchestrator_phase_transitions(self, sample_article_review_state):
        """Test orchestrator phase transitions for aggregation and reporting."""
        orchestrator = OrchestratorAgent()
        
        # Test aggregation phase check
        next_phase = orchestrator._check_aggregation(sample_article_review_state)
        assert next_phase == "aggregation"  # No aggregated scores yet
        
        # Add aggregated scores
        sample_article_review_state["aggregated_scores"] = {"overall": 81.67}
        next_phase = orchestrator._check_aggregation(sample_article_review_state)
        assert next_phase == "reporting"  # Should move to reporting
        
        # Test reporting phase check
        next_phase = orchestrator._check_reporting(sample_article_review_state)
        assert next_phase == "reporting"  # No final report yet
        
        # Add final report
        sample_article_review_state["final_report"] = {"executive_summary": {}}
        next_phase = orchestrator._check_reporting(sample_article_review_state)
        assert next_phase == "completed"  # Should complete

    @pytest.mark.asyncio
    async def test_error_handling_in_aggregation(self, sample_article_review_state):
        """Test error handling during aggregation phase."""
        orchestrator = OrchestratorAgent()
        
        # Mock aggregator to raise an error
        with patch('src.agents.aggregator.AggregatorAgent.aggregate', side_effect=Exception("Test error")):
            with pytest.raises(Exception) as exc_info:
                await orchestrator._aggregator_node(sample_article_review_state)
            assert str(exc_info.value) == "Test error"

    @pytest.mark.asyncio
    async def test_error_handling_in_reporting(self, sample_article_review_state):
        """Test error handling during reporting phase."""
        # Add required data for reporter
        sample_article_review_state["aggregated_scores"] = {"overall": 81.67}
        sample_article_review_state["improvement_suggestions"] = []
        
        orchestrator = OrchestratorAgent()
        
        # Mock reporter to raise an error
        with patch('src.agents.reporter.ReporterAgent.generate_report', side_effect=Exception("Report error")):
            with pytest.raises(Exception) as exc_info:
                await orchestrator._reporter_node(sample_article_review_state)
            assert str(exc_info.value) == "Report error"

    @pytest.mark.asyncio
    async def test_aggregator_with_empty_evaluations(self):
        """Test aggregator handling of empty evaluations."""
        state = ArticleReviewState(
            article_content="Test article",
            article_metadata={},
            current_phase="aggregation",
            phase_status={},
            active_agents=["aggregator"],
            agent_status={},
            analysis_results={},
            persona_count=0,
            generated_personas=[],
            persona_generation_complete=True,
            persona_evaluations={},  # Empty evaluations
            evaluation_complete=True,
            aggregated_scores={},
            improvement_suggestions=[],
            final_report={},
            messages=[],
            errors=[],
            retry_count={},
            simulation_id="test_empty",
            start_time=datetime.now(),
            end_time=None
        )
        
        orchestrator = OrchestratorAgent()
        result = await orchestrator._aggregator_node(state)
        
        # Should handle empty evaluations gracefully
        assert result["aggregated_scores"] == {}
        assert result["improvement_suggestions"] == []

    @pytest.mark.asyncio
    async def test_reporter_with_minimal_data(self):
        """Test reporter handling of minimal data."""
        state = ArticleReviewState(
            article_content="Test article",
            article_metadata={"title": "Test"},
            current_phase="reporting",
            phase_status={},
            active_agents=["reporter"],
            agent_status={},
            analysis_results={},
            persona_count=0,
            generated_personas=[],
            persona_generation_complete=False,
            persona_evaluations={},
            evaluation_complete=False,
            aggregated_scores={"overall": 50.0},
            improvement_suggestions=[],
            final_report={},
            messages=[],
            errors=[],
            retry_count={},
            simulation_id="test_minimal",
            start_time=datetime.now(),
            end_time=None
        )
        
        orchestrator = OrchestratorAgent()
        result = await orchestrator._reporter_node(state)
        
        # Should generate report even with minimal data
        assert "final_report" in result
        report = result["final_report"]
        assert report["executive_summary"]["overall_score"] == 50.0

    def test_get_node_for_phase_mapping(self):
        """Test phase to node mapping."""
        orchestrator = OrchestratorAgent()
        
        assert orchestrator._get_node_for_phase("analysis") == "analyze"
        assert orchestrator._get_node_for_phase("persona_generation") == "generate_personas"
        assert orchestrator._get_node_for_phase("evaluation") == "evaluate"
        assert orchestrator._get_node_for_phase("aggregation") == "aggregate"
        assert orchestrator._get_node_for_phase("reporting") == "report"
        assert orchestrator._get_node_for_phase("unknown") == "error"