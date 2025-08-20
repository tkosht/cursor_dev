"""
Unit tests for PersonaDesignOrchestrator - Using REAL LLM APIs
Following CLAUDE.md mandatory rules: NO MOCKS ALLOWED
"""

import os
import sys
from pathlib import Path

import pytest

# Add tests directory to path for test helper
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.persona_design_orchestrator import PersonaDesignOrchestrator
from src.agents.target_audience_analyzer import AudienceAnalysis, AudienceSegment
from src.core.types import InformationChannel, PersonaAttributes, PersonalityType


class TestPersonaDesignOrchestrator:
    """Test suite for PersonaDesignOrchestrator with real LLM"""

    @pytest.fixture
    def orchestrator(self):
        """Create PersonaDesignOrchestrator instance"""
        return PersonaDesignOrchestrator()

    @pytest.fixture
    def tech_article_content(self):
        """Sample technology article for testing"""
        return """
        # Next-Generation Cloud Infrastructure: The Edge Computing Revolution
        
        Organizations are rapidly adopting edge computing to reduce latency and improve
        performance for real-time applications. This paradigm shift moves computation
        closer to data sources, enabling faster processing and reduced bandwidth costs.
        
        Key benefits include:
        - Ultra-low latency for IoT applications
        - Improved data privacy and security
        - Reduced cloud infrastructure costs
        - Enhanced reliability through distributed architecture
        
        Early adopters in manufacturing, healthcare, and autonomous vehicles report
        significant improvements in operational efficiency and user experience.
        The edge computing market is projected to grow to $250 billion by 2025.
        """

    @pytest.fixture
    def article_analysis(self):
        """Sample article analysis for testing"""
        return {
            "core_context": {
                "domain_analysis": {
                    "primary_domain": "technology",
                    "technical_complexity": 8,
                    "innovation_level": "high",
                },
                "emotional_landscape": {"controversy_potential": "low", "excitement_level": "high"},
                "stakeholder_mapping": {
                    "beneficiaries": ["IT professionals", "CTOs", "DevOps engineers"],
                    "impact_areas": ["infrastructure", "operations", "cost"],
                },
            },
            "hierarchy": {
                "persona_slots": [
                    {
                        "id": "slot_1",
                        "major_segment": "tech_leaders",
                        "network_position": {"type": "influencer"},
                    },
                    {
                        "id": "slot_2",
                        "major_segment": "developers",
                        "network_position": {"type": "active"},
                    },
                    {
                        "id": "slot_3",
                        "major_segment": "business_analysts",
                        "network_position": {"type": "observer"},
                    },
                ],
                "major_segments": [
                    {
                        "id": "tech_leaders",
                        "name": "Technology Leaders",
                        "characteristics": ["strategic", "innovative", "decision-maker"],
                    },
                    {
                        "id": "developers",
                        "name": "Software Developers",
                        "characteristics": ["technical", "hands-on", "problem-solver"],
                    },
                    {
                        "id": "business_analysts",
                        "name": "Business Analysts",
                        "characteristics": ["analytical", "cost-conscious", "practical"],
                    },
                ],
            },
            "reach_potential": 0.8,
            "metadata": {"topic": "edge computing", "industry": "technology"},
        }

    @pytest.mark.asyncio
    async def test_orchestrate_persona_generation_small(
        self, orchestrator, tech_article_content, article_analysis, real_llm
    ):
        """Test orchestrated persona generation with small count"""
        # Skip if no API key
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")

        # Generate small number of personas to save API calls
        personas = await orchestrator.orchestrate_persona_generation(
            article_content=tech_article_content,
            article_analysis=article_analysis,
            target_count=3,  # Small count for testing
            simulation_config={"max_api_calls": 10},
        )

        # Verify basic structure
        assert isinstance(personas, list)
        assert len(personas) == 3

        # Check each persona
        for persona in personas:
            assert isinstance(persona, PersonaAttributes)
            assert persona.age > 0
            assert persona.occupation is not None
            assert len(persona.values) > 0
            assert len(persona.interests) > 0
            assert persona.personality_traits is not None
            assert PersonalityType.OPENNESS in persona.personality_traits

    @pytest.mark.asyncio
    async def test_persona_distribution_design(self, orchestrator):
        """Test persona distribution across segments"""
        # Create mock audience analysis
        primary_segment = AudienceSegment(
            name="Tech Professionals",
            description="Technology professionals interested in infrastructure",
            size_estimate="large",
            relevance_score=0.9,
            key_characteristics=["technical", "innovative"],
            interests=["cloud", "infrastructure", "DevOps"],
            pain_points=["latency", "costs", "scalability"],
            engagement_potential=0.8,
        )

        secondary_segments = [
            AudienceSegment(
                name="Business Leaders",
                description="Business decision makers",
                size_estimate="medium",
                relevance_score=0.7,
                key_characteristics=["strategic", "cost-conscious"],
                interests=["ROI", "efficiency", "innovation"],
                pain_points=["budget", "complexity"],
                engagement_potential=0.6,
            ),
            AudienceSegment(
                name="Researchers",
                description="Academic and industry researchers",
                size_estimate="small",
                relevance_score=0.5,
                key_characteristics=["analytical", "curious"],
                interests=["innovation", "research", "trends"],
                pain_points=["access", "resources"],
                engagement_potential=0.4,
            ),
        ]

        audience_analysis = AudienceAnalysis(
            primary_audience=primary_segment,
            secondary_audiences=secondary_segments,
            total_reach_potential=0.7,
            engagement_distribution={
                "Tech Professionals": 0.5,
                "Business Leaders": 0.3,
                "Researchers": 0.2,
            },
            demographic_insights={},
            psychographic_insights={},
            behavioral_patterns={},
        )

        # Design distribution
        distribution = await orchestrator._design_persona_distribution(
            audience_analysis=audience_analysis, target_count=10
        )

        # Verify distribution
        assert isinstance(distribution, dict)
        assert "Tech Professionals" in distribution
        assert distribution["Tech Professionals"] >= 4  # ~45% of 10
        assert sum(distribution.values()) == 10

    @pytest.mark.asyncio
    async def test_unique_persona_generation(
        self, orchestrator, tech_article_content, article_analysis, real_llm
    ):
        """Test generation of unique persona within segment"""
        # Skip if no API key
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")

        # Create test segment
        segment = AudienceSegment(
            name="Cloud Architects",
            description="Senior cloud infrastructure architects",
            size_estimate="medium",
            relevance_score=0.85,
            key_characteristics=["technical", "strategic", "experienced"],
            interests=["cloud", "architecture", "scalability", "security"],
            pain_points=["complexity", "migration", "costs"],
            engagement_potential=0.75,
        )

        # Create mock audience analysis
        audience_analysis = type(
            "obj",
            (object,),
            {
                "demographic_insights": {
                    "age_distribution": {"35-44": 0.4, "45-54": 0.3, "25-34": 0.3},
                    "education_levels": {"graduate": 0.7, "bachelor": 0.3},
                    "professional_fields": ["IT", "Engineering", "Consulting"],
                },
                "psychographic_insights": {
                    "values": ["innovation", "efficiency", "reliability"],
                    "motivations": ["career growth", "technical excellence"],
                },
                "behavioral_patterns": {
                    "content_consumption": "active",
                    "sharing_behavior": "selective",
                },
            },
        )()

        # Generate unique persona
        persona_data = await orchestrator._generate_unique_persona(
            segment=segment,
            index=0,
            article_content=tech_article_content,
            article_analysis=article_analysis,
            audience_analysis=audience_analysis,
        )

        # Verify persona data structure
        assert isinstance(persona_data, dict)
        assert "age" in persona_data
        assert "occupation" in persona_data
        assert "values" in persona_data
        assert "interests" in persona_data
        assert isinstance(persona_data.get("age"), (int, float))
        assert len(persona_data.get("values", [])) > 0

    @pytest.mark.asyncio
    async def test_persona_attributes_creation(self, orchestrator):
        """Test conversion of persona data to PersonaAttributes"""
        # Create test persona data
        persona_data = {
            "age": 38,
            "occupation": "Senior DevOps Engineer",
            "location": "San Francisco, CA",
            "education_level": "Master's Degree",
            "values": ["automation", "efficiency", "reliability"],
            "interests": ["kubernetes", "cloud", "CI/CD", "monitoring"],
            "personality_traits": {
                "openness": 0.8,
                "conscientiousness": 0.85,
                "extraversion": 0.6,
                "agreeableness": 0.7,
                "neuroticism": 0.3,
            },
            "information_seeking_behavior": "active",
            "preferred_channels": ["tech blogs", "podcasts", "forums"],
            "influence_potential": 0.7,
        }

        segment = AudienceSegment(
            name="DevOps Professionals",
            description="DevOps engineers and SREs",
            size_estimate="large",
            relevance_score=0.9,
            key_characteristics=["technical", "automated", "efficient"],
            interests=["DevOps", "cloud", "automation"],
            pain_points=["downtime", "manual processes", "scalability"],
            engagement_potential=0.8,
        )

        # Convert to PersonaAttributes
        persona = orchestrator._create_persona_attributes(persona_data, segment, 0)

        # Verify PersonaAttributes
        assert isinstance(persona, PersonaAttributes)
        assert persona.age == 38
        assert persona.occupation == "Senior DevOps Engineer"
        assert len(persona.values) == 3
        assert "automation" in persona.values
        assert PersonalityType.OPENNESS in persona.personality_traits
        assert persona.personality_traits[PersonalityType.OPENNESS] == 0.8
        assert InformationChannel.TECH_BLOGS in persona.preferred_channels

    @pytest.mark.asyncio
    async def test_network_position_enhancement(self, orchestrator, real_llm):
        """Test enhancement of personas with network positions"""
        # Skip if no API key
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")

        # Create test personas
        personas = []
        for i in range(3):
            persona = PersonaAttributes(
                age=30 + i * 5,
                occupation=f"Professional {i}",
                location="Tech Hub",
                education_level="Bachelor's",
                values=["innovation"],
                interests=["technology"],
                personality_traits={PersonalityType.OPENNESS: 0.7},
                information_seeking_behavior="active",
                preferred_channels=[InformationChannel.TECH_BLOGS],
                social_influence_score=0.3 + i * 0.2,
                network_size="medium",
            )
            personas.append(persona)

        # Build network (this will populate network_graph)
        article_analysis = {"metadata": {"topic": "tech"}}
        await orchestrator.network_simulator.build_network(personas, article_analysis)

        # Enhance with network positions
        enhanced = await orchestrator._enhance_with_network_positions(personas)

        # Verify enhancement
        assert len(enhanced) == 3
        for persona in enhanced:
            assert isinstance(persona, PersonaAttributes)
            # Network positions should have updated influence scores
            assert persona.social_influence_score >= 0

    @pytest.mark.asyncio
    async def test_persona_validation_and_diversity(self, orchestrator):
        """Test persona validation and diversity adjustment"""
        # Create test personas with limited diversity
        personas = []
        for i in range(5):
            persona = PersonaAttributes(
                age=35,  # Same age for all
                occupation="Software Engineer",  # Same occupation
                location="San Francisco",
                education_level="Bachelor's",
                values=["innovation", "efficiency"],
                interests=["coding", "tech"],
                personality_traits={PersonalityType.OPENNESS: 0.7},
                information_seeking_behavior="active",
                preferred_channels=[InformationChannel.TECH_BLOGS],
            )
            personas.append(persona)

        article_content = "Tech article content"

        # Validate and adjust
        adjusted = await orchestrator._validate_and_adjust(personas, article_content)

        # Check diversity improvements
        ages = [p.age for p in adjusted]
        occupations = [p.occupation for p in adjusted]

        # Ages should be more diverse
        assert len(set(ages)) > 1

        # Occupations should have variations
        assert len(set(occupations)) > 1 or any(
            "Senior" in occ or "Junior" in occ for occ in occupations
        )

    @pytest.mark.asyncio
    async def test_fallback_persona_creation(self, orchestrator):
        """Test fallback persona creation when API fails"""
        segment = AudienceSegment(
            name="Test Segment",
            description="Test segment description",
            size_estimate="medium",
            relevance_score=0.5,
            key_characteristics=["test1", "test2"],
            interests=["interest1", "interest2"],
            pain_points=["pain1"],
            engagement_potential=0.5,
        )

        # Create fallback persona
        fallback_data = orchestrator._create_fallback_persona_data(segment, 0)

        # Verify fallback data
        assert isinstance(fallback_data, dict)
        assert "age" in fallback_data
        assert "occupation" in fallback_data
        assert fallback_data["age"] == 35
        assert "Test Segment" in fallback_data["occupation"]
        assert len(fallback_data["values"]) > 0
        assert len(fallback_data["interests"]) > 0

    @pytest.mark.asyncio
    async def test_segment_retrieval(self, orchestrator):
        """Test getting segment by name from audience analysis"""
        primary = AudienceSegment(
            name="Primary",
            description="Primary audience",
            size_estimate="large",
            relevance_score=0.9,
            key_characteristics=["primary"],
            interests=["main"],
            pain_points=["key"],
            engagement_potential=0.8,
        )

        secondary = AudienceSegment(
            name="Secondary",
            description="Secondary audience",
            size_estimate="medium",
            relevance_score=0.6,
            key_characteristics=["secondary"],
            interests=["other"],
            pain_points=["minor"],
            engagement_potential=0.5,
        )

        audience_analysis = type(
            "obj", (object,), {"primary_audience": primary, "secondary_audiences": [secondary]}
        )()

        # Test retrieval
        result_primary = orchestrator._get_segment_by_name(audience_analysis, "Primary")
        result_secondary = orchestrator._get_segment_by_name(audience_analysis, "Secondary")
        result_none = orchestrator._get_segment_by_name(audience_analysis, "NonExistent")

        assert result_primary == primary
        assert result_secondary == secondary
        assert result_none is None
