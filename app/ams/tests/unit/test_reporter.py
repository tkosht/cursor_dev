"""Unit tests for ReporterAgent - Real LLM API calls only."""

from datetime import datetime
from typing import Any

import pytest

from src.agents.reporter import ReporterAgent
from src.core.types import (
    EvaluationMetric,
    EvaluationResult,
    InformationChannel,
    PersonaAttributes,
    PersonalityType,
)


class TestReporterAgent:
    """Test suite for ReporterAgent with real LLM."""

    @pytest.fixture
    def minimal_state(self) -> dict[str, Any]:
        """Create minimal ArticleReviewState for testing."""
        return {
            "article_content": "AI is transforming business.",
            "article_metadata": {
                "title": "AI Impact",
                "author": "Test",
                "category": "Tech",
            },
            "current_phase": "reporting",
            "phase_status": {
                "initialization": "completed",
                "analysis": "completed",
                "persona_generation": "completed",
                "evaluation": "completed",
                "aggregation": "completed",
                "reporting": "in_progress",
            },
            "active_agents": ["reporter"],
            "agent_status": {"reporter": "active"},
            "analysis_results": {
                "topics": ["AI", "Technology"],
                "tone": "informative",
                "target_audience": "professionals",
                "complexity": "intermediate",
            },
            "persona_count": 2,
            "generated_personas": [
                PersonaAttributes(
                    age=30,
                    occupation="Engineer",
                    location="NYC",
                    education_level="MS",
                    interests=["AI", "Tech"],
                    values=["Innovation"],
                    personality_traits={
                        PersonalityType.OPENNESS: 0.8,
                        PersonalityType.CONSCIENTIOUSNESS: 0.7,
                        PersonalityType.EXTRAVERSION: 0.6,
                        PersonalityType.AGREEABLENESS: 0.7,
                        PersonalityType.NEUROTICISM: 0.3,
                    },
                    information_seeking_behavior="proactive",
                    preferred_channels=[InformationChannel.TECH_BLOGS],
                ),
                PersonaAttributes(
                    age=35,
                    occupation="Manager",
                    location="SF",
                    education_level="MBA",
                    interests=["Business", "Tech"],
                    values=["Efficiency"],
                    personality_traits={
                        PersonalityType.OPENNESS: 0.7,
                        PersonalityType.CONSCIENTIOUSNESS: 0.9,
                        PersonalityType.EXTRAVERSION: 0.8,
                        PersonalityType.AGREEABLENESS: 0.8,
                        PersonalityType.NEUROTICISM: 0.2,
                    },
                    information_seeking_behavior="strategic",
                    preferred_channels=[InformationChannel.EMAIL],
                ),
            ],
            "persona_generation_complete": True,
            "persona_evaluations": {
                "persona_1": EvaluationResult(
                    persona_id="persona_1",
                    article_id="test_article",
                    metrics=[
                        EvaluationMetric(name="relevance", score=85.0, weight=0.3),
                        EvaluationMetric(name="clarity", score=80.0, weight=0.3),
                        EvaluationMetric(name="engagement", score=75.0, weight=0.4),
                    ],
                    overall_score=79.5,
                    strengths=["Clear", "Relevant"],
                    weaknesses=["Needs examples"],
                    suggestions=["Add examples"],
                    sharing_probability=0.7,
                    engagement_level="high",
                    sentiment="positive",
                ),
                "persona_2": EvaluationResult(
                    persona_id="persona_2",
                    article_id="test_article",
                    metrics=[
                        EvaluationMetric(name="relevance", score=70.0, weight=0.3),
                        EvaluationMetric(name="clarity", score=75.0, weight=0.3),
                        EvaluationMetric(name="engagement", score=70.0, weight=0.4),
                    ],
                    overall_score=71.5,
                    strengths=["Practical"],
                    weaknesses=["Too technical"],
                    suggestions=["Simplify"],
                    sharing_probability=0.5,
                    engagement_level="medium",
                    sentiment="neutral",
                ),
            },
            "aggregated_scores": {
                "overall_average": 75.5,
                "metric_averages": {"relevance": 77.5, "clarity": 77.5, "engagement": 72.5},
                "sentiment_distribution": {"positive": 1, "neutral": 1, "negative": 0},
                "engagement_distribution": {"high": 1, "medium": 1, "low": 0},
                "sharing_likelihood": 0.6,
            },
            "improvement_suggestions": [
                {"category": "high_priority", "suggestion": "Add examples"},
                {"category": "medium_priority", "suggestion": "Simplify language"},
            ],
            "report_generated": False,
            "simulation_complete": False,
            "error": None,
            "start_time": datetime.now(),
            "end_time": None,
        }

    def test_initialization(self):
        """Test ReporterAgent initialization with real LLM."""
        agent = ReporterAgent()
        assert agent.llm is not None
        assert agent.call_tracker is not None
        assert agent.template_engine is not None

    @pytest.mark.asyncio
    async def test_generate_report_minimal(self, minimal_state):
        """Test basic report generation with minimal state and real LLM."""
        agent = ReporterAgent()

        # Generate report with real LLM (using minimal state to reduce API calls)
        report = await agent.generate_report(minimal_state)

        # Verify report structure
        assert isinstance(report, dict)
        assert "metadata" in report
        assert "summary" in report
        assert "detailed_analysis" in report
        assert "recommendations" in report

        # Verify metadata
        metadata = report["metadata"]
        assert "report_id" in metadata
        assert "generated_at" in metadata
        assert "personas_evaluated" in metadata
        assert metadata["personas_evaluated"] == 2

        # Verify summary
        summary = report["summary"]
        assert "overall_score" in summary
        assert summary["overall_score"] == 75.5

    def test_generate_detailed_analysis(self, minimal_state):
        """Test detailed analysis generation (no LLM needed)."""
        agent = ReporterAgent()

        analysis = agent._generate_detailed_analysis(minimal_state)

        assert "article_analysis" in analysis
        assert "persona_analysis" in analysis
        assert "evaluation_results" in analysis
        assert "improvement_areas" in analysis

        # Check article analysis
        assert analysis["article_analysis"]["topics"] == ["AI", "Technology"]
        assert analysis["article_analysis"]["target_audience"] == "professionals"

        # Check persona analysis
        assert "total_count" in analysis["persona_analysis"]
        assert "segments" in analysis["persona_analysis"]
        assert "diversity_score" in analysis["persona_analysis"]

        # Check evaluation results
        assert "overall_score" in analysis["evaluation_results"]
        assert analysis["evaluation_results"]["overall_score"] == 75.5

    def test_prepare_visualization_data(self, minimal_state):
        """Test visualization data preparation (no LLM needed)."""
        agent = ReporterAgent()

        viz_data = agent._prepare_visualization_data(minimal_state)

        assert "charts" in viz_data
        charts = viz_data["charts"]

        # Check for expected chart types
        assert "score_distribution" in charts
        assert "metric_radar" in charts
        assert "sentiment_pie" in charts

        # Check chart structure
        for chart_name, chart_data in charts.items():
            assert "type" in chart_data
            assert "data" in chart_data
            assert "layout" in chart_data

    @pytest.mark.asyncio
    async def test_format_report_json(self, minimal_state):
        """Test JSON format report generation with real LLM."""
        agent = ReporterAgent()

        # Generate report with real LLM
        report_data = await agent.generate_report(minimal_state)
        formatted = agent._format_report(report_data, "json")

        # JSON format should return the dictionary as-is
        assert isinstance(formatted, dict)
        assert formatted == report_data

    @pytest.mark.asyncio
    async def test_format_report_markdown(self, minimal_state):
        """Test Markdown format report generation with real LLM."""
        agent = ReporterAgent()

        # Generate report with real LLM
        report_data = await agent.generate_report(minimal_state)
        formatted = agent._format_report(report_data, "markdown")

        # Markdown format should return a string
        assert isinstance(formatted, str)
        assert "# Article Review Report" in formatted
        assert "## Executive Summary" in formatted
        assert "## Recommendations" in formatted

    def test_calculate_confidence_score(self, minimal_state):
        """Test confidence score calculation (no LLM needed)."""
        agent = ReporterAgent()

        # Calculate confidence with 2 personas
        confidence = agent._calculate_confidence_score(persona_count=2, score_variance=5.0)

        # With only 2 personas, confidence should be low
        assert 0 <= confidence <= 100
        assert confidence < 50  # Low confidence with few personas

        # Test with more personas
        confidence_high = agent._calculate_confidence_score(persona_count=50, score_variance=2.0)

        assert confidence_high > confidence  # More personas = higher confidence

    def test_generate_key_insights(self, minimal_state):
        """Test key insights generation (deterministic)."""
        agent = ReporterAgent()

        # Generate insights from aggregated scores
        insights = agent._generate_key_insights(minimal_state["aggregated_scores"])

        assert isinstance(insights, list)
        assert len(insights) > 0

        # Check for expected insight patterns
        for insight in insights:
            assert isinstance(insight, str)
            assert len(insight) > 10  # Meaningful insights

    def test_error_handling_missing_data(self):
        """Test error handling with missing required data."""
        agent = ReporterAgent()

        # Create state with missing required fields
        incomplete_state = {
            "article_content": "Test",
            # Missing other required fields
        }

        # Should handle gracefully
        analysis = agent._prepare_analysis_structure(incomplete_state)
        assert analysis is not None  # Should return something even with missing data
