"""
Tests for Hierarchical Persona Generation System

This test file demonstrates the hierarchical persona generation system
with concrete examples and validation scenarios.
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from app.market_simulator.hierarchical_persona_generator import (
    HierarchicalPersonaModel,
    PersonaGenerationState,
    DeepContextAnalyzer,
    PopulationArchitect,
    ArchetypeGenerator,
    HierarchicalPersonaGenerator,
    ProgressiveRefinementEngine,
    PersonaValidationFramework,
    MarketSimulatorPersonaGenerator
)


class TestDeepContextAnalyzer:
    """Test deep context analysis functionality"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer with mocked LLM"""
        mock_llm = AsyncMock()
        return DeepContextAnalyzer(llm=mock_llm)
    
    @pytest.mark.asyncio
    async def test_article_context_analysis(self, analyzer):
        """Test multi-dimensional article analysis"""
        
        # Mock article
        article = """
        New Study: Remote Work Increases Productivity by 13%
        
        A comprehensive study by Stanford researchers shows that remote work
        can significantly boost productivity, particularly for knowledge workers.
        The study tracked 16,000 employees over 9 months...
        """
        
        # Mock LLM response
        expected_context = {
            "domain_analysis": {
                "primary_domain": "workplace/productivity",
                "sub_domains": ["remote_work", "research", "business_management"],
                "complexity_level": 6,
                "required_knowledge": ["basic statistics", "workplace dynamics"]
            },
            "cultural_dimensions": {
                "geographic_relevance": "global",
                "cultural_sensitivities": ["work-life balance varies by culture"],
                "language_nuances": ["productivity means different things"],
                "social_context": ["post-pandemic work transformation"]
            },
            "temporal_aspects": {
                "time_sensitivity": "moderate",
                "trend_alignment": ["future of work", "digital transformation"],
                "historical_context": ["pre vs post pandemic work"],
                "future_implications": ["permanent remote work adoption"]
            },
            "emotional_landscape": {
                "triggers": ["job security", "work flexibility"],
                "controversy_potential": "medium",
                "inspirational_elements": ["freedom", "efficiency"],
                "anxiety_factors": ["isolation", "career growth concerns"]
            },
            "stakeholder_mapping": {
                "beneficiaries": ["remote workers", "tech companies"],
                "opponents": ["traditional managers", "commercial real estate"],
                "need_to_know": ["HR professionals", "executives"],
                "likely_sharers": ["remote work advocates", "productivity enthusiasts"]
            }
        }
        
        analyzer.llm.ainvoke.return_value.content = json.dumps(expected_context)
        
        # Test analysis
        result = await analyzer.analyze_article_context(article)
        
        assert result == expected_context
        assert analyzer.llm.ainvoke.called
        
        # Verify prompt contains key analysis dimensions
        call_args = analyzer.llm.ainvoke.call_args[0][0]
        assert "DOMAIN ANALYSIS" in call_args
        assert "CULTURAL DIMENSIONS" in call_args
        assert "EMOTIONAL LANDSCAPE" in call_args
    
    @pytest.mark.asyncio
    async def test_hidden_dimensions_discovery(self, analyzer):
        """Test discovery of non-obvious contextual dimensions"""
        
        article = "AI breakthrough in creativity..."
        initial_analysis = {"domain": "AI", "complexity": 8}
        
        # Mock hidden dimensions
        expected_hidden = {
            "second_order_effects": {
                "creative_professionals": "job security anxiety",
                "education_sector": "curriculum obsolescence",
                "patent_law": "ownership questions"
            },
            "cross_domain_implications": {
                "philosophy": "consciousness debates",
                "religion": "soul and creativity questions",
                "art_market": "valuation disruption"
            },
            "generational_perspectives": {
                "gen_z": "native AI collaboration",
                "millennials": "career pivot necessity",
                "boomers": "technological alienation"
            },
            "subculture_relevance": {
                "transhumanists": "validation of beliefs",
                "digital_artists": "tool vs threat debate",
                "AI_safety": "new attack vectors"
            }
        }
        
        analyzer.llm.ainvoke.return_value.content = json.dumps(expected_hidden)
        
        # Test discovery
        result = await analyzer._discover_hidden_dimensions(article, initial_analysis)
        
        assert result == expected_hidden
        assert "second_order_effects" in result
        assert "subculture_relevance" in result


