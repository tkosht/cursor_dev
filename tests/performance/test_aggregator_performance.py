"""Performance tests for AggregatorAgent."""

import asyncio
import pytest
from typing import List, Dict, Any
from unittest.mock import AsyncMock, MagicMock

from src.agents.aggregator import AggregatorAgent
from src.core.types import AgentState, EvaluationResult, AggregatedResults


@pytest.mark.performance
class TestAggregatorPerformance:
    """Performance tests for AggregatorAgent."""
    
    @pytest.fixture
    def aggregator_agent(self):
        """Create AggregatorAgent with mocked LLM for performance testing."""
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content='{"insights": "Performance test insights", "patterns": []}'
        ))
        
        agent = AggregatorAgent(
            agent_id="test_aggregator",
            llm=mock_llm,
            config={}
        )
        return agent
    
    def create_evaluation_results(self, count: int) -> List[EvaluationResult]:
        """Create test evaluation results."""
        results = []
        for i in range(count):
            result = EvaluationResult(
                persona_id=f"persona_{i}",
                ratings={
                    "overall": (i % 10) * 10,
                    "usability": ((i + 2) % 10) * 10,
                    "performance": ((i + 5) % 10) * 10,
                },
                suggestions=[
                    f"Suggestion {i}: Improve feature {chr(65 + (i % 26))}"
                ],
                comments={
                    "positive": f"Great aspect {i}",
                    "negative": f"Could improve {i}" if i % 3 == 0 else "",
                },
                metadata={
                    "timestamp": f"2025-08-03T{10 + (i % 12):02d}:00:00Z"
                }
            )
            results.append(result)
        return results
    
    @pytest.mark.benchmark(group="aggregator-throughput")
    @pytest.mark.asyncio
    async def test_aggregate_10_evaluations(self, aggregator_agent, benchmark):
        """Benchmark aggregation of 10 evaluations."""
        evaluations = self.create_evaluation_results(10)
        state = AgentState(evaluations={"results": evaluations})
        
        async def run_aggregation():
            result = await aggregator_agent.aggregate(state)
            return result
        
        result = await benchmark.pedantic(
            run_aggregation,
            rounds=5,
            iterations=3,
            warmup_rounds=2
        )
        
        assert "aggregated_results" in result
        assert isinstance(result["aggregated_results"], AggregatedResults)
    
    @pytest.mark.benchmark(group="aggregator-throughput")
    @pytest.mark.asyncio
    async def test_aggregate_100_evaluations(self, aggregator_agent, benchmark):
        """Benchmark aggregation of 100 evaluations."""
        evaluations = self.create_evaluation_results(100)
        state = AgentState(evaluations={"results": evaluations})
        
        async def run_aggregation():
            result = await aggregator_agent.aggregate(state)
            return result
        
        result = await benchmark.pedantic(
            run_aggregation,
            rounds=3,
            iterations=2,
            warmup_rounds=1
        )
        
        assert "aggregated_results" in result
    
    @pytest.mark.benchmark(group="aggregator-throughput")
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_aggregate_1000_evaluations(self, aggregator_agent, benchmark):
        """Benchmark aggregation of 1000 evaluations."""
        evaluations = self.create_evaluation_results(1000)
        state = AgentState(evaluations={"results": evaluations})
        
        async def run_aggregation():
            result = await aggregator_agent.aggregate(state)
            return result
        
        result = await benchmark.pedantic(
            run_aggregation,
            rounds=2,
            iterations=1,
            warmup_rounds=1
        )
        
        assert "aggregated_results" in result
    
    @pytest.mark.asyncio
    async def test_memory_usage_scaling(self, aggregator_agent, performance_metrics):
        """Test memory usage scaling with different evaluation counts."""
        memory_results = []
        
        for count in [10, 100, 500, 1000]:
            evaluations = self.create_evaluation_results(count)
            state = AgentState(evaluations={"results": evaluations})
            
            with performance_metrics() as metrics:
                await aggregator_agent.aggregate(state)
            
            memory_results.append({
                "count": count,
                "memory_mb": metrics.memory_delta / 1024 / 1024,
                "duration": metrics.duration
            })
        
        # Verify memory usage doesn't grow exponentially
        for i in range(1, len(memory_results)):
            ratio = memory_results[i]["memory_mb"] / memory_results[i-1]["memory_mb"]
            count_ratio = memory_results[i]["count"] / memory_results[i-1]["count"]
            # Memory should grow roughly linearly with data size
            assert ratio < count_ratio * 1.5, f"Memory usage grew too fast: {ratio}x for {count_ratio}x data"
    
    @pytest.mark.benchmark(group="aggregator-operations")
    @pytest.mark.asyncio
    async def test_outlier_detection_performance(self, aggregator_agent, benchmark):
        """Benchmark outlier detection performance."""
        # Create data with outliers
        evaluations = []
        for i in range(95):
            evaluations.append(EvaluationResult(
                persona_id=f"normal_{i}",
                ratings={"overall": 50 + (i % 20)},  # Normal range: 50-70
                suggestions=[],
                comments={},
                metadata={}
            ))
        
        # Add outliers
        for i in range(5):
            evaluations.append(EvaluationResult(
                persona_id=f"outlier_{i}",
                ratings={"overall": 5 if i < 3 else 95},  # Extreme values
                suggestions=[],
                comments={},
                metadata={}
            ))
        
        state = AgentState(evaluations={"results": evaluations})
        
        async def run_aggregation():
            result = await aggregator_agent.aggregate(state)
            return result
        
        result = await benchmark.pedantic(
            run_aggregation,
            rounds=5,
            iterations=3,
            warmup_rounds=2
        )
        
        # Verify outliers were detected
        assert result["aggregated_results"].metrics.outliers_detected == True
        assert result["aggregated_results"].metrics.outlier_count == 5