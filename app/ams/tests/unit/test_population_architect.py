"""Unit tests for PopulationArchitect class."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

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
        self, sample_context
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

        # Mock LLM responses
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock()
        
        # Response for major segments (direct array, not nested)
        major_response = MagicMock()
        major_response.content = json.dumps(mock_segments)
        
        # Responses for sub-segments (one for each major segment)
        sub_responses = []
        for segment in mock_segments:
            sub_response = MagicMock()
            sub_response.content = json.dumps([
                {
                    "id": f"{segment['id']}_sub1",
                    "name": f"{segment['id']}_sub1",
                    "percentage_of_segment": 60,
                    "characteristics": ["sub-trait1", "sub-trait2"]
                },
                {
                    "id": f"{segment['id']}_sub2",
                    "name": f"{segment['id']}_sub2",
                    "percentage_of_segment": 40,
                    "characteristics": ["sub-trait3", "sub-trait4"]
                }
            ])
            sub_responses.append(sub_response)
        
        # Set up side_effect to return different responses
        mock_llm.ainvoke.side_effect = [major_response] + sub_responses
        
        with patch('src.agents.population_architect.create_llm', return_value=mock_llm):
            architect = PopulationArchitect()
            
            result = await architect.design_population_hierarchy(
                sample_context, target_size=10
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
            
            # Verify major segments were created
            assert len(hierarchy["major_segments"]) == 3
            assert hierarchy["major_segments"][0]["id"] == "early_adopters"

    @pytest.mark.asyncio
    async def test_design_major_segments(self):
        """Test major segment design."""
        # Direct array, not nested under "major_segments"
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

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.content = json.dumps(mock_response)
        mock_llm.ainvoke.return_value = mock_response_obj

        with patch('src.agents.population_architect.create_llm', return_value=mock_llm):
            architect = PopulationArchitect()
            
            # Create essential context matching _extract_essential_context
            essential_context = {
                "domain": "healthcare",
                "complexity": 7,
                "stakeholders": ["patients", "providers", "tech companies"],
                "emotional_tone": "medium",
                "time_sensitivity": "medium",
                "complexity_score": 0.5,
                "reach_potential": 0.5
            }
            
            segments = await architect._design_major_segments(essential_context)

            assert len(segments) == 2
            assert segments[0]["id"] == "tech_evangelists"
            # Percentages should be normalized to sum to 100
            assert segments[0]["percentage"] == 25  # 10/(10+30)*100
            assert segments[1]["percentage"] == 75  # 30/(10+30)*100
            assert "unexpected_traits" in segments[0]

    @pytest.mark.asyncio
    async def test_design_sub_segments_for_one(self):
        """Test sub-segment design for a single major segment."""
        major_segment = {
            "id": "medical_professionals",
            "name": "Medical Professionals",
            "percentage": 25,
            "characteristics": ["evidence-based", "patient-focused"]
        }
        
        essential_context = {
            "domain": "healthcare",
            "complexity": 7
        }

        # Direct array for sub-segments
        mock_response = [
            {
                "id": "young_doctors",
                "name": "young_doctors",
                "characteristics": ["Digital natives", "Research-oriented"],
                "percentage_of_segment": 40,
            },
            {
                "id": "veteran_specialists",
                "name": "veteran_specialists",
                "characteristics": ["Experience-based", "Cautious adopters"],
                "percentage_of_segment": 60,
            },
        ]

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.content = json.dumps(mock_response)
        mock_llm.ainvoke.return_value = mock_response_obj

        with patch('src.agents.population_architect.create_llm', return_value=mock_llm):
            architect = PopulationArchitect()
            
            sub_segments = await architect._design_sub_segments_for_one(
                major_segment, essential_context
            )

            assert len(sub_segments) == 2
            assert sub_segments[0]["id"] == "young_doctors"
            assert sub_segments[0]["name"] == "young_doctors"
            assert sub_segments[1]["percentage_of_segment"] == 60

    def test_allocate_persona_slots(self, architect):
        """Test persona slot allocation across segments."""
        major_segments = [
            {"id": "early_adopters", "percentage": 20},
            {"id": "mainstream", "percentage": 50},
            {"id": "laggards", "percentage": 30},
        ]

        sub_segments = {
            "early_adopters": [
                {"id": "tech_leaders", "parent_segment": "early_adopters", "percentage_of_parent": 30},
                {"id": "innovators", "parent_segment": "early_adopters", "percentage_of_parent": 70},
            ],
            "mainstream": [
                {"id": "pragmatists", "parent_segment": "mainstream", "percentage_of_parent": 60},
                {"id": "followers", "parent_segment": "mainstream", "percentage_of_parent": 40},
            ],
            "laggards": [{"id": "skeptics", "parent_segment": "laggards", "percentage_of_parent": 100}],
        }

        # Micro clusters should be dicts with proper structure
        micro_clusters = {
            "early_adopters": [
                {"id": "tech_leaders_cluster_0", "name": "Tech Leaders Group 1", "size": 1},
                {"id": "innovators_cluster_0", "name": "Innovators Group 1", "size": 2}
            ],
            "mainstream": [
                {"id": "pragmatists_cluster_0", "name": "Pragmatists Group 1", "size": 1},
                {"id": "followers_cluster_0", "name": "Followers Group 1", "size": 2}
            ],
            "laggards": [
                {"id": "skeptics_cluster_0", "name": "Skeptics Group 1", "size": 1}
            ]
        }

        slots = architect._allocate_persona_slots(
            major_segments, sub_segments, micro_clusters, target_size=100
        )

        # Check total allocation
        assert len(slots) == 100

        # Check distribution roughly matches percentages
        early_adopter_count = sum(
            1 for s in slots if s["major_segment"] == "early_adopters"
        )
        assert 15 <= early_adopter_count <= 25  # Allow some variance

        # Check that all slots have required fields
        for slot in slots:
            assert "id" in slot
            assert "major_segment" in slot
            assert "network_position" in slot

    def test_design_network_topology(self, architect):
        """Test network topology design."""
        persona_slots = [
            {"id": f"persona_{i}", "major_segment": "test", "network_position": {"type": "hub" if i == 0 else "active"}} 
            for i in range(10)
        ]

        result = architect._design_network_topology(persona_slots)

        assert "type" in result
        assert "density" in result
        assert "clustering_coefficient" in result
        assert "hub_nodes" in result
        assert "average_path_length" in result
        
        # Check network type matches implementation
        assert result["type"] == "scale-free"
        assert result["hub_nodes"] == 1  # Only one hub in our test data

    def test_design_influence_patterns(self, architect):
        """Test influence pattern design."""
        persona_slots = [
            {
                "id": "persona_0",
                "major_segment": "early_adopters",
                "network_position": {"type": "hub", "influence": 0.9}
            },
            {
                "id": "persona_1",
                "major_segment": "mainstream",
                "network_position": {"type": "connector", "influence": 0.7}
            },
            {
                "id": "persona_2",
                "major_segment": "laggards",
                "network_position": {"type": "peripheral", "influence": 0.3}
            },
            {
                "id": "persona_5",
                "major_segment": "mainstream",
                "network_position": {"type": "active", "influence": 0.5}
            },
            {
                "id": "persona_6",
                "major_segment": "mainstream",
                "network_position": {"type": "active", "influence": 0.5}
            },
        ]

        result = architect._design_influence_patterns(persona_slots)

        assert "influencer_nodes" in result
        assert "influence_paths" in result
        assert "cascade_probability" in result
        
        # Check that high influence nodes are identified as influencers (> 0.7)
        assert "persona_0" in result["influencer_nodes"]
        # persona_1 has exactly 0.7, but implementation checks for > 0.7
        assert len(result["influencer_nodes"]) == 1
        assert len(result["influence_paths"]) == 1  # Min of 3 and number of influencers

    def test_design_micro_clusters(self, architect):
        """Test micro cluster design."""
        major_segments = [
            {"id": "early_adopters", "percentage": 30},
            {"id": "mainstream", "percentage": 70},
        ]
        
        sub_segments = {
            "early_adopters": [
                {"id": "tech_leaders", "name": "Tech Leaders"},
                {"id": "innovators", "name": "Innovators"},
            ],
            "mainstream": [
                {"id": "pragmatists", "name": "Pragmatists"},
            ],
        }
        
        target_size = 50

        result = architect._design_micro_clusters(
            major_segments, sub_segments, target_size
        )

        # Check that micro clusters were created for segments, not sub-segments
        assert "early_adopters" in result
        assert "mainstream" in result
        
        # Check structure of micro clusters
        for segment_id, clusters in result.items():
            assert isinstance(clusters, list)
            assert len(clusters) >= 1
            for cluster in clusters:
                assert "id" in cluster
                assert "name" in cluster
                assert "size" in cluster
                assert "sub_segment_id" in cluster

    def test_assign_network_position(self, architect):
        """Test network position assignment."""
        # Test hub position (index 0)
        position = architect._assign_network_position(0, 10)
        assert position["type"] == "hub"
        assert position["influence"] == 0.9
        
        # Test connector position (index 1, < 20% of total)
        position = architect._assign_network_position(1, 10)
        assert position["type"] == "connector"
        assert position["influence"] == 0.7
        
        # Test active position (index 3, < 50% of total)
        position = architect._assign_network_position(3, 10)
        assert position["type"] == "active"
        assert position["influence"] == 0.5
        
        # Test peripheral position (index 8, >= 50% of total)
        position = architect._assign_network_position(8, 10)
        assert position["type"] == "peripheral"
        assert position["influence"] == 0.3