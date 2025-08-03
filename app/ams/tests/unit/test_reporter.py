"""Unit tests for ReporterAgent."""

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.reporter import ReporterAgent
from src.core.types import EvaluationMetric, EvaluationResult, PersonaAttributes


class TestReporterAgent:
    """Test suite for ReporterAgent."""

    @pytest.fixture
    def sample_state(self) -> dict[str, Any]:
        """Create sample ArticleReviewState for testing."""
        return {
            "article_content": "This is a test article about AI and machine learning.",
            "article_metadata": {
                "title": "Understanding AI",
                "author": "Test Author",
                "category": "Technology",
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
                "topics": ["AI", "Machine Learning", "Technology"],
                "tone": "informative",
                "target_audience": "tech professionals",
                "complexity": "intermediate",
            },
            "persona_count": 3,
            "generated_personas": [
                PersonaAttributes(
                    age=30,
                    occupation="Software Engineer",
                    interests=["AI", "Technology"],
                    values=["Innovation", "Learning"],
                ),
                PersonaAttributes(
                    age=25,
                    occupation="Data Scientist",
                    interests=["Machine Learning", "Statistics"],
                    values=["Accuracy", "Research"],
                ),
                PersonaAttributes(
                    age=35,
                    occupation="Product Manager",
                    interests=["Technology", "Business"],
                    values=["Efficiency", "User Experience"],
                ),
            ],
            "persona_generation_complete": True,
            "persona_evaluations": {
                "persona_1": EvaluationResult(
                    persona_id="persona_1",
                    persona_type="tech_enthusiast",
                    article_id="test_001",
                    overall_score=85,
                    metrics=[
                        EvaluationMetric(name="relevance", score=90),
                        EvaluationMetric(name="clarity", score=80),
                    ],
                    sentiment="positive",
                    suggestions=["Add more examples"],
                    strengths=["Clear structure"],
                    weaknesses=["Lacks examples"],
                    sharing_probability=0.8,
                    engagement_level="high",
                )
            },
            "evaluation_complete": True,
            "aggregated_scores": {
                "overall": 82.5,
                "relevance": 87.0,
                "clarity": 78.0,
                "engagement": 80.0,
            },
            "improvement_suggestions": [
                {
                    "suggestion": "Add more examples",
                    "priority": "high",
                    "affected_personas": 2,
                    "impact": 15.0,
                    "category": "content",
                },
                {
                    "suggestion": "Simplify technical terms",
                    "priority": "medium",
                    "affected_personas": 1,
                    "impact": 10.0,
                    "category": "clarity",
                },
            ],
            "final_report": {},
            "messages": [],
            "errors": [],
            "retry_count": {},
            "simulation_id": "test_sim_001",
            "start_time": datetime.now(),
            "end_time": None,
        }

    @pytest.mark.asyncio
    async def test_generate_report_basic(self, sample_state):
        """Test basic report generation functionality."""
        agent = ReporterAgent()
        report = await agent.generate_report(sample_state)

        assert isinstance(report, dict)
        assert "executive_summary" in report
        assert "detailed_analysis" in report
        assert "recommendations" in report
        assert "visualization_data" in report
        assert "metadata" in report

    @pytest.mark.asyncio
    async def test_executive_summary_generation(self, sample_state):
        """Test executive summary generation."""
        agent = ReporterAgent()
        summary = await agent._generate_executive_summary(sample_state)

        assert "overview" in summary
        assert "key_findings" in summary
        assert "overall_score" in summary
        assert "top_recommendations" in summary

        # Check key findings structure
        assert isinstance(summary["key_findings"], list)
        assert len(summary["key_findings"]) >= 3

        # Check overall score
        assert summary["overall_score"] == sample_state["aggregated_scores"]["overall"]

    @pytest.mark.asyncio
    async def test_detailed_analysis_generation(self, sample_state):
        """Test detailed analysis section generation."""
        agent = ReporterAgent()
        analysis = agent._generate_detailed_analysis(sample_state)

        assert "article_analysis" in analysis
        assert "persona_analysis" in analysis
        assert "evaluation_results" in analysis
        assert "improvement_areas" in analysis

    @pytest.mark.asyncio
    async def test_recommendations_generation(self, sample_state):
        """Test recommendations generation with LLM enhancement."""
        agent = ReporterAgent()

        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = (
            '{"recommendations": [{"action": "Add examples", "impact": "high", '
            '"steps": ["Step 1", "Step 2"]}]}'
        )

        with patch.object(agent, "llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)

            recommendations = await agent._generate_recommendations(
                sample_state["aggregated_scores"], sample_state["improvement_suggestions"]
            )

            assert isinstance(recommendations, list)
            assert len(recommendations) > 0
            assert "action" in recommendations[0]
            assert "impact" in recommendations[0]
            assert "steps" in recommendations[0]

    @pytest.mark.asyncio
    async def test_visualization_data_preparation(self, sample_state):
        """Test visualization data preparation."""
        agent = ReporterAgent()
        viz_data = agent._prepare_visualization_data(sample_state)

        assert "charts" in viz_data
        charts = viz_data["charts"]

        # Check for expected chart types
        assert "score_distribution" in charts
        assert "metric_radar" in charts
        assert "sentiment_pie" in charts

        # Check chart structure
        for _chart_name, chart_data in charts.items():
            assert "type" in chart_data
            assert "data" in chart_data
            assert "layout" in chart_data

    @pytest.mark.asyncio
    async def test_format_report_json(self, sample_state):
        """Test JSON format report generation."""
        agent = ReporterAgent()
        report_data = await agent.generate_report(sample_state)

        formatted = agent._format_report(report_data, "json")

        # JSON format should return the dictionary as-is
        assert isinstance(formatted, dict)
        assert formatted == report_data

    @pytest.mark.asyncio
    async def test_format_report_markdown(self, sample_state):
        """Test Markdown format report generation."""
        agent = ReporterAgent()
        report_data = await agent.generate_report(sample_state)

        formatted = agent._format_report(report_data, "markdown")

        # Markdown format should return a string
        assert isinstance(formatted, str)
        assert "# Article Review Report" in formatted
        assert "## Executive Summary" in formatted
        assert "## Recommendations" in formatted

    @pytest.mark.asyncio
    async def test_format_report_html(self, sample_state):
        """Test HTML format report generation."""
        agent = ReporterAgent()
        report_data = await agent.generate_report(sample_state)

        formatted = agent._format_report(report_data, "html")

        # HTML format should return a string with HTML tags
        assert isinstance(formatted, str)
        assert "<html>" in formatted
        assert "<body>" in formatted
        assert "Article Review Report" in formatted

    @pytest.mark.asyncio
    async def test_empty_state_handling(self):
        """Test handling of minimal/empty state."""
        minimal_state = {
            "article_content": "",
            "article_metadata": {},
            "current_phase": "reporting",
            "phase_status": {},
            "active_agents": [],
            "agent_status": {},
            "analysis_results": {},
            "persona_count": 0,
            "generated_personas": [],
            "persona_generation_complete": False,
            "persona_evaluations": {},
            "evaluation_complete": False,
            "aggregated_scores": {},
            "improvement_suggestions": [],
            "final_report": {},
            "messages": [],
            "errors": [],
            "retry_count": {},
            "simulation_id": "empty_001",
            "start_time": datetime.now(),
            "end_time": None,
        }

        agent = ReporterAgent()
        report = await agent.generate_report(minimal_state)

        assert isinstance(report, dict)
        assert "executive_summary" in report
        assert report["metadata"]["warning"] == "Report generated with incomplete data"

    @pytest.mark.asyncio
    async def test_error_handling_in_generation(self, sample_state):
        """Test error handling during report generation."""
        agent = ReporterAgent()

        # Mock LLM to raise an error
        with patch.object(agent, "llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM Error"))

            # Should still generate a report, but with fallback content
            report = await agent.generate_report(sample_state)

            assert isinstance(report, dict)
            assert "executive_summary" in report
            # Executive summary should have basic findings even with LLM error
            assert len(report["executive_summary"]["key_findings"]) > 0

    def test_calculate_metrics(self, sample_state):
        """Test internal metrics calculation."""
        agent = ReporterAgent()

        metrics = agent._calculate_report_metrics(sample_state)

        assert "total_personas" in metrics
        assert "average_score" in metrics
        assert "sentiment_distribution" in metrics
        assert "completion_time" in metrics

        assert metrics["total_personas"] == 3
        assert metrics["average_score"] == 82.5

    @pytest.mark.asyncio
    async def test_template_rendering(self, sample_state):
        """Test template rendering functionality."""
        agent = ReporterAgent()

        # Test that templates are properly set up
        assert agent.template_engine is not None

        # Test rendering a simple template

        # This will test the actual template rendering when implemented
        # For now, we just verify the setup
        assert hasattr(agent, "_render_template")

    @pytest.mark.asyncio
    async def test_boundary_empty_aggregated_results(self):
        """Test report generation with empty aggregated results."""
        agent = ReporterAgent()

        state = {
            "article_content": "Test article",
            "analysis_results": {"topics": ["AI"]},
            "aggregated_scores": {},  # Empty results
            "improvement_suggestions": [],
            "simulation_id": "test_001",
        }

        result = await agent.generate_report(state)

        assert "executive_summary" in result
        assert "detailed_analysis" in result
        assert "recommendations" in result
        assert "metadata" in result
        # Should generate a minimal report even with empty data

    @pytest.mark.asyncio
    async def test_boundary_maximum_size_report(self):
        """Test handling of extremely large report data."""
        agent = ReporterAgent()

        # Generate large amount of data
        large_suggestions = []
        for i in range(100):
            large_suggestions.append(
                {
                    "suggestion": f"This is a very long suggestion number {i} with lots of "
                    f"details and explanations about improvements needed in the article "
                    f"content and structure",
                    "personas": [f"persona_{j}" for j in range(20)],
                    "impact": 15.0,  # Numeric impact value
                    "priority": "high",
                    "category": "content",
                }
            )

        state = {
            "article_content": "Test article " * 1000,  # Large article
            "analysis_results": {"topics": ["AI"] * 50, "sentiment": "positive", "complexity": 8.5},
            "aggregated_scores": {
                "overall_score": {"mean": 75, "std": 10, "min": 50, "max": 95},
                "relevance": {"mean": 80, "std": 8},
                "clarity": {"mean": 70, "std": 12},
            },
            "improvement_suggestions": large_suggestions,
            "persona_evaluations": {},
            "simulation_id": "test_large",
        }

        result = await agent.generate_report(state)

        assert "executive_summary" in result
        assert "detailed_analysis" in result
        # Should handle large data without crashing

    @pytest.mark.asyncio
    async def test_boundary_special_characters_handling(self):
        """Test handling of special characters in report data."""
        agent = ReporterAgent()

        state = {
            "article_content": "Article with special chars: <>&\"'@#$%^&*()",
            "analysis_results": {
                "topics": ["AI & ML", "Data <Science>", 'Web"Development"'],
                "sentiment": "positive",
            },
            "aggregated_scores": {"overall_score": {"mean": 80, "std": 5, "min": 70, "max": 90}},
            "improvement_suggestions": [
                {
                    "suggestion": 'Add more <examples> & "quotes"',
                    "personas": ["tech_expert"],
                    "impact": 10.0,
                    "priority": "medium",
                    "category": "content",
                }
            ],
            "simulation_id": "test_special",
        }

        result = await agent.generate_report(state)

        assert "executive_summary" in result
        assert "detailed_analysis" in result
        # Special characters should be properly escaped in different formats

    @pytest.mark.asyncio
    async def test_boundary_invalid_format_request(self):
        """Test handling of invalid format requests."""
        agent = ReporterAgent()

        # Test invalid format
        invalid_format_report = agent._format_report(
            {"content": "Test"}, "invalid_format"  # Not a valid format
        )

        # Should default to JSON format (returns dict)
        assert isinstance(invalid_format_report, dict)
        assert invalid_format_report == {"content": "Test"}

    @pytest.mark.asyncio
    async def test_boundary_multilingual_content(self):
        """Test handling of multilingual content in reports."""
        agent = ReporterAgent()

        state = {
            "article_content": "Article in English, 日本語のテキスト, Texto en español",
            "analysis_results": {
                "topics": ["多言語処理", "Multilingüe", "Multilingual"],
                "sentiment": "positive",
            },
            "aggregated_scores": {"overall_score": {"mean": 85}},
            "improvement_suggestions": [
                {
                    "suggestion": "もっと例を追加してください",
                    "personas": ["japanese_reader"],
                    "impact": 15.0,
                    "priority": "high",
                    "category": "content",
                }
            ],
            "simulation_id": "test_multilingual",
        }

        result = await agent.generate_report(state)

        assert "executive_summary" in result
        assert "detailed_analysis" in result
        # Should handle multilingual content properly

    @pytest.mark.asyncio
    async def test_boundary_zero_evaluations(self):
        """Test report generation with zero evaluations."""
        agent = ReporterAgent()

        state = {
            "article_content": "Test article",
            "analysis_results": {"topics": ["AI"]},
            "aggregated_scores": {},
            "improvement_suggestions": [],
            "persona_evaluations": {},
            "simulation_id": "test_zero",
        }

        result = await agent.generate_report(state)

        assert "executive_summary" in result
        assert "detailed_analysis" in result
        # Should handle zero evaluations gracefully

    @pytest.mark.asyncio
    async def test_boundary_extreme_scores(self):
        """Test handling of extreme score values."""
        agent = ReporterAgent()

        state = {
            "article_content": "Test article",
            "analysis_results": {"topics": ["AI"]},
            "aggregated_scores": {
                "overall_score": {
                    "mean": 0,  # Minimum possible score
                    "std": 0,
                    "min": 0,
                    "max": 0,
                },
                "extreme_metric": {
                    "mean": 999999,  # Very large score
                    "std": 100000,
                    "min": -999999,  # Negative extreme
                    "max": 999999,
                },
            },
            "improvement_suggestions": [],
            "simulation_id": "test_extreme",
        }

        result = await agent.generate_report(state)

        assert "executive_summary" in result
        assert "detailed_analysis" in result
        # Should handle extreme values without overflow issues

    @pytest.mark.asyncio
    async def test_boundary_missing_required_fields(self):
        """Test report generation with missing required fields."""
        agent = ReporterAgent()

        # Missing aggregated_scores
        state = {
            "article_content": "Test article",
            "analysis_results": {"topics": ["AI"]},
            "simulation_id": "test_missing",
            # aggregated_scores is missing
        }

        result = await agent.generate_report(state)

        assert "executive_summary" in result
        assert "detailed_analysis" in result
        # Should generate a report even with missing data

    @pytest.mark.asyncio
    async def test_llm_failure_during_report_generation(self):
        """Test handling of LLM failures during report generation."""
        agent = ReporterAgent()

        # Mock LLM to fail
        agent.llm = AsyncMock()
        agent.llm.ainvoke.side_effect = Exception("LLM API Error")

        state = {
            "article_content": "Test article",
            "analysis_results": {"topics": ["AI"]},
            "aggregated_scores": {"overall_score": {"mean": 75}},
            "improvement_suggestions": [],
            "simulation_id": "test_llm_fail",
        }

        result = await agent.generate_report(state)

        assert "executive_summary" in result
        assert "detailed_analysis" in result
        # Should generate a basic report even if LLM fails

    @pytest.mark.asyncio
    async def test_format_conversion_edge_cases(self):
        """Test format conversion with edge cases."""
        agent = ReporterAgent()

        # Create a properly structured report with edge case values
        complex_report = {
            "executive_summary": {
                "overview": "Test report with special values 🎉",
                "key_findings": ["Finding 1", "Finding 2 with unicode: 🚀"],
                "overall_score": float("inf"),  # Edge case: infinity
                "top_recommendations": [],
            },
            "detailed_analysis": {
                "article_analysis": {
                    "title": "Test Article",
                    "category": "Testing",
                    "word_count": 100,
                    "topics": ["AI", "Testing"],
                    "complexity": 5.0,
                },
                "persona_analysis": {"total_personas": 10, "persona_types": {}},
                "evaluation_results": {"total_evaluations": 10},
                "improvement_areas": {"total_suggestions": 5},
            },
            "recommendations": [],
            "visualization_data": {"charts": {}},
            "metadata": {
                "simulation_id": "test_edge_case",
                "generation_time": "2025-08-03T00:00:00",
                "special_value": float("-inf"),  # Edge case: negative infinity
            },
        }

        # Test JSON format with special values
        json_report = agent._format_report(complex_report, "json")
        assert isinstance(json_report, dict)
        assert json_report == complex_report

        # Test Markdown format
        md_report = agent._format_report(complex_report, "markdown")
        assert isinstance(md_report, str)
        assert "# Article Review Report" in md_report
        assert "## Executive Summary" in md_report
        assert "🎉" in md_report  # Unicode should be preserved

        # Test HTML format
        html_report = agent._format_report(complex_report, "html")
        assert isinstance(html_report, str)
        assert "<html>" in html_report
        assert "<body>" in html_report
        assert "Article Review Report" in html_report
