"""Unit tests for PersonaGenerator class."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.persona_generator import PersonaGenerator
from src.core.types import PersonaAttributes, PersonalityType


class TestPersonaGenerator:
    """Test cases for PersonaGenerator."""

    @pytest.fixture
    def sample_article(self):
        """Sample article for testing."""
        return """
        # The Future of AI in Healthcare: A Revolutionary Approach

        Artificial Intelligence is transforming healthcare delivery in unprecedented ways.
        From diagnostic imaging to personalized treatment plans, AI algorithms are
        enhancing medical decision-making and patient outcomes.
        """

    @pytest.fixture
    def sample_analysis_results(self):
        """Sample analysis results."""
        return {
            "core_context": {
                "domain_analysis": {
                    "primary_domain": "healthcare",
                    "sub_domains": ["AI", "medical technology"],
                    "technical_complexity": 7,
                },
                "stakeholder_mapping": {
                    "beneficiaries": ["patients", "healthcare providers"],
                    "opponents": ["privacy advocates"],
                    "likely_sharers": [
                        "tech enthusiasts",
                        "medical professionals",
                    ],
                },
            },
            "hidden_dimensions": {
                "generational_perspectives": {
                    "gen_z": "Expects AI integration",
                    "boomers": "Concerns about human touch",
                }
            },
            "complexity_score": 0.8,
            "reach_potential": 0.7,
        }

    @pytest.fixture
    def sample_population_structure(self):
        """Sample population structure from PopulationArchitect."""
        return {
            "hierarchy": {
                "major_segments": [
                    {
                        "id": "early_adopters",
                        "name": "Healthcare Tech Early Adopters",
                        "percentage": 20,
                        "characteristics": [
                            "tech-savvy",
                            "innovation-seeking",
                        ],
                    },
                    {
                        "id": "medical_professionals",
                        "name": "Medical Professionals",
                        "percentage": 30,
                        "characteristics": [
                            "evidence-based",
                            "patient-focused",
                        ],
                    },
                ],
                "sub_segments": {
                    "early_adopters": [
                        {
                            "id": "tech_leaders",
                            "parent_segment": "early_adopters",
                            "percentage_of_parent": 40,
                        }
                    ]
                },
                "micro_clusters": {"tech_leaders": ["innovators", "influencers"]},
                "persona_slots": [
                    {
                        "id": "persona_0",
                        "major_segment": "early_adopters",
                        "sub_segment": "tech_leaders",
                        "micro_cluster": "innovators",
                        "network_position": {
                            "centrality": 0.7,
                            "clustering": 0.5,
                        },
                    },
                    {
                        "id": "persona_1",
                        "major_segment": "medical_professionals",
                        "sub_segment": None,
                        "micro_cluster": None,
                        "network_position": {
                            "centrality": 0.4,
                            "clustering": 0.6,
                        },
                    },
                ],
            },
            "network_topology": {
                "network_type": "small-world",
                "density": 0.3,
            },
            "influence_map": {
                "influencer_nodes": [{"id": "persona_0", "influence_score": 0.8}],
                "influence_paths": [],
            },
        }

    @pytest.fixture
    def generator(self):
        """Create a PersonaGenerator instance."""
        return PersonaGenerator()

    @pytest.mark.asyncio
    async def test_generate_personas_structure(
        self,
        sample_article,
        sample_analysis_results,
        sample_population_structure,
    ):
        """Test that generate_personas returns proper structure."""
        # Add hierarchy to analysis results for new implementation
        sample_analysis_results["hierarchy"] = sample_population_structure["hierarchy"]

        # Mock LLM response
        mock_llm_response = {
            "name": "Dr. Sarah Chen",
            "age": 32,
            "occupation": "Healthcare IT Director",
            "background": "Leading digital transformation in healthcare",
            "personality_traits": ["analytical", "pragmatic", "innovative", "collaborative"],
            "interests": ["AI", "healthcare innovation", "digital health"],
            "decision_factors": ["innovation potential", "evidence quality"],
            "article_relationship": {
                "relevance_score": 0.9,
                "interest_level": "high",
                "sharing_likelihood": 0.8,
                "discussion_points": ["AI implementation", "Patient safety"],
                "action_likelihood": 0.7,
            },
            "information_preferences": ["tech blogs", "medical journals"],
        }

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = json.dumps(mock_llm_response)
        mock_llm.ainvoke.return_value = mock_response

        with patch("src.agents.persona_generator.create_llm", return_value=mock_llm):
            generator = PersonaGenerator()

            result = await generator.generate_personas(
                article_content=sample_article,
                analysis_results=sample_analysis_results,
                count=1,
            )

            # Verify result is list of PersonaAttributes
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], PersonaAttributes)
            assert result[0].occupation == "Healthcare IT Director"
            assert result[0].age == 32

    @pytest.mark.asyncio
    async def test_generate_personas_with_multiple_slots(
        self, sample_article, sample_analysis_results, sample_population_structure
    ):
        """Test persona generation with multiple slots."""
        # Add hierarchy to analysis results
        sample_analysis_results["hierarchy"] = sample_population_structure["hierarchy"]

        # Mock different LLM responses for each persona
        mock_llm_responses = [
            {
                "name": "Dr. Sarah Chen",
                "age": 45,
                "occupation": "Emergency Medicine Physician",
                "background": "20 years in emergency medicine, early AI adopter",
                "personality_traits": ["analytical", "pragmatic", "innovative", "dedicated"],
                "interests": ["medical AI", "patient safety", "emergency protocols"],
                "decision_factors": ["evidence quality", "patient impact", "time efficiency"],
                "article_relationship": {
                    "relevance_score": 0.9,
                    "interest_level": "high",
                    "sharing_likelihood": 0.8,
                    "discussion_points": ["Clinical applications", "Safety protocols"],
                    "action_likelihood": 0.85,
                },
                "information_preferences": ["medical journals", "peer networks"],
            },
            {
                "name": "Dr. Alex Rodriguez",
                "age": 38,
                "occupation": "Chief Medical Information Officer",
                "background": "Physician turned healthcare technology executive",
                "personality_traits": ["visionary", "analytical", "collaborative", "strategic"],
                "interests": ["AI in healthcare", "digital transformation", "clinical workflow"],
                "decision_factors": ["innovation potential", "clinical evidence", "scalability"],
                "article_relationship": {
                    "relevance_score": 0.95,
                    "interest_level": "very high",
                    "sharing_likelihood": 0.9,
                    "discussion_points": ["Implementation challenges", "ROI metrics"],
                    "action_likelihood": 0.9,
                },
                "information_preferences": ["tech publications", "industry reports"],
            },
        ]

        response_iter = iter(mock_llm_responses)

        mock_llm = MagicMock()

        def mock_ainvoke(prompt):
            mock_response = MagicMock()
            mock_response.content = json.dumps(next(response_iter))
            return mock_response

        mock_llm.ainvoke = AsyncMock(side_effect=mock_ainvoke)

        with patch("src.agents.persona_generator.create_llm", return_value=mock_llm):
            generator = PersonaGenerator()

            result = await generator.generate_personas(
                article_content=sample_article,
                analysis_results=sample_analysis_results,
                count=2,
            )

            # Should generate 2 personas
            assert len(result) == 2
            assert all(isinstance(p, PersonaAttributes) for p in result)
            assert result[0].occupation == "Emergency Medicine Physician"
            assert result[1].occupation == "Chief Medical Information Officer"

    @pytest.mark.asyncio
    async def test_generate_single_persona_optimized(self):
        """Test single persona generation with optimized method."""
        article_summary = "AI transforms healthcare..."
        essential_context = {
            "domain": "healthcare",
            "complexity": 7,
            "stakeholders": ["doctors", "patients", "tech companies"],
        }
        persona_slot = {
            "id": "persona_0",
            "major_segment": "early_adopters",
            "network_position": {"type": "influencer", "centrality": 0.8},
        }
        segment_info = {
            "name": "Healthcare Tech Early Adopters",
            "characteristics": ["tech-savvy", "innovation-seeking", "forward-thinking"],
        }

        mock_response = {
            "name": "Dr. Alex Rodriguez",
            "age": 38,
            "occupation": "Chief Medical Information Officer",
            "background": "Physician turned healthcare technology executive",
            "personality_traits": ["visionary", "analytical", "collaborative", "strategic"],
            "interests": ["AI in healthcare", "digital transformation", "clinical workflow"],
            "decision_factors": ["innovation potential", "clinical evidence", "scalability"],
            "information_preferences": ["tech publications", "industry reports"],
            "article_relationship": {
                "relevance_score": 0.95,
                "interest_level": "very high",
                "sharing_likelihood": 0.9,
                "discussion_points": ["Implementation challenges", "ROI metrics"],
                "action_likelihood": 0.9,
            },
        }

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.content = json.dumps(mock_response)
        mock_llm.ainvoke.return_value = mock_response_obj

        with patch("src.agents.persona_generator.create_llm", return_value=mock_llm):
            generator = PersonaGenerator()

            result = await generator._generate_single_persona_optimized(
                article_summary, essential_context, persona_slot, segment_info
            )

            assert result["name"] == "Dr. Alex Rodriguez"
            assert result["age"] == 38
            assert "article_relationship" in result
            assert result["id"] == "persona_0"  # Should use slot id
            assert result["network_position"] == persona_slot["network_position"]

    def test_convert_to_persona_attributes(self, generator):
        """Test conversion to PersonaAttributes."""
        persona_data = {
            "id": "persona_0",
            "name": "Dr. Emma Wilson",
            "age": 42,
            "occupation": "Radiologist",
            "background": "Specialist in diagnostic imaging with AI research interest",
            "personality_traits": ["curious", "analytical", "organized"],
            "interests": [
                "medical imaging",
                "AI diagnostics",
                "patient safety",
            ],
            "decision_factors": ["accuracy", "evidence", "patient impact"],
            "information_preferences": [
                "medical journals",
                "news websites",
                "professional networks",
            ],
            "network_position": {"centrality": 0.7},
            "article_relationship": {
                "relevance_score": 0.8,
                "sharing_likelihood": 0.6,
            },
        }

        result = generator._convert_to_persona_attributes(persona_data)

        assert isinstance(result, PersonaAttributes)
        assert result.age == 42
        assert result.occupation == "Radiologist"
        assert "medical imaging" in result.interests
        # values field is not mapped in the new implementation
        assert result.values == []  # Empty by default

        # Network metrics from the new implementation
        assert result.network_centrality == 0.5  # Default value in implementation
        assert result.content_sharing_likelihood == 0.6
        # Influence score is from network_position.influence, defaults to 0.5
        assert result.influence_score == 0.5

        # Personality traits should be mapped to Big Five model with default values
        assert len(result.personality_traits) == 5  # All Big Five traits
        assert result.personality_traits[PersonalityType.OPENNESS] == 0.5

        # Preferred channels is empty by default in new implementation
        assert result.preferred_channels == []

    @pytest.mark.asyncio
    async def test_error_handling(self, sample_article, sample_analysis_results):
        """Test error handling in persona generation."""
        # Mock LLM to raise an exception
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM API error"))

        with patch("src.agents.persona_generator.create_llm", return_value=mock_llm):
            generator = PersonaGenerator()

            # Should handle error gracefully and return default personas
            result = await generator.generate_personas(
                article_content=sample_article,
                analysis_results=sample_analysis_results,
                count=5,
            )

            assert isinstance(result, list)
            assert len(result) == 5  # Should return default personas
            # Check that all are valid PersonaAttributes
            for persona in result:
                assert isinstance(persona, PersonaAttributes)
                assert persona.age >= 25
                assert persona.occupation is not None

    @pytest.mark.asyncio
    async def test_persona_count_compliance(self, sample_article, sample_analysis_results):
        """Test that correct number of personas are generated."""
        # Mock population with fewer slots than requested
        sample_analysis_results["hierarchy"] = {
            "major_segments": [
                {"id": "test", "name": "Test Segment", "characteristics": ["curious"]}
            ],
            "persona_slots": [
                {
                    "id": "persona_0",
                    "major_segment": "test",
                    "network_position": {"type": "central"},
                },
                {
                    "id": "persona_1",
                    "major_segment": "test",
                    "network_position": {"type": "peripheral"},
                },
            ],
        }

        # Mock LLM responses for the two available slots
        mock_response = {
            "name": "Test Person",
            "age": 30,
            "occupation": "Test Professional",
            "background": "Test background",
            "personality_traits": ["curious", "analytical", "open", "friendly"],
            "interests": ["testing", "technology", "innovation"],
            "decision_factors": ["quality", "reliability"],
            "article_relationship": {
                "relevance_score": 0.5,
                "interest_level": "medium",
                "sharing_likelihood": 0.5,
                "discussion_points": ["Point 1", "Point 2"],
                "action_likelihood": 0.5,
            },
            "information_preferences": ["online", "social media"],
        }

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.content = json.dumps(mock_response)
        mock_llm.ainvoke.return_value = mock_response_obj

        with patch("src.agents.persona_generator.create_llm", return_value=mock_llm):
            generator = PersonaGenerator()

            result = await generator.generate_personas(
                article_content=sample_article,
                analysis_results=sample_analysis_results,
                count=5,  # Request 5 but only 2 slots available
            )

            # Should generate 5 personas (2 from slots + 3 defaults)
            assert len(result) == 5
            assert all(isinstance(p, PersonaAttributes) for p in result)
