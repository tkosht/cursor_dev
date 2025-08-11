"""
Unit tests for TargetAudienceAnalyzer - Using REAL LLM APIs
Following CLAUDE.md mandatory rules: NO MOCKS ALLOWED
"""

import os
import sys
from pathlib import Path

import pytest

# Add tests directory to path for test helper
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_test_helper import get_llm_helper
from src.agents.target_audience_analyzer import (
    TargetAudienceAnalyzer,
    AudienceSegment,
    AudienceAnalysis
)


class TestTargetAudienceAnalyzer:
    """Test suite for TargetAudienceAnalyzer with real LLM"""
    
    @pytest.fixture
    def analyzer(self):
        """Create TargetAudienceAnalyzer instance"""
        return TargetAudienceAnalyzer()
    
    @pytest.fixture
    def tech_article_content(self):
        """Sample technology article for testing"""
        return """
        # Revolutionary AI Framework Transforms Enterprise Software Development
        
        A groundbreaking AI-powered framework has emerged that promises to revolutionize
        how enterprises build and deploy software applications. The framework, developed
        by leading researchers in machine learning and software engineering, combines
        advanced language models with automated code generation to dramatically reduce
        development time while improving code quality.
        
        Key features include:
        - Intelligent code completion that understands business context
        - Automated testing and bug detection using AI analysis
        - Real-time performance optimization suggestions
        - Natural language to code translation capabilities
        
        Early adopters report 40% reduction in development time and 60% fewer bugs
        in production. The framework supports multiple programming languages and
        integrates seamlessly with existing CI/CD pipelines.
        
        Industry experts predict this could fundamentally change the software
        development landscape, particularly for large enterprises dealing with
        complex legacy systems and rapid digital transformation requirements.
        """
    
    @pytest.fixture
    def lifestyle_article_content(self):
        """Sample lifestyle article for testing"""
        return """
        # The Rise of Mindful Morning Routines: Transform Your Day
        
        More people are discovering the power of intentional morning routines
        to boost productivity, mental health, and overall life satisfaction.
        Research shows that how you spend the first hour of your day can
        significantly impact your mood, energy levels, and decision-making
        throughout the day.
        
        Popular morning routine elements include:
        - Meditation or mindfulness practice (10-15 minutes)
        - Journaling and gratitude exercises
        - Physical movement or yoga
        - Healthy breakfast without screens
        - Reading or learning something new
        
        Psychologists note that consistent morning routines help reduce
        decision fatigue and create a sense of control and accomplishment
        early in the day. Many successful entrepreneurs and creatives
        credit their morning routines as key to their achievements.
        """
    
    @pytest.mark.asyncio
    async def test_analyze_tech_article_audience(self, analyzer, tech_article_content, real_llm):
        """Test audience analysis for technology article with real LLM"""
        # Skip if no API key is available
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")
        
        # Analyze audience
        analysis = await analyzer.analyze_audience(tech_article_content)
        
        # Verify structure
        assert isinstance(analysis, AudienceAnalysis)
        assert analysis.primary_audience is not None
        assert isinstance(analysis.primary_audience, AudienceSegment)
        
        # Verify primary audience makes sense for tech content
        primary = analysis.primary_audience
        assert primary.name is not None
        assert primary.relevance_score > 0
        assert len(primary.key_characteristics) > 0
        assert len(primary.interests) > 0
        
        # Check that tech-related interests are identified
        all_interests = primary.interests + [
            interest for seg in analysis.secondary_audiences 
            for interest in seg.interests
        ]
        tech_keywords = ["technology", "software", "AI", "development", "innovation", "digital"]
        assert any(
            any(keyword.lower() in interest.lower() for keyword in tech_keywords)
            for interest in all_interests
        ), "Should identify technology-related interests"
        
        # Verify demographics make sense
        assert "professional_fields" in analysis.demographic_insights
        assert isinstance(analysis.demographic_insights["professional_fields"], list)
        
        # Verify psychographics
        assert "values" in analysis.psychographic_insights
        assert isinstance(analysis.psychographic_insights["values"], list)
    
    @pytest.mark.asyncio
    async def test_analyze_lifestyle_article_audience(self, analyzer, lifestyle_article_content, real_llm):
        """Test audience analysis for lifestyle article with real LLM"""
        # Skip if no API key is available
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")
        
        # Analyze audience
        analysis = await analyzer.analyze_audience(lifestyle_article_content)
        
        # Verify structure
        assert isinstance(analysis, AudienceAnalysis)
        assert analysis.primary_audience is not None
        
        # Check that lifestyle/wellness interests are identified
        primary = analysis.primary_audience
        lifestyle_keywords = ["health", "wellness", "mindful", "lifestyle", "personal", "self"]
        
        interests_text = " ".join(primary.interests + primary.key_characteristics).lower()
        assert any(
            keyword in interests_text for keyword in lifestyle_keywords
        ), "Should identify lifestyle/wellness-related interests"
        
        # Verify behavioral patterns
        assert "content_consumption" in analysis.behavioral_patterns
        assert "engagement_patterns" in analysis.behavioral_patterns
    
    @pytest.mark.asyncio
    async def test_segment_identification(self, analyzer, tech_article_content, real_llm):
        """Test that multiple audience segments are identified"""
        # Skip if no API key is available
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")
        
        # Analyze audience
        analysis = await analyzer.analyze_audience(tech_article_content)
        
        # Should identify primary and secondary audiences
        assert analysis.primary_audience is not None
        assert len(analysis.secondary_audiences) > 0, "Should identify secondary audiences"
        
        # Each segment should be distinct
        segment_names = [analysis.primary_audience.name] + [s.name for s in analysis.secondary_audiences]
        assert len(segment_names) == len(set(segment_names)), "Segment names should be unique"
        
        # Segments should have different relevance scores
        all_segments = [analysis.primary_audience] + analysis.secondary_audiences
        relevance_scores = [s.relevance_score for s in all_segments]
        assert len(set(relevance_scores)) > 1, "Segments should have varied relevance scores"
    
    @pytest.mark.asyncio
    async def test_reach_potential_calculation(self, analyzer, tech_article_content, real_llm):
        """Test reach potential calculation"""
        # Skip if no API key is available
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")
        
        # Analyze audience
        analysis = await analyzer.analyze_audience(tech_article_content)
        
        # Verify reach potential is calculated
        assert 0 <= analysis.total_reach_potential <= 1.0
        
        # Verify engagement distribution
        assert len(analysis.engagement_distribution) > 0
        
        # Sum of engagement distribution should be approximately 1.0
        total_engagement = sum(analysis.engagement_distribution.values())
        assert 0.95 <= total_engagement <= 1.05, "Engagement distribution should sum to ~1.0"
    
    @pytest.mark.asyncio
    async def test_audience_analysis_caching(self, analyzer, tech_article_content, real_llm):
        """Test that audience analysis results are cached"""
        # Skip if no API key is available
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")
        
        # First analysis
        analysis1 = await analyzer.analyze_audience(tech_article_content)
        
        # Second analysis (should use cache)
        analysis2 = await analyzer.analyze_audience(tech_article_content)
        
        # Results should be the same (from cache)
        assert analysis1.primary_audience.name == analysis2.primary_audience.name
        assert len(analysis1.secondary_audiences) == len(analysis2.secondary_audiences)
        assert analysis1.total_reach_potential == analysis2.total_reach_potential
    
    @pytest.mark.asyncio
    async def test_demographic_insights(self, analyzer, tech_article_content, real_llm):
        """Test demographic insights generation"""
        # Skip if no API key is available
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")
        
        # Analyze audience
        analysis = await analyzer.analyze_audience(tech_article_content)
        
        # Verify demographic insights structure
        demographics = analysis.demographic_insights
        assert "age_distribution" in demographics
        assert "education_levels" in demographics
        assert "professional_fields" in demographics
        assert "geographic_relevance" in demographics
        
        # Age distribution should have percentages
        if isinstance(demographics["age_distribution"], dict):
            total_percentage = sum(
                float(v) for v in demographics["age_distribution"].values()
                if isinstance(v, (int, float))
            )
            assert total_percentage > 0, "Age distribution should have values"
    
    @pytest.mark.asyncio
    async def test_psychographic_insights(self, analyzer, lifestyle_article_content, real_llm):
        """Test psychographic insights generation"""
        # Skip if no API key is available
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available for testing")
        
        # Analyze audience
        analysis = await analyzer.analyze_audience(lifestyle_article_content)
        
        # Verify psychographic insights
        psychographics = analysis.psychographic_insights
        assert "values" in psychographics
        assert "motivations" in psychographics
        assert "lifestyle_preferences" in psychographics
        
        # Values should align with lifestyle content
        values = psychographics.get("values", [])
        assert len(values) > 0, "Should identify values"
        
        # Check for relevant values
        lifestyle_values = ["health", "wellness", "balance", "growth", "mindfulness", "personal"]
        values_text = " ".join(values).lower()
        assert any(
            value in values_text for value in lifestyle_values
        ), "Should identify lifestyle-related values"