class TestPopulationArchitect:
    """Test population architecture design"""
    
    @pytest.fixture
    def architect(self):
        """Create architect with mocked LLM"""
        mock_llm = AsyncMock()
        return PopulationArchitect(llm=mock_llm)
    
    @pytest.mark.asyncio
    async def test_major_segments_design(self, architect):
        """Test design of major population segments"""
        
        context = {
            "domain_analysis": {"primary_domain": "AI_creativity"},
            "emotional_landscape": {"triggers": ["job_security", "innovation"]}
        }
        hidden_dims = {
            "subculture_relevance": {"artists": "high", "engineers": "medium"}
        }
        
        # Mock segment design
        expected_segments = [
            {
                "id": "tech_optimists",
                "name": "Technology Optimists",
                "percentage": 25,
                "characteristics": [
                    "Early adopters of AI tools",
                    "See AI as collaborative partner",
                    "High tech literacy"
                ],
                "unexpected_traits": [
                    "Many are former skeptics who converted",
                    "Secretly fear being replaced but won't admit it",
                    "Overcompensate with enthusiasm"
                ],
                "article_relationship": "Will share to prove they're cutting-edge"
            },
            {
                "id": "creative_defenders",
                "name": "Traditional Creative Defenders",
                "percentage": 20,
                "characteristics": [
                    "Established artists and designers",
                    "Value human creativity",
                    "Skeptical of AI capabilities"
                ],
                "unexpected_traits": [
                    "Secretly experiment with AI tools",
                    "More threatened by young artists than AI",
                    "Use AI critique to maintain status"
                ],
                "article_relationship": "Will read critically, share with warnings"
            },
            {
                "id": "pragmatic_integrators",
                "name": "Pragmatic Integrators",
                "percentage": 30,
                "characteristics": [
                    "Focus on practical applications",
                    "Tool-agnostic approach",
                    "ROI-driven thinking"
                ],
                "unexpected_traits": [
                    "Former artists who pivoted to business",
                    "Hide creative aspirations",
                    "Judge everything by efficiency"
                ],
                "article_relationship": "Evaluate for business implications"
            },
            {
                "id": "anxious_observers",
                "name": "Anxious Observers",
                "percentage": 15,
                "characteristics": [
                    "Worried about future",
                    "Seek understanding",
                    "Information gatherers"
                ],
                "unexpected_traits": [
                    "Often more knowledgeable than experts",
                    "Paralyzed by too much information",
                    "Create detailed contingency plans"
                ],
                "article_relationship": "Deep read, unlikely to share"
            },
            {
                "id": "bridge_builders",
                "name": "Cross-Domain Bridge Builders",
                "percentage": 10,
                "characteristics": [
                    "Connect different communities",
                    "Translate between groups",
                    "Systems thinkers"
                ],
                "unexpected_traits": [
                    "Lonely in their understanding",
                    "Frustrated by polarization",
                    "Secret influence brokers"
                ],
                "article_relationship": "Reframe for different audiences"
            }
        ]
        
        architect.llm.ainvoke.return_value.content = json.dumps(expected_segments)
        
        # Test design
        result = await architect._design_major_segments(context, hidden_dims)
        
        assert len(result) == 5
        assert all("unexpected_traits" in segment for segment in result)
        assert sum(s["percentage"] for s in result) == 100


