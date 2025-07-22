"""
Unit tests for article analysis agent
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json

from src.agents.analyzer import AnalysisAgent


class TestAnalysisAgent:
    """Test AnalysisAgent functionality"""
    
    @pytest.fixture
    def sample_article(self):
        """Sample article for testing"""
        return """# Understanding AI Ethics

## Introduction
Artificial Intelligence has become increasingly important in our daily lives. 
As we integrate AI systems into critical decision-making processes, we must 
carefully consider the ethical implications.

## Key Challenges
- Bias in algorithms
- Privacy concerns
- Accountability and transparency
- Job displacement

## Code Example
```python
def ethical_ai_check(model, data):
    # Check for bias
    if has_bias(model, data):
        raise EthicalConcern("Model shows bias")
    return True
```

## Conclusion
We must work together to ensure AI benefits humanity while minimizing harm.
Contact us at ai-ethics@example.com for more information.
"""
    
    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response factory"""
        def _create_response(content):
            response = MagicMock()
            response.content = f"```json\n{json.dumps(content)}\n```"
            return response
        return _create_response
    
    @patch('src.agents.analyzer.get_config')
    @patch('src.agents.analyzer.select_optimal_llm')
    @patch('src.agents.analyzer.create_llm')
    def test_initialization(self, mock_create_llm, mock_select_llm, mock_get_config):
        """Test agent initialization"""
        # Setup mocks
        mock_get_config.return_value = MagicMock()
        mock_select_llm.return_value = ("gemini", "gemini-2.5-flash")
        mock_create_llm.return_value = MagicMock()
        
        # Create agent
        agent = AnalysisAgent()
        
        # Verify initialization
        assert agent.config is not None
        mock_select_llm.assert_called_once()
        mock_create_llm.assert_called_once_with(provider="gemini", model="gemini-2.5-flash")
        assert len(agent.analysis_dimensions) == 8
    
    @pytest.mark.asyncio
    @patch('src.agents.analyzer.get_config')
    @patch('src.agents.analyzer.select_optimal_llm')
    @patch('src.agents.analyzer.create_llm')
    async def test_analyze_success(self, mock_create_llm, mock_select_llm, mock_get_config, sample_article, mock_llm_response):
        """Test successful article analysis"""
        # Setup mocks
        mock_get_config.return_value = MagicMock()
        mock_select_llm.return_value = ("gemini", "gemini-2.5-flash")
        mock_llm = AsyncMock()
        mock_create_llm.return_value = mock_llm
        
        # Setup LLM responses for each dimension
        mock_llm.ainvoke.side_effect = [
            mock_llm_response({  # content
                "main_theme": "AI Ethics",
                "sub_themes": ["Bias", "Privacy"],
                "topics": ["Algorithm bias", "Transparency"],
                "domain": "technology",
                "content_type": "educational",
                "key_messages": ["AI must be ethical"]
            }),
            mock_llm_response({  # sentiment
                "overall_sentiment": "positive",
                "sentiment_score": 0.7,
                "emotional_tones": ["concerned", "hopeful"],
                "controversy_level": "medium",
                "bias_indicators": []
            }),
            mock_llm_response({  # keywords
                "primary_keywords": ["AI", "Ethics", "Bias"],
                "secondary_keywords": ["Algorithm", "Privacy"],
                "key_phrases": ["ethical implications"],
                "technical_terms": ["algorithms", "AI systems"],
                "trending_topics": ["AI ethics"]
            }),
            mock_llm_response({  # target_audience
                "primary_audience": "Tech professionals",
                "audience_segments": ["Developers", "Researchers"],
                "required_knowledge": "Basic AI understanding",
                "age_range": "25-45",
                "professional_level": "intermediate",
                "interests": ["AI", "Ethics", "Technology"]
            }),
            mock_llm_response({  # technical_depth
                "technical_level": 6,
                "concepts_introduced": ["Bias detection"],
                "requires_prerequisites": True,
                "code_examples": 1,
                "implementation_ready": True,
                "theoretical_vs_practical": 0.7
            }),
            mock_llm_response({  # emotional_impact
                "primary_emotion": "concern",
                "emotional_journey": ["curiosity", "concern", "hope"],
                "motivation_level": 7,
                "stress_factors": ["Job displacement"],
                "positive_triggers": ["Working together"],
                "call_to_action_strength": 6
            })
        ]
        
        # Create agent and analyze
        agent = AnalysisAgent()
        results = await agent.analyze(sample_article)
        
        # Verify results structure
        assert "metadata" in results
        assert results["metadata"]["dimensions_analyzed"] == 8  # All 8 dimensions
        assert results["metadata"]["errors"] == []
        assert "content" in results
        assert "structure" in results
        assert "sentiment" in results
        assert "readability" in results
        assert "keywords" in results
        assert "target_audience" in results
        assert "technical_depth" in results
        assert "emotional_impact" in results
        
        # Verify content analysis
        assert results["content"]["main_theme"] == "AI Ethics"
        assert len(results["content"]["sub_themes"]) == 2
    
    @pytest.mark.asyncio
    @patch('src.agents.analyzer.get_config')
    @patch('src.agents.analyzer.select_optimal_llm')
    @patch('src.agents.analyzer.create_llm')
    async def test_analyze_with_errors(self, mock_create_llm, mock_select_llm, mock_get_config, sample_article):
        """Test analysis with some dimensions failing"""
        # Setup mocks
        mock_get_config.return_value = MagicMock()
        mock_select_llm.return_value = ("gemini", "gemini-2.5-flash")
        mock_llm = AsyncMock()
        mock_create_llm.return_value = mock_llm
        
        # Setup LLM to fail for some calls
        mock_llm.ainvoke.side_effect = [
            Exception("LLM API Error"),  # content fails
            MagicMock(content='{"overall_sentiment": "neutral"}'),  # sentiment succeeds
            Exception("Rate limit exceeded"),  # keywords fails
            MagicMock(content='{"primary_audience": "General"}'),  # target_audience succeeds
            MagicMock(content='{"technical_level": 5}'),  # technical_depth succeeds
            MagicMock(content='{"primary_emotion": "neutral"}'),  # emotional_impact succeeds
        ]
        
        # Create agent and analyze
        agent = AnalysisAgent()
        results = await agent.analyze(sample_article)
        
        # Verify error handling
        assert len(results["metadata"]["errors"]) == 2
        assert results["metadata"]["errors"][0]["dimension"] == "content"
        assert "LLM API Error" in results["metadata"]["errors"][0]["error"]
        assert results["metadata"]["errors"][1]["dimension"] == "keywords"
        
        # Verify successful dimensions are still present
        assert "sentiment" in results
        assert "structure" in results  # This doesn't use LLM
        assert "readability" in results  # This doesn't use LLM
    
    def test_analyze_structure(self):
        """Test structure analysis (doesn't use LLM)"""
        agent = AnalysisAgent.__new__(AnalysisAgent)  # Skip __init__
        
        text = """# Title
        
First paragraph with some text.

Second paragraph with more text.

- List item 1
- List item 2

```python
code_block()
```
"""
        
        # Run synchronously since this method doesn't actually use async
        import asyncio
        result = asyncio.run(agent._analyze_structure(text))
        
        assert result["total_words"] == 23
        assert result["total_paragraphs"] == 4
        assert result["has_sections"] is True
        assert result["has_lists"] is True
        assert result["has_code_blocks"] is True
    
    def test_analyze_readability(self):
        """Test readability analysis"""
        agent = AnalysisAgent.__new__(AnalysisAgent)  # Skip __init__
        
        text = "This is a simple sentence. Here is another one! Complex terminology appears occasionally?"
        
        import asyncio
        result = asyncio.run(agent._analyze_readability(text))
        
        assert result["sentence_count"] == 3
        assert result["avg_sentence_length"] == pytest.approx(4.33, 0.1)
        assert result["complex_word_ratio"] == pytest.approx(0.46, 0.1)  # 6/13 words
        assert result["difficulty_level"] == "very_difficult"
    
    def test_estimate_difficulty(self):
        """Test difficulty estimation"""
        agent = AnalysisAgent.__new__(AnalysisAgent)  # Skip __init__
        
        # Test easy
        assert agent._estimate_difficulty(100, 10, 5) == "easy"
        
        # Test moderate
        assert agent._estimate_difficulty(150, 10, 20) == "moderate"
        
        # Test difficult
        assert agent._estimate_difficulty(200, 10, 50) == "difficult"
        
        # Test very difficult
        assert agent._estimate_difficulty(300, 10, 100) == "very_difficult"
        
        # Test edge case
        assert agent._estimate_difficulty(100, 0, 10) == "unknown"
    
    def test_parse_json_response(self):
        """Test JSON response parsing"""
        agent = AnalysisAgent.__new__(AnalysisAgent)  # Skip __init__
        
        # Test with ```json markers
        response1 = """Here's the analysis:
```json
{"key": "value", "number": 42}
```
"""
        result1 = agent._parse_json_response(response1)
        assert result1["key"] == "value"
        assert result1["number"] == 42
        
        # Test with plain ``` markers
        response2 = """```
{"another": "test"}
```"""
        result2 = agent._parse_json_response(response2)
        assert result2["another"] == "test"
        
        # Test with no markers
        response3 = '{"plain": "json"}'
        result3 = agent._parse_json_response(response3)
        assert result3["plain"] == "json"
        
        # Test error handling
        response4 = "invalid json"
        result4 = agent._parse_json_response(response4)
        assert result4["error"] == "Failed to parse response"
        assert result4["raw"] == "invalid json"
    
    @pytest.mark.asyncio
    @patch('src.agents.analyzer.get_config')
    @patch('src.agents.analyzer.select_optimal_llm')
    @patch('src.agents.analyzer.create_llm')
    async def test_parallel_execution(self, mock_create_llm, mock_select_llm, mock_get_config, sample_article):
        """Test that analyses run in parallel"""
        # Setup mocks
        mock_get_config.return_value = MagicMock()
        mock_select_llm.return_value = ("gemini", "gemini-2.5-flash")
        mock_llm = AsyncMock()
        mock_create_llm.return_value = mock_llm
        
        # Track call times
        call_times = []
        
        async def slow_response(*args):
            call_times.append(datetime.now())
            await asyncio.sleep(0.1)  # Simulate slow API
            return MagicMock(content='{"result": "ok"}')
        
        mock_llm.ainvoke.side_effect = slow_response
        
        # Create agent and analyze
        agent = AnalysisAgent()
        start = datetime.now()
        await agent.analyze(sample_article)
        duration = (datetime.now() - start).total_seconds()
        
        # If running in parallel, should take ~0.1s, not 0.6s (6 * 0.1)
        assert duration < 0.3  # Allow some overhead
        assert len(call_times) == 6  # 6 LLM-based analyses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])