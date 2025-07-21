"""
Hierarchical Persona Generation System - Core Implementation

This module implements the hierarchical persona generation system for creating
extremely realistic, high-resolution personas through progressive refinement.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, TypedDict
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import hashlib

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import Send, Command


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class HierarchicalPersonaModel:
    """Complete hierarchical persona representation with multiple layers of detail"""
    
    # Level 0: Identity
    id: str
    generation_timestamp: datetime
    
    # Level 1: Hierarchical Position
    hierarchy: Dict[str, Any] = field(default_factory=lambda: {
        "segment_id": None,
        "sub_segment_id": None,
        "archetype_id": None,
        "micro_cluster_id": None
    })
    
    # Level 2: Core Attributes
    core_attributes: Dict[str, Any] = field(default_factory=lambda: {
        "demographics": {},
        "psychographics": {},
        "life_stage": {},
        "social_position": {}
    })
    
    # Level 3: Deep Psychology
    psychological_layers: Dict[str, Any] = field(default_factory=lambda: {
        "conscious_beliefs": {},
        "unconscious_drives": {},
        "cognitive_patterns": {},
        "emotional_patterns": {},
        "defense_mechanisms": {}
    })
    
    # Level 4: Behavioral Patterns
    behavioral_model: Dict[str, Any] = field(default_factory=lambda: {
        "information_seeking": {},
        "decision_making": {},
        "social_interaction": {},
        "content_sharing": {},
        "influence_response": {}
    })
    
    # Level 5: Micro Details
    micro_details: Dict[str, Any] = field(default_factory=lambda: {
        "daily_routines": {},
        "quirks": {},
        "triggers": {},
        "language_patterns": {},
        "attention_patterns": {}
    })
    
    # Level 6: Network Position
    network_attributes: Dict[str, Any] = field(default_factory=lambda: {
        "connections": [],
        "influence_score": 0.0,
        "network_role": None,
        "information_paths": []
    })
    
    # Level 7: Simulation State
    simulation_state: Dict[str, Any] = field(default_factory=lambda: {
        "current_state": {},
        "history": [],
        "pending_actions": [],
        "influence_received": []
    })
    
    # Validation metadata
    validation_scores: Dict[str, float] = field(default_factory=dict)
    consistency_checks: List[Dict] = field(default_factory=list)


class PersonaGenerationState(TypedDict):
    """State management for hierarchical generation process"""
    
    # Input
    article: str
    target_population_size: int
    quality_threshold: float
    
    # Context layers
    article_context: Dict[str, Any]
    hidden_dimensions: Dict[str, Any]
    
    # Hierarchy design
    population_architecture: Dict[str, Any]
    segment_definitions: Dict[str, Dict]
    archetype_library: Dict[str, List[Dict]]
    
    # Generation progress
    generation_stage: str
    completed_personas: List[Dict]
    pending_refinements: List[Dict]
    
    # Validation state
    consistency_matrix: Dict[str, Dict]
    realism_scores: Dict[str, float]
    interaction_test_results: List[Dict]
    
    # Network construction
    network_topology: Dict[str, Any]
    influence_paths: List[List[str]]
    community_structures: List[Dict]
    
    # Quality metrics
    diversity_scores: Dict[str, float]
    realism_metrics: Dict[str, float]
    emergence_indicators: Dict[str, Any]


# ============================================================================
# Stage 0: Deep Context Analysis
# ============================================================================

class DeepContextAnalyzer:
    """Extract multi-dimensional context for persona generation"""
    
    def __init__(self, llm: Optional[ChatGoogleGenerativeAI] = None):
        self.llm = llm or ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7
        )
    
    async def __call__(self, state: PersonaGenerationState) -> Dict:
        """Analyze article context deeply"""
        article = state["article"]
        
        # Multi-dimensional analysis
        context_analysis = await self.analyze_article_context(article)
        
        # Discover hidden dimensions
        hidden_dimensions = await self._discover_hidden_dimensions(
            article, context_analysis
        )
        
        return {
            "article_context": context_analysis,
            "hidden_dimensions": hidden_dimensions,
            "generation_stage": "context_analyzed"
        }
    
    async def analyze_article_context(self, article: str) -> Dict:
        """Extract deep contextual information from article"""
        
        analysis_prompt = f"""
        Analyze this article across multiple dimensions:
        
        1. DOMAIN ANALYSIS:
           - Primary domain and sub-domains
           - Technical complexity level (1-10)
           - Required background knowledge
           - Industry/sector relevance
        
        2. CULTURAL DIMENSIONS:
           - Geographic relevance
           - Cultural sensitivities
           - Language nuances
           - Social context
        
        3. TEMPORAL ASPECTS:
           - Time sensitivity
           - Trend alignment
           - Historical context
           - Future implications
        
        4. EMOTIONAL LANDSCAPE:
           - Emotional triggers
           - Controversy potential
           - Inspirational elements
           - Fear/anxiety factors
        
        5. STAKEHOLDER MAPPING:
           - Who benefits from this information
           - Who might oppose it
           - Who needs to know about it
           - Who would share it
        
        Article: {article[:2000]}...
        
        Provide structured JSON analysis with specific examples.
        """
        
        response = await self.llm.ainvoke(analysis_prompt)
        return json.loads(response.content)
    
    async def _discover_hidden_dimensions(self, article: str, initial_analysis: Dict) -> Dict:
        """Use LLM to discover non-obvious contextual dimensions"""
        
        discovery_prompt = f"""
        Given this article and initial analysis:
        {json.dumps(initial_analysis, indent=2)}
        
        Identify UNEXPECTED or HIDDEN dimensions that might affect readership:
        
        1. Second-order effects (who is indirectly affected?)
        2. Cross-domain implications (unexpected fields this impacts)
        3. Generational perspectives (how different age groups interpret this)
        4. Subculture relevance (niche communities that care deeply)
        5. Contrarian viewpoints (who would read this critically?)
        6. Emotional projections (what personal experiences this triggers)
        
        Be creative and think beyond obvious connections.
        Return as structured JSON.
        """
        
        response = await self.llm.ainvoke(discovery_prompt)
        return json.loads(response.content)


# ============================================================================
# Stage 1: Population Architecture Design
# ============================================================================

class PopulationArchitect:
    """Design the hierarchical structure of the persona population"""
    
    def __init__(self, llm: Optional[ChatGoogleGenerativeAI] = None):
        self.llm = llm or ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.8
        )
    
    async def __call__(self, state: PersonaGenerationState) -> Dict:
        """Design population hierarchy"""
        context = state["article_context"]
        hidden_dims = state["hidden_dimensions"]
        target_size = state["target_population_size"]
        
        # Design hierarchical population structure
        population_arch = await self.design_population_hierarchy(
            context, hidden_dims, target_size
        )
        
        return {
            "population_architecture": population_arch,
            "segment_definitions": population_arch["segments"],
            "generation_stage": "architecture_designed"
        }
    
    async def design_population_hierarchy(
        self, 
        context: Dict,
        hidden_dimensions: Dict,
        target_size: int = 50
    ) -> Dict:
        """Create a hierarchical population structure"""
        
        # Design major segments
        major_segments = await self._design_major_segments(context, hidden_dimensions)
        
        # Design sub-segments
        sub_segments = {}
        for segment in major_segments:
            sub_segments[segment['id']] = await self._design_sub_segments(
                segment, context
            )
        
        # Allocate persona counts
        persona_allocation = await self._allocate_persona_counts(
            major_segments, sub_segments, target_size
        )
        
        return {
            "segments": major_segments,
            "sub_segments": sub_segments,
            "persona_allocation": persona_allocation,
            "total_personas": target_size
        }
    
    async def _design_major_segments(self, context: Dict, hidden_dims: Dict) -> List[Dict]:
        """Design major population segments based on context"""
        
        segment_prompt = f"""
        Context: {json.dumps(context, indent=2)}
        Hidden Dimensions: {json.dumps(hidden_dims, indent=2)}
        
        Design 3-5 major population segments for this article.
        Go beyond obvious categories. Consider:
        
        1. UNEXPECTED INTERSECTIONS:
           - People at the intersection of multiple interests
           - Those with contradictory positions
           - Bridge populations between communities
        
        2. TEMPORAL RELATIONSHIPS:
           - Early adopters vs late majority
           - Those who knew "before it was cool"
           - People waiting for this information
        
        3. EMOTIONAL STAKES:
           - High emotional investment
           - Professional stakes
           - Personal history connections
        
        4. COGNITIVE STYLES:
           - Analytical vs intuitive processors
           - Visual vs textual learners
           - Systems vs detail thinkers
        
        Return as JSON array with each segment containing:
        - id: unique identifier
        - name: segment name
        - percentage: population percentage
        - characteristics: key traits
        - unexpected_traits: non-obvious characteristics
        - article_relationship: how they relate to the article
        """
        
        response = await self.llm.ainvoke(segment_prompt)
        return json.loads(response.content)


# ============================================================================
# Stage 2: Archetype Generation
# ============================================================================

class ArchetypeGenerator:
    """Generate nuanced archetypes within each segment"""
    
    def __init__(self, llm: Optional[ChatGoogleGenerativeAI] = None):
        self.llm = llm or ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.9
        )
    
    async def __call__(self, state: PersonaGenerationState) -> Dict:
        """Generate archetypes for all segments"""
        segments = state["segment_definitions"]
        context = state["article_context"]
        
        archetype_library = {}
        
        # Generate archetypes for each segment
        for segment_id, segment in segments.items():
            archetypes = await self.generate_archetypes(segment, context)
            archetype_library[segment_id] = archetypes
        
        return {
            "archetype_library": archetype_library,
            "generation_stage": "archetypes_created"
        }
    
    async def generate_archetypes(
        self, 
        segment: Dict,
        context: Dict,
        num_archetypes: int = 5
    ) -> List[Dict]:
        """Create detailed archetypes for a segment"""
        
        archetype_prompt = f"""
        Segment: {json.dumps(segment, indent=2)}
        Article Context: {json.dumps(context, indent=2)}
        
        Create {num_archetypes} distinct archetypes within this segment.
        
        IMPORTANT: Avoid stereotypes. Create complex, contradictory personalities:
        
        1. THE PARADOX ARCHETYPE:
           - Combines seemingly incompatible traits
           - Example: "Tech-savvy luddite" or "Introverted influencer"
        
        2. THE THRESHOLD ARCHETYPE:
           - People at turning points in life
           - About to change careers/beliefs/lifestyles
        
        3. THE SHADOW ARCHETYPE:
           - Hidden aspects not immediately visible
           - Public persona vs private reality
        
        4. THE BRIDGE ARCHETYPE:
           - Connects different worlds
           - Code-switchers, cultural translators
        
        5. THE OUTLIER ARCHETYPE:
           - Statistical anomalies that still exist
           - Edge cases that break assumptions
        
        Return as JSON array with each archetype containing:
        - id: unique identifier
        - name: archetype name
        - core_contradiction: main paradox
        - information_style: how they process information
        - social_position: network role
        - hidden_motivations: non-obvious drivers
        - article_connection: unexpected link to topic
        - count: suggested number of personas
        """
        
        response = await self.llm.ainvoke(archetype_prompt)
        archetypes = json.loads(response.content)
        
        # Add emergent properties
        for archetype in archetypes:
            archetype['emergent_behaviors'] = await self._predict_emergent_behaviors(
                archetype, context
            )
        
        return archetypes
    
    async def _predict_emergent_behaviors(self, archetype: Dict, context: Dict) -> Dict:
        """Predict behaviors that emerge from archetype complexity"""
        
        emergence_prompt = f"""
        Archetype: {json.dumps(archetype, indent=2)}
        Context: {json.dumps(context, indent=2)}
        
        Predict emergent behaviors from this archetype's contradictions:
        
        1. Unexpected information seeking patterns
        2. Paradoxical sharing behaviors
        3. Threshold triggers for engagement
        4. Compensatory mechanisms
        
        Return as structured JSON.
        """
        
        response = await self.llm.ainvoke(emergence_prompt)
        return json.loads(response.content)


# ============================================================================
# Stage 3: Individual Persona Generation
# ============================================================================

class HierarchicalPersonaGenerator:
    """Generate individual personas with extreme detail"""
    
    def __init__(self, llm: Optional[ChatGoogleGenerativeAI] = None):
        self.llm = llm or ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.85
        )
    
    async def generate_individual_persona(
        self,
        archetype: Dict,
        segment: Dict,
        context: Dict,
        network_position: Dict
    ) -> HierarchicalPersonaModel:
        """Generate a highly detailed individual persona"""
        
        # Layer 1: Core Identity
        core_identity = await self._generate_core_identity(
            archetype, segment, context
        )
        
        # Layer 2: Life History
        life_history = await self._generate_life_history(
            core_identity, archetype, context
        )
        
        # Layer 3: Psychological Profile
        psych_profile = await self._generate_psychological_profile(
            core_identity, life_history, archetype
        )
        
        # Layer 4: Behavioral Patterns
        behaviors = await self._generate_behavioral_patterns(
            psych_profile, life_history, context
        )
        
        # Layer 5: Micro-details
        micro_details = await self._generate_micro_details(
            core_identity, psych_profile, behaviors
        )
        
        # Create persona model
        persona = HierarchicalPersonaModel(
            id=self._generate_unique_id(),
            generation_timestamp=datetime.now(),
            hierarchy={
                "segment_id": segment['id'],
                "archetype_id": archetype['id'],
                "network_position": network_position
            },
            core_attributes=core_identity,
            psychological_layers=psych_profile,
            behavioral_model=behaviors,
            micro_details=micro_details,
            network_attributes=network_position
        )
        
        # Add article relationship
        persona.simulation_state['article_relationship'] = await self._compute_article_relationship(
            persona, context
        )
        
        return persona
    
    async def _generate_core_identity(
        self, 
        archetype: Dict,
        segment: Dict,
        context: Dict
    ) -> Dict:
        """Generate core identity attributes"""
        
        identity_prompt = f"""
        Archetype: {json.dumps(archetype, indent=2)}
        Segment: {json.dumps(segment, indent=2)}
        
        Generate a specific individual with core identity:
        
        1. DEMOGRAPHICS:
           - Age (specific, not range)
           - Location (specific city/neighborhood)
           - Occupation (specific role and company type)
           - Education (specific institutions and experiences)
        
        2. LIFE SITUATION:
           - Current life phase and transitions
           - Family/relationship status with specifics
           - Financial situation and pressures
           - Health and wellness factors
        
        3. IDENTITY MARKERS:
           - How they see themselves
           - How others see them
           - Identity conflicts
           - Aspirational identity
        
        Make it specific and nuanced. Return as structured JSON.
        """
        
        response = await self.llm.ainvoke(identity_prompt)
        return json.loads(response.content)
    
    async def _generate_life_history(
        self, 
        core_identity: Dict,
        archetype: Dict,
        context: Dict
    ) -> Dict:
        """Generate detailed life history that explains current state"""
        
        history_prompt = f"""
        Core Identity: {json.dumps(core_identity, indent=2)}
        Archetype: {json.dumps(archetype, indent=2)}
        
        Generate a detailed life history that explains their current state:
        
        1. FORMATIVE EXPERIENCES:
           - Specific events that shaped worldview (with dates)
           - Turning points and epiphanies
           - Failures and recoveries
           - Unexpected life paths
        
        2. RELATIONSHIP HISTORY:
           - Key relationships and their impact
           - Mentors and anti-mentors (specific people)
           - Betrayals and loyalties
           - Communities joined and left
        
        3. INFORMATION JOURNEY:
           - How they learned to process information
           - Past mistakes in judgment (specific examples)
           - Sources they trust and distrust (with reasons)
           - Evolution of media consumption
        
        4. HIDDEN TRAUMAS/JOYS:
           - Experiences they don't talk about
           - Secret successes
           - Private failures
           - Unresolved tensions
        
        5. CURRENT TRAJECTORY:
           - Where they're heading
           - What they're running from
           - Dreams vs. reality
           - Ticking clocks in their life
        
        Make it specific with names, dates, places. Return as structured JSON.
        """
        
        response = await self.llm.ainvoke(history_prompt)
        return json.loads(response.content)
    
    async def _generate_psychological_profile(
        self,
        core_identity: Dict,
        life_history: Dict,
        archetype: Dict
    ) -> Dict:
        """Generate deep psychological profile"""
        
        psych_prompt = f"""
        Identity: {json.dumps(core_identity, indent=2)}
        History: {json.dumps(life_history, indent=2)}
        Archetype: {json.dumps(archetype, indent=2)}
        
        Generate a deep psychological profile:
        
        1. CONSCIOUS BELIEFS:
           - Core values and their origins
           - Political/social beliefs with nuance
           - Professional philosophy
           - Personal ethics and contradictions
        
        2. UNCONSCIOUS DRIVES:
           - Hidden motivations
           - Compensatory behaviors
           - Shadow aspects
           - Repressed desires
        
        3. COGNITIVE PATTERNS:
           - Information processing style
           - Decision-making heuristics
           - Cognitive biases (specific ones)
           - Blind spots and awareness
        
        4. EMOTIONAL PATTERNS:
           - Emotional triggers (specific)
           - Regulation strategies
           - Attachment style impacts
           - Stress responses
        
        5. DEFENSE MECHANISMS:
           - Primary defenses
           - When they activate
           - Costs and benefits
           - Evolution over time
        
        Connect everything to their history. Return as structured JSON.
        """
        
        response = await self.llm.ainvoke(psych_prompt)
        return json.loads(response.content)
    
    async def _generate_behavioral_patterns(
        self,
        psych_profile: Dict,
        life_history: Dict,
        context: Dict
    ) -> Dict:
        """Generate detailed behavioral patterns"""
        
        behavior_prompt = f"""
        Psychology: {json.dumps(psych_profile, indent=2)}
        History: {json.dumps(life_history, indent=2)}
        Article Context: {json.dumps(context, indent=2)}
        
        Generate specific behavioral patterns:
        
        1. INFORMATION SEEKING:
           - Daily information routines (specific times, sources)
           - Trusted sources and why
           - Information validation methods
           - Sharing thresholds and patterns
        
        2. DECISION MAKING:
           - Quick decision heuristics
           - Deliberation triggers
           - Influence susceptibility
           - Regret patterns
        
        3. SOCIAL INTERACTION:
           - Communication style variations
           - Network maintenance patterns
           - Conflict approaches
           - Influence strategies
        
        4. CONTENT SHARING:
           - What they share vs consume
           - Platform preferences and why
           - Timing patterns
           - Framing strategies
        
        5. INFLUENCE RESPONSE:
           - Who influences them
           - How they resist influence
           - Peer pressure responses
           - Authority relationships
        
        Be specific about platforms, times, methods. Return as structured JSON.
        """
        
        response = await self.llm.ainvoke(behavior_prompt)
        return json.loads(response.content)
    
    async def _generate_micro_details(
        self,
        core_identity: Dict,
        psych_profile: Dict,
        behaviors: Dict
    ) -> Dict:
        """Generate micro-level details for extreme realism"""
        
        micro_prompt = f"""
        Identity: {json.dumps(core_identity, indent=2)}
        Psychology: {json.dumps(psych_profile, indent=2)}
        Behaviors: {json.dumps(behaviors, indent=2)}
        
        Generate micro-details for extreme realism:
        
        1. DAILY ROUTINES:
           - Morning routine (minute by minute)
           - Work patterns and breaks
           - Evening wind-down
           - Weekend differences
           - How routines affect information consumption
        
        2. QUIRKS AND HABITS:
           - Specific repeated behaviors
           - Superstitions and rituals
           - Comfort behaviors
           - Stress indicators
           - Unconscious patterns
        
        3. TRIGGERS:
           - Words that grab attention
           - Visual elements that stop scrolling
           - Sounds that create responses
           - Situations that change behavior
           - Memories that activate
        
        4. LANGUAGE PATTERNS:
           - Favorite phrases
           - Grammar quirks
           - Emoji usage
           - Punctuation habits
           - Code-switching patterns
        
        5. ATTENTION PATTERNS:
           - Peak focus times
           - Distraction triggers
           - Deep work conditions
           - Multitasking limits
           - Recovery needs
        
        Make it so specific you could recognize this person. Return as structured JSON.
        """
        
        response = await self.llm.ainvoke(micro_prompt)
        return json.loads(response.content)
    
    async def _compute_article_relationship(
        self,
        persona: HierarchicalPersonaModel,
        context: Dict
    ) -> Dict:
        """Compute how this specific persona relates to the article"""
        
        relationship_prompt = f"""
        Persona Summary:
        - Identity: {json.dumps(persona.core_attributes, indent=2)}
        - Psychology: {json.dumps(persona.psychological_layers, indent=2)}
        - Behaviors: {json.dumps(persona.behavioral_model, indent=2)}
        
        Article Context: {json.dumps(context, indent=2)}
        
        Compute this persona's specific relationship to the article:
        
        1. RELEVANCE FACTORS:
           - Personal relevance (0-1) with specific reasons
           - Professional relevance (0-1) with specific impacts
           - Social relevance (0-1) with network implications
           - Emotional relevance (0-1) with triggers
        
        2. LIKELY REACTIONS:
           - Initial emotional response
           - Cognitive processing path
           - Time to decision
           - Action likelihood
        
        3. BARRIERS AND MOTIVATORS:
           - What would prevent engagement
           - What would drive sharing
           - Trust factors
           - Skepticism triggers
        
        4. UNIQUE PERSPECTIVE:
           - What they see that others miss
           - Personal lens effects
           - Interpretation biases
           - Value extraction
        
        Be specific to this individual. Return as structured JSON.
        """
        
        response = await self.llm.ainvoke(relationship_prompt)
        return json.loads(response.content)
    
    def _generate_unique_id(self) -> str:
        """Generate unique persona ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]


