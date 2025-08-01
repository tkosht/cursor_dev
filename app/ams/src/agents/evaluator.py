"""
PersonaEvaluationAgent - Evaluates articles from persona perspectives

This agent evaluates articles from the unique perspective of each generated persona,
providing scores, qualitative feedback, and predicted behaviors.
"""

import asyncio
import logging
from typing import Any, Literal

from ..config import get_config
from ..core.base import BaseAction, BaseAgent
from ..core.interfaces import IAction
from ..core.types import EvaluationMetric, EvaluationResult, PersonaAttributes, PersonalityType
from ..utils.json_parser import parse_llm_json_response
from ..utils.llm_factory import create_llm
from ..utils.llm_transparency import LLMCallTracker

logger = logging.getLogger(__name__)


class EvaluationAgent(BaseAgent):
    """Agent that evaluates articles from individual persona perspectives"""

    def __init__(self) -> None:
        """Initialize the evaluation agent"""
        super().__init__()
        self.config = get_config()
        self.llm = create_llm()
        self.call_tracker = LLMCallTracker()
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    async def evaluate_persona(
        self,
        persona: PersonaAttributes,
        article_content: str,
        analysis_results: dict[str, Any],
    ) -> EvaluationResult:
        """
        Evaluate an article from a specific persona's perspective

        Args:
            persona: The persona attributes to evaluate from
            article_content: The article content to evaluate
            analysis_results: Analysis results from AnalysisAgent

        Returns:
            EvaluationResult with scores, feedback, and predictions
        """
        # Generate evaluation prompt
        prompt = self._generate_evaluation_prompt(persona, article_content, analysis_results)

        # Try to get evaluation with retries
        response_content = None
        for attempt in range(self.max_retries):
            try:
                # Set timeout from config
                timeout = self.config.llm.timeout

                # Call LLM with timeout
                response = await asyncio.wait_for(self.llm.ainvoke(prompt), timeout=timeout)
                response_content = str(response.content)
                break

            except TimeoutError:
                logger.warning(
                    f"Timeout on attempt {attempt + 1}/{self.max_retries} "
                    f"for persona evaluation"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("All attempts timed out for persona evaluation")

            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("All attempts failed for persona evaluation")

        # Parse response or use default
        # Generate persona ID from attributes
        persona_id = self._generate_persona_id(persona)

        if response_content:
            return self._parse_evaluation_response(
                response_content,
                persona_id=persona_id,
                article_id="default",  # Will be set by orchestrator
            )
        else:
            # Return default evaluation if all attempts failed
            return self._create_default_evaluation(persona_id=persona_id, article_id="default")

    def _generate_evaluation_prompt(
        self,
        persona: PersonaAttributes,
        article_content: str,
        analysis_results: dict[str, Any],
    ) -> str:
        """Generate the evaluation prompt for LLM"""
        # Format persona attributes
        demographics = f"""
        Demographics:
        - Age: {persona.age}
        - Occupation: {persona.occupation}
        - Location: {persona.location}
        - Education: {persona.education_level}
        - Income Bracket: {persona.income_bracket if persona.income_bracket else 'Not specified'}
        """

        psychographics = f"""
        Psychographics:
        - Values: {', '.join(persona.values)}
        - Interests: {', '.join(persona.interests)}
        - Personality Traits: {self._format_personality_traits(persona.personality_traits)}
        - Information Seeking: {persona.information_seeking_behavior}
        - Preferred Channels: {', '.join([ch.value for ch in persona.preferred_channels])}
        - Cognitive Biases: {(
            ', '.join(persona.cognitive_biases) if persona.cognitive_biases else 'None specified'
        )}
        - Emotional Triggers: {(
            ', '.join(persona.emotional_triggers)
            if persona.emotional_triggers else 'None specified'
        )}
        - Decision Making Style: {persona.decision_making_style}
        - Content Sharing Likelihood: {persona.content_sharing_likelihood}
        - Influence Susceptibility: {persona.influence_susceptibility}
        """

        # Format analysis results
        analysis_summary = f"""
        Article Analysis:
        - Readability: Flesch Reading Ease {
            analysis_results.get('readability', {}).get('flesch_reading_ease', 'N/A')
        }
        - Sentiment: {analysis_results.get('sentiment', {}).get('overall', 'N/A')} (
            confidence: {analysis_results.get('sentiment', {}).get('confidence', 'N/A')}
        )
        - Structure: {analysis_results.get('structure', {}).get('sections', 'N/A')} sections, {
            analysis_results.get('structure', {}).get('paragraphs', 'N/A')
        } paragraphs
        - Keywords: {', '.join(analysis_results.get('keywords', {}).get('main_topics', []))}
        - Technical Depth: {analysis_results.get('technical_depth', {}).get('level', 'N/A')}
        """

        prompt = f"""
        You are evaluating the following article from the perspective of a specific persona.

        PERSONA PROFILE:
        {demographics}
        {psychographics}

        ARTICLE TO EVALUATE:
        {article_content[:3000]}...  # Truncate for token limits

        {analysis_summary}

        EVALUATION CRITERIA:
        Based on this persona's unique characteristics, evaluate the article on the
        following dimensions:

        1. Relevance Score (0-100): How relevant is this article to the persona's
           interests and needs?
        2. Clarity Score (0-100): How clear and understandable is the article for
           this persona?
        3. Credibility Score (0-100): How credible does this persona find the
           article?
        4. Emotional Impact Score (0-100): How emotionally engaging is the article
           for this persona?
        5. Action Potential Score (0-100): How likely is this persona to take action
           based on the article?

        Additional metrics:
        - Interest Alignment (0.0-1.0): How well does the article align with persona's interests?
        - Value Alignment (0.0-1.0): How well does the article align with persona's values?
        - Bias Resonance (0.0-1.0): How much does the article resonate with
          persona's cognitive biases?

        Provide qualitative feedback:
        - Strengths: 3-5 specific strengths from this persona's perspective
        - Weaknesses: 2-4 specific weaknesses from this persona's perspective
        - Improvement Suggestions: 2-4 concrete suggestions that would make the
          article more appealing to this persona

        Predict engagement behavior:
        - Read Completion Probability (0.0-1.0)
        - Share Probability (0.0-1.0)
        - Bookmark Probability (0.0-1.0)
        - Discussion Probability (0.0-1.0)

        Emotional Response:
        - Primary Emotion (e.g., excitement, curiosity, skepticism, etc.)
        - Intensity (0.0-1.0)
        - Triggers (list of specific elements that triggered the emotion)

        Provide your evaluation in the following JSON format:
        {{
            "relevance_score": <int>,
            "clarity_score": <int>,
            "credibility_score": <int>,
            "emotional_impact_score": <int>,
            "action_potential_score": <int>,
            "interest_alignment": <float>,
            "value_alignment": <float>,
            "bias_resonance": <float>,
            "strengths": [<list of strings>],
            "weaknesses": [<list of strings>],
            "improvement_suggestions": [<list of strings>],
            "predicted_engagement": {{
                "read_completion_probability": <float>,
                "share_probability": <float>,
                "bookmark_probability": <float>,
                "discussion_probability": <float>
            }},
            "emotional_response": {{
                "primary_emotion": <string>,
                "intensity": <float>,
                "triggers": [<list of strings>]
            }},
            "key_insights": [
                <list of 2-3 key insights about how this persona perceives the article>
            ]
        }}
        """

        return prompt

    def _generate_persona_id(self, persona: PersonaAttributes) -> str:
        """Generate ID for persona based on attributes"""
        import hashlib

        # Create a stable ID based on persona attributes
        key_attrs = f"{persona.age}_{persona.occupation}_{persona.location}"
        return hashlib.md5(key_attrs.encode()).hexdigest()[:12]

    async def decide(self, perception: dict[str, Any]) -> IAction:
        """
        Decide action based on perception (required by BaseAgent)

        For evaluation agent, this creates an evaluation action
        """
        # EvaluationAgent doesn't make traditional decisions
        # It evaluates based on provided data
        return BaseAction(
            action_type="evaluate",
            parameters={
                "persona_id": perception.get("persona_id"),
                "article_id": perception.get("article_id"),
            },
        )

    def _format_personality_traits(self, traits: dict[PersonalityType, float]) -> str:
        """Format personality traits for prompt"""
        if not traits:
            return "Not specified"

        formatted = []
        for trait, value in traits.items():
            trait_name = trait.value if hasattr(trait, "value") else str(trait)
            formatted.append(f"{trait_name}: {value:.2f}")

        return ", ".join(formatted)

    def _parse_evaluation_response(
        self,
        response: str,
        persona_id: str,
        article_id: str,
    ) -> EvaluationResult:
        """Parse LLM response into EvaluationResult"""
        try:
            # Use the json parser utility
            parsed = parse_llm_json_response(response)

            # Create EvaluationResult with parsed data
            # Convert individual scores to metrics
            metrics = [
                EvaluationMetric(
                    name="relevance", score=parsed.get("relevance_score", 50), weight=0.3
                ),
                EvaluationMetric(name="clarity", score=parsed.get("clarity_score", 50), weight=0.2),
                EvaluationMetric(
                    name="credibility", score=parsed.get("credibility_score", 50), weight=0.2
                ),
                EvaluationMetric(
                    name="emotional_impact",
                    score=parsed.get("emotional_impact_score", 50),
                    weight=0.15,
                ),
                EvaluationMetric(
                    name="action_potential",
                    score=parsed.get("action_potential_score", 50),
                    weight=0.15,
                ),
            ]

            # Determine engagement level from scores
            overall = self._calculate_overall_score(parsed)
            engagement_level: Literal["low", "medium", "high"] = (
                "high" if overall >= 70 else "medium" if overall >= 40 else "low"
            )

            # Determine sentiment
            emotional_response = parsed.get("emotional_response", {})
            primary_emotion = emotional_response.get("primary_emotion", "neutral")
            sentiment: Literal["negative", "neutral", "positive"] = (
                "positive"
                if primary_emotion in ["excitement", "joy", "satisfaction"]
                else (
                    "negative"
                    if primary_emotion in ["anger", "frustration", "disappointment"]
                    else "neutral"
                )
            )

            return EvaluationResult(
                persona_id=persona_id,
                persona_type="dynamic",  # Will be set by orchestrator
                article_id=article_id,
                metrics=metrics,
                overall_score=overall,
                strengths=parsed.get("strengths", ["Unable to parse strengths"]),
                weaknesses=parsed.get("weaknesses", ["Unable to parse weaknesses"]),
                suggestions=parsed.get("improvement_suggestions", ["Unable to parse suggestions"]),
                sharing_probability=parsed.get("predicted_engagement", {}).get(
                    "share_probability", 0.3
                ),
                engagement_level=engagement_level,
                sentiment=sentiment,
                reasoning="\n".join(
                    parsed.get("key_insights", ["Evaluation completed with partial data"])
                ),
                confidence=(
                    0.8
                    if all(
                        key in parsed
                        for key in ["relevance_score", "clarity_score", "credibility_score"]
                    )
                    else 0.5
                ),
            )

        except Exception as e:
            logger.error(f"Failed to parse evaluation response: {str(e)}")
            return self._create_default_evaluation(persona_id, article_id)

    def _calculate_overall_score(self, parsed_data: dict[str, Any]) -> float:
        """Calculate weighted overall score"""
        scores = [
            parsed_data.get("relevance_score", 50) * 0.3,
            parsed_data.get("clarity_score", 50) * 0.2,
            parsed_data.get("credibility_score", 50) * 0.2,
            parsed_data.get("emotional_impact_score", 50) * 0.15,
            parsed_data.get("action_potential_score", 50) * 0.15,
        ]
        return float(sum(scores))

    def _create_default_evaluation(
        self,
        persona_id: str,
        article_id: str,
    ) -> EvaluationResult:
        """Create a default evaluation when LLM fails"""
        # Default metrics
        default_metrics = [
            EvaluationMetric(name="relevance", score=50, weight=0.3),
            EvaluationMetric(name="clarity", score=50, weight=0.2),
            EvaluationMetric(name="credibility", score=50, weight=0.2),
            EvaluationMetric(name="emotional_impact", score=50, weight=0.15),
            EvaluationMetric(name="action_potential", score=50, weight=0.15),
        ]

        return EvaluationResult(
            persona_id=persona_id,
            persona_type="dynamic",
            article_id=article_id,
            metrics=default_metrics,
            overall_score=50,
            strengths=["Content is present", "Article is readable"],
            weaknesses=["Unable to perform detailed evaluation"],
            suggestions=["Evaluation system needs review"],
            sharing_probability=0.3,
            engagement_level="medium",
            sentiment="neutral",
            reasoning="Default evaluation due to system error",
            confidence=0.1,
        )
