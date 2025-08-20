"""
Unit tests for NetworkEffectSimulator - Using REAL LLM APIs
Following CLAUDE.md mandatory rules: NO MOCKS ALLOWED
"""

import os
import sys
from pathlib import Path

import pytest

# Add tests directory to path for test helper
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.network_effect_simulator import (
    InfluenceType,
    NetworkEdge,
    NetworkEffectSimulator,
    NetworkNode,
    NetworkSimulationResult,
    PropagationEvent,
)
from src.core.types import InformationChannel, PersonaAttributes, PersonalityType


class TestNetworkEffectSimulator:
    """Test suite for NetworkEffectSimulator with real LLM"""

    @pytest.fixture
    def simulator(self):
        """Create NetworkEffectSimulator instance"""
        return NetworkEffectSimulator()

    @pytest.fixture
    def sample_personas(self):
        """Create sample personas for testing"""
        personas = []
        for i in range(5):
            persona = PersonaAttributes(
                age=25 + i * 5,
                occupation=["Engineer", "Manager", "Designer", "Analyst", "Researcher"][i],
                location="San Francisco",
                education_level="Bachelor's Degree",
                values=["innovation", "growth", "teamwork"],
                interests=["technology", "AI", "startups"] if i < 3 else ["business", "strategy"],
                personality_traits={
                    PersonalityType.OPENNESS: 0.7 + (i * 0.05),
                    PersonalityType.CONSCIENTIOUSNESS: 0.6,
                    PersonalityType.EXTRAVERSION: 0.5 + (i * 0.1),
                    PersonalityType.AGREEABLENESS: 0.7,
                    PersonalityType.NEUROTICISM: 0.3,
                },
                information_seeking_behavior="active" if i < 2 else "moderate",
                preferred_channels=[InformationChannel.TECH_BLOGS, InformationChannel.SOCIAL_MEDIA],
                social_influence_score=0.3 + (i * 0.15),
            )
            personas.append(persona)
        return personas

    @pytest.fixture
    def article_analysis(self):
        """Sample article analysis for context"""
        return {
            "core_context": {
                "domain_analysis": {"primary_domain": "technology", "technical_complexity": 7},
                "emotional_landscape": {"controversy_potential": "medium"},
            },
            "reach_potential": 0.7,
            "metadata": {"topic": "AI innovation", "target_audience": "tech professionals"},
        }

    @pytest.mark.asyncio
    async def test_build_network(self, simulator, sample_personas, article_analysis, real_llm):
        """Test network building from personas"""
        # Skip if no API key
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")

        # Build network
        await simulator.build_network(sample_personas, article_analysis)

        # Verify network structure
        assert len(simulator.network_graph) == len(sample_personas)
        assert len(simulator.edges) > 0

        # Check that all personas are represented as nodes
        for i, persona in enumerate(sample_personas):
            node_id = f"persona_{i}"
            assert node_id in simulator.network_graph
            node = simulator.network_graph[node_id]
            assert isinstance(node, NetworkNode)
            assert node.influence_score > 0
            assert node.connectivity > 0
            assert isinstance(node.influence_type, InfluenceType)

    @pytest.mark.asyncio
    async def test_network_node_creation(
        self, simulator, sample_personas, article_analysis, real_llm
    ):
        """Test individual network node creation"""
        # Skip if no API key
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")

        persona = sample_personas[0]
        node = await simulator._create_network_node(persona, 0, article_analysis)

        # Verify node properties
        assert isinstance(node, NetworkNode)
        assert node.persona_id == "persona_0"
        assert 0 <= node.influence_score <= 1.0
        assert node.connectivity > 0
        assert isinstance(node.influence_type, InfluenceType)
        assert len(node.interests) > 0
        assert 0 <= node.engagement_threshold <= 1.0
        assert node.amplification_factor > 0
        assert isinstance(node.position, tuple)
        assert len(node.position) == 2

    @pytest.mark.asyncio
    async def test_influence_type_determination(self, simulator, sample_personas, real_llm):
        """Test that influence types are determined correctly"""
        # Skip if no API key
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")

        # Test different persona types
        manager_persona = sample_personas[1]  # Manager
        influence_type = await simulator._determine_influence_type(manager_persona)

        assert isinstance(influence_type, InfluenceType)
        assert influence_type in [
            InfluenceType.AUTHORITY,
            InfluenceType.PEER,
            InfluenceType.ASPIRATIONAL,
            InfluenceType.VIRAL,
            InfluenceType.NICHE,
        ]

    @pytest.mark.asyncio
    async def test_propagation_simulation(
        self, simulator, sample_personas, article_analysis, real_llm
    ):
        """Test content propagation through network"""
        # Skip if no API key
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")

        # Build network first
        await simulator.build_network(sample_personas, article_analysis)

        # Simulate propagation from first persona
        initial_seeds = ["persona_0"]
        content_score = 0.7
        max_timesteps = 5

        result = await simulator.simulate_propagation(
            initial_seeds=initial_seeds,
            content_score=content_score,
            max_timesteps=max_timesteps,
            propagation_threshold=0.3,
        )

        # Verify simulation results
        assert isinstance(result, NetworkSimulationResult)
        assert result.total_reach >= 1  # At least the seed node
        assert result.total_reach <= len(sample_personas)
        assert isinstance(result.propagation_waves, list)
        assert isinstance(result.influence_map, dict)
        assert len(result.key_influencers) > 0
        assert 0 <= result.network_velocity
        assert result.saturation_point >= 0
        assert isinstance(result.propagation_events, list)

    @pytest.mark.asyncio
    async def test_edge_generation(self, simulator, sample_personas, article_analysis, real_llm):
        """Test network edge generation between nodes"""
        # Skip if no API key
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")

        # Build network
        await simulator.build_network(sample_personas, article_analysis)

        # Check edges
        assert len(simulator.edges) > 0

        for edge in simulator.edges[:5]:  # Check first 5 edges
            assert isinstance(edge, NetworkEdge)
            assert edge.source_id in simulator.network_graph
            assert edge.target_id in simulator.network_graph
            assert 0 <= edge.influence_weight <= 1.0
            assert edge.interaction_frequency in ["high", "medium", "low"]
            assert edge.relationship_type in [
                "mentor-follower",
                "peer",
                "influencer-audience",
                "social",
            ]

    @pytest.mark.asyncio
    async def test_propagation_probability_calculation(
        self, simulator, sample_personas, article_analysis
    ):
        """Test propagation probability calculation"""
        # Build network
        await simulator.build_network(sample_personas, article_analysis)

        # Get two nodes
        source_node = simulator.network_graph["persona_0"]
        target_node = simulator.network_graph.get("persona_1")

        if target_node and simulator.edges:
            # Find an edge between them (or create a test edge)
            test_edge = NetworkEdge(
                source_id="persona_0",
                target_id="persona_1",
                influence_weight=0.7,
                interaction_frequency="high",
                relationship_type="peer",
            )

            prob = simulator._calculate_propagation_probability(
                source_node, target_node, test_edge, content_score=0.8
            )

            assert 0 <= prob <= 1.0

    @pytest.mark.asyncio
    async def test_network_metrics(self, simulator, sample_personas, article_analysis, real_llm):
        """Test network metrics calculation"""
        # Skip if no API key
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")

        # Build network and simulate
        await simulator.build_network(sample_personas, article_analysis)

        result = await simulator.simulate_propagation(
            initial_seeds=["persona_0", "persona_1"], content_score=0.6, max_timesteps=3
        )

        # Test velocity calculation
        assert isinstance(result.network_velocity, float)

        # Test saturation point
        assert isinstance(result.saturation_point, int)
        assert 0 <= result.saturation_point <= 3

        # Test key influencers identification
        assert isinstance(result.key_influencers, list)
        assert all(influencer in simulator.network_graph for influencer in result.key_influencers)

    @pytest.mark.asyncio
    async def test_community_detection(self, simulator, sample_personas, article_analysis):
        """Test community detection in network"""
        # Build network
        await simulator.build_network(sample_personas, article_analysis)

        # Detect communities
        simulator._detect_communities()

        # Check communities were detected
        assert hasattr(simulator, "communities")
        assert isinstance(simulator.communities, list)

        # All nodes should be in some community
        all_nodes_in_communities = set()
        for community in simulator.communities:
            all_nodes_in_communities.update(community)

        # Communities should have some nodes
        if simulator.communities:
            assert len(all_nodes_in_communities) > 0

    @pytest.mark.asyncio
    async def test_influence_score_calculation(self, simulator):
        """Test influence score calculation for personas"""
        # Create test personas with different attributes
        ceo_persona = PersonaAttributes(
            age=45,
            occupation="CEO",
            location="Silicon Valley",
            education_level="MBA",
            values=["leadership", "innovation"],
            interests=["business", "technology"],
            personality_traits={PersonalityType.OPENNESS: 0.8, PersonalityType.EXTRAVERSION: 0.9},
            information_seeking_behavior="active",
            preferred_channels=[InformationChannel.NEWS_SITES],
        )

        student_persona = PersonaAttributes(
            age=22,
            occupation="Student",
            location="College Town",
            education_level="Undergraduate",
            values=["learning", "growth"],
            interests=["gaming", "social media"],
            personality_traits={PersonalityType.OPENNESS: 0.5, PersonalityType.EXTRAVERSION: 0.4},
            information_seeking_behavior="passive",
            preferred_channels=[InformationChannel.SOCIAL_MEDIA],
        )

        ceo_score = simulator._calculate_influence_score(ceo_persona)
        student_score = simulator._calculate_influence_score(student_persona)

        # CEO should have higher influence score
        assert ceo_score > student_score
        assert 0 <= ceo_score <= 1.0
        assert 0 <= student_score <= 1.0

    @pytest.mark.asyncio
    async def test_propagation_events_recording(
        self, simulator, sample_personas, article_analysis, real_llm
    ):
        """Test that propagation events are properly recorded"""
        # Skip if no API key
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")

        # Build network
        await simulator.build_network(sample_personas, article_analysis)

        # Clear history
        simulator.propagation_history = []

        # Simulate propagation
        result = await simulator.simulate_propagation(
            initial_seeds=["persona_0"], content_score=0.8, max_timesteps=3
        )

        # Check events were recorded
        assert len(simulator.propagation_history) > 0

        for event in simulator.propagation_history[:5]:
            assert isinstance(event, PropagationEvent)
            assert event.timestamp >= 0
            assert event.source_node in simulator.network_graph
            assert isinstance(event.target_nodes, list)
            assert 0 <= event.content_score <= 1.0
            assert 0 <= event.propagation_probability <= 1.0
            assert isinstance(event.actual_propagation, bool)