# ============================================================================
# Stage 4: Progressive Refinement
# ============================================================================

class ProgressiveRefinementEngine:
    """Iteratively refine personas to increase realism"""
    
    def __init__(self, llm: Optional[ChatGoogleGenerativeAI] = None):
        self.llm = llm or ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7
        )
    
    async def refine_persona(
        self,
        persona: HierarchicalPersonaModel,
        refinement_depth: int = 3
    ) -> HierarchicalPersonaModel:
        """Progressive refinement through multiple passes"""
        
        refined_persona = persona
        
        for depth in range(refinement_depth):
            # Stage 1: Consistency refinement
            refined_persona = await self._refine_consistency(
                refined_persona, depth
            )
            
            # Stage 2: Realism enhancement
            refined_persona = await self._enhance_realism(
                refined_persona, depth
            )
            
            # Stage 3: Detail enrichment
            refined_persona = await self._enrich_details(
                refined_persona, depth
            )
            
            # Stage 4: Emergent behavior prediction
            emergent_behaviors = await self._predict_emergent_behaviors(
                refined_persona, depth
            )
            refined_persona.simulation_state['emergent_behaviors'] = emergent_behaviors
            
            # Validation check
            validation_score = await self._quick_validation(refined_persona)
            
            if validation_score > 0.9:
                break
        
        return refined_persona
    
    async def _enhance_realism(
        self, 
        persona: HierarchicalPersonaModel,
        depth: int
    ) -> HierarchicalPersonaModel:
        """Add layers of realism through specific details"""
        
        enhancement_prompt = f"""
        Current persona depth: {depth}
        Persona summary:
        - Core: {json.dumps(persona.core_attributes, indent=2)}
        - Psychology: {json.dumps(persona.psychological_layers, indent=2)}
        - Behaviors: {json.dumps(persona.behavioral_model, indent=2)}
        
        Add the next layer of realism:
        
        Depth {depth} focus areas:
        0: Add specific life events that explain current state
        1: Add daily micro-routines that affect information consumption  
        2: Add specific people in their life who influence decisions
        3: Add current life pressures and deadlines
        4: Add secret desires and hidden shames
        
        For depth {depth}, generate:
        - Specific, named details (not generic)
        - Causal connections to existing attributes
        - Unexpected but logical elements
        - Time-bound factors
        
        Return specific enhancements as JSON.
        """
        
        response = await self.llm.ainvoke(enhancement_prompt)
        enhancements = json.loads(response.content)
        
        # Apply enhancements to persona
        return self._apply_enhancements(persona, enhancements, depth)
    
    def _apply_enhancements(
        self, 
        persona: HierarchicalPersonaModel, 
        enhancements: Dict,
        depth: int
    ) -> HierarchicalPersonaModel:
        """Apply enhancements to persona model"""
        
        # Deep merge enhancements into appropriate layers
        if depth == 0:
            persona.psychological_layers['life_events'] = enhancements.get('life_events', {})
        elif depth == 1:
            persona.micro_details['enhanced_routines'] = enhancements.get('micro_routines', {})
        elif depth == 2:
            persona.network_attributes['key_influences'] = enhancements.get('key_people', [])
        elif depth == 3:
            persona.simulation_state['current_pressures'] = enhancements.get('life_pressures', {})
        elif depth == 4:
            persona.psychological_layers['hidden_aspects'] = enhancements.get('secrets', {})
        
        return persona


