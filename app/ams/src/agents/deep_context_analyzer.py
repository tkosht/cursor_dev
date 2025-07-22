"""Deep Context Analyzer for Article Market Simulator.

This module analyzes articles across multiple dimensions to extract
contextual information for persona generation.
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime

from src.utils.llm_factory import create_llm
from src.utils.json_parser import parse_llm_json_response


class DeepContextAnalyzer:
    """Extract multi-dimensional context from articles for persona generation."""
    
    def __init__(self):
        """Initialize the DeepContextAnalyzer."""
        self.llm = create_llm()
        
    async def analyze_article_context(self, article: str) -> Dict[str, Any]:
        """Extract deep contextual information from article.
        
        Args:
            article: The article content to analyze
            
        Returns:
            Dict containing:
                - core_context: Multi-dimensional analysis results
                - hidden_dimensions: Non-obvious contextual dimensions
                - complexity_score: Article complexity (0-1)
                - reach_potential: Estimated reach potential (0-1)
        """
        try:
            # Perform multi-dimensional analysis
            core_context = await self._analyze_core_dimensions(article)
            
            # Discover hidden dimensions
            hidden_dimensions = await self._discover_hidden_dimensions(
                article, core_context
            )
            
            return {
                "core_context": core_context,
                "hidden_dimensions": hidden_dimensions,
                "complexity_score": self._calculate_complexity(core_context),
                "reach_potential": self._estimate_reach_potential(core_context)
            }
            
        except Exception as e:
            # Return default structure on error
            return {
                "core_context": {},
                "hidden_dimensions": {},
                "complexity_score": 0.5,
                "reach_potential": 0.5
            }
    
    async def _analyze_core_dimensions(self, article: str) -> Dict[str, Any]:
        """Analyze core contextual dimensions of the article."""
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
           - Who benefits from this information (beneficiaries)
           - Who might oppose it (opponents)
           - Who needs to know about it (need_to_know)
           - Who would share it (likely_sharers)
        
        Article: {article[:2000]}...
        
        Provide structured analysis with specific examples.
        Return as JSON with keys: domain_analysis, cultural_dimensions, 
        temporal_aspects, emotional_landscape, stakeholder_mapping
        """
        
        response = await self.llm.ainvoke(analysis_prompt)
        return self._parse_analysis_response(response)
    
    async def _discover_hidden_dimensions(
        self, 
        article: str, 
        initial_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM to discover non-obvious contextual dimensions."""
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
        Return as JSON with keys: second_order_effects, cross_domain_implications,
        generational_perspectives, subculture_relevance, contrarian_viewpoints,
        emotional_projections
        """
        
        response = await self.llm.ainvoke(discovery_prompt)
        return self._parse_analysis_response(response)
    
    def _calculate_complexity(self, context_analysis: Dict[str, Any]) -> float:
        """Calculate article complexity score (0-1).
        
        Args:
            context_analysis: The core context analysis results
            
        Returns:
            Complexity score between 0 and 1
        """
        score = 0.0
        
        # Technical complexity component (0-0.4)
        domain_analysis = context_analysis.get("domain_analysis", {})
        tech_complexity = domain_analysis.get("technical_complexity", 5) / 10
        score += tech_complexity * 0.4
        
        # Required knowledge component (0-0.2)
        required_knowledge = domain_analysis.get("required_knowledge", [])
        knowledge_score = min(len(required_knowledge) / 5, 1.0)
        score += knowledge_score * 0.2
        
        # Cultural sensitivity component (0-0.2)
        cultural = context_analysis.get("cultural_dimensions", {})
        sensitivities = cultural.get("cultural_sensitivities", [])
        sensitivity_score = min(len(sensitivities) / 4, 1.0)
        score += sensitivity_score * 0.2
        
        # Stakeholder complexity component (0-0.2)
        stakeholders = context_analysis.get("stakeholder_mapping", {})
        total_stakeholders = (
            len(stakeholders.get("beneficiaries", [])) +
            len(stakeholders.get("opponents", [])) +
            len(stakeholders.get("need_to_know", []))
        )
        stakeholder_score = min(total_stakeholders / 8, 1.0)
        score += stakeholder_score * 0.2
        
        return round(score, 2)
    
    def _estimate_reach_potential(self, context_analysis: Dict[str, Any]) -> float:
        """Estimate article reach potential (0-1).
        
        Args:
            context_analysis: The core context analysis results
            
        Returns:
            Reach potential score between 0 and 1
        """
        score = 0.0
        
        # Stakeholder reach component (0-0.3)
        stakeholders = context_analysis.get("stakeholder_mapping", {})
        beneficiaries = stakeholders.get("beneficiaries", [])
        sharers = stakeholders.get("likely_sharers", [])
        reach_score = min((len(beneficiaries) + len(sharers)) / 6, 1.0)
        score += reach_score * 0.3
        
        # Emotional impact component (0-0.3)
        emotional = context_analysis.get("emotional_landscape", {})
        controversy = 1.0 if emotional.get("controversy_potential") == "high" else 0.5
        inspiration = len(emotional.get("inspirational_elements", [])) / 3
        emotional_score = (controversy + min(inspiration, 1.0)) / 2
        score += emotional_score * 0.3
        
        # Trend alignment component (0-0.2)
        temporal = context_analysis.get("temporal_aspects", {})
        trends = temporal.get("trend_alignment", [])
        trend_score = min(len(trends) / 3, 1.0)
        score += trend_score * 0.2
        
        # Time sensitivity component (0-0.2)
        time_sensitive = temporal.get("time_sensitivity") == "high"
        score += 0.2 if time_sensitive else 0.1
        
        return round(score, 2)
    
    def _parse_analysis_response(self, response) -> Dict[str, Any]:
        """Parse LLM response into structured data.
        
        Args:
            response: LLM response object with content attribute
            
        Returns:
            Parsed dictionary or empty dict on error
        """
        try:
            # Use the utility parser
            return parse_llm_json_response(response.content)
        except Exception:
            return {}