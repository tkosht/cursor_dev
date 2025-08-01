"""Optimized Persona Generator for Article Market Simulator.

This module generates realistic personas based on analysis context.
Optimized version reduces prompt size and improves performance.
"""

import random
from typing import Any

from src.core.types import PersonaAttributes, PersonalityType
from src.utils.json_parser import parse_llm_json_response
from src.utils.llm_factory import create_llm


class PersonaGenerator:
    """Generate diverse personas for article evaluation.

    Optimized to reduce prompt sizes and improve performance.
    """

    def __init__(self):
        self.llm = create_llm()

    async def generate_personas(
        self,
        article_content: str,
        analysis_results: dict[str, Any],
        count: int = 10,
    ) -> list[PersonaAttributes]:
        """Generate personas based on article and analysis context.

        Args:
            article_content: Original article content
            analysis_results: Results from DeepContextAnalyzer
            count: Number of personas to generate

        Returns:
            List of PersonaAttributes objects
        """
        try:
            # Extract essential information once
            article_summary = self._extract_article_summary(article_content)
            essential_context = self._extract_essential_context(analysis_results)

            # Get hierarchy or use default
            hierarchy = analysis_results.get("hierarchy", {})
            persona_slots = hierarchy.get("persona_slots", [])

            # Generate personas for each slot
            personas = []
            for i in range(min(count, len(persona_slots))):
                persona_slot = persona_slots[i]

                # Get segment info
                major_segments = hierarchy.get("major_segments", [])
                segment_info = next(
                    (s for s in major_segments if s["id"] == persona_slot.get("major_segment")),
                    {"name": "General", "characteristics": ["curious", "open-minded"]},
                )

                # Generate persona with minimal context
                persona_data = await self._generate_single_persona_optimized(
                    article_summary,
                    essential_context,
                    persona_slot,
                    segment_info,
                )

                # Convert to PersonaAttributes
                persona = self._convert_to_persona_attributes(persona_data)
                personas.append(persona)

            # Fill remaining slots with defaults if needed
            while len(personas) < count:
                default_persona = self._create_default_persona(f"persona_{len(personas)}")
                personas.append(default_persona)

            return personas

        except Exception:
            # Return default personas on error
            return [self._create_default_persona(f"persona_{i}") for i in range(count)]

    def _extract_article_summary(self, article_content: str) -> str:
        """Extract key points from article for prompt."""
        # Take first 200 chars + last 100 chars for context
        if len(article_content) <= 300:
            return article_content
        return f"{article_content[:200]}... {article_content[-100:]}"

    def _extract_essential_context(self, analysis_results: dict[str, Any]) -> dict[str, Any]:
        """Extract only essential context information."""
        core = analysis_results.get("core_context", {})

        return {
            "domain": core.get("domain_analysis", {}).get("primary_domain", "general"),
            "complexity": core.get("domain_analysis", {}).get("technical_complexity", 5),
            "emotional_tone": core.get("emotional_landscape", {}).get(
                "controversy_potential", "medium"
            ),
            "key_stakeholders": core.get("stakeholder_mapping", {}).get("beneficiaries", [])[:2],
            "reach_potential": analysis_results.get("reach_potential", 0.5),
        }

    async def _generate_single_persona_optimized(
        self,
        article_summary: str,
        essential_context: dict[str, Any],
        persona_slot: dict[str, Any],
        segment_info: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate a single persona with optimized prompt."""
        # Minimal prompt focusing on key information
        persona_prompt = f"""
        Article: {article_summary}
        Domain: {essential_context['domain']} (complexity: {essential_context['complexity']}/10)

        Generate persona for segment: {segment_info['name']}
        Traits: {', '.join(segment_info.get('characteristics', [])[:3])}
        Position: {persona_slot.get('network_position', {}).get('type', 'active')}

        Return JSON with:
        - name, age (25-75), occupation
        - background (2 sentences max)
        - personality_traits (4 traits)
        - interests (3 items)
        - decision_factors (2-3 factors)
        - article_relationship: relevance_score, interest_level, sharing_likelihood,
          discussion_points (2), action_likelihood

        Make it specific and realistic for this segment.
        """

        try:
            response = await self.llm.ainvoke(persona_prompt)
            persona_data = parse_llm_json_response(response.content)

            # Add metadata
            persona_data["id"] = persona_slot.get("id", f"persona_{random.randint(1000, 9999)}")
            persona_data["segment_id"] = persona_slot.get("major_segment")
            persona_data["network_position"] = persona_slot.get("network_position", {})

            # Ensure information_preferences exists
            if "information_preferences" not in persona_data:
                persona_data["information_preferences"] = ["online news", "social media"]

            return persona_data

        except Exception:
            return self._create_fallback_persona(persona_slot, segment_info)

    def _create_fallback_persona(
        self, persona_slot: dict[str, Any], segment_info: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a fallback persona when generation fails."""
        return {
            "id": persona_slot.get("id", f"persona_{random.randint(1000, 9999)}"),
            "name": f"User {random.randint(100, 999)}",
            "age": random.randint(25, 65),
            "occupation": "Professional",
            "background": (
                f"Professional with interest in "
                f"{segment_info.get('name', 'various topics')}"
            ),
            "personality_traits": segment_info.get("characteristics", ["analytical", "curious"])[
                :4
            ],
            "interests": [segment_info.get("name", "general topics")],
            "decision_factors": ["evidence", "relevance"],
            "information_preferences": ["professional networks", "industry publications"],
            "segment_id": persona_slot.get("major_segment"),
            "network_position": persona_slot.get("network_position", {}),
            "article_relationship": {
                "relevance_score": 0.5,
                "interest_level": "medium",
                "sharing_likelihood": 0.4,
                "discussion_points": ["General discussion"],
                "concerns": [],
                "action_likelihood": 0.3,
            },
        }

    def _convert_to_persona_attributes(self, persona_data: dict[str, Any]) -> PersonaAttributes:
        """Convert persona data to PersonaAttributes object."""
        # Calculate network metrics
        sharing_likelihood = persona_data.get("article_relationship", {}).get(
            "sharing_likelihood", 0.5
        )
        influence = persona_data.get("network_position", {}).get("influence", 0.5)

        # Map to PersonaAttributes fields
        personality_traits_dict = {
            PersonalityType.OPENNESS: 0.5,
            PersonalityType.CONSCIENTIOUSNESS: 0.5,
            PersonalityType.EXTRAVERSION: 0.5,
            PersonalityType.AGREEABLENESS: 0.5,
            PersonalityType.NEUROTICISM: 0.5,
        }

        return PersonaAttributes(
            # Demographics
            age=persona_data.get("age", 35),
            occupation=persona_data.get("occupation", "Professional"),
            # Psychographics
            interests=persona_data.get("interests", []),
            personality_traits=personality_traits_dict,
            # Behavioral
            content_sharing_likelihood=sharing_likelihood,
            influence_susceptibility=0.5,
            # Network position
            influence_score=influence,
            network_centrality=0.5,
            # Dynamic attributes
            trust_level={"article_source": 0.7},
        )

    def _create_default_persona(self, persona_id: str) -> PersonaAttributes:
        """Create a default persona."""
        personality_traits_dict = {
            PersonalityType.OPENNESS: 0.7,
            PersonalityType.CONSCIENTIOUSNESS: 0.6,
            PersonalityType.EXTRAVERSION: 0.5,
            PersonalityType.AGREEABLENESS: 0.6,
            PersonalityType.NEUROTICISM: 0.3,
        }

        return PersonaAttributes(
            # Demographics
            age=random.randint(25, 65),
            occupation="Professional",
            # Psychographics
            interests=["technology", "business", "current events"],
            personality_traits=personality_traits_dict,
            # Behavioral
            content_sharing_likelihood=0.5,
            influence_susceptibility=0.5,
            # Network position
            influence_score=0.5,
            network_centrality=0.5,
            # Dynamic attributes
            trust_level={"article_source": 0.5},
        )
