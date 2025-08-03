"""Performance tests for ReporterAgent."""

import asyncio
import pytest
from typing import List, Dict, Any
from unittest.mock import AsyncMock, MagicMock

from src.agents.reporter import ReporterAgent
from src.core.types import (
    AgentState, AggregatedResults, Metrics, 
    SuggestionPriority, SegmentAnalysis
)


@pytest.mark.performance
class TestReporterPerformance:
    """Performance tests for ReporterAgent."""
    
    @pytest.fixture
    def reporter_agent(self):
        """Create ReporterAgent with mocked LLM for performance testing."""
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="""## Executive Summary
Performance test report generation.

## Key Findings
- Average score: 75
- Main patterns identified
- Recommendations provided"""
        ))
        
        agent = ReporterAgent(
            agent_id="test_reporter",
            llm=mock_llm,
            config={}
        )
        return agent
    
    def create_aggregated_results(self, evaluation_count: int) -> AggregatedResults:
        """Create test aggregated results."""
        # Create metrics
        metrics = Metrics(
            average_scores={"overall": 75, "usability": 80, "performance": 70},
            score_distribution={
                "0-20": evaluation_count // 10,
                "21-40": evaluation_count // 5,
                "41-60": evaluation_count // 3,
                "61-80": evaluation_count // 4,
                "81-100": evaluation_count - (evaluation_count // 10 + evaluation_count // 5 + evaluation_count // 3 + evaluation_count // 4)
            },
            total_evaluations=evaluation_count,
            sentiment_distribution={
                "positive": evaluation_count * 0.6,
                "neutral": evaluation_count * 0.3,
                "negative": evaluation_count * 0.1
            },
            response_rate=0.95,
            confidence_level=0.85
        )
        
        # Create suggestion priorities
        priorities = SuggestionPriority(
            high=[f"High priority suggestion {i}" for i in range(min(5, evaluation_count // 100))],
            medium=[f"Medium priority suggestion {i}" for i in range(min(10, evaluation_count // 50))],
            low=[f"Low priority suggestion {i}" for i in range(min(15, evaluation_count // 20))]
        )
        
        # Create segment analysis
        segments = []
        for i in range(min(5, evaluation_count // 200)):
            segment = SegmentAnalysis(
                segment_name=f"Segment {i}",
                characteristics={
                    "size": evaluation_count // 5,
                    "avg_score": 70 + (i * 5),
                    "main_concern": f"Concern {i}"
                },
                specific_insights=[f"Insight {j}" for j in range(3)]
            )
            segments.append(segment)
        
        return AggregatedResults(
            metrics=metrics,
            suggestion_priorities=priorities,
            segment_analysis=segments,
            llm_insights="Performance test insights",
            patterns_identified=[f"Pattern {i}" for i in range(min(10, evaluation_count // 100))]
        )
    
    @pytest.mark.benchmark(group="reporter-throughput")
    @pytest.mark.asyncio
    async def test_generate_report_small(self, reporter_agent, benchmark):
        """Benchmark report generation for small dataset (10 evaluations)."""
        aggregated_results = self.create_aggregated_results(10)
        state = AgentState(aggregated_results=aggregated_results)
        
        async def run_report_generation():
            result = await reporter_agent.generate_report(state)
            return result
        
        result = await benchmark.pedantic(
            run_report_generation,
            rounds=5,
            iterations=3,
            warmup_rounds=2
        )
        
        assert "final_report" in result
        assert result["final_report"]["executive_summary"]
    
    @pytest.mark.benchmark(group="reporter-throughput")
    @pytest.mark.asyncio
    async def test_generate_report_medium(self, reporter_agent, benchmark):
        """Benchmark report generation for medium dataset (100 evaluations)."""
        aggregated_results = self.create_aggregated_results(100)
        state = AgentState(aggregated_results=aggregated_results)
        
        async def run_report_generation():
            result = await reporter_agent.generate_report(state)
            return result
        
        result = await benchmark.pedantic(
            run_report_generation,
            rounds=3,
            iterations=2,
            warmup_rounds=1
        )
        
        assert "final_report" in result
    
    @pytest.mark.benchmark(group="reporter-throughput")
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_generate_report_large(self, reporter_agent, benchmark):
        """Benchmark report generation for large dataset (1000 evaluations)."""
        aggregated_results = self.create_aggregated_results(1000)
        state = AgentState(aggregated_results=aggregated_results)
        
        async def run_report_generation():
            result = await reporter_agent.generate_report(state)
            return result
        
        result = await benchmark.pedantic(
            run_report_generation,
            rounds=2,
            iterations=1,
            warmup_rounds=1
        )
        
        assert "final_report" in result
    
    @pytest.mark.benchmark(group="reporter-formats")
    @pytest.mark.asyncio
    async def test_format_conversion_performance(self, reporter_agent, benchmark):
        """Benchmark different report format conversions."""
        aggregated_results = self.create_aggregated_results(100)
        state = AgentState(aggregated_results=aggregated_results)
        
        # Generate base report first
        base_result = await reporter_agent.generate_report(state)
        report_content = base_result["final_report"]
        
        formats = ["json", "markdown", "html"]
        format_times = {}
        
        for fmt in formats:
            async def format_report():
                formatted = reporter_agent._format_report(report_content, fmt)
                return formatted
            
            result = benchmark.pedantic(
                format_report,
                rounds=10,
                iterations=5,
                warmup_rounds=2
            )
            
            format_times[fmt] = benchmark.stats["mean"]
        
        # JSON should be fastest (native), markdown second, HTML slowest
        assert format_times["json"] < format_times["html"]
    
    @pytest.mark.asyncio
    async def test_memory_efficiency_formats(self, reporter_agent, performance_metrics):
        """Test memory efficiency of different report formats."""
        aggregated_results = self.create_aggregated_results(1000)
        state = AgentState(aggregated_results=aggregated_results)
        
        # Generate base report
        base_result = await reporter_agent.generate_report(state)
        
        memory_results = {}
        
        for fmt in ["json", "markdown", "html"]:
            with performance_metrics() as metrics:
                formatted = reporter_agent._format_report(base_result["final_report"], fmt)
                # Force string conversion to measure actual memory
                _ = str(formatted) if fmt == "json" else formatted
            
            memory_results[fmt] = metrics.memory_delta / 1024 / 1024
        
        # HTML should use most memory due to tags
        assert memory_results["json"] < memory_results["html"]
    
    @pytest.mark.benchmark(group="reporter-scaling")
    @pytest.mark.asyncio
    async def test_visualization_data_scaling(self, reporter_agent, benchmark):
        """Test visualization data preparation performance scaling."""
        test_sizes = [10, 100, 500]
        scaling_results = []
        
        for size in test_sizes:
            aggregated_results = self.create_aggregated_results(size)
            state = AgentState(aggregated_results=aggregated_results)
            
            async def prepare_viz_data():
                result = await reporter_agent.generate_report(state)
                return result["final_report"].get("visualization_data", {})
            
            benchmark.pedantic(
                prepare_viz_data,
                rounds=3,
                iterations=2,
                warmup_rounds=1
            )
            
            scaling_results.append({
                "size": size,
                "time": benchmark.stats["mean"]
            })
        
        # Verify roughly linear scaling
        for i in range(1, len(scaling_results)):
            time_ratio = scaling_results[i]["time"] / scaling_results[i-1]["time"]
            size_ratio = scaling_results[i]["size"] / scaling_results[i-1]["size"]
            # Allow up to 50% overhead for larger sizes
            assert time_ratio < size_ratio * 1.5