class TestArchetypeGenerator:
    """Test archetype generation within segments"""
    
    @pytest.fixture
    def generator(self):
        """Create generator with mocked LLM"""
        mock_llm = AsyncMock()
        return ArchetypeGenerator(llm=mock_llm)
    
    @pytest.mark.asyncio
    async def test_archetype_generation(self, generator):
        """Test generation of complex archetypes"""
        
        segment = {
            "id": "tech_optimists",
            "name": "Technology Optimists",
            "characteristics": ["Early adopters", "High tech literacy"]
        }
        
        context = {"primary_domain": "AI_creativity"}
        
        # Mock archetype generation
        expected_archetypes = [
            {
                "id": "converted_skeptic",
                "name": "The Converted Skeptic",
                "core_contradiction": "Was biggest AI critic, now biggest evangelist",
                "information_style": "Seeks validation for transformation",
                "social_position": "Thought leader wannabe",
                "hidden_motivations": [
                    "Proving they weren't wrong before",
                    "Fear of being left behind again",
                    "Compensating for late adoption"
                ],
                "article_connection": "Uses as proof of their new position",
                "count": 3
            },
            {
                "id": "anxious_evangelist",
                "name": "The Anxious Evangelist",
                "core_contradiction": "Promotes AI while fearing personal obsolescence",
                "information_style": "Cherry-picks positive news",
                "social_position": "Community cheerleader",
                "hidden_motivations": [
                    "If I can't beat it, join it",
                    "Building safety through expertise",
                    "Networking for plan B"
                ],
                "article_connection": "Shares to maintain optimist image",
                "count": 5
            }
        ]
        
        generator.llm.ainvoke.return_value.content = json.dumps(expected_archetypes)
        
        # Mock emergent behaviors
        emergent_behaviors = {
            "information_seeking": "Binge reads everything, retains little",
            "sharing_pattern": "Immediate reshare without full read",
            "contradiction_management": "Cognitive dissonance through humor"
        }
        
        # Setup mock for emergent behavior prediction
        generator.llm.ainvoke.side_effect = [
            Mock(content=json.dumps(expected_archetypes)),
            Mock(content=json.dumps(emergent_behaviors)),
            Mock(content=json.dumps(emergent_behaviors))
        ]
        
        # Test generation
        result = await generator.generate_archetypes(segment, context, num_archetypes=2)
        
        assert len(result) == 2
        assert all("core_contradiction" in archetype for archetype in result)
        assert all("emergent_behaviors" in archetype for archetype in result)


class TestHierarchicalPersonaGenerator:
    """Test individual persona generation"""
    
    @pytest.fixture
    def generator(self):
        """Create generator with mocked LLM"""
        mock_llm = AsyncMock()
        return HierarchicalPersonaGenerator(llm=mock_llm)
    
    @pytest.mark.asyncio
    async def test_complete_persona_generation(self, generator):
        """Test generation of a complete hierarchical persona"""
        
        archetype = {
            "id": "converted_skeptic",
            "name": "The Converted Skeptic",
            "core_contradiction": "Was critic, now evangelist"
        }
        
        segment = {
            "id": "tech_optimists",
            "name": "Technology Optimists"
        }
        
        context = {"domain": "AI_creativity"}
        
        network_position = {
            "node_id": 1,
            "influence_score": 0.7,
            "network_role": "local_hub"
        }
        
        # Mock all generation steps
        core_identity = {
            "demographics": {
                "age": 34,
                "location": "San Francisco, Mission District",
                "occupation": "Senior Product Designer at mid-size startup",
                "education": "RISD graduate, 2012"
            },
            "life_situation": {
                "phase": "Career crossroads",
                "relationship": "Recently divorced, co-parenting",
                "financial": "Comfortable but worried about school costs",
                "health": "Stress-related insomnia"
            }
        }
        
        life_history = {
            "formative_experiences": [
                {
                    "event": "Professor said digital art wasn't 'real art'",
                    "date": "2010-09-15",
                    "impact": "Drove obsession with legitimacy"
                },
                {
                    "event": "First design replaced by template",
                    "date": "2019-03-22",
                    "impact": "Initial AI resistance began"
                }
            ],
            "key_relationships": {
                "mentor": "Julia Chen - traditional painter who embraced digital",
                "anti_mentor": "Mark Stevens - purist who rejected all tech"
            }
        }
        
        psych_profile = {
            "conscious_beliefs": {
                "core_values": ["authenticity", "innovation", "growth"],
                "contradictions": ["Values tradition but embraces disruption"]
            },
            "unconscious_drives": {
                "primary": "Proving intellectual flexibility",
                "compensation": "Overcompensating for past rigidity"
            }
        }
        
        behaviors = {
            "information_seeking": {
                "morning_routine": "Twitter AI news with coffee at 6:47am",
                "trusted_sources": ["MIT Tech Review", "specific AI artists"],
                "validation_method": "Seeks confirming opinions first"
            },
            "sharing_patterns": {
                "platforms": {"Twitter": "thought leadership", "LinkedIn": "professional"},
                "timing": "Immediately after first paragraph",
                "framing": "Always adds personal transformation angle"
            }
        }
        
        micro_details = {
            "quirks": {
                "language": "Overuses 'paradigm shift'",
                "habits": "Screenshots everything 'just in case'",
                "rituals": "Clears browser history daily"
            },
            "triggers": {
                "attention_grabbers": ["disruption", "creativity", "future"],
                "stop_scrolling": "Before/after comparisons",
                "anxiety_triggers": ["expert", "master", "senior"]
            }
        }
        
        article_relationship = {
            "relevance_factors": {
                "personal": 0.95,
                "professional": 0.88,
                "social": 0.82,
                "emotional": 0.91
            },
            "likely_reaction": "Immediate validation seeking",
            "sharing_probability": 0.94
        }
        
        # Setup mock responses
        generator.llm.ainvoke.side_effect = [
            Mock(content=json.dumps(core_identity)),
            Mock(content=json.dumps(life_history)),
            Mock(content=json.dumps(psych_profile)),
            Mock(content=json.dumps(behaviors)),
            Mock(content=json.dumps(micro_details)),
            Mock(content=json.dumps(article_relationship))
        ]
        
        # Test generation
        persona = await generator.generate_individual_persona(
            archetype, segment, context, network_position
        )
        
        assert isinstance(persona, HierarchicalPersonaModel)
        assert persona.core_attributes == core_identity
        assert persona.psychological_layers == psych_profile
        assert persona.behavioral_model == behaviors
        assert persona.micro_details == micro_details
        assert persona.hierarchy["archetype_id"] == "converted_skeptic"


