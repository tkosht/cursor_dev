"""
Article analysis agent - Level 0 context analysis
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from ..config import TaskType, get_config, select_optimal_llm
from ..utils.llm_factory import create_llm

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """Agent responsible for deep multi-dimensional article analysis"""

    def __init__(self):
        self.config = get_config()
        # Select optimal LLM for analysis tasks
        provider, model = select_optimal_llm(
            task_type=TaskType.ANALYSIS,
            required_features=["json_mode"],
        )
        self.llm = create_llm(provider=provider, model=model)

        # Analysis dimensions
        self.analysis_dimensions = {
            "content": self._analyze_content,
            "structure": self._analyze_structure,
            "sentiment": self._analyze_sentiment,
            "readability": self._analyze_readability,
            "keywords": self._analyze_keywords,
            "target_audience": self._analyze_target_audience,
            "technical_depth": self._analyze_technical_depth,
            "emotional_impact": self._analyze_emotional_impact,
        }

    async def analyze(self, article_content: str) -> dict[str, Any]:
        """
        Perform comprehensive article analysis

        Args:
            article_content: The article text to analyze

        Returns:
            Analysis results across multiple dimensions
        """
        logger.info("Starting article analysis")
        start_time = datetime.now()

        # Run all analyses in parallel
        analysis_tasks = [
            analyzer(article_content) for analyzer in self.analysis_dimensions.values()
        ]

        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

        # Combine results
        analysis_results: dict[str, Any] = {}
        errors: list[dict[str, str]] = []

        for dimension, result in zip(self.analysis_dimensions.keys(), results, strict=False):
            if isinstance(result, Exception):
                errors.append({"dimension": dimension, "error": str(result)})
                logger.error(f"Error in {dimension} analysis: {result}")
            else:
                analysis_results[dimension] = result

        # Add metadata
        analysis_results["metadata"] = {
            "analysis_timestamp": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "dimensions_analyzed": len(analysis_results),  # Count before adding metadata
            "errors": errors,
        }

        logger.info(
            f"Analysis completed in {analysis_results['metadata']['duration_seconds']:.2f}s"
        )
        return analysis_results

    async def _analyze_content(self, text: str) -> dict[str, Any]:
        """Analyze content themes and topics"""
        prompt = f"""
        Analyze the main content themes and topics in this article.

        Article:
        {text[:3000]}...
        Provide a JSON response with:
        1. main_theme: Primary theme of the article
        2. sub_themes: List of secondary themes
        3. topics: List of specific topics covered
        4. domain: Content domain (tech, business, lifestyle, etc.)
        5. content_type: Type of content (tutorial, opinion, news, etc.)
        6. key_messages: List of key messages/takeaways
        """

        response = await self.llm.ainvoke(prompt)
        return self._parse_json_response(response.content)

    async def _analyze_structure(self, text: str) -> dict[str, Any]:
        """Analyze article structure"""
        # Simple structural analysis
        lines = text.split("\n")
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        words = text.split()

        return {
            "total_words": len(words),
            "total_lines": len(lines),
            "total_paragraphs": len(paragraphs),
            "avg_paragraph_length": (len(words) / len(paragraphs) if paragraphs else 0),
            "has_sections": any(line.startswith("#") for line in lines),
            "has_lists": any(line.strip().startswith(("-", "*", "1.")) for line in lines),
            "has_code_blocks": "```" in text,
        }

    async def _analyze_sentiment(self, text: str) -> dict[str, Any]:
        """Analyze sentiment and emotional tone"""
        prompt = f"""
        Analyze the sentiment and emotional tone of this article.

        Article:
        {text[:2000]}...
        Provide a JSON response with:
        1. overall_sentiment: positive/negative/neutral
        2. sentiment_score: -1.0 to 1.0
        3. emotional_tones: List of emotional tones present
        4. controversy_level: low/medium/high
        5. bias_indicators: List of potential biases detected
        """

        response = await self.llm.ainvoke(prompt)
        return self._parse_json_response(response.content)

    async def _analyze_readability(self, text: str) -> dict[str, Any]:
        """Analyze readability metrics"""
        # Simple readability metrics
        sentences = text.count(".") + text.count("!") + text.count("?")
        words = len(text.split())
        complex_words = len([w for w in text.split() if len(w) > 6])

        return {
            "sentence_count": sentences,
            "avg_sentence_length": words / sentences if sentences else 0,
            "complex_word_ratio": complex_words / words if words else 0,
            "estimated_reading_time_minutes": words / 200,  # Assuming 200 wpm
            "difficulty_level": self._estimate_difficulty(words, sentences, complex_words),
        }

    async def _analyze_keywords(self, text: str) -> dict[str, Any]:
        """Extract keywords and key phrases"""
        prompt = f"""
        Extract keywords and key phrases from this article.

        Article:
        {text[:2000]}...
        Provide a JSON response with:
        1. primary_keywords: List of 5-10 most important keywords
        2. secondary_keywords: List of 10-20 secondary keywords
        3. key_phrases: List of important multi-word phrases
        4. technical_terms: List of technical/specialized terms
        5. trending_topics: Any trending or timely topics mentioned
        """

        response = await self.llm.ainvoke(prompt)
        return self._parse_json_response(response.content)

    async def _analyze_target_audience(self, text: str) -> dict[str, Any]:
        """Identify target audience characteristics"""
        prompt = f"""
        Analyze the target audience for this article based on content, tone, and complexity.

        Article:
        {text[:2000]}...
        Provide a JSON response with:
        1. primary_audience: Description of primary target audience
        2. audience_segments: List of specific audience segments
        3. required_knowledge: Prerequisites or background knowledge needed
        4. age_range: Estimated age range of target readers
        5. professional_level: Entry/intermediate/advanced/expert
        6. interests: List of interests that would attract readers
        """

        response = await self.llm.ainvoke(prompt)
        return self._parse_json_response(response.content)

    async def _analyze_technical_depth(self, text: str) -> dict[str, Any]:
        """Analyze technical depth and complexity"""
        prompt = f"""
        Analyze the technical depth and complexity of this article.

        Article:
        {text[:2000]}...
        Provide a JSON response with:
        1. technical_level: Score from 1-10
        2. concepts_introduced: List of technical concepts
        3. requires_prerequisites: Boolean
        4. code_examples: Number of code examples
        5. implementation_ready: Whether content is actionable
        6. theoretical_vs_practical: Balance score (0=theoretical, 1=practical)
        """

        response = await self.llm.ainvoke(prompt)
        return self._parse_json_response(response.content)

    async def _analyze_emotional_impact(self, text: str) -> dict[str, Any]:
        """Analyze potential emotional impact on readers"""
        prompt = f"""
        Analyze the potential emotional impact of this article on readers.

        Article:
        {text[:2000]}...
        Provide a JSON response with:
        1. primary_emotion: Main emotion evoked
        2. emotional_journey: List of emotions throughout the article
        3. motivation_level: How motivating/inspiring (1-10)
        4. stress_factors: Elements that might cause stress/anxiety
        5. positive_triggers: Elements that evoke positive emotions
        6. call_to_action_strength: How compelling is the CTA (1-10)
        """

        response = await self.llm.ainvoke(prompt)
        return self._parse_json_response(response.content)

    def _estimate_difficulty(self, words: int, sentences: int, complex_words: int) -> str:
        """Estimate reading difficulty level"""
        if sentences == 0:
            return "unknown"

        avg_sentence_length = words / sentences
        complex_ratio = complex_words / words if words else 0

        if avg_sentence_length < 15 and complex_ratio < 0.1:
            return "easy"
        elif avg_sentence_length < 20 and complex_ratio < 0.2:
            return "moderate"
        elif avg_sentence_length < 25 and complex_ratio < 0.3:
            return "difficult"
        else:
            return "very_difficult"

    def _parse_json_response(self, response: str) -> dict[str, Any]:
        """Parse JSON response from LLM"""
        import json

        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {"error": "Failed to parse response", "raw": response}
