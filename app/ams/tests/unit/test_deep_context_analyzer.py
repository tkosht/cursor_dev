"""Unit tests for DeepContextAnalyzer class."""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from src.agents.deep_context_analyzer import DeepContextAnalyzer


class TestDeepContextAnalyzer:
    """Test cases for DeepContextAnalyzer."""

    @pytest.fixture
    def sample_article(self):
        """Sample article for testing."""
        return """
        # The Future of AI in Healthcare: A Revolutionary Approach

        Artificial Intelligence is transforming healthcare delivery in unprecedented ways.
        From diagnostic imaging to personalized treatment plans, AI algorithms are
        enhancing medical decision-making and patient outcomes.

        Recent breakthroughs in deep learning have enabled systems to detect diseases
        like cancer at earlier stages than ever before. Healthcare professionals are
        now leveraging these tools to provide more accurate and timely care.

        However, challenges remain. Privacy concerns, regulatory hurdles, and the need
        for transparent AI systems continue to shape the conversation around AI adoption
        in healthcare settings.
        """

    @pytest.fixture
    def analyzer(self):
        """Create a DeepContextAnalyzer instance."""
        return DeepContextAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_article_context_structure(
        self, analyzer, sample_article
    ):
        """Test that analyze_article_context returns proper structure."""
        # Mock LLM response
        mock_response = {
            "domain_analysis": {
                "primary_domain": "healthcare",
                "sub_domains": ["AI", "medical technology", "diagnostics"],
                "technical_complexity": 7,
                "required_knowledge": [
                    "basic AI concepts",
                    "healthcare systems",
                ],
            },
            "cultural_dimensions": {
                "geographic_relevance": "global",
                "cultural_sensitivities": ["medical privacy", "AI ethics"],
                "language_nuances": ["technical medical terms"],
                "social_context": "healthcare innovation",
            },
            "temporal_aspects": {
                "time_sensitivity": "high",
                "trend_alignment": [
                    "AI advancement",
                    "healthcare digitization",
                ],
                "historical_context": "post-pandemic healthcare transformation",
                "future_implications": "automated diagnostics",
            },
            "emotional_landscape": {
                "emotional_triggers": [
                    "hope for better healthcare",
                    "fear of job displacement",
                ],
                "controversy_potential": "medium",
                "inspirational_elements": ["life-saving potential"],
                "fear_factors": ["privacy concerns", "AI errors"],
            },
            "stakeholder_mapping": {
                "beneficiaries": ["patients", "healthcare providers"],
                "opponents": [
                    "privacy advocates",
                    "traditional practitioners",
                ],
                "need_to_know": ["healthcare professionals", "policymakers"],
                "likely_sharers": [
                    "tech enthusiasts",
                    "healthcare innovators",
                ],
            },
        }

        with patch.object(analyzer, "llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock()
            mock_llm.ainvoke.return_value.content = json.dumps(mock_response)

            result = await analyzer.analyze_article_context(sample_article)

            # Verify structure
            assert "core_context" in result
            assert "hidden_dimensions" in result
            assert "complexity_score" in result
            assert "reach_potential" in result

            # Verify core context contains expected keys
            core_context = result["core_context"]
            assert "domain_analysis" in core_context
            assert "cultural_dimensions" in core_context
            assert "temporal_aspects" in core_context
            assert "emotional_landscape" in core_context
            assert "stakeholder_mapping" in core_context

    @pytest.mark.asyncio
    async def test_discover_hidden_dimensions(self, analyzer, sample_article):
        """Test discovery of non-obvious contextual dimensions."""
        initial_analysis = {
            "domain_analysis": {"primary_domain": "healthcare"}
        }

        mock_hidden_dimensions = {
            "second_order_effects": [
                "Insurance industry disruption",
                "Medical education transformation",
            ],
            "cross_domain_implications": [
                "Legal liability for AI decisions",
                "Economic impact on healthcare costs",
            ],
            "generational_perspectives": {
                "gen_z": "Expects AI-powered healthcare as default",
                "boomers": "Concerns about human touch in medicine",
            },
            "subculture_relevance": [
                "Biohackers interested in AI self-diagnosis",
                "Medical students adapting curriculum",
            ],
            "contrarian_viewpoints": [
                "Holistic medicine practitioners opposing AI diagnostics",
                "Data sovereignty advocates",
            ],
            "emotional_projections": [
                "Personal experiences with misdiagnosis",
                "Hope for rare disease detection",
            ],
        }

        with patch.object(analyzer, "llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock()
            mock_llm.ainvoke.return_value.content = json.dumps(
                mock_hidden_dimensions
            )

            result = await analyzer._discover_hidden_dimensions(
                sample_article, initial_analysis
            )

            assert "second_order_effects" in result
            assert "cross_domain_implications" in result
            assert "generational_perspectives" in result
            assert "subculture_relevance" in result
            assert "contrarian_viewpoints" in result
            assert "emotional_projections" in result

    @pytest.mark.asyncio
    async def test_calculate_complexity_score(self, analyzer):
        """Test complexity score calculation."""
        context_analysis = {
            "domain_analysis": {
                "technical_complexity": 8,
                "required_knowledge": [
                    "AI",
                    "healthcare",
                    "regulations",
                    "ethics",
                ],
            },
            "cultural_dimensions": {
                "cultural_sensitivities": ["privacy", "ethics", "equity"]
            },
            "stakeholder_mapping": {
                "beneficiaries": ["patients", "doctors"],
                "opponents": ["privacy advocates"],
                "need_to_know": ["regulators", "insurers"],
            },
        }

        score = analyzer._calculate_complexity(context_analysis)

        # Score should be between 0 and 1
        assert 0 <= score <= 1
        # With high technical complexity and multiple stakeholders, score should be high
        assert score > 0.7

    @pytest.mark.asyncio
    async def test_estimate_reach_potential(self, analyzer):
        """Test reach potential estimation."""
        context_analysis = {
            "stakeholder_mapping": {
                "beneficiaries": [
                    "large patient population",
                    "healthcare industry",
                ],
                "likely_sharers": [
                    "tech community",
                    "healthcare professionals",
                ],
            },
            "emotional_landscape": {
                "controversy_potential": "high",
                "inspirational_elements": ["life-saving potential"],
            },
            "temporal_aspects": {
                "trend_alignment": ["AI boom", "healthcare innovation"]
            },
        }

        potential = analyzer._estimate_reach_potential(context_analysis)

        # Score should be between 0 and 1
        assert 0 <= potential <= 1
        # With high controversy and trend alignment, potential should be high
        assert potential > 0.6

    @pytest.mark.asyncio
    async def test_analyze_article_context_integration(
        self, analyzer, sample_article
    ):
        """Test full integration of analyze_article_context."""
        # Mock comprehensive responses
        mock_core_response = {
            "domain_analysis": {
                "primary_domain": "healthcare",
                "technical_complexity": 7,
            }
        }

        mock_hidden_response = {
            "second_order_effects": ["Insurance disruption"],
            "cross_domain_implications": ["Legal ramifications"],
        }

        with patch.object(analyzer, "llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock()
            # First call for core analysis, second for hidden dimensions
            mock_llm.ainvoke.side_effect = [
                Mock(content=json.dumps(mock_core_response)),
                Mock(content=json.dumps(mock_hidden_response)),
            ]

            result = await analyzer.analyze_article_context(sample_article)

            # Verify all components are present
            assert result["core_context"] == mock_core_response
            assert result["hidden_dimensions"] == mock_hidden_response
            assert isinstance(result["complexity_score"], float)
            assert isinstance(result["reach_potential"], float)

            # Verify LLM was called twice
            assert mock_llm.ainvoke.call_count == 2

    @pytest.mark.asyncio
    async def test_parse_analysis_response(self, analyzer):
        """Test parsing of LLM responses."""
        # Test valid JSON response
        valid_response = Mock(
            content='{"key": "value", "nested": {"item": 1}}'
        )
        parsed = analyzer._parse_analysis_response(valid_response)
        assert parsed == {"key": "value", "nested": {"item": 1}}

        # Test invalid JSON response
        invalid_response = Mock(content="Not a JSON {invalid}")
        parsed = analyzer._parse_analysis_response(invalid_response)
        assert parsed == {}  # Should return empty dict on parse error

    @pytest.mark.asyncio
    async def test_error_handling(self, analyzer, sample_article):
        """Test error handling in analysis."""
        with patch.object(analyzer, "llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock()
            mock_llm.ainvoke.side_effect = Exception("LLM API Error")

            # Should handle error gracefully
            result = await analyzer.analyze_article_context(sample_article)

            # Should return default structure even on error
            assert "core_context" in result
            assert "hidden_dimensions" in result
            assert "complexity_score" in result
            assert "reach_potential" in result

            # Values should be defaults
            assert result["core_context"] == {}
            assert (
                result["complexity_score"] == 0.5
            )  # Default medium complexity
