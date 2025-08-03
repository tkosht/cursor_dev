"""Unit tests for AggregatorAgent."""

from unittest.mock import AsyncMock, MagicMock

import pydantic_core
import pytest

from src.agents.aggregator import AggregatorAgent
from src.core.types import EvaluationMetric, EvaluationResult


class TestAggregatorAgent:
    """Test suite for AggregatorAgent."""

    @pytest.fixture
    def sample_evaluations(self) -> dict[str, EvaluationResult]:
        """Create sample evaluation results for testing."""
        return {
            "persona_1": EvaluationResult(
                persona_id="persona_1",
                persona_type="tech_enthusiast",
                article_id="test_article_001",
                overall_score=85,
                metrics=[
                    EvaluationMetric(name="relevance", score=90),
                    EvaluationMetric(name="clarity", score=80),
                    EvaluationMetric(name="engagement", score=85),
                ],
                sentiment="positive",
                suggestions=["Add more examples", "Improve introduction"],
                strengths=["Well-structured", "Good flow"],
                weaknesses=["Lacks examples"],
                sharing_probability=0.8,
                engagement_level="high",
                reasoning="Well-structured article with good technical content",
            ),
            "persona_2": EvaluationResult(
                persona_id="persona_2",
                persona_type="general_reader",
                article_id="test_article_001",
                overall_score=70,
                metrics=[
                    EvaluationMetric(name="relevance", score=75),
                    EvaluationMetric(name="clarity", score=65),
                    EvaluationMetric(name="engagement", score=70),
                ],
                sentiment="neutral",
                suggestions=["Add more examples", "Simplify technical terms"],
                strengths=["Good structure"],
                weaknesses=["Too technical"],
                sharing_probability=0.5,
                engagement_level="medium",
                reasoning="Good but needs simplification",
            ),
            "persona_3": EvaluationResult(
                persona_id="persona_3",
                persona_type="novice",
                article_id="test_article_001",
                overall_score=60,
                metrics=[
                    EvaluationMetric(name="relevance", score=55),
                    EvaluationMetric(name="clarity", score=65),
                    EvaluationMetric(name="engagement", score=60),
                ],
                sentiment="negative",
                suggestions=["Improve introduction", "Add visual aids"],
                strengths=["Has structure"],
                weaknesses=["Hard to follow", "Too complex"],
                sharing_probability=0.3,
                engagement_level="low",
                reasoning="Difficult to follow",
            ),
        }

    @pytest.mark.asyncio
    async def test_aggregate_basic_metrics(self, sample_evaluations):
        """Test basic metric aggregation functionality."""
        agent = AggregatorAgent()
        result = await agent.aggregate(sample_evaluations)

        assert "scores" in result
        assert "overall_score" in result["scores"]

        # Check mean calculation
        expected_mean = (85 + 70 + 60) / 3
        assert result["scores"]["overall_score"]["mean"] == pytest.approx(expected_mean, 0.1)

        # Check median calculation
        assert result["scores"]["overall_score"]["median"] == 70

        # Check standard deviation exists
        assert "std" in result["scores"]["overall_score"]
        assert result["scores"]["overall_score"]["std"] > 0

    @pytest.mark.asyncio
    async def test_suggestion_prioritization(self, sample_evaluations):
        """Test that suggestions are properly prioritized."""
        agent = AggregatorAgent()
        result = await agent.aggregate(sample_evaluations)

        assert "suggestions" in result
        assert len(result["suggestions"]) > 0

        # Check that most frequent suggestion has higher priority
        first_suggestion = result["suggestions"][0]
        assert first_suggestion["suggestion"] == "Add more examples"  # Mentioned twice
        assert first_suggestion["priority"] == "high"
        assert first_suggestion["affected_personas"] == 2

    @pytest.mark.asyncio
    async def test_sentiment_distribution(self, sample_evaluations):
        """Test sentiment analysis distribution."""
        agent = AggregatorAgent()
        result = await agent.aggregate(sample_evaluations)

        assert "sentiment" in result
        assert "distribution" in result["sentiment"]

        distribution = result["sentiment"]["distribution"]
        assert distribution["positive"] == 1
        assert distribution["neutral"] == 1
        assert distribution["negative"] == 1

    @pytest.mark.asyncio
    async def test_segment_analysis(self, sample_evaluations):
        """Test that segment analysis is performed."""
        agent = AggregatorAgent()
        result = await agent.aggregate(sample_evaluations)

        assert "segments" in result
        # Segments should be created based on sentiment
        assert "by_sentiment" in result["segments"]

    @pytest.mark.asyncio
    async def test_empty_evaluations(self):
        """Test handling of empty evaluation data."""
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
            "persona_1": EvaluationResult(
                persona_id="persona_1",
                persona_type="general",
                article_id="test_001",
                overall_score=80,
                metrics=[],
                sentiment="positive",
                suggestions=["Test suggestion"],
                strengths=[],
                weaknesses=[],
                sharing_probability=0.7,
                engagement_level="high",
            )
        }

        result = await agent.aggregate(single_eval)

        assert result["scores"]["overall_score"]["mean"] == 80
        assert result["scores"]["overall_score"]["median"] == 80
        assert result["scores"]["overall_score"]["std"] == 0

    @pytest.mark.asyncio
    async def test_metric_aggregation_completeness(self, sample_evaluations):
        """Test that all metrics are properly aggregated."""
        agent = AggregatorAgent()
        result = await agent.aggregate(sample_evaluations)

        # Check overall score is aggregated
        assert "overall_score" in result["scores"]
        assert "mean" in result["scores"]["overall_score"]
        assert "median" in result["scores"]["overall_score"]
        assert "std" in result["scores"]["overall_score"]
        assert "min" in result["scores"]["overall_score"]
        assert "max" in result["scores"]["overall_score"]

        # Check individual metrics are aggregated
        for metric in ["relevance", "clarity", "engagement"]:
            assert metric in result["scores"]
            assert "mean" in result["scores"][metric]
            assert "median" in result["scores"][metric]
            assert "std" in result["scores"][metric]
            assert "min" in result["scores"][metric]
            assert "max" in result["scores"][metric]

    @pytest.mark.asyncio
    async def test_outlier_handling(self):
        """Test handling of outlier values."""
        evaluations_with_outlier = {
            "persona_1": EvaluationResult(
                persona_id="persona_1",
                persona_type="general",
                article_id="test_001",
                overall_score=80,
                metrics=[],
                sentiment="positive",
                suggestions=[],
                strengths=[],
                weaknesses=[],
                sharing_probability=0.7,
                engagement_level="high",
            ),
            "persona_2": EvaluationResult(
                persona_id="persona_2",
                persona_type="general",
                article_id="test_001",
                overall_score=85,
                metrics=[],
                sentiment="positive",
                suggestions=[],
                strengths=[],
                weaknesses=[],
                sharing_probability=0.8,
                engagement_level="high",
            ),
            "persona_3": EvaluationResult(
                persona_id="persona_3",
                persona_type="general",
                article_id="test_001",
                overall_score=10,  # Outlier
                metrics=[],
                sentiment="negative",
                suggestions=[],
                strengths=[],
                weaknesses=[],
                sharing_probability=0.1,
                engagement_level="low",
            ),
        }

        agent = AggregatorAgent()
        result = await agent.aggregate(evaluations_with_outlier)

        # Should detect and handle outliers appropriately
        assert "outliers_detected" in result.get("metadata", {})

    @pytest.mark.asyncio
    async def test_llm_insights_generation(self, sample_evaluations, monkeypatch):
        """Test LLM insights generation."""
        # Mock LLM response
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = MagicMock(content='{"insights": "Test insight summary"}')

        agent = AggregatorAgent()
        agent.llm = mock_llm

        result = await agent.aggregate(sample_evaluations)

        assert "insights" in result
        assert result["insights"] == "Test insight summary"

    def test_aggregate_metrics_calculation(self):
        """Test the internal metrics aggregation method."""
        agent = AggregatorAgent()

        evaluations = [
            EvaluationResult(
                persona_id="p1",
                persona_type="general",
                article_id="test_001",
                overall_score=80,
                metrics=[
                    EvaluationMetric(name="relevance", score=90),
                    EvaluationMetric(name="clarity", score=85),
                ],
                sentiment="positive",
                suggestions=[],
                strengths=[],
                weaknesses=[],
                sharing_probability=0.7,
                engagement_level="high",
            ),
            EvaluationResult(
                persona_id="p2",
                persona_type="general",
                article_id="test_001",
                overall_score=70,
                metrics=[
                    EvaluationMetric(name="relevance", score=80),
                    EvaluationMetric(name="clarity", score=75),
                ],
                sentiment="neutral",
                suggestions=[],
                strengths=[],
                weaknesses=[],
                sharing_probability=0.5,
                engagement_level="medium",
            ),
        ]

        metrics = agent._aggregate_metrics(evaluations)

        assert metrics["overall_score"]["mean"] == 75
        assert metrics["overall_score"]["min"] == 70
        assert metrics["overall_score"]["max"] == 80
        assert metrics["relevance"]["mean"] == 85

    async def test_boundary_value_zero_score(self):
        """Test aggregation with zero scores."""
        agent = AggregatorAgent()

        evaluations = [
            EvaluationResult(
                persona_id="persona_1",
                persona_type="test_type",
                article_id="test_article",
                overall_score=0,  # Boundary value: minimum score
                metrics=[
                    EvaluationMetric(name="relevance", score=0),
                    EvaluationMetric(name="clarity", score=0),
                ],
                sentiment="negative",
                suggestions=["Complete rewrite needed"],
                strengths=[],
                weaknesses=["No value provided"],
                sharing_probability=0.0,
                engagement_level="low",
            )
        ]

        result = await agent.aggregate({e.persona_id: e for e in evaluations})

        assert result["scores"]["overall_score"]["mean"] == 0
        assert result["scores"]["overall_score"]["min"] == 0
        assert result["scores"]["overall_score"]["max"] == 0

    async def test_boundary_value_maximum_score(self):
        """Test aggregation with maximum scores (100)."""
        agent = AggregatorAgent()

        evaluations = [
            EvaluationResult(
                persona_id="persona_1",
                persona_type="test_type",
                article_id="test_article",
                overall_score=100,  # Boundary value: maximum score
                metrics=[
                    EvaluationMetric(name="relevance", score=100),
                    EvaluationMetric(name="clarity", score=100),
                ],
                sentiment="positive",
                suggestions=[],
                strengths=["Perfect in every way"],
                weaknesses=[],
                sharing_probability=1.0,
                engagement_level="high",
            )
        ]

        result = await agent.aggregate({e.persona_id: e for e in evaluations})

        assert result["scores"]["overall_score"]["mean"] == 100
        assert result["scores"]["overall_score"]["min"] == 100
        assert result["scores"]["overall_score"]["max"] == 100

    async def test_boundary_value_invalid_negative_score(self):
        """Test handling of invalid negative scores."""
        # Test that negative overall_score raises validation error
        with pytest.raises(pydantic_core._pydantic_core.ValidationError) as exc_info:
            EvaluationResult(
                persona_id="persona_1",
                persona_type="test_type",
                article_id="test_article",
                overall_score=-10,  # Invalid negative score
                metrics=[
                    EvaluationMetric(name="relevance", score=0),
                    EvaluationMetric(name="clarity", score=0),
                ],
                sentiment="negative",
                suggestions=["Fix negative scores"],
                strengths=[],
                weaknesses=["Invalid data"],
                sharing_probability=0,
                engagement_level="low",
            )
        assert "greater than or equal to 0" in str(exc_info.value)

        # Test that negative metric score raises validation error
        with pytest.raises(pydantic_core._pydantic_core.ValidationError) as exc_info:
            EvaluationMetric(name="relevance", score=-5)
        assert "greater than or equal to 0" in str(exc_info.value)

    async def test_boundary_value_invalid_above_maximum(self):
        """Test handling of scores above maximum (>100)."""
        # Test that score > 100 raises validation error
        with pytest.raises(pydantic_core._pydantic_core.ValidationError) as exc_info:
            EvaluationResult(
                persona_id="persona_1",
                persona_type="test_type",
                article_id="test_article",
                overall_score=150,  # Invalid score above maximum
                metrics=[
                    EvaluationMetric(name="relevance", score=100),
                    EvaluationMetric(name="clarity", score=100),
                ],
                sentiment="positive",
                suggestions=[],
                strengths=["Too good to be true"],
                weaknesses=[],
                sharing_probability=1.0,
                engagement_level="high",
            )
        assert "less than or equal to 100" in str(exc_info.value)

        # Test that metric score > 100 raises validation error
        with pytest.raises(pydantic_core._pydantic_core.ValidationError) as exc_info:
            EvaluationMetric(name="relevance", score=200)
        assert "less than or equal to 100" in str(exc_info.value)

    async def test_large_dataset_aggregation(self):
        """Test aggregation with large number of evaluations."""
        agent = AggregatorAgent()

        # Generate 1000 evaluations
        evaluations = []
        for i in range(1000):
            score = 50 + (i % 50)  # Scores between 50-99
            evaluations.append(
                EvaluationResult(
                    persona_id=f"persona_{i}",
                    persona_type=f"type_{i % 10}",
                    article_id="test_article",
                    overall_score=score,
                    metrics=[
                        EvaluationMetric(name="relevance", score=min(score + 5, 100)),
                        EvaluationMetric(name="clarity", score=max(score - 5, 0)),
                    ],
                    sentiment="positive" if score > 75 else "neutral",
                    suggestions=["Improvement needed"] if score < 60 else [],
                    strengths=["Good content"],
                    weaknesses=[],
                    sharing_probability=score / 100,
                    engagement_level="high" if score > 80 else "medium",
                )
            )

        result = await agent.aggregate({e.persona_id: e for e in evaluations})

        assert result is not None
        assert len(evaluations) == 1000
        # Verify aggregation completed successfully
        assert len(evaluations) == 1000

    async def test_all_same_score_aggregation(self):
        """Test when all personas give the same score."""
        agent = AggregatorAgent()

        evaluations = []
        for i in range(10):
            evaluations.append(
                EvaluationResult(
                    persona_id=f"persona_{i}",
                    persona_type="uniform_type",
                    article_id="test_article",
                    overall_score=75,  # All same score
                    metrics=[
                        EvaluationMetric(name="relevance", score=75),
                        EvaluationMetric(name="clarity", score=75),
                    ],
                    sentiment="neutral",
                    suggestions=["Standard improvement"],
                    strengths=["Consistent"],
                    weaknesses=[],
                    sharing_probability=0.75,
                    engagement_level="medium",
                )
            )

        result = await agent.aggregate({e.persona_id: e for e in evaluations})

        metrics = result["scores"]
        assert metrics["overall_score"]["mean"] == 75
        assert metrics["overall_score"]["std"] == 0  # No variation
        assert metrics["overall_score"]["min"] == 75
        assert metrics["overall_score"]["max"] == 75

    async def test_extreme_outlier_detection(self):
        """Test outlier detection with extreme values."""
        agent = AggregatorAgent()

        evaluations = []
        # Most scores around 70-80
        for i in range(8):
            evaluations.append(
                EvaluationResult(
                    persona_id=f"persona_{i}",
                    persona_type="normal_type",
                    article_id="test_article",
                    overall_score=75,
                    metrics=[
                        EvaluationMetric(name="relevance", score=75),
                        EvaluationMetric(name="clarity", score=75),
                    ],
                    sentiment="neutral",
                    suggestions=[],
                    strengths=["Consistent"],
                    weaknesses=[],
                    sharing_probability=0.75,
                    engagement_level="medium",
                )
            )

        # Add extreme outliers
        evaluations.extend(
            [
                EvaluationResult(
                    persona_id="outlier_low",
                    persona_type="outlier_type",
                    article_id="test_article",
                    overall_score=5,  # Extreme low outlier
                    metrics=[
                        EvaluationMetric(name="relevance", score=5),
                        EvaluationMetric(name="clarity", score=5),
                    ],
                    sentiment="negative",
                    suggestions=["Complete failure"],
                    strengths=[],
                    weaknesses=["Everything"],
                    sharing_probability=0.0,
                    engagement_level="low",
                ),
                EvaluationResult(
                    persona_id="outlier_high",
                    persona_type="outlier_type",
                    article_id="test_article",
                    overall_score=100,  # Extreme high outlier
                    metrics=[
                        EvaluationMetric(name="relevance", score=100),
                        EvaluationMetric(name="clarity", score=100),
                    ],
                    sentiment="positive",
                    suggestions=[],
                    strengths=["Perfect"],
                    weaknesses=[],
                    sharing_probability=1.0,
                    engagement_level="high",
                ),
            ]
        )

        result = await agent.aggregate({e.persona_id: e for e in evaluations})

        # Check that outliers were detected
        assert "metadata" in result
        assert "outliers_detected" in result["metadata"]
        assert result["metadata"]["outliers_detected"] is True
        assert "outlier_count" in result["metadata"]
        assert result["metadata"]["outlier_count"] == 2
        assert "outlier_indices" in result["metadata"]
        assert len(result["metadata"]["outlier_indices"]) == 2

    async def test_llm_insights_error_handling(self):
        """Test error handling in LLM insights generation."""
        agent = AggregatorAgent()

        # Mock LLM to raise an exception
        agent.llm = AsyncMock()
        agent.llm.ainvoke.side_effect = Exception("LLM API Error")

        evaluations = [
            EvaluationResult(
                persona_id="persona_1",
                persona_type="test_type",
                article_id="test_article",
                overall_score=75,
                metrics=[
                    EvaluationMetric(name="relevance", score=75),
                    EvaluationMetric(name="clarity", score=75),
                ],
                sentiment="neutral",
                suggestions=["Improvement needed"],
                strengths=["Good structure"],
                weaknesses=["Lacks depth"],
                sharing_probability=0.75,
                engagement_level="medium",
            )
        ]

        result = await agent.aggregate({e.persona_id: e for e in evaluations})

        # Should handle error gracefully
        assert "insights" in result
        assert "Error generating insights" in result["insights"]

    async def test_empty_suggestions_handling(self):
        """Test handling when no suggestions are provided."""
        agent = AggregatorAgent()

        evaluations = []
        for i in range(5):
            evaluations.append(
                EvaluationResult(
                    persona_id=f"persona_{i}",
                    persona_type="satisfied_type",
                    article_id="test_article",
                    overall_score=90,
                    metrics=[
                        EvaluationMetric(name="relevance", score=90),
                        EvaluationMetric(name="clarity", score=90),
                    ],
                    sentiment="positive",
                    suggestions=[],  # No suggestions
                    strengths=["Excellent content"],
                    weaknesses=[],
                    sharing_probability=0.9,
                    engagement_level="high",
                )
            )

        result = await agent.aggregate({e.persona_id: e for e in evaluations})

        # Should handle empty suggestions gracefully
        assert "suggestions" in result
        assert len(result["suggestions"]) == 0
