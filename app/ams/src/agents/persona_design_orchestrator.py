"""
Persona Design Orchestrator for dynamic persona generation
Orchestrates the entire persona generation process based on article content
"""

import logging
from dataclasses import dataclass
from typing import Any

from src.agents.network_effect_simulator import NetworkEffectSimulator, NetworkNode
from src.agents.target_audience_analyzer import AudienceSegment, TargetAudienceAnalyzer
from src.core.types import InformationChannel, PersonaAttributes, PersonalityType
from src.utils.json_parser import parse_llm_json_response
from src.utils.llm_factory import create_llm

logger = logging.getLogger(__name__)


@dataclass
class PersonaDesign:
    """Complete persona design with all attributes"""

    persona_id: str
    segment: AudienceSegment
    network_position: NetworkNode | None
    attributes: PersonaAttributes
    generation_metadata: dict[str, Any]


class PersonaDesignOrchestrator:
    """
    Orchestrates the complete persona design process
    Integrates audience analysis, network effects, and persona generation
    """

    def __init__(self):
        self.llm = create_llm()
        self.audience_analyzer = TargetAudienceAnalyzer()
        self.network_simulator = NetworkEffectSimulator()
        self.generated_personas: list[PersonaDesign] = []

    async def orchestrate_persona_generation(
        self,
        article_content: str,
        article_analysis: dict[str, Any],
        target_count: int = 50,
        simulation_config: dict[str, Any] | None = None,
    ) -> list[PersonaAttributes]:
        """
        Orchestrate the complete persona generation process

        Args:
            article_content: The article to analyze
            article_analysis: Deep analysis results
            target_count: Number of personas to generate
            simulation_config: Optional simulation configuration

        Returns:
            List of dynamically generated PersonaAttributes
        """
        logger.info(f"Starting orchestrated persona generation for {target_count} personas")

        # Step 1: Analyze target audience
        audience_analysis = await self.audience_analyzer.analyze_audience(
            article_content, article_analysis.get("metadata")
        )

        # Step 2: Design persona distribution across segments
        distribution = await self._design_persona_distribution(audience_analysis, target_count)

        # Step 3: Generate personas for each segment
        all_personas = []
        for segment_name, count in distribution.items():
            segment = self._get_segment_by_name(audience_analysis, segment_name)
            if segment:
                personas = await self._generate_segment_personas(
                    segment, count, article_content, article_analysis, audience_analysis
                )
                all_personas.extend(personas)

        # Step 4: Build network structure
        await self.network_simulator.build_network(all_personas, article_analysis)

        # Step 5: Enhance personas with network positions
        enhanced_personas = await self._enhance_with_network_positions(all_personas)

        # Step 6: Validate and adjust personas
        final_personas = await self._validate_and_adjust(enhanced_personas, article_content)

        logger.info(f"Generated {len(final_personas)} dynamic personas")

        return final_personas

    async def _design_persona_distribution(
        self, audience_analysis: Any, target_count: int
    ) -> dict[str, int]:
        """Design how many personas to generate for each segment"""
        distribution = {}

        # Calculate based on engagement potential and size
        primary = audience_analysis.primary_audience
        secondary = audience_analysis.secondary_audiences

        # Primary audience gets 40-50% of personas
        primary_count = int(target_count * 0.45)
        distribution[primary.name] = primary_count

        # Distribute remaining among secondary audiences
        remaining = target_count - primary_count
        if secondary:
            per_secondary = remaining // len(secondary)
            for seg in secondary:
                distribution[seg.name] = per_secondary

            # Add remainder to highest engagement secondary
            remainder = remaining % len(secondary)
            if remainder > 0 and secondary:
                best_secondary = max(secondary, key=lambda s: s.engagement_potential)
                distribution[best_secondary.name] += remainder
        else:
            # All to primary if no secondary
            distribution[primary.name] = target_count

        return distribution

    async def _generate_segment_personas(
        self,
        segment: AudienceSegment,
        count: int,
        article_content: str,
        article_analysis: dict[str, Any],
        audience_analysis: Any,
    ) -> list[PersonaAttributes]:
        """Generate personas for a specific segment"""
        personas = []

        for i in range(count):
            # Generate unique persona within segment
            persona_data = await self._generate_unique_persona(
                segment, i, article_content, article_analysis, audience_analysis
            )

            # Convert to PersonaAttributes
            persona = self._create_persona_attributes(persona_data, segment, i)
            personas.append(persona)

        return personas

    async def _generate_unique_persona(
        self,
        segment: AudienceSegment,
        index: int,
        article_content: str,
        article_analysis: dict[str, Any],
        audience_analysis: Any,
    ) -> dict[str, Any]:
        """Generate a unique persona within a segment"""

        # Extract relevant context
        demographics = audience_analysis.demographic_insights
        psychographics = audience_analysis.psychographic_insights
        # behavioral patterns are part of the prompt context; not used directly in code here
        _behaviors = audience_analysis.behavioral_patterns

        prompt = f"""
        Generate a unique persona for segment: {segment.name}
        Segment description: {segment.description}

        Article context: {article_content[:500]}...

        Segment characteristics: {', '.join(segment.key_characteristics)}
        Interests: {', '.join(segment.interests)}
        Pain points: {', '.join(segment.pain_points)}

        Demographics context:
        - Age distribution: {demographics.get('age_distribution', {})}
        - Education: {demographics.get('education_levels', {})}
        - Professions: {demographics.get('professional_fields', [])}

        Psychographics:
        - Values: {psychographics.get('values', [])}
        - Motivations: {psychographics.get('motivations', [])}

        Make this persona #{index + 1} unique within the segment.

        Return detailed JSON with:
        - age: specific age (not range)
        - occupation: specific job title
        - location: specific city/region
        - education_level: specific education
        - values: 3-5 core values
        - interests: 4-6 specific interests
        - personality_traits: openness, conscientiousness, extraversion, agreeableness,
          neuroticism (0-1 scores)
        - information_seeking_behavior: active/moderate/passive
        - preferred_channels: list of information channels
        - unique_perspective: what makes this persona's view unique
        - article_relevance: how this article relates to them specifically
        - likely_reaction: their probable response to the article
        - sharing_likelihood: 0-1 probability
        - influence_potential: low/medium/high
        """

        try:
            response = await self.llm.ainvoke(prompt)
            data = parse_llm_json_response(str(response.content))
            return data
        except Exception as e:
            logger.error(f"Failed to generate unique persona: {e}")
            return self._create_fallback_persona_data(segment, index)

    def _create_persona_attributes(
        self, persona_data: dict[str, Any], segment: AudienceSegment, index: int
    ) -> PersonaAttributes:
        """Convert persona data to PersonaAttributes object"""

        # Parse personality traits
        personality = persona_data.get("personality_traits", {})
        personality_traits = {
            PersonalityType.OPENNESS: float(personality.get("openness", 0.5)),
            PersonalityType.CONSCIENTIOUSNESS: float(personality.get("conscientiousness", 0.5)),
            PersonalityType.EXTRAVERSION: float(personality.get("extraversion", 0.5)),
            PersonalityType.AGREEABLENESS: float(personality.get("agreeableness", 0.5)),
            PersonalityType.NEUROTICISM: float(personality.get("neuroticism", 0.5)),
        }

        # Parse information channels
        channel_map = {
            "social media": InformationChannel.SOCIAL_MEDIA,
            "social": InformationChannel.SOCIAL_MEDIA,
            "news sites": InformationChannel.NEWS_SITES,
            "news": InformationChannel.NEWS_WEBSITE,
            "online news": InformationChannel.NEWS_WEBSITE,
            "tech blogs": InformationChannel.TECH_BLOGS,
            "blogs": InformationChannel.TECH_BLOGS,
            "forums": InformationChannel.FORUMS,
            "forum": InformationChannel.FORUMS,
            "podcasts": InformationChannel.PODCASTS,
            "podcast": InformationChannel.PODCASTS,
            "video": InformationChannel.VIDEO_PLATFORMS,
            "videos": InformationChannel.VIDEO_PLATFORMS,
            "youtube": InformationChannel.VIDEO_PLATFORMS,
            "email": InformationChannel.EMAIL,
            "email newsletter": InformationChannel.EMAIL_NEWSLETTERS,
            "newsletters": InformationChannel.EMAIL_NEWSLETTERS,
            "messaging": InformationChannel.MESSAGING_APPS,
            "chat": InformationChannel.MESSAGING_APPS,
            "traditional": InformationChannel.TRADITIONAL_MEDIA,
            "tv": InformationChannel.TRADITIONAL_MEDIA,
            "radio": InformationChannel.TRADITIONAL_MEDIA,
            "word of mouth": InformationChannel.WORD_OF_MOUTH,
            "search": InformationChannel.SEARCH_ENGINE,
            "search engine": InformationChannel.SEARCH_ENGINE,
            "google": InformationChannel.SEARCH_ENGINE,
            "rss": InformationChannel.RSS_FEED,
            "rss feed": InformationChannel.RSS_FEED,
        }

        channels = []
        for channel_str in persona_data.get("preferred_channels", ["social media"]):
            for key, enum_val in channel_map.items():
                if key in channel_str.lower():
                    channels.append(enum_val)
                    break

        if not channels:
            channels = [InformationChannel.SOCIAL_MEDIA]

        # Convert influence_potential to float
        influence_potential = persona_data.get("influence_potential", 0.5)
        if isinstance(influence_potential, str):
            influence_map = {"low": 0.3, "medium": 0.5, "high": 0.7, "very high": 0.9}
            influence_score = influence_map.get(influence_potential.lower(), 0.5)
        else:
            influence_score = float(influence_potential)

        # Map sharing_likelihood to content_sharing_likelihood
        sharing_likelihood = persona_data.get("sharing_likelihood", 0.5)
        if isinstance(sharing_likelihood, str):
            try:
                sharing_likelihood = float(sharing_likelihood)
            except (ValueError, TypeError):
                sharing_likelihood = 0.5

        return PersonaAttributes(
            age=int(persona_data.get("age", 35)),
            occupation=persona_data.get("occupation", "Professional"),
            location=persona_data.get("location", "Urban Area"),
            education_level=persona_data.get("education_level", "Bachelor's Degree"),
            values=persona_data.get("values", ["growth", "learning", "innovation"]),
            interests=persona_data.get("interests", segment.interests),
            personality_traits=personality_traits,
            information_seeking_behavior=persona_data.get(
                "information_seeking_behavior", "moderate"
            ),
            preferred_channels=channels,
            cognitive_biases=persona_data.get("cognitive_biases"),
            emotional_triggers=persona_data.get("emotional_triggers", []),
            income_bracket=persona_data.get("income_bracket"),
            decision_making_style=persona_data.get("decision_making_style", "analytical"),
            content_sharing_likelihood=sharing_likelihood,
            influence_susceptibility=influence_score,  # Using the influence_score as susceptibility
        )

    async def _enhance_with_network_positions(
        self, personas: list[PersonaAttributes]
    ) -> list[PersonaAttributes]:
        """Enhance personas with network position information"""
        # Network positions are already built in the simulator
        # Here we can add network-based attributes to personas

        for i, persona in enumerate(personas):
            persona_id = f"persona_{i}"
            if persona_id in self.network_simulator.network_graph:
                node = self.network_simulator.network_graph[persona_id]

                # Update influence susceptibility based on network position
                # (PersonaAttributes doesn't have social_influence_score or network_size fields)
                persona.influence_susceptibility = node.influence_score

        return personas

    async def _validate_and_adjust(
        self, personas: list[PersonaAttributes], article_content: str
    ) -> list[PersonaAttributes]:
        """Validate and adjust personas for consistency and realism"""

        # Check for diversity
        occupations = [p.occupation for p in personas]
        ages = [p.age for p in personas]

        # Ensure age diversity
        if len(set(ages)) < len(personas) * 0.5:
            # Adjust ages for more diversity
            for i, persona in enumerate(personas):
                if i % 3 == 0:
                    persona.age = max(25, persona.age - 5)
                elif i % 3 == 1:
                    persona.age = min(75, persona.age + 5)

        # Ensure occupation diversity
        occupation_counts = {}
        for occupation in occupations:
            occupation_counts[occupation] = occupation_counts.get(occupation, 0) + 1

        # If any occupation is overrepresented, diversify
        max_count = max(occupation_counts.values())
        if max_count > len(personas) * 0.2:
            # Add variations to overrepresented occupations
            for i, persona in enumerate(personas):
                if occupation_counts.get(persona.occupation, 0) > 2:
                    persona.occupation = (
                        f"{persona.occupation} - {['Senior', 'Junior', 'Lead', 'Principal'][i % 4]}"
                    )

        return personas

    def _get_segment_by_name(
        self, audience_analysis: Any, segment_name: str
    ) -> AudienceSegment | None:
        """Get segment by name from audience analysis"""
        if audience_analysis.primary_audience.name == segment_name:
            return audience_analysis.primary_audience

        for seg in audience_analysis.secondary_audiences:
            if seg.name == segment_name:
                return seg

        return None

    def _create_fallback_persona_data(self, segment: AudienceSegment, index: int) -> dict[str, Any]:
        """Create fallback persona data when generation fails"""
        return {
            "age": 35 + (index % 30),
            "occupation": f"Professional in {segment.name}",
            "location": "Major City",
            "education_level": "Bachelor's Degree",
            "values": (
                segment.key_characteristics[:3]
                if segment.key_characteristics
                else ["growth", "learning"]
            ),
            "interests": (
                segment.interests[:4] if segment.interests else ["technology", "innovation"]
            ),
            "personality_traits": {
                "openness": 0.6,
                "conscientiousness": 0.7,
                "extraversion": 0.5,
                "agreeableness": 0.6,
                "neuroticism": 0.4,
            },
            "information_seeking_behavior": "moderate",
            "preferred_channels": ["online news", "social media"],
            "unique_perspective": f"Member of {segment.name} segment",
            "article_relevance": 0.7,
            "likely_reaction": "interested",
            "sharing_likelihood": 0.5,
            "influence_potential": "medium",
        }
