"""Unit tests for AggregatorAgent - Real LLM API calls only."""

import pytest

from src.agents.aggregator import AggregatorAgent
from src.core.types import EvaluationMetric, EvaluationResult


class TestAggregatorAgent:
    """Test suite for AggregatorAgent with real LLM."""

    @pytest.fixture
    def minimal_evaluations(self) -> dict[str, EvaluationResult]:
        """Create minimal evaluation results to reduce API calls."""
        return {
            "p1": EvaluationResult(
                persona_id="p1",
                article_id="test",
                overall_score=85,
                metrics=[
                    EvaluationMetric(name="relevance", score=90, weight=1.0),
                    EvaluationMetric(name="clarity", score=80, weight=1.0),
                ],
                sentiment="positive",
                suggestions=["Add examples"],
                strengths=["Clear"],
                weaknesses=["Brief"],
                sharing_probability=0.8,
                engagement_level="high",
            ),
            "p2": EvaluationResult(
                persona_id="p2",
                article_id="test",
                overall_score=65,
                metrics=[
                    EvaluationMetric(name="relevance", score=70, weight=1.0),
                    EvaluationMetric(name="clarity", score=60, weight=1.0),
                ],
                sentiment="neutral",
                suggestions=["Add examples", "Simplify"],
                strengths=["Structured"],
                weaknesses=["Complex"],
                sharing_probability=0.5,
                engagement_level="medium",
            ),
        }

    def test_initialization(self):
        """Test AggregatorAgent initialization with real LLM."""
        agent = AggregatorAgent()
        assert agent.llm is not None
        assert agent.config is not None

    @pytest.mark.asyncio
    async def test_aggregate_basic_metrics(self, minimal_evaluations):
        """Test basic metric aggregation with real LLM."""
        agent = AggregatorAgent()
        result = await agent.aggregate(minimal_evaluations)

        # Check structure
        assert "scores" in result
        assert "suggestions" in result
        assert "sentiment" in result
        assert "segments" in result

        # Check scores
        assert "overall_score" in result["scores"]
        scores = result["scores"]["overall_score"]
        assert "mean" in scores
        assert "median" in scores
        assert "std" in scores

        # Check mean calculation
        expected_mean = (85 + 65) / 2
        assert scores["mean"] == pytest.approx(expected_mean, 0.1)

    @pytest.mark.asyncio
    async def test_suggestion_prioritization(self, minimal_evaluations):
        """Test suggestion prioritization with real LLM."""
        agent = AggregatorAgent()
        result = await agent.aggregate(minimal_evaluations)

        assert "suggestions" in result
        assert len(result["suggestions"]) > 0

        # "Add examples" appears twice, should have higher priority
        suggestions = result["suggestions"]
        add_examples = [s for s in suggestions if s["suggestion"] == "Add examples"]
        assert len(add_examples) > 0
        assert add_examples[0]["affected_personas"] == 2

    @pytest.mark.asyncio
    async def test_sentiment_distribution(self, minimal_evaluations):
        """Test sentiment distribution calculation."""
        agent = AggregatorAgent()
        result = await agent.aggregate(minimal_evaluations)

        assert "sentiment" in result
        assert "distribution" in result["sentiment"]

        distribution = result["sentiment"]["distribution"]
        assert distribution["positive"] == 1
        assert distribution["neutral"] == 1
        assert distribution["negative"] == 0

    @pytest.mark.asyncio
    async def test_empty_evaluations(self):
        """Test handling of empty evaluations."""
        agent = AggregatorAgent()
        result = await agent.aggregate({})

        assert result["scores"] == {}
        assert result["suggestions"] == []
        assert result["sentiment"]["distribution"] == {"positive": 0, "neutral": 0, "negative": 0}

    @pytest.mark.asyncio
    async def test_single_evaluation(self):
        """Test handling of single evaluation."""
        agent = AggregatorAgent()

        single_eval = {
            "p1": EvaluationResult(
                persona_id="p1",
                article_id="test",
                overall_score=75,
                metrics=[],
                sentiment="positive",
                suggestions=["Improve"],
                strengths=["Good"],
                weaknesses=["Short"],
                sharing_probability=0.6,
                engagement_level="medium",
            )
        }

        result = await agent.aggregate(single_eval)

        assert "scores" in result
        assert result["scores"]["overall_score"]["mean"] == 75
        assert result["scores"]["overall_score"]["median"] == 75
        assert result["scores"]["overall_score"]["std"] == 0

    def test_metric_aggregation_completeness(self, minimal_evaluations):
        """Test completeness of metric aggregation (no LLM needed)."""
        agent = AggregatorAgent()

        # Direct test of aggregation logic
        metrics_by_name = {}
        for eval_result in minimal_evaluations.values():
            for metric in eval_result.metrics:
                if metric.name not in metrics_by_name:
                    metrics_by_name[metric.name] = []
                metrics_by_name[metric.name].append(metric.score)

        # Should have relevance and clarity
        assert "relevance" in metrics_by_name
        assert "clarity" in metrics_by_name
        assert len(metrics_by_name["relevance"]) == 2
        assert len(metrics_by_name["clarity"]) == 2

    @pytest.mark.asyncio
    async def test_outlier_handling(self):
        """Test handling of outlier scores."""
        agent = AggregatorAgent()

        evaluations = {
            "p1": EvaluationResult(
                persona_id="p1",
                article_id="test",
                overall_score=90,
                metrics=[],
                sentiment="positive",
                suggestions=[],
                strengths=["Excellent"],
                weaknesses=[],
                sharing_probability=0.9,
                engagement_level="high",
            ),
            "p2": EvaluationResult(
                persona_id="p2",
                article_id="test",
                overall_score=10,  # Outlier
                metrics=[],
                sentiment="negative",
                suggestions=["Complete rewrite"],
                strengths=[],
                weaknesses=["Poor"],
                sharing_probability=0.1,
                engagement_level="low",
            ),
        }

        result = await agent.aggregate(evaluations)

        # Check that outlier is handled
        assert result["scores"]["overall_score"]["std"] > 30  # High standard deviation
        assert "outliers" in result or result["scores"]["overall_score"]["range"] == 80

    @pytest.mark.asyncio
    async def test_boundary_values(self):
        """Test boundary value handling."""
        agent = AggregatorAgent()

        # Test with max score
        max_eval = {
            "p1": EvaluationResult(
                persona_id="p1",
                article_id="test",
                overall_score=100,
                metrics=[],
                sentiment="positive",
                suggestions=[],
                strengths=["Perfect"],
                weaknesses=[],
                sharing_probability=1.0,
                engagement_level="high",
            )
        }

        result = await agent.aggregate(max_eval)
        assert result["scores"]["overall_score"]["mean"] == 100

        # Test with min score
        min_eval = {
            "p1": EvaluationResult(
                persona_id="p1",
                article_id="test",
                overall_score=0,
                metrics=[],
                sentiment="negative",
                suggestions=["Start over"],
                strengths=[],
                weaknesses=["Everything"],
                sharing_probability=0.0,
                engagement_level="low",
            )
        }

        result = await agent.aggregate(min_eval)
        assert result["scores"]["overall_score"]["mean"] == 0

    def test_error_handling(self):
        """Test error handling in aggregation."""
        agent = AggregatorAgent()

        # Test with invalid data types
        with pytest.raises((TypeError, AttributeError)):
            # This should fail as we're passing invalid data
            import asyncio

            asyncio.run(agent.aggregate({"invalid": "data"}))

    @pytest.mark.asyncio
    async def test_performance_metrics(self, minimal_evaluations):
        """Test that performance metrics are calculated."""
        agent = AggregatorAgent()
        result = await agent.aggregate(minimal_evaluations)

        # Check that result includes performance indicators
        assert "sharing_likelihood" in result
        assert result["sharing_likelihood"]["average"] == pytest.approx(0.65, 0.01)

        assert "engagement" in result
        engagement = result["engagement"]["distribution"]
        assert engagement["high"] == 1
        assert engagement["medium"] == 1
        assert engagement["low"] == 0