# ============================================================================
# Stage 5: Validation Framework
# ============================================================================

class PersonaValidationFramework:
    """Multi-level validation for generated personas"""
    
    def __init__(self, llm: Optional[ChatGoogleGenerativeAI] = None):
        self.llm = llm or ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.3
        )
    
    async def validate_persona_hierarchy(
        self, 
        persona: HierarchicalPersonaModel,
        population_context: Dict
    ) -> Dict:
        """Perform hierarchical validation"""
        
        validation_results = {}
        
        # Level 1: Internal consistency
        internal_consistency = await self._check_internal_consistency(persona)
        validation_results['internal'] = internal_consistency
        
        # Level 2: Behavioral realism
        behavioral_realism = await self._check_behavioral_realism(persona)
        validation_results['behavioral'] = behavioral_realism
        
        # Level 3: Emergent property validation
        emergent_validation = await self._validate_emergent_properties(persona)
        validation_results['emergent'] = emergent_validation
        
        return {
            "is_valid": all(r.get('score', 0) > 0.8 for r in validation_results.values()),
            "scores": validation_results,
            "recommendations": self._generate_refinement_recommendations(
                validation_results
            )
        }
    
    async def _check_internal_consistency(
        self, 
        persona: HierarchicalPersonaModel
    ) -> Dict:
        """Check for internal logical consistency"""
        
        consistency_prompt = f"""
        Analyze this persona for internal consistency:
        
        Demographics: {json.dumps(persona.core_attributes, indent=2)}
        Psychology: {json.dumps(persona.psychological_layers, indent=2)}
        Behaviors: {json.dumps(persona.behavioral_model, indent=2)}
        Micro-details: {json.dumps(persona.micro_details, indent=2)}
        
        Check for:
        1. Logical contradictions
        2. Impossible combinations
        3. Unrealistic correlations
        4. Missing causal links
        5. Implausible trajectories
        
        Rate consistency (0-1) and list specific issues.
        Return as JSON with score and issues array.
        """
        
        response = await self.llm.ainvoke(consistency_prompt)
        return json.loads(response.content)