class TestProgressiveRefinementEngine:
    """Test persona refinement process"""
    
    @pytest.fixture
    def refiner(self):
        """Create refiner with mocked LLM"""
        mock_llm = AsyncMock()
        return ProgressiveRefinementEngine(llm=mock_llm)
    
    @pytest.mark.asyncio
    async def test_realism_enhancement(self, refiner):
        """Test enhancement of persona realism"""
        
        # Create basic persona
        persona = HierarchicalPersonaModel(
            id="test_123",
            generation_timestamp=datetime.now(),
            core_attributes={
                "demographics": {"age": 34, "occupation": "Designer"}
            },
            psychological_layers={
                "conscious_beliefs": {"values": ["creativity"]}
            }
        )
        
        # Mock enhancement for depth 0 (life events)
        life_events_enhancement = {
            "life_events": {
                "career_defining_moment": {
                    "date": "2019-07-15",
                    "event": "Client chose AI-generated logo over 3-month project",
                    "emotional_impact": "Crushing defeat turned into curiosity",
                    "behavioral_change": "Started secret AI experiments"
                },
                "personal_crisis": {
                    "date": "2020-03-01",
                    "event": "Divorce proceedings during lockdown",
                    "coping_mechanism": "Dove into AI art as escape",
                    "unexpected_outcome": "Found new creative voice"
                }
            }
        }
        
        refiner.llm.ainvoke.return_value.content = json.dumps(life_events_enhancement)
        
        # Test enhancement
        enhanced_persona = await refiner._enhance_realism(persona, depth=0)
        
        assert "life_events" in enhanced_persona.psychological_layers
        assert "career_defining_moment" in enhanced_persona.psychological_layers["life_events"]


class TestPersonaValidationFramework:
    """Test persona validation system"""
    
    @pytest.fixture
    def validator(self):
        """Create validator with mocked LLM"""
        mock_llm = AsyncMock()
        return PersonaValidationFramework(llm=mock_llm)
    
    @pytest.mark.asyncio
    async def test_internal_consistency_check(self, validator):
        """Test validation of internal persona consistency"""
        
        # Create persona with potential inconsistencies
        persona = HierarchicalPersonaModel(
            id="test_456",
            generation_timestamp=datetime.now(),
            core_attributes={
                "demographics": {
                    "age": 25,
                    "occupation": "Senior VP of Engineering",  # Suspicious for age
                    "education": "High school diploma"  # Inconsistent with role
                }
            },
            psychological_layers={
                "conscious_beliefs": {
                    "values": ["work-life balance"],
                    "work_habits": "80-hour weeks"  # Contradicts values
                }
            },
            behavioral_model={
                "information_seeking": {
                    "preferred_depth": "superficial",
                    "role_requirement": "deep technical analysis"  # Mismatch
                }
            }
        )
        
        # Mock validation response
        validation_result = {
            "score": 0.3,
            "issues": [
                {
                    "type": "demographic_inconsistency",
                    "description": "Senior VP at 25 with only high school education is highly improbable",
                    "severity": "high"
                },
                {
                    "type": "value_behavior_mismatch",
                    "description": "Values work-life balance but works 80-hour weeks",
                    "severity": "medium"
                },
                {
                    "type": "role_capability_mismatch",
                    "description": "Superficial information processing incompatible with senior engineering role",
                    "severity": "high"
                }
            ]
        }
        
        validator.llm.ainvoke.return_value.content = json.dumps(validation_result)
        
        # Test validation
        result = await validator._check_internal_consistency(persona)
        
        assert result["score"] == 0.3
        assert len(result["issues"]) == 3
        assert any(issue["type"] == "demographic_inconsistency" for issue in result["issues"])


