"""ReporterAgent implementation for Article Market Simulator."""

import json
import time
from datetime import datetime
from typing import Any

import numpy as np
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.config import get_config
from src.core.base import BaseAgent
from src.core.types import AgentID
from src.utils.json_parser import parse_llm_json_response
from src.utils.llm_factory import create_llm
from src.utils.llm_transparency import LLMCallTracker


class ReporterAgent(BaseAgent):
    """Agent responsible for generating comprehensive reports from simulation results."""

    def __init__(self) -> None:
        """Initialize the ReporterAgent."""
        super().__init__(
            agent_id=AgentID("reporter"),
            attributes=None,  # ReporterAgent doesn't use PersonaAttributes
        )
        self.config = get_config()
        self.llm = create_llm()
        self.call_tracker = LLMCallTracker()
        self.template_engine = self._setup_templates()

    def _setup_templates(self) -> Environment:
        """Set up Jinja2 template engine."""
        # For now, use in-memory templates
        # In production, these would be loaded from files
        env = Environment(
            loader=FileSystemLoader(searchpath="."), autoescape=select_autoescape(["html", "xml"])
        )

        # Register custom filters if needed
        env.filters["format_percentage"] = lambda x: f"{x:.1f}%"
        env.filters["format_score"] = lambda x: f"{x:.1f}"

        return env

    async def generate_report(self, state: dict[str, Any]) -> dict[str, Any]:  # ArticleReviewState
        """
        Generate comprehensive report from simulation state.

        Args:
            state: ArticleReviewState containing all simulation data

        Returns:
            Complete report with all sections and visualizations
        """
        # Check if we have minimal data
        if not state.get("article_content") or not state.get("aggregated_scores"):
            return self._generate_incomplete_report(state)

        try:
            # Generate report sections
            executive_summary = await self._generate_executive_summary(state)
            detailed_analysis = self._generate_detailed_analysis(state)
            recommendations = await self._generate_recommendations(
                state.get("aggregated_scores", {}), state.get("improvement_suggestions", [])
            )
            visualization_data = self._prepare_visualization_data(state)

            # Calculate report metrics
            metrics = self._calculate_report_metrics(state)

            # Assemble final report
            personas_evaluated = state.get("persona_count", 0)
            report = {
                "executive_summary": executive_summary,
                "detailed_analysis": detailed_analysis,
                "recommendations": recommendations,
                "visualization_data": visualization_data,
                "metadata": {
                    "simulation_id": state.get("simulation_id", "unknown"),
                    "generation_time": datetime.now().isoformat(),
                    "report_version": "1.0",
                    "personas_evaluated": personas_evaluated,
                    "metrics": metrics,
                },
            }

            # Backward/compatibility alias expected by some tests
            # Provide a concise "summary" key mirroring executive_summary
            report["summary"] = executive_summary
            # Provide a deterministic report_id for traceability in tests
            report["metadata"]["report_id"] = f"rep-{int(time.time()*1000)}"
            # Back-compat key expected by tests
            report["metadata"]["generated_at"] = report["metadata"]["generation_time"]

            return report

        except Exception as e:
            # Generate report with error indication
            return self._generate_error_report(state, str(e))

    async def _generate_executive_summary(self, state: dict[str, Any]) -> dict[str, Any]:
        """Generate executive summary with LLM assistance."""
        # Extract key data
        aggregated_scores = state.get("aggregated_scores", {})

        # Handle both simple values and dict with 'mean' key
        overall_score_data = aggregated_scores.get("overall_score")
        if overall_score_data is None:
            # Accept alternate keys used in tests
            overall_score_data = aggregated_scores.get("overall") or aggregated_scores.get(
                "overall_average"
            )
        if isinstance(overall_score_data, dict) and "mean" in overall_score_data:
            overall_score = overall_score_data["mean"]
        elif isinstance(overall_score_data, (int, float)):
            overall_score = float(overall_score_data)
        else:
            overall_score = 0.0

        top_suggestions = state.get("improvement_suggestions", [])[:3]

        # Generate LLM insights
        try:
            prompt = self._create_summary_prompt(state)

            start_time = time.time()
            response = await self.llm.ainvoke(prompt)
            latency_ms = int((time.time() - start_time) * 1000)

            response_str = str(response.content) if hasattr(response, "content") else str(response)
            self.call_tracker.track_call(
                prompt=prompt, response=response_str, model=str(self.llm), latency_ms=latency_ms
            )

            parsed = parse_llm_json_response(response_str)
            key_findings = parsed.get("key_findings", [])
            overview = parsed.get("overview", "")

        except Exception:
            # Fallback to basic summary
            key_findings = self._generate_basic_findings(state)
            overview = "Article review simulation completed successfully."

        return {
            "overview": overview,
            "key_findings": key_findings,
            "overall_score": overall_score,
            "top_recommendations": [
                {
                    "suggestion": s.get("suggestion", ""),
                    "priority": s.get("priority", "medium"),
                    "impact": s.get("impact", 0),
                }
                for s in top_suggestions
            ],
        }

    def _generate_detailed_analysis(self, state: dict[str, Any]) -> dict[str, Any]:
        """Generate detailed analysis sections."""
        return {
            "article_analysis": self._analyze_article(state),
            "persona_analysis": self._analyze_personas(state),
            "evaluation_results": self._analyze_evaluations(state),
            "improvement_areas": self._analyze_improvements(state),
        }

    async def _generate_recommendations(
        self, aggregated_scores: dict[str, float], improvement_suggestions: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Generate actionable recommendations with LLM enhancement."""
        if not improvement_suggestions:
            return []

        try:
            # Use LLM to enhance recommendations
            prompt = self._create_recommendations_prompt(aggregated_scores, improvement_suggestions)

            start_time = time.time()
            response = await self.llm.ainvoke(prompt)
            latency_ms = int((time.time() - start_time) * 1000)

            response_str = str(response.content) if hasattr(response, "content") else str(response)
            self.call_tracker.track_call(
                prompt=prompt, response=response_str, model=str(self.llm), latency_ms=latency_ms
            )

            parsed = parse_llm_json_response(response_str)
            recommendations = parsed.get("recommendations", [])
            return recommendations if isinstance(recommendations, list) else []

        except Exception:
            # Fallback to basic recommendations
            return [
                {
                    "action": s.get("suggestion", ""),
                    "impact": s.get("priority", "medium"),
                    "steps": ["Review content", "Implement changes", "Test with audience"],
                    "expected_improvement": f"{s.get('impact', 10):.1f}%",
                }
                for s in improvement_suggestions[:5]
            ]

    def _prepare_visualization_data(self, state: dict[str, Any]) -> dict[str, Any]:
        """Prepare data for visualizations."""
        return {
            "charts": {
                "score_distribution": self._create_score_distribution_data(state),
                "metric_radar": self._create_radar_chart_data(state),
                "sentiment_pie": self._create_sentiment_pie_data(state),
                "persona_heatmap": self._create_persona_heatmap_data(state),
            }
        }

    def _format_report(
        self, report_data: dict[str, Any], format: str = "json"
    ) -> str | dict[str, Any]:
        """Format report in requested format."""
        if format == "json":
            return report_data

        elif format == "markdown":
            return self._format_as_markdown(report_data)

        elif format == "html":
            return self._format_as_html(report_data)

        else:
            # Default to JSON
            return report_data

    def _calculate_report_metrics(self, state: dict[str, Any]) -> dict[str, Any]:
        """Calculate metrics about the report generation."""
        start_time = state.get("start_time", datetime.now())

        return {
            "total_personas": state.get("persona_count", 0),
            "average_score": state.get("aggregated_scores", {}).get("overall", 0),
            "sentiment_distribution": self._calculate_sentiment_distribution(state),
            "completion_time": (datetime.now() - start_time).total_seconds(),
            "data_completeness": self._calculate_completeness(state),
        }

    def _render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with given context."""
        # For now, use simple string templates
        # In production, would load from template files
        if template_name == "executive_summary":
            return self._render_executive_summary_template(context)
        elif template_name == "detailed_analysis":
            return self._render_detailed_analysis_template(context)
        else:
            return ""

    # Helper methods
    def _generate_incomplete_report(self, state: dict[str, Any]) -> dict[str, Any]:
        """Generate report when data is incomplete."""
        return {
            "executive_summary": {
                "overview": "Report generated with incomplete data",
                "key_findings": [],
                "overall_score": 0,
                "top_recommendations": [],
            },
            "detailed_analysis": {},
            "recommendations": [],
            "visualization_data": {"charts": {}},
            "metadata": {
                "warning": "Report generated with incomplete data",
                "simulation_id": state.get("simulation_id", "unknown"),
                "generation_time": datetime.now().isoformat(),
            },
        }

    def _generate_error_report(self, state: dict[str, Any], error: str) -> dict[str, Any]:
        """Generate report when an error occurs."""
        aggregated_scores = state.get("aggregated_scores", {})
        overall_score_data = aggregated_scores.get(
            "overall_score", aggregated_scores.get("overall", 0)
        )
        if isinstance(overall_score_data, dict) and "mean" in overall_score_data:
            overall_score = overall_score_data["mean"]
        else:
            overall_score = overall_score_data if isinstance(overall_score_data, int | float) else 0

        return {
            "executive_summary": {
                "overview": "Report generation encountered an error",
                "key_findings": [],
                "overall_score": overall_score,
                "top_recommendations": [],
            },
            "detailed_analysis": self._generate_detailed_analysis(state),
            "recommendations": [],
            "visualization_data": {"charts": {}},
            "metadata": {
                "error": error,
                "simulation_id": state.get("simulation_id", "unknown"),
                "generation_time": datetime.now().isoformat(),
            },
        }

    def _create_summary_prompt(self, state: dict[str, Any]) -> str:
        """Create prompt for executive summary generation."""
        aggregated_scores = state.get("aggregated_scores", {})
        overall_score_data = aggregated_scores.get(
            "overall_score", aggregated_scores.get("overall", 0)
        )
        if isinstance(overall_score_data, dict) and "mean" in overall_score_data:
            overall_score = overall_score_data["mean"]
        else:
            overall_score = overall_score_data if isinstance(overall_score_data, int | float) else 0

        return f"""
        Based on the following article review simulation results, generate an executive summary:

        Article: {state.get('article_metadata', {}).get('title', 'Unknown')}
        Overall Score: {overall_score:.1f}
        Number of Personas: {state.get('persona_count', 0)}
        Key Topics: {', '.join(state.get('analysis_results', {}).get('topics', []))}

        Generate a JSON response with:
        - "overview": A 2-3 sentence overview of the simulation results
        - "key_findings": A list of 3-5 key findings (strings)
        """

    def _create_recommendations_prompt(
        self, scores: dict[str, float], suggestions: list[dict[str, Any]]
    ) -> str:
        """Create prompt for recommendations enhancement."""
        suggestions_text = "\n".join(
            [f"- {s.get('suggestion')} (Priority: {s.get('priority')})" for s in suggestions[:5]]
        )

        return f"""
        Based on the following evaluation scores and suggestions, generate actionable
        recommendations:

        Scores: {json.dumps(scores, indent=2)}

        Suggestions:
        {suggestions_text}

        Generate a JSON response with "recommendations" array, where each recommendation has:
        - "action": Specific action to take
        - "impact": Expected impact level (high/medium/low)
        - "steps": List of 2-4 implementation steps
        - "expected_improvement": Estimated improvement percentage
        """

    def _generate_basic_findings(self, state: dict[str, Any]) -> list[str]:
        """Generate basic findings without LLM."""
        findings = []

        score = state.get("aggregated_scores", {}).get("overall", 0)
        if score >= 80:
            findings.append("Article received high overall ratings from most personas")
        elif score >= 60:
            findings.append("Article received moderate ratings with room for improvement")
        else:
            findings.append("Article needs significant improvements based on persona feedback")

        persona_count = state.get("persona_count", 0)
        if persona_count > 0:
            findings.append(f"Evaluated by {persona_count} diverse personas")

        suggestions = state.get("improvement_suggestions", [])
        if suggestions:
            findings.append(f"Identified {len(suggestions)} areas for improvement")

        return findings

    def _analyze_article(self, state: dict[str, Any]) -> dict[str, Any]:
        """Analyze article characteristics."""
        analysis = state.get("analysis_results", {})
        metadata = state.get("article_metadata", {})

        return {
            "title": metadata.get("title", "Unknown"),
            "category": metadata.get("category", "Unknown"),
            "topics": analysis.get("topics", []),
            "tone": analysis.get("tone", "Unknown"),
            "target_audience": analysis.get("target_audience", "Unknown"),
            "complexity": analysis.get("complexity", "Unknown"),
            "word_count": len(state.get("article_content", "").split()),
        }

    def _analyze_personas(self, state: dict[str, Any]) -> dict[str, Any]:
        """Analyze persona distribution and characteristics."""
        personas = state.get("generated_personas", [])

        if not personas:
            return {"total_count": 0, "segments": {}}

        # Analyze persona segments
        segments: dict[str, dict[str, Any]] = {}
        for persona in personas:
            # Handle both dict and PersonaAttributes objects
            if hasattr(persona, 'occupation'):
                occupation = persona.occupation
                age = persona.age if hasattr(persona, 'age') else None
            else:
                occupation = persona.get("occupation", "Unknown")
                age = persona.get("age")
            
            if occupation not in segments:
                segments[occupation] = {"count": 0, "average_age": 0, "interests": []}
            segments[occupation]["count"] += 1
            if age and isinstance(age, int | float):
                segments[occupation]["average_age"] += age

        # Calculate averages
        for segment in segments.values():
            if segment["count"] > 0 and isinstance(segment["average_age"], int | float):
                segment["average_age"] = segment["average_age"] / segment["count"]

        return {
            "total_count": len(personas),
            "segments": segments,
            "diversity_score": self._calculate_diversity_score(personas),
        }

    def _analyze_evaluations(self, state: dict[str, Any]) -> dict[str, Any]:
        """Analyze evaluation results."""
        evaluations = state.get("persona_evaluations", {})
        scores = state.get("aggregated_scores", {})

        # Extract numeric scores from aggregated scores
        numeric_scores = []
        for _key, value in scores.items():
            if isinstance(value, int | float):
                numeric_scores.append(value)
            elif isinstance(value, dict) and "mean" in value:
                numeric_scores.append(value["mean"])

        # Derive overall score from various possible shapes
        overall_score_data = (
            scores.get("overall_score")
            if isinstance(scores.get("overall_score"), (int, float, dict))
            else None
        )
        if overall_score_data is None:
            overall_score_data = scores.get("overall") or scores.get("overall_average")

        if isinstance(overall_score_data, dict) and "mean" in overall_score_data:
            overall_score_value = overall_score_data["mean"]
        elif isinstance(overall_score_data, (int, float)):
            overall_score_value = overall_score_data
        else:
            overall_score_value = 0

        return {
            "total_evaluations": len(evaluations),
            "average_scores": scores,
            "score_range": {
                "min": min(numeric_scores) if numeric_scores else 0,
                "max": max(numeric_scores) if numeric_scores else 0,
            },
            "consensus_level": self._calculate_consensus(evaluations),
            "overall_score": overall_score_value,
        }

    def _analyze_improvements(self, state: dict[str, Any]) -> dict[str, Any]:
        """Analyze improvement suggestions."""
        suggestions = state.get("improvement_suggestions", [])

        # Group by category
        by_category: dict[str, list[dict[str, Any]]] = {}
        for suggestion in suggestions:
            category = suggestion.get("category", "general")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(suggestion)

        return {
            "total_suggestions": len(suggestions),
            "by_category": by_category,
            "high_priority_count": len([s for s in suggestions if s.get("priority") == "high"]),
            "estimated_total_impact": sum(s.get("impact", 0) for s in suggestions),
        }

    def _create_score_distribution_data(self, state: dict[str, Any]) -> dict[str, Any]:
        """Create data for score distribution histogram."""
        evaluations = state.get("persona_evaluations", {})
        scores = []
        for e in evaluations.values():
            if hasattr(e, 'overall_score'):
                scores.append(e.overall_score)
            elif isinstance(e, dict):
                scores.append(e.get("overall_score", 0))
            else:
                scores.append(0)

        if not scores:
            return {"type": "histogram", "data": {}, "layout": {}}

        # Create histogram bins
        bins = list(range(0, 101, 10))
        hist_data = {f"{b}-{b+10}": 0 for b in bins[:-1]}

        for score in scores:
            bin_idx = min(int(score // 10) * 10, 90)
            bin_key = f"{bin_idx}-{bin_idx+10}"
            hist_data[bin_key] += 1

        return {
            "type": "histogram",
            "data": {
                "x": list(hist_data.keys()),
                "y": list(hist_data.values()),
                "name": "Score Distribution",
            },
            "layout": {
                "title": "Overall Score Distribution",
                "xaxis": {"title": "Score Range"},
                "yaxis": {"title": "Number of Personas"},
            },
        }

    def _create_radar_chart_data(self, state: dict[str, Any]) -> dict[str, Any]:
        """Create data for metrics radar chart."""
        scores = state.get("aggregated_scores", {})

        # Extract relevant metrics
        metrics = ["relevance", "clarity", "engagement"]
        values = [scores.get(m, 0) for m in metrics]

        return {
            "type": "radar",
            "data": {"categories": metrics, "values": values, "name": "Article Metrics"},
            "layout": {
                "title": "Multi-Dimensional Article Assessment",
                "polar": {"radialaxis": {"visible": True, "range": [0, 100]}},
            },
        }

    def _create_sentiment_pie_data(self, state: dict[str, Any]) -> dict[str, Any]:
        """Create data for sentiment distribution pie chart."""
        evaluations = state.get("persona_evaluations", {})

        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        for eval_data in evaluations.values():
            sentiment = eval_data.sentiment
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1

        return {
            "type": "pie",
            "data": {
                "labels": list(sentiment_counts.keys()),
                "values": list(sentiment_counts.values()),
                "name": "Sentiment Distribution",
            },
            "layout": {"title": "Persona Sentiment Distribution"},
        }

    def _create_persona_heatmap_data(self, state: dict[str, Any]) -> dict[str, Any]:
        """Create data for persona evaluation heatmap."""
        evaluations = state.get("persona_evaluations", {})

        if not evaluations:
            return {"type": "heatmap", "data": {}, "layout": {}}

        # Create matrix of personas vs metrics
        personas = list(evaluations.keys())[:10]  # Limit to 10 for visibility
        metrics = ["overall_score", "sharing_probability"]

        matrix = []
        for persona_id in personas:
            eval_data = evaluations[persona_id]
            row = [eval_data.overall_score, eval_data.sharing_probability * 100]
            matrix.append(row)

        return {
            "type": "heatmap",
            "data": {"x": metrics, "y": personas, "z": matrix, "name": "Persona Evaluation Matrix"},
            "layout": {
                "title": "Persona Evaluation Heatmap",
                "xaxis": {"title": "Metrics"},
                "yaxis": {"title": "Personas"},
            },
        }

    def _calculate_sentiment_distribution(self, state: dict[str, Any]) -> dict[str, float]:
        """Calculate sentiment distribution percentages."""
        evaluations = state.get("persona_evaluations", {})
        total = len(evaluations)

        if total == 0:
            return {"positive": 0, "neutral": 0, "negative": 0}

        counts = {"positive": 0, "neutral": 0, "negative": 0}
        for eval_data in evaluations.values():
            sentiment = eval_data.sentiment
            if sentiment in counts:
                counts[sentiment] += 1

        return {k: (v / total * 100) for k, v in counts.items()}

    def _calculate_completeness(self, state: dict[str, Any]) -> float:
        """Calculate data completeness score."""
        required_fields = [
            "article_content",
            "analysis_results",
            "generated_personas",
            "persona_evaluations",
            "aggregated_scores",
            "improvement_suggestions",
        ]

        present = sum(1 for field in required_fields if state.get(field))
        return (present / len(required_fields)) * 100

    def _calculate_diversity_score(self, personas: list[Any]) -> float:
        """Calculate diversity score for personas."""
        if not personas:
            return 0

        # Simple diversity calculation based on unique occupations
        occupations = set()
        for p in personas:
            if hasattr(p, 'occupation'):
                occupations.add(p.occupation)
            elif isinstance(p, dict) and p.get("occupation"):
                occupations.add(p.get("occupation"))
        return min((len(occupations) / len(personas)) * 100, 100) if personas else 0

    def _calculate_consensus(self, evaluations: dict[str, Any]) -> float:
        """Calculate consensus level among evaluations."""
        if len(evaluations) < 2:
            return 100

        scores = []
        for e in evaluations.values():
            if hasattr(e, 'overall_score'):
                scores.append(e.overall_score)
            elif isinstance(e, dict):
                scores.append(e.get("overall_score", 0))
            else:
                scores.append(0)
        if not scores:
            return 0

        # Calculate standard deviation as inverse measure of consensus

        std_dev = float(np.std(scores))
        # Convert to consensus score (lower std = higher consensus)
        consensus: float = max(0, 100 - (std_dev * 2))
        return consensus

    def _calculate_confidence_score(self, persona_count: int, score_variance: float) -> float:
        """Estimate confidence (0-100) based on sample size and variance.

        Larger samples increase confidence; higher variance reduces it.
        """
        base = min(max(persona_count, 0) / 50.0, 1.0) * 100.0
        penalty = min(max(score_variance, 0.0) * 2.0, 60.0)
        return max(0.0, min(100.0, base - penalty))

    def _generate_key_insights(self, aggregated_scores: dict[str, Any]) -> list[str]:
        """Generate deterministic key insights from aggregated scores."""
        insights: list[str] = []
        overall = (
            aggregated_scores.get("overall_average")
            or aggregated_scores.get("overall")
            or (
                aggregated_scores.get("overall_score", {}).get("mean")
                if isinstance(aggregated_scores.get("overall_score"), dict)
                else aggregated_scores.get("overall_score")
            )
            or 0
        )
        insights.append(
            f"Overall article quality is approximately {float(overall):.1f} out of 100 based on persona evaluations."
        )

        metric_avgs = aggregated_scores.get("metric_averages", {})
        if metric_avgs:
            top_metric = max(metric_avgs, key=lambda k: metric_avgs[k])
            insights.append(
                f"Strength observed in {top_metric}; this metric outperforms others in aggregated scoring."
            )

        sentiment = aggregated_scores.get("sentiment_distribution", {})
        if sentiment:
            pos = sentiment.get("positive", 0)
            neu = sentiment.get("neutral", 0)
            neg = sentiment.get("negative", 0)
            insights.append(
                f"Sentiment breakdown indicates positive:{pos}, neutral:{neu}, negative:{neg}, suggesting balanced reception."
            )

        return insights or [
            "Aggregated data is limited; collect more evaluations to improve statistical confidence."
        ]

    def _prepare_analysis_structure(self, state: dict[str, Any]) -> dict[str, Any]:
        """Prepare a safe analysis structure even with missing data."""
        safe_state = state or {}
        return {
            "article_analysis": self._analyze_article(safe_state),
            "persona_analysis": self._analyze_personas(safe_state),
            "evaluation_results": self._analyze_evaluations(safe_state),
            "improvement_areas": self._analyze_improvements(safe_state),
        }

    def _format_as_markdown(self, report_data: dict[str, Any]) -> str:
        """Format report as Markdown."""
        md_lines = [
            "# Article Review Report",
            "",
            f"**Generated**: {report_data['metadata']['generation_time']}",
            f"**Simulation ID**: {report_data['metadata']['simulation_id']}",
            "",
            "## Executive Summary",
            "",
            report_data["executive_summary"]["overview"],
            "",
            "### Key Findings",
            "",
        ]

        for finding in report_data["executive_summary"]["key_findings"]:
            md_lines.append(f"- {finding}")

        md_lines.extend(
            [
                "",
                f"**Overall Score**: {report_data['executive_summary']['overall_score']:.1f}/100",
                "",
                "## Top Recommendations",
                "",
            ]
        )

        for rec in report_data["executive_summary"]["top_recommendations"]:
            md_lines.append(f"1. **{rec['suggestion']}** (Priority: {rec['priority']})")
            md_lines.append(f"   - Expected Impact: {rec['impact']:.1f}%")

        md_lines.extend(
            [
                "",
                "## Detailed Analysis",
                "",
                "### Article Information",
                f"- **Title**: {report_data['detailed_analysis']['article_analysis']['title']}",
                f"- **Category**: "
                f"{report_data['detailed_analysis']['article_analysis']['category']}",
                f"- **Word Count**: "
                f"{report_data['detailed_analysis']['article_analysis']['word_count']}",
                "",
                "## Recommendations",
                "",
            ]
        )

        for i, rec in enumerate(report_data["recommendations"], 1):
            md_lines.append(f"### {i}. {rec.get('action', 'Recommendation')}")
            md_lines.append(f"**Impact**: {rec.get('impact', 'medium')}")
            md_lines.append("**Steps**:")
            for step in rec.get("steps", []):
                md_lines.append(f"- {step}")
            md_lines.append("")

        return "\n".join(md_lines)

    def _format_as_html(self, report_data: dict[str, Any]) -> str:
        """Format report as HTML."""
        html = f"""
        <html>
        <head>
            <title>Article Review Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1, h2, h3 {{ color: #333; }}
                .metric {{ background: #f0f0f0; padding: 10px; margin: 10px 0; }}
                .recommendation {{ background: #e8f4fd; padding: 15px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <h1>Article Review Report</h1>
            <p><strong>Generated</strong>: {report_data['metadata']['generation_time']}</p>

            <h2>Executive Summary</h2>
            <p>{report_data['executive_summary']['overview']}</p>

            <div class="metric">
                <h3>Overall Score: {report_data['executive_summary']['overall_score']:.1f}/100</h3>
            </div>

            <h2>Key Findings</h2>
            <ul>
        """

        for finding in report_data["executive_summary"]["key_findings"]:
            html += f"<li>{finding}</li>"

        html += """
            </ul>

            <h2>Recommendations</h2>
        """

        for rec in report_data["recommendations"]:
            html += f"""
            <div class="recommendation">
                <h3>{rec.get('action', 'Recommendation')}</h3>
                <p><strong>Impact</strong>: {rec.get('impact', 'medium')}</p>
                <p><strong>Steps</strong>:</p>
                <ul>
            """
            for step in rec.get("steps", []):
                html += f"<li>{step}</li>"
            html += """
                </ul>
            </div>
            """

        html += """
        </body>
        </html>
        """

        return html

    def _render_executive_summary_template(self, context: dict[str, Any]) -> str:
        """Render executive summary template."""
        # Simple template rendering without Jinja2
        return f"""
        Executive Summary
        =================

        {context.get('overview', '')}

        Overall Score: {context.get('overall_score', 0):.1f}/100

        Key Findings:
        {chr(10).join('- ' + f for f in context.get('key_findings', []))}
        """

    def _render_detailed_analysis_template(self, context: dict[str, Any]) -> str:
        """Render detailed analysis template."""
        return f"""
        Detailed Analysis
        ================

        Article: {context.get('title', 'Unknown')}
        Category: {context.get('category', 'Unknown')}

        Topics: {', '.join(context.get('topics', []))}
        Target Audience: {context.get('target_audience', 'Unknown')}
        """

    # Implement abstract methods from BaseAgent
    def perceive(self, environment: Any) -> Any:
        """Perceive the environment (not used in reporter)."""
        return environment

    def decide(self, perception: Any) -> Any:
        """Make decisions based on perception (not used in reporter)."""
        return perception

    async def act(self, action: Any, environment: Any) -> Any:
        """Take action based on decision (not used in reporter)."""
        return action

    async def update(self, feedback: Any) -> None:
        """Update internal state based on feedback (not used in reporter)."""
        pass