# ============================================================================
# Parallel Generation Orchestration
# ============================================================================

async def generate_personas_parallel(state: PersonaGenerationState) -> Dict:
    """Generate personas in parallel using Send API"""
    
    archetype_library = state["archetype_library"]
    context = state["article_context"]
    
    # Create parallel generation tasks
    sends = []
    persona_id_counter = 0
    
    for segment_id, archetypes in archetype_library.items():
        segment = state["segment_definitions"][segment_id]
        
        for archetype in archetypes:
            for i in range(archetype.get("count", 1)):
                sends.append(Send(
                    "generate_single_persona",
                    {
                        "persona_id": f"persona_{persona_id_counter}",
                        "segment": segment,
                        "archetype": archetype,
                        "context": context,
                        "network_position": {
                            "node_id": persona_id_counter,
                            "initial_connections": []
                        }
                    }
                ))
                persona_id_counter += 1
    
    return {
        "generation_stage": "generating_personas",
        "pending_personas": sends
    }


async def generate_single_persona(inputs: Dict) -> Dict:
    """Generate a single hierarchical persona"""
    
    generator = HierarchicalPersonaGenerator()
    
    # Generate persona with full hierarchy
    persona = await generator.generate_individual_persona(
        archetype=inputs["archetype"],
        segment=inputs["segment"],
        context=inputs["context"],
        network_position=inputs["network_position"]
    )
    
    # Initial refinement
    refiner = ProgressiveRefinementEngine()
    refined_persona = await refiner.refine_persona(persona, refinement_depth=2)
    
    return {
        "persona_id": inputs["persona_id"],
        "persona": refined_persona,
        "generation_metadata": {
            "timestamp": datetime.now().isoformat(),
            "archetype_id": inputs["archetype"]["id"],
            "segment_id": inputs["segment"]["id"]
        }
    }


