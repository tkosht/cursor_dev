"""Performance tests for Orchestrator concurrent execution."""

import asyncio
import pytest
from typing import List, Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch
from concurrent.futures import ThreadPoolExecutor

from src.agents.orchestrator import OrchestratorAgent
from src.core.types import AgentState


@pytest.mark.performance
class TestOrchestratorPerformance:
    """Performance tests for OrchestratorAgent concurrent execution."""
    
    @pytest.fixture
    def mock_agents(self):
        """Create mock agents for testing."""
        agents = {}
        
        # Mock each agent type with realistic delays
        agent_delays = {
            "population_architect": 0.1,
            "persona_generator": 0.2,
            "analyzer": 0.15,
            "evaluator": 0.25,
            "aggregator": 0.1,
            "reporter": 0.15
        }
        
        for agent_name, delay in agent_delays.items():
            mock_agent = AsyncMock()
            
            async def make_invoke(d):
                await asyncio.sleep(d)  # Simulate processing time
                return {"status": "completed", "data": f"{agent_name}_result"}
            
            mock_agent.ainvoke = make_invoke(delay)
            agents[agent_name] = mock_agent
        
        return agents
    
    @pytest.fixture
    def orchestrator_agent(self, mock_agents):
        """Create OrchestratorAgent with mocked sub-agents."""
        with patch.multiple(
            'src.agents.orchestrator',
            PopulationArchitect=lambda **kwargs: mock_agents["population_architect"],
            PersonaGenerator=lambda **kwargs: mock_agents["persona_generator"],
            AnalyzerAgent=lambda **kwargs: mock_agents["analyzer"],
            EvaluatorAgent=lambda **kwargs: mock_agents["evaluator"],
            AggregatorAgent=lambda **kwargs: mock_agents["aggregator"],
            ReporterAgent=lambda **kwargs: mock_agents["reporter"]
        ):
            orchestrator = OrchestratorAgent(
                agent_id="test_orchestrator",
                llm=AsyncMock(),
                config={"max_concurrent_agents": 4}
            )
            return orchestrator
    
    @pytest.mark.benchmark(group="orchestrator-concurrency")
    @pytest.mark.asyncio
    async def test_sequential_vs_concurrent_execution(self, orchestrator_agent, benchmark):
        """Compare sequential vs concurrent agent execution."""
        state = AgentState(
            task="Performance test task",
            personas=["persona1", "persona2", "persona3"],
            evaluations={"results": []}
        )
        
        # Test concurrent execution
        async def run_concurrent():
            # Simulate running multiple agents concurrently
            tasks = []
            for agent_name in ["analyzer", "evaluator", "aggregator"]:
                task = orchestrator_agent.agents[agent_name].ainvoke(state)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            return results
        
        concurrent_result = await benchmark.pedantic(
            run_concurrent,
            rounds=5,
            iterations=3,
            warmup_rounds=2
        )
        
        # Expected time should be close to max individual time (0.25s)
        # not sum of all times (0.5s)
        assert benchmark.stats["mean"] < 0.35  # Allow some overhead
    
    @pytest.mark.benchmark(group="orchestrator-scaling")
    @pytest.mark.asyncio
    async def test_concurrent_agent_scaling(self, benchmark):
        """Test performance with different numbers of concurrent agents."""
        scaling_results = []
        
        for num_agents in [2, 4, 8, 16]:
            # Create mock agents
            agents = []
            for i in range(num_agents):
                agent = AsyncMock()
                
                async def work():
                    await asyncio.sleep(0.1)  # Simulate work
                    return {"agent_id": i, "result": "done"}
                
                agent.process = work
                agents.append(agent)
            
            async def run_agents():
                tasks = [agent.process() for agent in agents]
                results = await asyncio.gather(*tasks)
                return results
            
            result = benchmark.pedantic(
                run_agents,
                rounds=3,
                iterations=2,
                warmup_rounds=1
            )
            
            scaling_results.append({
                "num_agents": num_agents,
                "mean_time": benchmark.stats["mean"]
            })
        
        # With proper concurrency, time shouldn't increase linearly
        # 16 agents shouldn't take 8x the time of 2 agents
        time_ratio = scaling_results[-1]["mean_time"] / scaling_results[0]["mean_time"]
        assert time_ratio < 3.0  # Should be much less than 8x
    
    @pytest.mark.asyncio
    async def test_resource_contention(self, performance_metrics):
        """Test resource usage under high concurrent load."""
        num_tasks = 50
        
        async def cpu_bound_task(task_id):
            """Simulate CPU-bound work."""
            total = 0
            for i in range(100000):
                total += i * task_id
            return total
        
        async def io_bound_task(task_id):
            """Simulate I/O-bound work."""
            await asyncio.sleep(0.01)
            return f"Task {task_id} completed"
        
        # Test CPU-bound tasks
        with performance_metrics() as cpu_metrics:
            cpu_tasks = [cpu_bound_task(i) for i in range(num_tasks)]
            await asyncio.gather(*cpu_tasks)
        
        # Test I/O-bound tasks
        with performance_metrics() as io_metrics:
            io_tasks = [io_bound_task(i) for i in range(num_tasks)]
            await asyncio.gather(*io_tasks)
        
        # I/O-bound should be more efficient in terms of time
        assert io_metrics.duration < cpu_metrics.duration
        
        # Memory usage should be reasonable for both
        assert cpu_metrics.memory_delta / 1024 / 1024 < 100  # Less than 100MB
        assert io_metrics.memory_delta / 1024 / 1024 < 50   # Less than 50MB
    
    @pytest.mark.benchmark(group="orchestrator-patterns")
    @pytest.mark.asyncio
    async def test_pipeline_vs_batch_processing(self, orchestrator_agent, benchmark):
        """Compare pipeline vs batch processing patterns."""
        num_items = 20
        
        # Pipeline pattern: process items one by one through all stages
        async def pipeline_process():
            results = []
            for i in range(num_items):
                state = AgentState(task=f"Item {i}")
                # Process through each agent sequentially
                for agent_name in ["analyzer", "evaluator", "aggregator"]:
                    state = await orchestrator_agent.agents[agent_name].ainvoke(state)
                results.append(state)
            return results
        
        # Batch pattern: process all items through each stage
        async def batch_process():
            states = [AgentState(task=f"Item {i}") for i in range(num_items)]
            
            # Process all items through each stage
            for agent_name in ["analyzer", "evaluator", "aggregator"]:
                tasks = [orchestrator_agent.agents[agent_name].ainvoke(state) for state in states]
                states = await asyncio.gather(*tasks)
            
            return states
        
        # Benchmark pipeline
        pipeline_time = benchmark.pedantic(
            pipeline_process,
            rounds=2,
            iterations=1,
            warmup_rounds=1
        )
        
        # Benchmark batch
        batch_time = benchmark.pedantic(
            batch_process,
            rounds=2,
            iterations=1,
            warmup_rounds=1
        )
        
        # Batch processing should be significantly faster
        # due to better parallelization
        assert benchmark.stats["mean"] < pipeline_time  # Current run is batch