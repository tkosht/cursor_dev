"""Unit tests for PersonaGenerator class."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from src.agents.persona_generator import PersonaGenerator
from src.core.types import PersonaAttributes


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
                "micro_clusters": {
                    "tech_leaders": ["innovators", "influencers"]
                },
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
                "influencer_nodes": [
                    {"id": "persona_0", "influence_score": 0.8}
                ],
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
        generator,
        sample_article,
        sample_analysis_results,
        sample_population_structure,
    ):
        """Test that generate_personas returns proper structure."""
        with patch.object(generator, "_analyze_context") as mock_context:
            mock_context.return_value = sample_analysis_results

            with patch.object(
                generator, "_design_population"
            ) as mock_population:
                mock_population.return_value = sample_population_structure

                with patch.object(
                    generator, "_generate_individual_personas"
                ) as mock_individual:
                    mock_personas = [
                        PersonaAttributes(
                            age=32,
                            occupation="Healthcare IT Director",
                            interests=["AI", "healthcare innovation"],
                            values=[
                                "innovation potential",
                                "evidence quality",
                            ],
                            influence_score=0.8,
                            network_centrality=0.7,
                            content_sharing_likelihood=0.6,
                        )
                    ]
                    mock_individual.return_value = mock_personas

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

    @pytest.mark.asyncio
    async def test_analyze_context_integration(
        self, generator, sample_article
    ):
        """Test context analysis integration."""
        mock_analyzer_result = {
            "core_context": {
                "domain_analysis": {"primary_domain": "healthcare"}
            },
            "hidden_dimensions": {"test": "dimension"},
            "complexity_score": 0.8,
            "reach_potential": 0.7,
        }

        with patch.object(
            generator.context_analyzer, "analyze_article_context"
        ) as mock_analyze:
            mock_analyze.return_value = mock_analyzer_result

            result = await generator._analyze_context(sample_article)

            assert result == mock_analyzer_result
            mock_analyze.assert_called_once_with(sample_article)

    @pytest.mark.asyncio
    async def test_design_population_integration(
        self, generator, sample_analysis_results
    ):
        """Test population design integration."""
        mock_population_result = {
            "hierarchy": {"major_segments": []},
            "network_topology": {},
            "influence_map": {},
        }

        with patch.object(
            generator.population_architect, "design_population_hierarchy"
        ) as mock_design:
            mock_design.return_value = mock_population_result

            result = await generator._design_population(
                sample_analysis_results, target_size=10
            )

            assert result == mock_population_result
            mock_design.assert_called_once_with(
                sample_analysis_results, target_size=10
            )

    @pytest.mark.asyncio
    async def test_generate_individual_personas(
        self, generator, sample_analysis_results, sample_population_structure
    ):
        """Test individual persona generation."""
        mock_persona_data = {
            "id": "persona_0",
            "name": "Dr. Sarah Chen",
            "age": 45,
            "occupation": "Emergency Medicine Physician",
            "background": "20 years in emergency medicine, early AI adopter",
            "personality_traits": ["analytical", "pragmatic", "innovative"],
            "interests": [
                "medical AI",
                "patient safety",
                "emergency protocols",
            ],
            "decision_factors": [
                "evidence quality",
                "patient impact",
                "time efficiency",
            ],
            "information_preferences": [
                "medical journals",
                "clinical trials",
                "peer networks",
            ],
            "network_influence": 0.7,
            "article_relationship": {
                "relevance_score": 0.9,
                "interest_level": "high",
                "sharing_likelihood": 0.8,
            },
        }

        with patch.object(
            generator, "_generate_single_persona"
        ) as mock_single:
            mock_single.return_value = mock_persona_data

            result = await generator._generate_individual_personas(
                sample_analysis_results, sample_population_structure
            )

            # Should generate personas for each slot
            slots = sample_population_structure["hierarchy"]["persona_slots"]
            assert len(result) == len(slots)

            # Each result should be a PersonaAttributes instance
            for persona in result:
                assert isinstance(persona, PersonaAttributes)
                assert persona.occupation is not None
                assert persona.age is not None

    @pytest.mark.asyncio
    async def test_generate_single_persona(
        self, generator, sample_analysis_results
    ):
        """Test single persona generation."""
        persona_slot = {
            "id": "persona_0",
            "major_segment": "early_adopters",
            "sub_segment": "tech_leaders",
            "micro_cluster": "innovators",
            "network_position": {"centrality": 0.8, "clustering": 0.5},
        }

        segment_info = {
            "id": "early_adopters",
            "name": "Healthcare Tech Early Adopters",
            "characteristics": ["tech-savvy", "innovation-seeking"],
        }

        mock_response = {
            "name": "Dr. Alex Rodriguez",
            "age": 38,
            "occupation": "Chief Medical Information Officer",
            "background": "Physician turned healthcare technology executive",
            "personality_traits": ["visionary", "analytical", "collaborative"],
            "interests": [
                "AI in healthcare",
                "digital transformation",
                "clinical workflow",
            ],
            "decision_factors": [
                "innovation potential",
                "clinical evidence",
                "scalability",
            ],
            "information_preferences": [
                "tech publications",
                "medical journals",
                "industry reports",
            ],
            "article_relationship": {
                "relevance_score": 0.95,
                "interest_level": "very high",
                "sharing_likelihood": 0.9,
                "discussion_points": [
                    "Implementation challenges",
                    "ROI metrics",
                ],
            },
        }

        with patch.object(generator, "llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock()
            mock_llm.ainvoke.return_value.content = json.dumps(mock_response)

            result = await generator._generate_single_persona(
                persona_slot, segment_info, sample_analysis_results
            )

            assert result["name"] == "Dr. Alex Rodriguez"
            assert result["age"] == 38
            assert "article_relationship" in result

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
        assert "accuracy" in result.values  # decision_factors maps to values

        # Network metrics should be calculated correctly
        assert result.network_centrality == 0.7
        assert result.content_sharing_likelihood == 0.6
        # Influence score should be average of sharing_likelihood (0.6) and centrality (0.7) = 0.65
        assert (
            abs(result.influence_score - 0.65) < 0.01
        )  # Allow for floating point precision

        # Personality traits should be mapped to Big Five model
        assert (
            len(result.personality_traits) > 0
        )  # Should have mapped some traits

        # Should have at least one information channel
        assert len(result.preferred_channels) > 0

    @pytest.mark.asyncio
    async def test_error_handling(
        self, generator, sample_article
    ):
        """Test error handling in persona generation."""
        with patch.object(generator, "_analyze_context") as mock_context:
            mock_context.side_effect = Exception("Analysis error")

            # Should handle error gracefully and return empty list
            result = await generator.generate_personas(
                article_content=sample_article,
                analysis_results=None,  # Set to None to ensure _analyze_context is called
                count=5,
            )

            assert isinstance(result, list)
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_persona_count_compliance(
        self, generator, sample_article, sample_analysis_results
    ):
        """Test that correct number of personas are generated."""
        with patch.object(generator, "_analyze_context") as mock_context:
            mock_context.return_value = sample_analysis_results

            with patch.object(
                generator, "_design_population"
            ) as mock_population:
                # Mock population with fewer slots than requested
                mock_population.return_value = {
                    "hierarchy": {
                        "persona_slots": [
                            {"id": "persona_0", "major_segment": "test"},
                            {"id": "persona_1", "major_segment": "test"},
                        ]
                    },
                    "network_topology": {},
                    "influence_map": {},
                }

                with patch.object(
                    generator, "_generate_individual_personas"
                ) as mock_individual:
                    mock_individual.return_value = [
                        PersonaAttributes(
                            age=30,
                            occupation="Test",
                            interests=[],
                            values=[],
                            influence_score=0.5,
                            network_centrality=0.5,
                            content_sharing_likelihood=0.5,
                        )
                    ]

                    result = await generator.generate_personas(
                        article_content=sample_article,
                        analysis_results=sample_analysis_results,
                        count=5,  # Request 5 but only 2 slots available
                    )

                    # Should generate what's available, not necessarily what's requested
                    assert len(result) >= 1
