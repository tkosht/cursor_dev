"""Persona Generator - Hierarchical persona generation system coordinator.

This module coordinates the complete persona generation pipeline, integrating
DeepContextAnalyzer and PopulationArchitect to create detailed individual personas.
"""
import json
import logging
from typing import Dict, List, Any, Optional
import random

from src.agents.deep_context_analyzer import DeepContextAnalyzer
from src.agents.population_architect import PopulationArchitect
from src.core.types import PersonaAttributes, InformationChannel
from src.utils.llm_factory import create_llm
from src.utils.json_parser import parse_llm_json_response

logger = logging.getLogger(__name__)


class PersonaGenerator:
    """Coordinate hierarchical persona generation process."""
    
    def __init__(self):
        """Initialize the PersonaGenerator."""
        self.llm = create_llm()
        self.context_analyzer = DeepContextAnalyzer()
        self.population_architect = PopulationArchitect()
        
    async def generate_personas(
        self,
        article_content: str,
        analysis_results: Optional[Dict[str, Any]] = None,
        count: int = 50
    ) -> List[PersonaAttributes]:
        """Generate a list of detailed personas for article evaluation.
        
        Args:
            article_content: The article to generate personas for
            analysis_results: Optional pre-computed analysis results
            count: Target number of personas to generate
            
        Returns:
            List of PersonaAttributes objects representing individual personas
        """
        try:
            logger.info(f"Starting persona generation for {count} personas")
            
            # Stage 1: Analyze context (if not provided)
            if analysis_results is None:
                analysis_results = await self._analyze_context(article_content)
            
            # Stage 2: Design population structure
            population_structure = await self._design_population(analysis_results, target_size=count)
            
            # Stage 3: Generate individual personas
            personas = await self._generate_individual_personas(
                analysis_results, 
                population_structure
            )
            
            logger.info(f"Successfully generated {len(personas)} personas")
            return personas
            
        except Exception as e:
            logger.error(f"Error in persona generation: {e}")
            return []
    
    async def _analyze_context(self, article_content: str) -> Dict[str, Any]:
        """Analyze article context using DeepContextAnalyzer."""
        logger.info("Analyzing article context")
        return await self.context_analyzer.analyze_article_context(article_content)
    
    async def _design_population(
        self, 
        analysis_results: Dict[str, Any], 
        target_size: int
    ) -> Dict[str, Any]:
        """Design population structure using PopulationArchitect."""
        logger.info(f"Designing population structure for {target_size} personas")
        return await self.population_architect.design_population_hierarchy(
            analysis_results, 
            target_size=target_size
        )
    
    async def _generate_individual_personas(
        self,
        analysis_results: Dict[str, Any],
        population_structure: Dict[str, Any]
    ) -> List[PersonaAttributes]:
        """Generate individual personas from population structure."""
        logger.info("Generating individual personas")
        
        personas = []
        persona_slots = population_structure.get("hierarchy", {}).get("persona_slots", [])
        major_segments = population_structure.get("hierarchy", {}).get("major_segments", [])
        
        # Create segment lookup for easy access
        segment_lookup = {segment["id"]: segment for segment in major_segments}
        
        for slot in persona_slots:
            try:
                # Get segment information for this persona slot
                segment_info = segment_lookup.get(slot.get("major_segment"))
                if not segment_info:
                    logger.warning(f"No segment info found for slot {slot.get('id')}")
                    continue
                
                # Generate individual persona
                persona_data = await self._generate_single_persona(
                    slot, 
                    segment_info, 
                    analysis_results
                )
                
                # Convert to PersonaAttributes
                persona = self._convert_to_persona_attributes(persona_data)
                personas.append(persona)
                
            except Exception as e:
                logger.error(f"Error generating persona for slot {slot.get('id')}: {e}")
                continue
        
        return personas
    
    async def _generate_single_persona(
        self,
        persona_slot: Dict[str, Any],
        segment_info: Dict[str, Any],
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a single detailed persona."""
        
        # Extract context information
        domain = analysis_results.get("core_context", {}).get("domain_analysis", {})
        stakeholders = analysis_results.get("core_context", {}).get("stakeholder_mapping", {})
        cultural = analysis_results.get("core_context", {}).get("cultural_dimensions", {})
        hidden = analysis_results.get("hidden_dimensions", {})
        
        persona_prompt = f"""
        Generate a detailed, realistic persona based on these parameters:
        
        POPULATION SEGMENT:
        - Segment: {segment_info.get('name', 'Unknown')}
        - Characteristics: {segment_info.get('characteristics', [])}
        - Sub-segment: {persona_slot.get('sub_segment', 'None')}
        - Micro-cluster: {persona_slot.get('micro_cluster', 'None')}
        - Network position: {persona_slot.get('network_position', {})}
        
        ARTICLE CONTEXT:
        - Primary domain: {domain.get('primary_domain', 'General')}
        - Technical complexity: {domain.get('technical_complexity', 5)}/10
        - Cultural context: {cultural.get('social_context', 'Mainstream')}
        - Key stakeholders: {stakeholders.get('beneficiaries', [])}
        
        HIDDEN DIMENSIONS:
        {json.dumps(hidden, indent=2) if hidden else 'None'}
        
        Generate a JSON response with:
        {{
            "name": "Full name (realistic)",
            "age": 25-75,
            "occupation": "Specific job title",
            "background": "2-3 sentence background explaining their relationship to this topic",
            "personality_traits": ["trait1", "trait2", "trait3", "trait4"],
            "interests": ["interest1", "interest2", "interest3"],
            "decision_factors": ["What influences their decisions about information"],
            "information_preferences": ["Where/how they consume information"],
            "article_relationship": {{
                "relevance_score": 0.0-1.0,
                "interest_level": "low/medium/high/very high",
                "sharing_likelihood": 0.0-1.0,
                "discussion_points": ["What they'd discuss about this article"],
                "concerns": ["Any concerns or skepticism they'd have"],
                "action_likelihood": 0.0-1.0
            }}
        }}
        
        Make the persona SPECIFIC and REALISTIC. Avoid generic descriptions.
        Consider how their segment characteristics and network position influence their response.
        Include unexpected but believable details that make them memorable.
        """
        
        try:
            response = await self.llm.ainvoke(persona_prompt)
            persona_data = parse_llm_json_response(response.content)
            
            # Add slot metadata
            persona_data["id"] = persona_slot.get("id", f"persona_{random.randint(1000, 9999)}")
            persona_data["segment_id"] = persona_slot.get("major_segment")
            persona_data["network_position"] = persona_slot.get("network_position", {})
            
            return persona_data
            
        except Exception as e:
            logger.error(f"Error generating single persona: {e}")
            return self._create_fallback_persona(persona_slot, segment_info)
    
    def _create_fallback_persona(
        self, 
        persona_slot: Dict[str, Any], 
        segment_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a basic fallback persona when LLM generation fails."""
        names = [
            "Alex Johnson", "Taylor Smith", "Jordan Brown", "Casey Wilson",
            "Morgan Davis", "Riley Garcia", "Avery Miller", "Quinn Anderson"
        ]
        
        occupations = [
            "Professional", "Consultant", "Analyst", "Manager", 
            "Specialist", "Coordinator", "Administrator", "Executive"
        ]
        
        return {
            "id": persona_slot.get("id", f"persona_{random.randint(1000, 9999)}"),
            "name": random.choice(names),
            "age": random.randint(25, 65),
            "occupation": f"{segment_info.get('name', 'General')} {random.choice(occupations)}",
            "background": f"Professional with interest in {segment_info.get('name', 'various topics')}",
            "personality_traits": segment_info.get("characteristics", ["analytical", "curious"]),
            "interests": [segment_info.get('name', 'general topics')],
            "decision_factors": ["evidence", "relevance", "trustworthiness"],
            "information_preferences": ["professional networks", "industry publications"],
            "segment_id": persona_slot.get("major_segment"),
            "network_position": persona_slot.get("network_position", {}),
            "article_relationship": {
                "relevance_score": 0.5,
                "interest_level": "medium",
                "sharing_likelihood": 0.4,
                "discussion_points": ["General discussion"],
                "concerns": [],
                "action_likelihood": 0.3
            }
        }
    
    def _convert_to_persona_attributes(self, persona_data: Dict[str, Any]) -> PersonaAttributes:
        """Convert persona data to PersonaAttributes object."""
        # Calculate network metrics from article relationship and network position
        sharing_likelihood = persona_data.get("article_relationship", {}).get("sharing_likelihood", 0.5)
        network_centrality = persona_data.get("network_position", {}).get("centrality", 0.5)
        
        # Convert personality traits from list to dict with PersonalityType mapping
        personality_traits = {}
        traits_list = persona_data.get("personality_traits", [])
        if traits_list:
            # Simple mapping of traits to Big Five model
            trait_mapping = {
                "curious": "openness", "analytical": "openness", "creative": "openness",
                "organized": "conscientiousness", "responsible": "conscientiousness", 
                "outgoing": "extraversion", "social": "extraversion",
                "cooperative": "agreeableness", "empathetic": "agreeableness",
                "anxious": "neuroticism", "emotional": "neuroticism"
            }
            
            # Assign random scores for traits found in mapping
            for trait in traits_list:
                personality_type = trait_mapping.get(trait.lower())
                if personality_type:
                    personality_traits[personality_type] = random.uniform(0.6, 0.9)
        
        return PersonaAttributes(
            # Demographics
            age=persona_data.get("age", 35),
            occupation=persona_data.get("occupation", "Professional"),
            
            # Psychographics  
            interests=persona_data.get("interests", []),
            personality_traits=personality_traits,
            values=persona_data.get("decision_factors", []),
            
            # Behavioral patterns
            content_sharing_likelihood=min(max(sharing_likelihood, 0.0), 1.0),
            decision_making_style="analytical" if "analytical" in traits_list else "intuitive",
            
            # Network position
            network_centrality=min(max(network_centrality, 0.0), 1.0),
            influence_score=min(max((sharing_likelihood + network_centrality) / 2, 0.0), 1.0),
            
            # Preferences
            preferred_channels=self._map_to_information_channels(
                persona_data.get("information_preferences", [])
            )
        )
    
    def _map_to_information_channels(self, preferences: List[str]) -> List[InformationChannel]:
        """Map preference strings to InformationChannel enums."""
        channel_mapping = {
            "social": InformationChannel.SOCIAL_MEDIA,
            "news": InformationChannel.NEWS_WEBSITE,
            "email": InformationChannel.EMAIL,
            "word_of_mouth": InformationChannel.WORD_OF_MOUTH,
            "search": InformationChannel.SEARCH_ENGINE,
            "rss": InformationChannel.RSS_FEED,
            "social media": InformationChannel.SOCIAL_MEDIA,
            "news website": InformationChannel.NEWS_WEBSITE,
            "search engine": InformationChannel.SEARCH_ENGINE,
        }
        
        channels = []
        for pref in preferences:
            pref_lower = pref.lower()
            for key, channel in channel_mapping.items():
                if key in pref_lower:
                    channels.append(channel)
                    break
        
        # Default to NEWS_WEBSITE if no matches
        if not channels:
            channels.append(InformationChannel.NEWS_WEBSITE)
            
        return channels