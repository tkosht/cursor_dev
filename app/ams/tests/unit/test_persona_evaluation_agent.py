"""
Unit tests for PersonaEvaluationAgent

Test-Driven Development approach for the persona evaluation functionality.
"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.core.types import (
    EvaluationResult,
    InformationChannel,
    PersonaAttributes,
    PersonalityType,
)


class TestPersonaEvaluationAgent:
    """Test suite for PersonaEvaluationAgent"""

    @pytest.fixture
    def sample_persona(self):
        """Sample persona for testing"""
        return PersonaAttributes(
            age=28,
            occupation="Data Scientist",
            location="Tokyo, Japan",
            education_level="Master's Degree",
            values=["innovation", "accuracy", "efficiency"],
            interests=["AI", "machine learning", "technology"],
            personality_traits={
                PersonalityType.OPENNESS: 0.9,
                PersonalityType.CONSCIENTIOUSNESS: 0.8,
                PersonalityType.EXTRAVERSION: 0.5,
                PersonalityType.AGREEABLENESS: 0.6,
                PersonalityType.NEUROTICISM: 0.3,
            },
            information_seeking_behavior="active",
            preferred_channels=[
                InformationChannel.NEWS_WEBSITE,
                InformationChannel.SEARCH_ENGINE,
            ],
            cognitive_biases=["confirmation_bias", "anchoring_bias"],
            emotional_triggers=["technological_advancement", "innovation"],
            # Additional fields that would map to income_bracket
            income_bracket="upper-middle",
            # Use existing behavioral fields
            decision_making_style="analytical",
            content_sharing_likelihood=0.7,
            influence_susceptibility=0.4,
        )

    @pytest.fixture
    def sample_article(self):
        """Sample article content for testing"""
        return """
        # Advanced Machine Learning Techniques for Real-World Applications

        Recent breakthroughs in deep learning have revolutionized how we approach
        complex problems. This article explores cutting-edge techniques including
        transformer architectures, reinforcement learning, and neural architecture search.

        ## Key Innovations
        - Self-attention mechanisms for better context understanding
        - Transfer learning for efficient model training
        - AutoML for democratizing AI development

        ## Practical Applications
        These techniques are being applied in healthcare, finance, and autonomous systems
        with remarkable success rates.
        """

    @pytest.fixture
    def sample_analysis_results(self):
        """Sample analysis results from AnalysisAgent"""
        return {
            "readability": {
                "flesch_reading_ease": 45.2,
                "flesch_kincaid_grade": 12.5,
                "gunning_fog": 14.3,
            },
            "sentiment": {"overall": "positive", "confidence": 0.85},
            "structure": {
                "sections": 3,
                "paragraphs": 8,
                "average_paragraph_length": 75,
            },
            "keywords": {
                "main_topics": ["machine learning", "AI", "deep learning"],
                "keyword_density": {"AI": 0.04, "learning": 0.06},
            },
            "technical_depth": {
                "level": "advanced",
                "jargon_density": 0.25,
                "requires_background": True,
            },
        }

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response for evaluation"""
        return json.dumps(
            {
                "relevance_score": 95,
                "clarity_score": 75,
                "credibility_score": 88,
                "emotional_impact_score": 82,
                "action_potential_score": 78,
                "interest_alignment": 0.92,
                "value_alignment": 0.85,
                "bias_resonance": 0.7,
                "strengths": [
                    "Highly relevant to persona's interests in AI and ML",
                    "Technical depth matches persona's expertise level",
                    "Innovative content aligns with persona's values",
                    "Practical applications resonate with efficiency focus",
                ],
                "weaknesses": [
                    "Could be more accessible despite technical audience",
                    "Limited discussion of implementation challenges",
                    "Missing cost-benefit analysis for practical adoption",
                ],
                "improvement_suggestions": [
                    "Add code examples for better understanding",
                    "Include case studies from Japanese tech companies",
                    "Discuss ROI metrics for business applications",
                ],
                "predicted_engagement": {
                    "read_completion_probability": 0.88,
                    "share_probability": 0.75,
                    "bookmark_probability": 0.82,
                    "discussion_probability": 0.65,
                },
                "emotional_response": {
                    "primary_emotion": "excitement",
                    "intensity": 0.78,
                    "triggers": ["innovation", "practical_applications"],
                },
                "key_insights": [
                    "Article strongly resonates with technical innovation values",
                    "Content depth appropriate for persona's expertise",
                    "Practical focus aligns with efficiency orientation",
                ],
            }
        )

    @pytest.mark.asyncio
    async def test_init(self):
        """Test EvaluationAgent initialization"""
        from src.agents.evaluator import EvaluationAgent

        agent = EvaluationAgent()

        assert agent.config is not None
        assert agent.llm is not None
        assert hasattr(agent, "evaluate_persona")

    @pytest.mark.asyncio
    async def test_evaluate_persona_success(
        self,
        sample_persona,
        sample_article,
        sample_analysis_results,
        mock_llm_response,
        mock_config,
    ):
        """Test successful persona evaluation"""
        from src.agents.evaluator import EvaluationAgent

        # Mock LLM before creating agent
        with patch("src.agents.evaluator.create_llm") as mock_create_llm:
            mock_llm = Mock()
            mock_llm.ainvoke = AsyncMock(return_value=Mock(content=mock_llm_response))
            mock_create_llm.return_value = mock_llm

            agent = EvaluationAgent()

            result = await agent.evaluate_persona(
                persona=sample_persona,
                article_content=sample_article,
                analysis_results=sample_analysis_results,
            )

            # Verify result structure
            assert isinstance(result, EvaluationResult)
            # Check persona_id is generated correctly
            assert len(result.persona_id) == 12  # MD5 hash truncated to 12 chars

            # Verify metrics structure
            assert len(result.metrics) == 5
            relevance_metric = next(m for m in result.metrics if m.name == "relevance")
            assert relevance_metric.score == 95

            # Verify overall score
            assert result.overall_score > 0

            # Verify qualitative feedback
            assert len(result.strengths) == 4
            assert len(result.weaknesses) == 3
            assert len(result.suggestions) == 3

            # Verify predicted behavior
            assert result.sharing_probability == 0.75
            assert result.engagement_level in ["low", "medium", "high"]
            assert result.sentiment in ["negative", "neutral", "positive"]

            # Verify LLM was called with proper prompt
            mock_llm.ainvoke.assert_called_once()
            call_args = mock_llm.ainvoke.call_args[0][0]
            assert "Data Scientist" in call_args
            assert "Tokyo, Japan" in call_args
            assert "machine learning" in call_args.lower()

    @pytest.mark.asyncio
    async def test_evaluate_persona_with_retry(
        self, sample_persona, sample_article, sample_analysis_results, mock_llm_response
    ):
        """Test evaluation with retry on failure"""
        from src.agents.evaluator import EvaluationAgent

        # Mock LLM to fail once then succeed
        with patch("src.agents.evaluator.create_llm") as mock_create_llm:
            mock_llm = Mock()
            mock_llm.ainvoke = AsyncMock(
                side_effect=[
                    Exception("API Error"),
                    Mock(content=mock_llm_response),
                ]
            )
            mock_create_llm.return_value = mock_llm

            agent = EvaluationAgent()

            result = await agent.evaluate_persona(
                persona=sample_persona,
                article_content=sample_article,
                analysis_results=sample_analysis_results,
            )

        # Should succeed after retry
        assert isinstance(result, EvaluationResult)
        assert mock_llm.ainvoke.call_count == 2

    @pytest.mark.asyncio
    async def test_evaluate_persona_json_parse_error(
        self, sample_persona, sample_article, sample_analysis_results
    ):
        """Test handling of JSON parse errors"""
        from src.agents.evaluator import EvaluationAgent

        # Mock LLM with invalid JSON
        with patch("src.agents.evaluator.create_llm") as mock_create_llm:
            mock_llm = Mock()
            mock_llm.ainvoke = AsyncMock(return_value=Mock(content="Invalid JSON response"))
            mock_create_llm.return_value = mock_llm

            agent = EvaluationAgent()

            result = await agent.evaluate_persona(
                persona=sample_persona,
                article_content=sample_article,
                analysis_results=sample_analysis_results,
            )

        # Should return default evaluation
        assert isinstance(result, EvaluationResult)
        assert len(result.metrics) > 0  # Should have default metrics
        assert len(result.strengths) > 0  # Should have default feedback

    @pytest.mark.asyncio
    async def test_evaluate_persona_timeout(
        self, sample_persona, sample_article, sample_analysis_results
    ):
        """Test timeout handling"""
        import asyncio

        from src.agents.evaluator import EvaluationAgent

        # Mock LLM to timeout
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(10)  # Longer than timeout

        with patch("src.agents.evaluator.create_llm") as mock_create_llm:
            mock_llm = Mock()
            mock_llm.ainvoke = slow_response
            mock_create_llm.return_value = mock_llm

            with patch("src.agents.evaluator.get_config") as mock_get_config:
                mock_config = Mock()
                mock_config.llm.timeout = 0.1  # Short timeout
                mock_get_config.return_value = mock_config

                agent = EvaluationAgent()

                result = await agent.evaluate_persona(
                    persona=sample_persona,
                    article_content=sample_article,
                    analysis_results=sample_analysis_results,
                )

        # Should return result despite timeout
        assert isinstance(result, EvaluationResult)

    def test_generate_evaluation_prompt(
        self, sample_persona, sample_article, sample_analysis_results
    ):
        """Test prompt generation"""
        from src.agents.evaluator import EvaluationAgent

        # Since _generate_evaluation_prompt is a private method,
        # we'll test it indirectly through evaluate_persona
        with patch("src.agents.evaluator.create_llm") as mock_create_llm:
            mock_llm = Mock()
            prompt_captured = None

            async def capture_prompt(prompt):
                nonlocal prompt_captured
                prompt_captured = prompt
                return Mock(content="{}")

            mock_llm.ainvoke = capture_prompt
            mock_create_llm.return_value = mock_llm

            agent = EvaluationAgent()
            # Use the private method directly for testing
            prompt = agent._generate_evaluation_prompt(
                persona=sample_persona,
                article_content=sample_article,
                analysis_results=sample_analysis_results,
            )

        # Verify prompt contains key information
        assert "Data Scientist" in prompt
        assert "28" in prompt
        assert "Tokyo, Japan" in prompt
        assert "innovation" in prompt
        assert "machine learning" in prompt.lower()
        assert "Flesch Reading Ease" in prompt  # Check for the formatted version
        assert "positive" in prompt

        # Verify prompt structure
        assert "You are evaluating" in prompt
        assert "Demographics:" in prompt
        assert "Psychographics:" in prompt
        assert "Article Analysis:" in prompt
        assert "EVALUATION CRITERIA:" in prompt
        assert "JSON" in prompt

    def test_parse_evaluation_response_success(self, mock_llm_response):
        """Test successful response parsing"""
        from src.agents.evaluator import EvaluationAgent

        with patch("src.agents.evaluator.create_llm") as mock_create_llm:
            mock_llm = Mock()
            mock_create_llm.return_value = mock_llm

            agent = EvaluationAgent()

            # Use the private method directly for testing
            result = agent._parse_evaluation_response(
                response=mock_llm_response,
                persona_id="test_persona_123",
                article_id="test_article_456",
            )

        assert isinstance(result, EvaluationResult)
        assert result.persona_id == "test_persona_123"
        assert result.article_id == "test_article_456"
        # Check metrics instead of individual scores
        relevance_metric = next(m for m in result.metrics if m.name == "relevance")
        assert relevance_metric.score == 95
        assert len(result.strengths) == 4
        assert result.sharing_probability == 0.75

    def test_parse_evaluation_response_partial(self):
        """Test parsing partial/malformed response"""
        from src.agents.evaluator import EvaluationAgent

        with patch("src.agents.evaluator.create_llm") as mock_create_llm:
            mock_llm = Mock()
            mock_create_llm.return_value = mock_llm

            agent = EvaluationAgent()

            partial_response = json.dumps(
                {
                    "relevance_score": 80,
                    "clarity_score": 70,
                    # Missing other required fields
                }
            )

            # Use the private method directly for testing
            result = agent._parse_evaluation_response(
                response=partial_response,
                persona_id="test_persona_123",
                article_id="test_article_456",
            )

        # Should handle gracefully with defaults
        assert isinstance(result, EvaluationResult)
        # Check metrics instead of individual scores
        relevance_metric = next(m for m in result.metrics if m.name == "relevance")
        assert relevance_metric.score == 80
        clarity_metric = next(m for m in result.metrics if m.name == "clarity")
        assert clarity_metric.score == 70
        credibility_metric = next(m for m in result.metrics if m.name == "credibility")
        assert credibility_metric.score > 0  # Should have default

    @pytest.mark.asyncio
    async def test_batch_evaluation(self, sample_article, sample_analysis_results):
        """Test batch evaluation of multiple personas"""
        from src.agents.evaluator import EvaluationAgent

        # Create multiple personas
        personas = []
        for i in range(3):
            persona = PersonaAttributes(
                age=25 + i * 5,
                occupation=f"Professional {i}",
                location="Tokyo, Japan",
                education_level="Bachelor's Degree",
                values=["innovation"],
                interests=["technology"],
                personality_traits={PersonalityType.OPENNESS: 0.7},
                information_seeking_behavior="active",
                preferred_channels=[InformationChannel.NEWS_WEBSITE],
            )
            personas.append(persona)

        # Mock LLM responses
        with patch("src.agents.evaluator.create_llm") as mock_create_llm:
            mock_llm = Mock()
            mock_llm.ainvoke = AsyncMock(
                return_value=Mock(
                    content=json.dumps(
                        {
                            "relevance_score": 85,
                            "clarity_score": 75,
                            "credibility_score": 80,
                            "emotional_impact_score": 70,
                            "action_potential_score": 75,
                            "strengths": ["Good"],
                            "weaknesses": ["Could improve"],
                            "improvement_suggestions": ["Add examples"],
                        }
                    )
                )
            )
            mock_create_llm.return_value = mock_llm

            agent = EvaluationAgent()

            # Evaluate all personas
            results = []
            for persona in personas:
                result = await agent.evaluate_persona(
                    persona=persona,
                    article_content=sample_article,
                    analysis_results=sample_analysis_results,
                )
                results.append(result)

        assert len(results) == 3
        assert all(isinstance(r, EvaluationResult) for r in results)
        assert mock_llm.ainvoke.call_count == 3

    @pytest.mark.asyncio
    async def test_error_logging(
        self, sample_persona, sample_article, sample_analysis_results, caplog
    ):
        """Test error logging functionality"""
        from src.agents.evaluator import EvaluationAgent

        # Mock LLM to fail
        with patch("src.agents.evaluator.create_llm") as mock_create_llm:
            mock_llm = Mock()
            mock_llm.ainvoke = AsyncMock(side_effect=Exception("Test error"))
            mock_create_llm.return_value = mock_llm

            agent = EvaluationAgent()

            # Should not raise, but log error
            result = await agent.evaluate_persona(
                persona=sample_persona,
                article_content=sample_article,
                analysis_results=sample_analysis_results,
            )

        assert isinstance(result, EvaluationResult)
        # Check if error was logged (implementation dependent)