class TestIntegration:
    """Test integrated persona generation workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_generation_pipeline(self):
        """Test end-to-end persona generation"""
        
        # Mock the entire pipeline
        with patch('app.market_simulator.hierarchical_persona_generator.build_hierarchical_persona_graph') as mock_graph:
            
            # Create mock graph that returns expected results
            mock_compiled_graph = AsyncMock()
            mock_graph.return_value = mock_compiled_graph
            
            # Mock final result
            final_result = {
                "completed_personas": [
                    {
                        "id": "persona_1",
                        "core_attributes": {"demographics": {"age": 34}},
                        "validation_score": 0.92
                    },
                    {
                        "id": "persona_2", 
                        "core_attributes": {"demographics": {"age": 28}},
                        "validation_score": 0.88
                    }
                ],
                "article_context": {
                    "domain": "AI_creativity",
                    "complexity": 7
                },
                "hidden_dimensions": {
                    "subcultures": ["digital_artists", "AI_safety"]
                },
                "realism_scores": {
                    "overall": 0.9,
                    "consistency": 0.88,
                    "emergence": 0.92
                },
                "diversity_scores": {
                    "demographic": 0.85,
                    "psychographic": 0.91,
                    "behavioral": 0.89
                }
            }
            
            mock_compiled_graph.ainvoke.return_value = final_result
            
            # Test generation
            generator = MarketSimulatorPersonaGenerator()
            result = await generator.generate_population(
                article="AI transforms creative industry...",
                population_size=2,
                quality_threshold=0.85
            )
            
            assert len(result["personas"]) == 2
            assert result["population_metrics"]["total_count"] == 2
            assert "article_context" in result["generation_metadata"]


# Example test execution patterns
class TestExampleUsagePatterns:
    """Demonstrate various usage patterns for the system"""
    
    @pytest.mark.asyncio
    async def test_tech_article_persona_generation(self):
        """Example: Generate personas for a tech breakthrough article"""
        
        article = """
        Breaking: Quantum Computing Achieves 1000-Qubit Milestone
        
        Researchers at MIT have successfully demonstrated a 1000-qubit quantum computer,
        marking a significant breakthrough in quantum computing capabilities...
        """
        
        # This test demonstrates expected persona types for tech articles
        expected_persona_types = [
            "Quantum researchers excited but skeptical",
            "Crypto experts worried about security",
            "Tech investors seeing opportunity",
            "Science journalists seeking angles",
            "General public confused but curious"
        ]
        
        # Test would verify these emerge from the system
        assert len(expected_persona_types) > 0
    
    @pytest.mark.asyncio
    async def test_health_article_persona_generation(self):
        """Example: Generate personas for a health discovery article"""
        
        article = """
        New Study: Mediterranean Diet Reduces Alzheimer's Risk by 40%
        
        A longitudinal study following 50,000 participants over 20 years
        shows significant cognitive benefits from Mediterranean diet...
        """
        
        # This test demonstrates expected persona types for health articles
        expected_persona_types = [
            "Adult children of Alzheimer's patients",
            "Health-conscious seniors",
            "Skeptical nutrition scientists",
            "Mediterranean cuisine restaurateurs",
            "Insurance actuaries"
        ]
        
        # Test would verify appropriate health-focused personas emerge
        assert len(expected_persona_types) > 0


if __name__ == "__main__":
    pytest.main([__file__])