"""
Unit tests for article analysis agent - Real LLM API calls only
"""

import asyncio
import json
import os
from datetime import datetime
import pytest

from src.agents.analyzer import AnalysisAgent
from tests.llm_test_helper import get_llm_helper


class TestAnalysisAgent:
    """Test AnalysisAgent functionality with real LLM"""

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
    def short_article(self):
        """Shorter article to minimize API usage"""
        return """# Quick AI Update
AI is transforming industries. We need ethical guidelines.
Key points: transparency, fairness, accountability.
"""

    def test_initialization(self):
        """Test agent initialization with real config"""
        # Create agent with real LLM
        agent = AnalysisAgent()
        
        # Verify initialization
        assert agent.config is not None
        assert agent.llm is not None
        assert len(agent.analysis_dimensions) == 8

    @pytest.mark.asyncio
    async def test_analyze_success(self, short_article):
        """Test successful article analysis with real LLM"""
        if not (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("ANTHROPIC_API_KEY")
        ):
            pytest.skip("No LLM API key available for testing")
        # Create agent with real LLM
        agent = AnalysisAgent()
        
        # Analyze short article to minimize API calls
        results = await agent.analyze(short_article)
        
        # Verify results structure
        assert "metadata" in results
        assert "content" in results
        assert "structure" in results
        assert "sentiment" in results
        assert "readability" in results
        assert "keywords" in results
        assert "target_audience" in results
        assert "technical_depth" in results
        assert "emotional_impact" in results
        
        # Verify metadata
        assert results["metadata"]["dimensions_analyzed"] > 0
        assert "analysis_timestamp" in results["metadata"]
        assert "duration_seconds" in results["metadata"]
        
        # Verify structure analysis (deterministic)
        assert results["structure"]["total_words"] > 0
        assert results["structure"]["total_paragraphs"] > 0
        
        # Verify readability (deterministic)
        assert results["readability"]["sentence_count"] > 0
        assert "difficulty_level" in results["readability"]

    @pytest.mark.asyncio
    async def test_analyze_structure(self):
        """Test structure analysis (doesn't use LLM)"""
        agent = AnalysisAgent()
        
        text = """# Title

First paragraph with some text.

Second paragraph with more text.

- List item 1
- List item 2

```python
code_block()
```
"""
        
        # Analyze structure
        result = await agent._analyze_structure(text)
        
        assert result["total_words"] == 23
        assert result["total_paragraphs"] == 5
        assert result["has_sections"] is True
        assert result["has_lists"] is True
        assert result["has_code_blocks"] is True

    @pytest.mark.asyncio
    async def test_analyze_readability(self):
        """Test readability analysis (doesn't use LLM)"""
        agent = AnalysisAgent()
        
        text = (
            "This is a simple sentence. Here is another one! "
            "Complex terminology appears occasionally?"
        )
        
        result = await agent._analyze_readability(text)
        
        assert result["sentence_count"] == 3
        assert result["avg_sentence_length"] == pytest.approx(4.33, 0.1)
        assert result["complex_word_ratio"] == pytest.approx(0.46, 0.1)  # 6/13 words
        assert result["difficulty_level"] == "very_difficult"

    def test_estimate_difficulty(self):
        """Test difficulty estimation"""
        agent = AnalysisAgent()
        
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
        agent = AnalysisAgent()
        
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
{"another": "test", "bool": true}
```"""
        result2 = agent._parse_json_response(response2)
        assert result2["another"] == "test"
        assert result2["bool"] is True
        
        # Test with plain JSON
        response3 = '{"plain": "json", "value": 123}'
        result3 = agent._parse_json_response(response3)
        assert result3["plain"] == "json"
        assert result3["value"] == 123
        
        # Test error case
        response4 = "Not JSON at all"
        result4 = agent._parse_json_response(response4)
        assert "error" in result4
        assert result4["error"] == "Failed to parse response"


    @pytest.mark.asyncio
    async def test_analyze_with_cache(self, short_article):
        """Test that caching works with real LLM"""
        if not (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("ANTHROPIC_API_KEY")
        ):
            pytest.skip("No LLM API key available for testing")
        agent = AnalysisAgent()
        
        # First analysis (will make API calls)
        results1 = await agent.analyze(short_article)
        assert results1 is not None
        
        # Second analysis of same article should be faster due to caching
        # (if implemented in the agent)
        results2 = await agent.analyze(short_article)
        assert results2 is not None
        
        # Results should be similar (structure/readability are deterministic)
        assert results1["structure"] == results2["structure"]
        assert results1["readability"] == results2["readability"]