# ============================================================================
# LangGraph Integration
# ============================================================================

def build_hierarchical_persona_graph():
    """Build the complete hierarchical persona generation graph"""
    
    workflow = StateGraph(PersonaGenerationState)
    
    # Add nodes
    workflow.add_node("analyze_context", DeepContextAnalyzer())
    workflow.add_node("design_population", PopulationArchitect())
    workflow.add_node("generate_archetypes", ArchetypeGenerator())
    workflow.add_node("generate_personas", generate_personas_parallel)
    workflow.add_node("validate_personas", PersonaValidationFramework())
    
    # Add edges
    workflow.add_edge(START, "analyze_context")
    workflow.add_edge("analyze_context", "design_population")
    workflow.add_edge("design_population", "generate_archetypes")
    workflow.add_edge("generate_archetypes", "generate_personas")
    workflow.add_edge("generate_personas", "validate_personas")
    workflow.add_edge("validate_personas", END)
    
    return workflow.compile()


# ============================================================================
# High-Level API
# ============================================================================

class MarketSimulatorPersonaGenerator:
    """High-level API for hierarchical persona generation"""
    
    def __init__(self):
        self.graph = build_hierarchical_persona_graph()
    
    async def generate_population(
        self,
        article: str,
        population_size: int = 50,
        quality_threshold: float = 0.85
    ) -> Dict:
        """Generate a complete persona population"""
        
        # Initialize state
        initial_state = {
            "article": article,
            "target_population_size": population_size,
            "quality_threshold": quality_threshold,
            "generation_stage": "initialization",
            "completed_personas": [],
            "article_context": {},
            "hidden_dimensions": {},
            "population_architecture": {},
            "segment_definitions": {},
            "archetype_library": {},
            "network_topology": {},
            "consistency_matrix": {},
            "realism_scores": {},
            "diversity_scores": {},
            "realism_metrics": {},
            "emergence_indicators": {}
        }
        
        # Run hierarchical generation
        result = await self.graph.ainvoke(initial_state)
        
        return {
            "personas": result["completed_personas"],
            "population_metrics": self._calculate_population_metrics(result),
            "generation_metadata": {
                "article_context": result["article_context"],
                "hidden_dimensions": result["hidden_dimensions"],
                "generation_timestamp": datetime.now().isoformat()
            }
        }
    
    def _calculate_population_metrics(self, result: Dict) -> Dict:
        """Calculate population-level metrics"""
        
        personas = result.get("completed_personas", [])
        
        return {
            "total_count": len(personas),
            "quality_scores": result.get("realism_scores", {}),
            "diversity_metrics": result.get("diversity_scores", {}),
            "emergence_indicators": result.get("emergence_indicators", {})
        }


# Example usage
if __name__ == "__main__":
    async def main():
        # Example article
        article = """
        Revolutionary AI breakthrough: Scientists develop new neural architecture
        that mimics human creativity, raising questions about consciousness...
        """
        
        # Generate population
        generator = MarketSimulatorPersonaGenerator()
        result = await generator.generate_population(
            article=article,
            population_size=30,
            quality_threshold=0.85
        )
        
        print(f"Generated {len(result['personas'])} personas")
        print(f"Population metrics: {result['population_metrics']}")
    
    asyncio.run(main())