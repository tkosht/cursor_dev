"""Deep Context Analyzer for Article Market Simulator.

This module analyzes articles across multiple dimensions to extract
contextual information for persona generation.
"""

from typing import Any

from src.utils.json_parser import parse_llm_json_response
from src.utils.llm_factory import create_llm


class DeepContextAnalyzer:
    """Extract multi-dimensional context from articles for persona generation."""

    def __init__(self, force_lightweight: bool = False):
        """Initialize the DeepContextAnalyzer.

        Args:
            force_lightweight: If True, always use lightweight analysis mode
        """
        self.llm = create_llm()
        self.force_lightweight = force_lightweight

    async def analyze_article_context(self, article: str) -> dict[str, Any]:
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
            # Use lightweight mode for short articles or when forced
            is_lightweight = self.force_lightweight or len(article) <= 500

            if is_lightweight:
                # Perform lightweight analysis
                core_context = await self._analyze_core_dimensions_lightweight(article)
                # Skip hidden dimensions for lightweight mode
                hidden_dimensions = {}
            else:
                # Perform multi-dimensional analysis
                core_context = await self._analyze_core_dimensions(article)
                # Discover hidden dimensions with optimized prompt
                hidden_dimensions = await self._discover_hidden_dimensions_optimized(
                    article, core_context
                )

            return {
                "core_context": core_context,
                "hidden_dimensions": hidden_dimensions,
                "complexity_score": self._calculate_complexity(core_context),
                "reach_potential": self._estimate_reach_potential(core_context),
            }

        except Exception:
            # Return default structure on error
            return {
                "core_context": {},
                "hidden_dimensions": {},
                "complexity_score": 0.5,
                "reach_potential": 0.5,
            }

    async def _analyze_core_dimensions_lightweight(self, article: str) -> dict[str, Any]:
        """Perform lightweight analysis for short articles."""
        # Very concise prompt
        analysis_prompt = f"""
        Analyze: {article[:300]}...

        Return JSON:
        - domain_analysis: primary_domain (string), technical_complexity (1-10)
        - stakeholder_mapping: beneficiaries (list), likely_sharers (list)
        - emotional_landscape: controversy_potential (low/medium/high)
        - temporal_aspects: time_sensitivity (low/medium/high)
        """

        response = await self.llm.ainvoke(analysis_prompt)
        result = self._parse_analysis_response(response)

        # Ensure consistent structure with full analysis
        return {
            "domain_analysis": result.get(
                "domain_analysis", {"primary_domain": "general", "technical_complexity": 5}
            ),
            "cultural_dimensions": {},  # Empty for lightweight
            "temporal_aspects": result.get("temporal_aspects", {"time_sensitivity": "medium"}),
            "emotional_landscape": result.get(
                "emotional_landscape", {"controversy_potential": "low"}
            ),
            "stakeholder_mapping": result.get(
                "stakeholder_mapping", {"beneficiaries": [], "likely_sharers": []}
            ),
        }

    async def _analyze_core_dimensions(self, article: str) -> dict[str, Any]:
        """Analyze core contextual dimensions of the article."""
        analysis_prompt = f"""
        Analyze this article concisely:

        1. DOMAIN: Primary domain, complexity (1-10), required knowledge
        2. CULTURAL: Geographic relevance, sensitivities
        3. TEMPORAL: Time sensitivity, trend alignment
        4. EMOTIONAL: Controversy potential, inspirational elements
        5. STAKEHOLDERS: beneficiaries, opponents, need_to_know, likely_sharers (3-4 each)

        Article: {article[:1500]}...

        Return as JSON with keys: domain_analysis, cultural_dimensions,
        temporal_aspects, emotional_landscape, stakeholder_mapping
        """

        response = await self.llm.ainvoke(analysis_prompt)
        return self._parse_analysis_response(response)

    async def _discover_hidden_dimensions(
        self, article: str, initial_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Use LLM to discover non-obvious contextual dimensions."""
        # Extract key insights from initial analysis to reduce prompt size
        summary = self._summarize_initial_analysis(initial_analysis)

        discovery_prompt = f"""
        Article: {article[:300]}...

        Key insights:
        - Domain: {summary.get('domain', 'Unknown')}
        - Complexity: {summary.get('complexity', 5)}/10
        - Key stakeholders: {', '.join(summary.get('stakeholders', [])[:3])}

        Identify 3 UNEXPECTED dimensions:
        1. Second-order effects (indirect impacts)
        2. Cross-domain implications
        3. Contrarian viewpoints

        Return concise JSON with these keys only.
        """

        response = await self.llm.ainvoke(discovery_prompt)
        return self._parse_analysis_response(response)

    def _summarize_initial_analysis(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Extract key information from initial analysis to reduce prompt size."""
        return {
            "domain": analysis.get("domain_analysis", {}).get("primary_domain", "Unknown"),
            "complexity": analysis.get("domain_analysis", {}).get("technical_complexity", 5),
            "stakeholders": list(
                analysis.get("stakeholder_mapping", {}).get("beneficiaries", [])
            ),
            "controversy": analysis.get("emotional_landscape", {}).get(
                "controversy_potential", "medium"
            ),
            "time_sensitivity": analysis.get("temporal_aspects", {}).get(
                "time_sensitivity", "medium"
            ),
        }

    async def _discover_hidden_dimensions_optimized(
        self, article: str, initial_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Optimized version with minimal prompt."""
        # Use only essential information
        domain = initial_analysis.get("domain_analysis", {}).get("primary_domain", "Unknown")

        minimal_prompt = f"""
        Article domain: {domain}
        Find 2 unexpected impacts:
        1. Side effects?
        2. Who else affected?

        Brief JSON response.
        """

        response = await self.llm.ainvoke(minimal_prompt)
        result = self._parse_analysis_response(response)

        # Provide structure with defaults
        return {
            "second_order_effects": result.get("second_order_effects", ["Indirect market impact"]),
            "cross_domain_implications": result.get(
                "cross_domain_implications", ["Adjacent industry effects"]
            ),
            "subculture_relevance": result.get(
                "subculture_relevance", ["Niche community interest"]
            ),
            "contrarian_viewpoints": result.get(
                "contrarian_viewpoints", ["Alternative perspective"]
            ),
        }

    def _calculate_complexity(self, context_analysis: dict[str, Any]) -> float:
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
            len(stakeholders.get("beneficiaries", []))
            + len(stakeholders.get("opponents", []))
            + len(stakeholders.get("need_to_know", []))
        )
        stakeholder_score = min(total_stakeholders / 8, 1.0)
        score += stakeholder_score * 0.2

        return round(score, 2)

    def _estimate_reach_potential(self, context_analysis: dict[str, Any]) -> float:
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

    def _parse_analysis_response(self, response) -> dict[str, Any]:
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
