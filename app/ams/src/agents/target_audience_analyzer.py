"""
Target Audience Analyzer for dynamic persona generation
This module analyzes article content to identify and segment target audiences
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from src.utils.llm_factory import create_llm
from src.utils.json_parser import parse_llm_json_response

logger = logging.getLogger(__name__)


@dataclass
class AudienceSegment:
    """Represents a segment of the target audience"""
    name: str
    description: str
    size_estimate: str  # "large", "medium", "small"
    relevance_score: float  # 0.0 to 1.0
    key_characteristics: List[str]
    interests: List[str]
    pain_points: List[str]
    engagement_potential: float  # 0.0 to 1.0


@dataclass
class AudienceAnalysis:
    """Complete audience analysis results"""
    primary_audience: AudienceSegment
    secondary_audiences: List[AudienceSegment]
    total_reach_potential: float
    engagement_distribution: Dict[str, float]
    demographic_insights: Dict[str, Any]
    psychographic_insights: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]


class TargetAudienceAnalyzer:
    """
    Analyzes article content to identify target audiences dynamically
    Generates audience segments based on actual content, not fixed personas
    """
    
    def __init__(self):
        self.llm = create_llm()
        self.analysis_cache: Dict[str, AudienceAnalysis] = {}
    
    async def analyze_audience(
        self, 
        article_content: str,
        article_metadata: Optional[Dict[str, Any]] = None
    ) -> AudienceAnalysis:
        """
        Analyze article to identify target audiences dynamically
        
        Args:
            article_content: The article text to analyze
            article_metadata: Optional metadata about the article
        
        Returns:
            Complete audience analysis with segments
        """
        # Check cache first
        cache_key = hash(article_content[:500])  # Use first 500 chars for cache key
        if cache_key in self.analysis_cache:
            logger.debug("Using cached audience analysis")
            return self.analysis_cache[cache_key]
        
        # Extract key topics and themes
        topics = await self._extract_topics(article_content)
        
        # Identify potential audience segments
        segments = await self._identify_segments(article_content, topics)
        
        # Analyze demographics and psychographics
        demographics = await self._analyze_demographics(article_content, segments)
        psychographics = await self._analyze_psychographics(article_content, segments)
        
        # Determine behavioral patterns
        behaviors = await self._analyze_behaviors(article_content, segments)
        
        # Calculate reach and engagement potential
        reach_potential = self._calculate_reach_potential(segments)
        engagement_dist = self._calculate_engagement_distribution(segments)
        
        # Determine primary and secondary audiences
        sorted_segments = sorted(segments, key=lambda s: s.relevance_score, reverse=True)
        primary = sorted_segments[0] if sorted_segments else self._create_default_segment()
        secondary = sorted_segments[1:] if len(sorted_segments) > 1 else []
        
        analysis = AudienceAnalysis(
            primary_audience=primary,
            secondary_audiences=secondary,
            total_reach_potential=reach_potential,
            engagement_distribution=engagement_dist,
            demographic_insights=demographics,
            psychographic_insights=psychographics,
            behavioral_patterns=behaviors
        )
        
        # Cache the result
        self.analysis_cache[cache_key] = analysis
        
        return analysis
    
    async def _extract_topics(self, article_content: str) -> List[str]:
        """Extract main topics from article"""
        prompt = f"""
        Analyze this article and extract the main topics (max 5):
        
        Article: {article_content[:1000]}...
        
        Return JSON with:
        - topics: list of main topics
        - complexity_level: technical/general/mixed
        - domain: primary domain (tech/business/science/lifestyle/etc)
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            data = parse_llm_json_response(str(response.content))
            return data.get("topics", ["general"])
        except Exception as e:
            logger.error(f"Failed to extract topics: {e}")
            return ["general"]
    
    async def _identify_segments(
        self, 
        article_content: str, 
        topics: List[str]
    ) -> List[AudienceSegment]:
        """Identify audience segments based on content analysis"""
        prompt = f"""
        Based on this article about {', '.join(topics)}, identify target audience segments.
        
        Article excerpt: {article_content[:800]}...
        
        For each segment, provide:
        - name: descriptive segment name
        - description: 1-2 sentence description
        - size_estimate: large/medium/small
        - relevance_score: 0.0-1.0
        - key_characteristics: list of 3-5 traits
        - interests: list of 3-5 interests
        - pain_points: list of 2-3 pain points this article addresses
        - engagement_potential: 0.0-1.0
        
        Return JSON with "segments" array containing 3-5 audience segments.
        Make them specific to this article's content, not generic personas.
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            data = parse_llm_json_response(str(response.content))
            
            segments = []
            for seg_data in data.get("segments", []):
                segment = AudienceSegment(
                    name=seg_data.get("name", "Unknown Segment"),
                    description=seg_data.get("description", ""),
                    size_estimate=seg_data.get("size_estimate", "medium"),
                    relevance_score=float(seg_data.get("relevance_score", 0.5)),
                    key_characteristics=seg_data.get("key_characteristics", []),
                    interests=seg_data.get("interests", []),
                    pain_points=seg_data.get("pain_points", []),
                    engagement_potential=float(seg_data.get("engagement_potential", 0.5))
                )
                segments.append(segment)
            
            return segments if segments else [self._create_default_segment()]
            
        except Exception as e:
            logger.error(f"Failed to identify segments: {e}")
            return [self._create_default_segment()]
    
    async def _analyze_demographics(
        self, 
        article_content: str, 
        segments: List[AudienceSegment]
    ) -> Dict[str, Any]:
        """Analyze demographic patterns for identified segments"""
        segment_names = [s.name for s in segments[:3]]
        
        prompt = f"""
        For an article targeting {', '.join(segment_names)}, analyze demographics:
        
        Article context: {article_content[:500]}...
        
        Return JSON with:
        - age_distribution: dict of age ranges and percentages
        - education_levels: dict of education levels and percentages
        - professional_fields: list of relevant professions
        - geographic_relevance: list of regions/countries
        - income_brackets: relevant income levels
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            data = parse_llm_json_response(str(response.content))

            # NOTE(AMS design intent):
            # LLM応答は整数/小数/文字列(例: "35%") 混在や値欠落があり得る。
            # 本MVPでは、年齢分布は数値(0–1)の辞書として正規化し、
            # 合計ゼロの場合は安全なデフォルトにフォールバックする。
            # これはテスト安定性(再現性)とダッシュボード計算の堅牢性を担保するため。
            age_dist = data.get("age_distribution", {})
            if not isinstance(age_dist, dict):
                age_dist = {}

            normalized: Dict[str, float] = {}
            for k, v in age_dist.items():
                try:
                    if isinstance(v, (int, float)):
                        f = float(v)
                    elif isinstance(v, str):
                        s = v.strip().replace("%", "")
                        f = float(s)
                    else:
                        continue
                    # Convert 0-100 to 0-1 if needed
                    if f > 1.0 and f <= 100.0:
                        f = f / 100.0
                    normalized[k] = f
                except Exception:
                    continue

            # Fallback if nothing usable
            if sum(normalized.values()) <= 0:
                normalized = {"25-34": 0.3, "35-44": 0.3, "45-54": 0.2, "other": 0.2}

            data["age_distribution"] = normalized
            return data
        except Exception as e:
            logger.error(f"Failed to analyze demographics: {e}")
            return {
                "age_distribution": {"25-34": 0.3, "35-44": 0.3, "45-54": 0.2, "other": 0.2},
                "education_levels": {"college": 0.5, "graduate": 0.3, "other": 0.2},
                "professional_fields": ["general"],
                "geographic_relevance": ["global"],
                "income_brackets": ["middle"]
            }
    
    async def _analyze_psychographics(
        self, 
        article_content: str, 
        segments: List[AudienceSegment]
    ) -> Dict[str, Any]:
        """Analyze psychographic patterns"""
        prompt = f"""
        Analyze psychographics for readers of this article:
        
        Article excerpt: {article_content[:500]}...
        
        Return JSON with:
        - values: list of core values
        - attitudes: dict of attitudes towards key topics
        - lifestyle_preferences: list of lifestyle traits
        - motivations: list of primary motivations
        - personality_traits: dominant personality characteristics
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            return parse_llm_json_response(str(response.content))
        except Exception as e:
            logger.error(f"Failed to analyze psychographics: {e}")
            return {
                "values": ["learning", "growth"],
                "attitudes": {"technology": "positive"},
                "lifestyle_preferences": ["digital-first"],
                "motivations": ["stay informed"],
                "personality_traits": ["curious", "open-minded"]
            }
    
    async def _analyze_behaviors(
        self, 
        article_content: str, 
        segments: List[AudienceSegment]
    ) -> Dict[str, Any]:
        """Analyze behavioral patterns"""
        prompt = f"""
        Analyze behavioral patterns for readers of this article:
        
        Article topic: {article_content[:300]}...
        
        Return JSON with:
        - content_consumption: how they consume content
        - sharing_behavior: likelihood and channels for sharing
        - engagement_patterns: how they engage with content
        - decision_making: how they make decisions
        - information_sources: preferred information sources
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            return parse_llm_json_response(str(response.content))
        except Exception as e:
            logger.error(f"Failed to analyze behaviors: {e}")
            return {
                "content_consumption": "regular",
                "sharing_behavior": "selective",
                "engagement_patterns": "moderate",
                "decision_making": "research-based",
                "information_sources": ["online", "peers"]
            }
    
    def _calculate_reach_potential(self, segments: List[AudienceSegment]) -> float:
        """Calculate total reach potential"""
        if not segments:
            return 0.5
        
        size_weights = {"large": 1.0, "medium": 0.6, "small": 0.3}
        
        total_weight = sum(
            size_weights.get(s.size_estimate, 0.5) * s.relevance_score 
            for s in segments
        )
        
        # Normalize to 0-1 range
        return min(1.0, total_weight / len(segments))
    
    def _calculate_engagement_distribution(
        self, 
        segments: List[AudienceSegment]
    ) -> Dict[str, float]:
        """Calculate engagement distribution across segments"""
        if not segments:
            return {"default": 1.0}
        
        total_engagement = sum(s.engagement_potential for s in segments)
        if total_engagement == 0:
            return {s.name: 1.0 / len(segments) for s in segments}
        
        return {
            s.name: s.engagement_potential / total_engagement 
            for s in segments
        }
    
    def _create_default_segment(self) -> AudienceSegment:
        """Create a default segment when analysis fails"""
        return AudienceSegment(
            name="General Audience",
            description="General readers interested in the topic",
            size_estimate="medium",
            relevance_score=0.5,
            key_characteristics=["curious", "informed", "engaged"],
            interests=["current events", "learning", "technology"],
            pain_points=["staying informed", "understanding complexity"],
            engagement_potential=0.5
        )