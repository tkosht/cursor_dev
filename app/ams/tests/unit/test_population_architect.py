"""Unit tests for PopulationArchitect class."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from src.agents.population_architect import PopulationArchitect


class TestPopulationArchitect:
    """Test cases for PopulationArchitect."""

    @pytest.fixture
    def sample_context(self):
        """Sample context for testing."""
        return {
            "core_context": {
                "domain_analysis": {
                    "primary_domain": "healthcare",
                    "sub_domains": ["AI", "diagnostics"],
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
        }

    @pytest.fixture
    def architect(self):
        """Create a PopulationArchitect instance."""
        return PopulationArchitect()

    @pytest.mark.asyncio
    async def test_design_population_hierarchy_structure(
        self, architect, sample_context
    ):
        """Test that design_population_hierarchy returns proper structure."""
        # Mock major segments response
        mock_segments = [
            {
                "id": "early_adopters",
                "name": "Healthcare Tech Early Adopters",
                "percentage": 15,
                "characteristics": ["tech-savvy", "innovation-seeking"],
                "relationship_to_article": "Primary audience",
            },
            {
                "id": "medical_professionals",
                "name": "Medical Professionals",
                "percentage": 25,
                "characteristics": ["evidence-based", "patient-focused"],
                "relationship_to_article": "Implementation stakeholders",
            },
            {
                "id": "skeptics",
                "name": "AI Healthcare Skeptics",
                "percentage": 20,
                "characteristics": ["privacy-conscious", "traditional"],
                "relationship_to_article": "Critical audience",
            },
        ]

        with patch.object(architect, "_design_major_segments") as mock_design:
            mock_design.return_value = mock_segments

            # Mock other design methods
            with patch.object(architect, "_design_sub_segments") as mock_sub:
                mock_sub.return_value = {"subcategories": ["junior", "senior"]}

                with patch.object(
                    architect, "_design_micro_clusters"
                ) as mock_micro:
                    mock_micro.return_value = {
                        "clusters": ["innovators", "pragmatists"]
                    }

                    with patch.object(
                        architect, "_allocate_persona_slots"
                    ) as mock_slots:
                        mock_slots.return_value = [
                            {"slot": i} for i in range(50)
                        ]

                        with patch.object(
                            architect, "_design_network_topology"
                        ) as mock_network:
                            mock_network.return_value = {
                                "type": "small-world",
                                "density": 0.3,
                            }

                            with patch.object(
                                architect, "_design_influence_patterns"
                            ) as mock_influence:
                                mock_influence.return_value = {
                                    "influencers": ["tech_leaders"]
                                }

                                result = await architect.design_population_hierarchy(
                                    sample_context, target_size=50
                                )

        # Verify structure
        assert "hierarchy" in result
        assert "network_topology" in result
        assert "influence_map" in result

        hierarchy = result["hierarchy"]
        assert "major_segments" in hierarchy
        assert "sub_segments" in hierarchy
        assert "micro_clusters" in hierarchy
        assert "persona_slots" in hierarchy

    @pytest.mark.asyncio
    async def test_design_major_segments(self, architect, sample_context):
        """Test major segment design."""
        mock_response = [
            {
                "id": "tech_evangelists",
                "name": "Healthcare Tech Evangelists",
                "percentage": 10,
                "characteristics": [
                    "Early technology adopters",
                    "Active in tech communities",
                    "Share success stories",
                ],
                "relationship_to_article": "Champions and amplifiers",
                "unexpected_traits": ["Often have personal health stories"],
            },
            {
                "id": "cautious_practitioners",
                "name": "Cautious Medical Practitioners",
                "percentage": 30,
                "characteristics": [
                    "Evidence-based decision makers",
                    "Patient safety focused",
                    "Gradual adoption approach",
                ],
                "relationship_to_article": "Evaluators and gatekeepers",
                "unexpected_traits": ["Secretly excited about AI potential"],
            },
        ]

        with patch.object(architect, "llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock()
            mock_llm.ainvoke.return_value.content = json.dumps(mock_response)

            segments = await architect._design_major_segments(sample_context)

            assert len(segments) == 2
            assert segments[0]["id"] == "tech_evangelists"
            # Percentages are normalized to sum to 100
            assert segments[1]["percentage"] == 75  # 30/(10+30)*100
            assert "unexpected_traits" in segments[0]

    @pytest.mark.asyncio
    async def test_design_sub_segments(self, architect, sample_context):
        """Test sub-segment design within major segments."""
        major_segment = {
            "id": "medical_professionals",
            "name": "Medical Professionals",
            "percentage": 25,
        }

        mock_response = [
            {
                "id": "young_doctors",
                "parent_segment": "medical_professionals",
                "characteristics": ["Digital natives", "Research-oriented"],
                "percentage_of_parent": 40,
            },
            {
                "id": "veteran_specialists",
                "parent_segment": "medical_professionals",
                "characteristics": ["Experience-based", "Cautious adopters"],
                "percentage_of_parent": 60,
            },
        ]

        with patch.object(architect, "llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock()
            mock_llm.ainvoke.return_value.content = json.dumps(mock_response)

            sub_segments = await architect._design_sub_segments(
                major_segment, sample_context
            )

            assert len(sub_segments) == 2
            assert sub_segments[0]["id"] == "young_doctors"
            assert sub_segments[1]["percentage_of_parent"] == 60

    @pytest.mark.asyncio
    async def test_allocate_persona_slots(self, architect):
        """Test persona slot allocation across segments."""
        major_segments = [
            {"id": "early_adopters", "percentage": 20},
            {"id": "mainstream", "percentage": 50},
            {"id": "laggards", "percentage": 30},
        ]

        sub_segments = {
            "early_adopters": [
                {"id": "tech_leaders", "percentage_of_parent": 30},
                {"id": "innovators", "percentage_of_parent": 70},
            ],
            "mainstream": [
                {"id": "pragmatists", "percentage_of_parent": 60},
                {"id": "followers", "percentage_of_parent": 40},
            ],
            "laggards": [{"id": "skeptics", "percentage_of_parent": 100}],
        }

        micro_clusters = {
            "tech_leaders": ["influencer", "educator"],
            "innovators": ["experimenter", "early_user"],
        }

        slots = await architect._allocate_persona_slots(
            major_segments, sub_segments, micro_clusters, target_size=100
        )

        # Check total allocation
        assert len(slots) == 100

        # Check distribution roughly matches percentages
        early_adopter_count = sum(
            1 for s in slots if s["major_segment"] == "early_adopters"
        )
        assert 15 <= early_adopter_count <= 25  # Allow some variance

    @pytest.mark.asyncio
    async def test_design_network_topology(self, architect):
        """Test network topology design."""
        persona_slots = [
            {
                "id": f"persona_{i}",
                "major_segment": "early_adopters" if i < 20 else "mainstream",
            }
            for i in range(50)
        ]

        topology = architect._design_network_topology(persona_slots)

        assert "network_type" in topology
        assert "connections" in topology
        assert "density" in topology
        assert "clustering_coefficient" in topology

        # Check reasonable values
        assert 0 < topology["density"] < 1
        assert topology["network_type"] in [
            "small-world",
            "scale-free",
            "random",
            "hierarchical",
        ]

    @pytest.mark.asyncio
    async def test_design_influence_patterns(self, architect):
        """Test influence pattern design."""
        persona_slots = [
            {
                "id": f"persona_{i}",
                "major_segment": "early_adopters" if i < 10 else "mainstream",
                "sub_segment": "tech_leaders" if i < 5 else "followers",
                "micro_cluster": (
                    "influencers"
                    if i < 3
                    else "connectors" if i < 6 else "followers"
                ),
            }
            for i in range(30)
        ]

        influence_map = architect._design_influence_patterns(persona_slots)

        assert "influencer_nodes" in influence_map
        assert "influence_paths" in influence_map
        assert "influence_strength" in influence_map

        # Check that some personas are marked as influencers
        assert len(influence_map["influencer_nodes"]) > 0
        # Not everyone is an influencer
        assert len(influence_map["influencer_nodes"]) < len(persona_slots)

    @pytest.mark.asyncio
    async def test_calculate_network_position(self, architect):
        """Test network position calculation for personas."""
        position = architect._calculate_network_position(5, {"count": 20})

        assert "centrality" in position
        assert "clustering" in position
        assert "bridge_score" in position

        # Values should be between 0 and 1
        assert 0 <= position["centrality"] <= 1
        assert 0 <= position["clustering"] <= 1
        assert 0 <= position["bridge_score"] <= 1

    @pytest.mark.asyncio
    async def test_error_handling(self, architect, sample_context):
        """Test error handling in population design."""
        with patch.object(architect, "llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock()
            mock_llm.ainvoke.side_effect = Exception("LLM API Error")

            # Should handle error gracefully
            result = await architect.design_population_hierarchy(
                sample_context
            )

            # Should return valid structure even on error
            assert "hierarchy" in result
            assert "network_topology" in result
            assert "influence_map" in result

            # Should have empty/default values
            assert result["hierarchy"]["major_segments"] == []
