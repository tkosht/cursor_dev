"""AggregatorAgent implementation for Article Market Simulator."""

import time
from collections import Counter, defaultdict
from typing import Any

import numpy as np

from src.config import get_config
from src.core.base import BaseAgent
from src.core.types import AgentID, EvaluationResult
from src.utils.json_parser import parse_llm_json_response
from src.utils.llm_factory import create_llm
from src.utils.llm_transparency import LLMCallTracker


class AggregatorAgent(BaseAgent):
    """Agent responsible for aggregating persona evaluation results."""

    def __init__(self):
        """Initialize the AggregatorAgent."""
        super().__init__(
            agent_id=AgentID("aggregator"),
            attributes={"type": "aggregator", "role": "result_aggregation"},
        )
        self.config = get_config()
        self.llm = create_llm()
        self.call_tracker = LLMCallTracker()

    async def aggregate(self, persona_evaluations: dict[str, EvaluationResult]) -> dict[str, Any]:
        """
        Aggregate evaluation results from multiple personas.

        Args:
            persona_evaluations: Dictionary mapping persona IDs to their evaluation results

        Returns:
            Aggregated results including scores, suggestions, sentiment analysis, and insights
        """
        if not persona_evaluations:
            return self._empty_result()

        # Convert dict to list for easier processing
        evaluations = list(persona_evaluations.values())

        # Aggregate metrics
        scores = self._aggregate_metrics(evaluations)

        # Prioritize suggestions
        suggestions = self._prioritize_suggestions(evaluations)

        # Analyze sentiment distribution
        sentiment = self._analyze_sentiment_distribution(evaluations)

        # Create segment analysis
        segments = self._create_segments(evaluations)

        # Detect outliers
        metadata = self._detect_outliers(evaluations)

        # Generate LLM insights
        aggregated_data = {
            "scores": scores,
            "suggestions": suggestions,
            "sentiment": sentiment,
            "segments": segments,
        }
        insights = await self._generate_insights_summary(aggregated_data)

        result = {
            "scores": scores,
            "suggestions": suggestions,
            "sentiment": sentiment,
            "segments": segments,
            "insights": insights,
        }

        # Always include metadata if we have outlier detection results
        if metadata:
            result["metadata"] = metadata

        return result

    def _aggregate_metrics(
        self, evaluations: list[EvaluationResult]
    ) -> dict[str, dict[str, float]]:
        """Aggregate score metrics across all evaluations."""
        if not evaluations:
            return {}

        # Collect all metrics
        metrics_data = defaultdict(list)

        # Aggregate overall scores
        overall_scores = []
        for eval_result in evaluations:
            overall_scores.append(eval_result.overall_score)

            # Aggregate individual metrics
            for metric in eval_result.metrics:
                metrics_data[metric.name].append(metric.score)

        # Calculate statistics for overall score
        aggregated = {}
        if overall_scores:
            scores_array = np.array(overall_scores)
            aggregated["overall_score"] = {
                "mean": float(np.mean(scores_array)),
                "median": float(np.median(scores_array)),
                "std": float(np.std(scores_array)),
                "min": float(np.min(scores_array)),
                "max": float(np.max(scores_array)),
                "percentile_25": float(np.percentile(scores_array, 25)),
                "percentile_75": float(np.percentile(scores_array, 75)),
            }

        # Calculate statistics for each individual metric
        for metric_name, scores in metrics_data.items():
            scores_array = np.array(scores)
            aggregated[metric_name] = {
                "mean": float(np.mean(scores_array)),
                "median": float(np.median(scores_array)),
                "std": float(np.std(scores_array)),
                "min": float(np.min(scores_array)),
                "max": float(np.max(scores_array)),
                "percentile_25": float(np.percentile(scores_array, 25)),
                "percentile_75": float(np.percentile(scores_array, 75)),
            }

        return aggregated

    def _prioritize_suggestions(self, evaluations: list[EvaluationResult]) -> list[dict[str, Any]]:
        """Prioritize improvement suggestions based on frequency and impact."""
        if not evaluations:
            return []

        # Count suggestion frequency
        suggestion_counter = Counter()
        suggestion_personas = defaultdict(list)

        for eval_result in evaluations:
            for suggestion in eval_result.suggestions:
                suggestion_counter[suggestion] += 1
                suggestion_personas[suggestion].append(eval_result.persona_id)

        # Create prioritized list
        prioritized = []
        for suggestion, count in suggestion_counter.most_common():
            priority = (
                "high"
                if count >= len(evaluations) * 0.5
                else "medium" if count >= len(evaluations) * 0.3 else "low"
            )

            prioritized.append(
                {
                    "suggestion": suggestion,
                    "priority": priority,
                    "affected_personas": count,
                    "impact": self._estimate_impact(count, len(evaluations)),
                    "category": self._categorize_suggestion(suggestion),
                }
            )

        return prioritized

    def _analyze_sentiment_distribution(
        self, evaluations: list[EvaluationResult]
    ) -> dict[str, Any]:
        """Analyze the distribution of sentiments across evaluations."""
        sentiment_counts = Counter()

        for eval_result in evaluations:
            sentiment_counts[eval_result.sentiment] += 1

        total = len(evaluations)
        distribution = {
            "positive": sentiment_counts.get("positive", 0),
            "neutral": sentiment_counts.get("neutral", 0),
            "negative": sentiment_counts.get("negative", 0),
        }

        # Calculate percentages
        percentages = {k: (v / total * 100) if total > 0 else 0 for k, v in distribution.items()}

        return {
            "distribution": distribution,
            "percentages": percentages,
            "dominant": max(distribution, key=distribution.get) if distribution else None,
        }

    def _create_segments(self, evaluations: list[EvaluationResult]) -> dict[str, Any]:
        """Create segment analysis based on various criteria."""
        segments = {"by_sentiment": self._segment_by_sentiment(evaluations)}

        # Additional segmentation can be added here
        # e.g., by score ranges, by persona attributes, etc.

        return segments

    def _segment_by_sentiment(self, evaluations: list[EvaluationResult]) -> dict[str, Any]:
        """Segment evaluations by sentiment."""
        sentiment_segments = defaultdict(list)

        for eval_result in evaluations:
            sentiment_segments[eval_result.sentiment].append(
                {"persona_id": eval_result.persona_id, "overall_score": eval_result.overall_score}
            )

        # Calculate average scores per sentiment
        segment_stats = {}
        for sentiment, personas in sentiment_segments.items():
            scores = [p["overall_score"] for p in personas]
            segment_stats[sentiment] = {
                "count": len(personas),
                "average_score": np.mean(scores) if scores else 0,
                "personas": personas,
            }

        return segment_stats

    def _detect_outliers(self, evaluations: list[EvaluationResult]) -> dict[str, Any]:
        """Detect outliers in the evaluation scores."""
        if len(evaluations) < 3:
            return {}

        overall_scores = [eval_result.overall_score for eval_result in evaluations]

        scores_array = np.array(overall_scores)
        q1 = np.percentile(scores_array, 25)
        q3 = np.percentile(scores_array, 75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = [
            (i, score)
            for i, score in enumerate(overall_scores)
            if score < lower_bound or score > upper_bound
        ]

        return {
            "outliers_detected": len(outliers) > 0,
            "outlier_count": len(outliers),
            "outlier_indices": [i for i, _ in outliers] if outliers else [],
        }

    async def _generate_insights_summary(self, aggregated_data: dict[str, Any]) -> str:
        """Generate LLM-based insights summary."""
        try:
            prompt = self._create_insights_prompt(aggregated_data)

            # Track LLM call
            start_time = time.time()
            response = await self.llm.ainvoke(prompt)
            latency_ms = int((time.time() - start_time) * 1000)

            # Track the call
            self.call_tracker.track_call(
                prompt=prompt, response=response.content, model=str(self.llm), latency_ms=latency_ms
            )

            parsed = parse_llm_json_response(response.content)
            return parsed.get("insights", "Unable to generate insights")

        except Exception as e:
            return f"Error generating insights: {str(e)}"

    def _create_insights_prompt(self, data: dict[str, Any]) -> str:
        """Create prompt for LLM insights generation."""
        return f"""
        Based on the following aggregated evaluation data, provide a concise insights summary:

        Scores: {data['scores']}
        Top Suggestions: {data['suggestions'][:3] if data['suggestions'] else []}
        Sentiment Distribution: {data['sentiment']}

        Generate a JSON response with an "insights" field containing a 2-3 sentence summary
        of the key findings and recommendations.
        """

    def _estimate_impact(self, affected_count: int, total_count: int) -> float:
        """Estimate the impact score of a suggestion."""
        if total_count == 0:
            return 0.0
        return round((affected_count / total_count) * 100, 1)

    def _categorize_suggestion(self, suggestion: str) -> str:
        """Categorize a suggestion based on keywords."""
        suggestion_lower = suggestion.lower()

        if any(word in suggestion_lower for word in ["example", "detail", "explain"]):
            return "content"
        elif any(word in suggestion_lower for word in ["structure", "organization", "flow"]):
            return "structure"
        elif any(word in suggestion_lower for word in ["tone", "style", "voice"]):
            return "tone"
        elif any(word in suggestion_lower for word in ["visual", "image", "diagram"]):
            return "visual"
        else:
            return "general"

    def _empty_result(self) -> dict[str, Any]:
        """Return empty result structure."""
        return {
            "scores": {},
            "suggestions": [],
            "sentiment": {
                "distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "percentages": {"positive": 0, "neutral": 0, "negative": 0},
                "dominant": None,
            },
            "segments": {},
            "insights": "No evaluations to aggregate",
        }

    # Implement abstract methods from BaseAgent
    def perceive(self, environment: Any) -> Any:
        """Perceive the environment (not used in aggregator)."""
        return environment

    def decide(self, perception: Any) -> Any:
        """Make decisions based on perception (not used in aggregator)."""
        return perception

    def act(self, decision: Any) -> Any:
        """Take action based on decision (not used in aggregator)."""
        return decision

    def update(self, feedback: Any) -> None:
        """Update internal state based on feedback (not used in aggregator)."""
        pass
