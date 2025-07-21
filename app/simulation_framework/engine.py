"""
Simulation engine implementation for the multi-agent simulation framework.

This module provides the main orchestration logic for running simulations.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
import signal
import sys

from .core import (
    IAgent, IEnvironment, ISimulationPlugin, SimulationEvent,
    EventBus, SimulationClock, SimulationState, StreamableState,
    SimulationDataStream, MetricsCollector
)

logger = logging.getLogger(__name__)


class SimulationEngine:
    """Main simulation orchestrator with advanced control features"""
    
    def __init__(self, plugin: ISimulationPlugin, config: Dict[str, Any]):
        self.plugin = plugin
        self.config = config
        
        # Core components
        self.event_bus = EventBus(max_history=config.get('max_event_history', 10000))
        self.clock = SimulationClock(
            tick_rate=config.get('tick_rate', 0.1),
            time_scale=config.get('time_scale', 1.0)
        )
        self.metrics_collector = MetricsCollector()
        
        # Initialize plugin components
        self.agents: List[IAgent] = []
        self.environment: Optional[IEnvironment] = None
        self._initialize_simulation()
        
        # State management
        self.is_running = False
        self.is_paused = False
        self.simulation_state = SimulationState(
            current_time=0.0,
            total_agents=len(self.agents),
            active_agents=len(self.agents),
            total_events=0
        )
        
        # Performance monitoring
        self._cycle_times: List[float] = []
        self._max_cycle_times = 100
        
        # Control flags
        self._stop_requested = False
        self._setup_signal_handlers()
    
    def _initialize_simulation(self) -> None:
        """Initialize simulation components from plugin"""
        try:
            # Create agents
            self.agents = self.plugin.create_agents(self.config)
            logger.info(f"Created {len(self.agents)} agents")
            
            # Create environment
            self.environment = self.plugin.create_environment(self.config)
            logger.info("Environment created")
            
            # Register metrics
            metrics_defs = self.plugin.get_metrics_definitions()
            for metric_name, metric_def in metrics_defs.items():
                self.metrics_collector.register_metric(
                    metric_name,
                    metric_def.get('aggregator'),
                    metric_def.get('window_size', 100)
                )
            logger.info(f"Registered {len(metrics_defs)} metrics")
            
        except Exception as e:
            logger.error(f"Failed to initialize simulation: {e}")
            raise
    
    def _setup_signal_handlers(self) -> None:
        """Setup graceful shutdown handlers"""
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, initiating graceful shutdown...")
            self._stop_requested = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self, duration: Optional[float] = None, max_ticks: Optional[int] = None) -> SimulationState:
        """
        Run simulation for specified duration or number of ticks.
        
        Args:
            duration: Simulation time duration (in simulation time units)
            max_ticks: Maximum number of ticks to run
            
        Returns:
            Final simulation state
        """
        self.is_running = True
        start_time = self.clock.current_time
        start_tick = self.clock.tick_count
        
        logger.info(f"Starting simulation (duration={duration}, max_ticks={max_ticks})")
        
        try:
            while self.is_running and not self._stop_requested:
                # Check termination conditions
                if duration and (self.clock.current_time - start_time) >= duration:
                    logger.info(f"Reached duration limit: {duration}")
                    break
                
                if max_ticks and (self.clock.tick_count - start_tick) >= max_ticks:
                    logger.info(f"Reached tick limit: {max_ticks}")
                    break
                
                # Handle pause
                if self.is_paused:
                    await asyncio.sleep(0.1)
                    continue
                
                # Execute simulation cycle
                cycle_start = asyncio.get_event_loop().time()
                await self._simulation_cycle()
                cycle_time = asyncio.get_event_loop().time() - cycle_start
                
                # Track performance
                self._track_cycle_performance(cycle_time)
                
                # Real-time delay if configured
                if self.config.get('real_time', False):
                    remaining_time = self.clock.tick_rate - cycle_time
                    if remaining_time > 0:
                        await asyncio.sleep(remaining_time)
                    else:
                        logger.warning(f"Simulation lagging: cycle took {cycle_time:.3f}s, target: {self.clock.tick_rate}s")
        
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            raise
        
        finally:
            self.is_running = False
            logger.info("Simulation stopped")
        
        return self.simulation_state
    
    async def _simulation_cycle(self) -> None:
        """Execute a single simulation cycle"""
        try:
            # 1. Advance time and get scheduled events
            scheduled_events = await self.clock.advance()
            
            # 2. Update environment
            env_events = await self.environment.update(self.clock.tick_rate)
            
            # 3. Collect and publish all events
            all_events = scheduled_events + env_events
            for event in all_events:
                await self.event_bus.publish(event)
            
            # 4. Agent perception-decision-action cycle
            agent_events = await self._process_agents(all_events)
            
            # 5. Publish agent events
            for event in agent_events:
                await self.event_bus.publish(event)
            
            # 6. Update metrics
            await self._update_metrics()
            
            # 7. Update simulation state
            self._update_simulation_state()
            
        except Exception as e:
            logger.error(f"Error in simulation cycle: {e}")
            # Publish error event
            error_event = SimulationEvent(
                timestamp=datetime.now(),
                source_id="simulation_engine",
                event_type="simulation_error",
                payload={"error": str(e), "tick": self.clock.tick_count}
            )
            await self.event_bus.publish(error_event)
    
    async def _process_agents(self, events: List[SimulationEvent]) -> List[SimulationEvent]:
        """Process all agents in parallel or sequential based on config"""
        if self.config.get('parallel_agents', True):
            return await self._process_agents_parallel(events)
        else:
            return await self._process_agents_sequential(events)
    
    async def _process_agents_parallel(self, events: List[SimulationEvent]) -> List[SimulationEvent]:
        """Process agents in parallel for better performance"""
        tasks = []
        
        for agent in self.agents:
            task = self._process_single_agent(agent, events)
            tasks.append(task)
        
        # Gather results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and handle exceptions
        all_events = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Agent {self.agents[i].agent_id} error: {result}")
            else:
                all_events.extend(result)
        
        return all_events
    
    async def _process_agents_sequential(self, events: List[SimulationEvent]) -> List[SimulationEvent]:
        """Process agents sequentially (for debugging or deterministic behavior)"""
        all_events = []
        
        for agent in self.agents:
            try:
                agent_events = await self._process_single_agent(agent, events)
                all_events.extend(agent_events)
            except Exception as e:
                logger.error(f"Agent {agent.agent_id} error: {e}")
        
        return all_events
    
    async def _process_single_agent(self, agent: IAgent, events: List[SimulationEvent]) -> List[SimulationEvent]:
        """Process a single agent through perception-decision-action cycle"""
        agent_events = []
        
        # Perceive
        await agent.perceive(self.environment, events)
        
        # Decide
        actions = await agent.decide()
        
        # Act
        for action in actions:
            if action.validate(agent, self.environment):
                try:
                    action_events = await self.environment.apply_action(action, agent)
                    agent_events.extend(action_events)
                except Exception as e:
                    logger.error(f"Action execution error for agent {agent.agent_id}: {e}")
        
        return agent_events
    
    async def _update_metrics(self) -> None:
        """Calculate and record current metrics"""
        metrics_defs = self.plugin.get_metrics_definitions()
        current_metrics = {}
        
        # Calculate domain-specific metrics
        for metric_name, metric_def in metrics_defs.items():
            calculator = metric_def.get('calculator')
            if calculator:
                try:
                    value = await calculator(
                        self.agents,
                        self.environment,
                        self.event_bus.get_event_history(limit=100)
                    )
                    self.metrics_collector.record(
                        metric_name,
                        value,
                        self.clock.current_time
                    )
                    current_metrics[metric_name] = value
                except Exception as e:
                    logger.error(f"Error calculating metric {metric_name}: {e}")
        
        # Add system metrics
        system_metrics = self._calculate_system_metrics()
        for name, value in system_metrics.items():
            self.metrics_collector.record(name, value, self.clock.current_time)
            current_metrics[name] = value
        
        # Publish metrics event
        metrics_event = SimulationEvent(
            timestamp=datetime.now(),
            source_id='simulation_engine',
            event_type='metrics_update',
            payload=current_metrics,
            metadata={'tick': self.clock.tick_count}
        )
        await self.event_bus.publish(metrics_event)
    
    def _calculate_system_metrics(self) -> Dict[str, float]:
        """Calculate system-level metrics"""
        event_metrics = self.event_bus.get_metrics()
        
        return {
            'tick_rate_actual': self._get_actual_tick_rate(),
            'total_events': event_metrics['total_events'],
            'events_per_tick': event_metrics['total_events'] / max(1, self.clock.tick_count),
            'active_agents': len([a for a in self.agents if hasattr(a, 'is_active') and a.is_active]),
            'avg_cycle_time': sum(self._cycle_times) / len(self._cycle_times) if self._cycle_times else 0
        }
    
    def _track_cycle_performance(self, cycle_time: float) -> None:
        """Track cycle performance metrics"""
        self._cycle_times.append(cycle_time)
        if len(self._cycle_times) > self._max_cycle_times:
            self._cycle_times.pop(0)
    
    def _get_actual_tick_rate(self) -> float:
        """Calculate actual tick rate based on performance"""
        if len(self._cycle_times) < 2:
            return self.clock.tick_rate
        
        avg_cycle_time = sum(self._cycle_times) / len(self._cycle_times)
        return 1.0 / avg_cycle_time if avg_cycle_time > 0 else 0
    
    def _update_simulation_state(self) -> None:
        """Update simulation state"""
        self.simulation_state.current_time = self.clock.current_time
        self.simulation_state.total_events = self.event_bus.get_metrics()['total_events']
        self.simulation_state.active_agents = len([
            a for a in self.agents 
            if not hasattr(a, 'is_active') or a.is_active
        ])
    
    # Control methods
    
    def pause(self) -> None:
        """Pause simulation"""
        self.is_paused = True
        logger.info("Simulation paused")
    
    def resume(self) -> None:
        """Resume simulation"""
        self.is_paused = False
        logger.info("Simulation resumed")
    
    def stop(self) -> None:
        """Stop simulation"""
        self.is_running = False
        logger.info("Stop requested")
    
    def get_state(self) -> SimulationState:
        """Get current simulation state"""
        return self.simulation_state
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        return self.metrics_collector.get_all_metrics()
    
    def schedule_event(self, event: SimulationEvent, delay: float) -> None:
        """Schedule a future event"""
        self.clock.schedule_event(event, delay)
    
    def add_agent(self, agent: IAgent) -> None:
        """Add agent to simulation dynamically"""
        self.agents.append(agent)
        self.simulation_state.total_agents = len(self.agents)
        logger.info(f"Added agent {agent.agent_id}")
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove agent from simulation"""
        for i, agent in enumerate(self.agents):
            if agent.agent_id == agent_id:
                self.agents.pop(i)
                self.simulation_state.total_agents = len(self.agents)
                logger.info(f"Removed agent {agent_id}")
                return True
        return False


class SimulationController:
    """Advanced simulation control with multiple run modes"""
    
    def __init__(self, engine: SimulationEngine):
        self.engine = engine
        self._tasks: Set[asyncio.Task] = set()
    
    async def run_batch(self, configs: List[Dict[str, Any]], parallel: bool = True) -> List[SimulationState]:
        """Run multiple simulations with different configurations"""
        if parallel:
            tasks = [self._run_single(config) for config in configs]
            return await asyncio.gather(*tasks)
        else:
            results = []
            for config in configs:
                result = await self._run_single(config)
                results.append(result)
            return results
    
    async def _run_single(self, config: Dict[str, Any]) -> SimulationState:
        """Run single simulation with config override"""
        # Create new engine with modified config
        merged_config = {**self.engine.config, **config}
        engine = SimulationEngine(self.engine.plugin, merged_config)
        
        # Run simulation
        duration = config.get('duration', None)
        max_ticks = config.get('max_ticks', None)
        
        return await engine.run(duration=duration, max_ticks=max_ticks)
    
    async def run_parameter_sweep(
        self,
        parameter_name: str,
        values: List[Any],
        base_config: Optional[Dict[str, Any]] = None
    ) -> Dict[Any, SimulationState]:
        """Run parameter sweep experiments"""
        base_config = base_config or self.engine.config
        results = {}
        
        for value in values:
            config = base_config.copy()
            config[parameter_name] = value
            
            logger.info(f"Running simulation with {parameter_name}={value}")
            result = await self._run_single(config)
            results[value] = result
        
        return results
    
    async def run_ab_test(
        self,
        config_a: Dict[str, Any],
        config_b: Dict[str, Any],
        num_runs: int = 10
    ) -> Dict[str, List[SimulationState]]:
        """Run A/B test with multiple runs"""
        results_a = []
        results_b = []
        
        for i in range(num_runs):
            logger.info(f"A/B test run {i+1}/{num_runs}")
            
            # Run both configs
            result_a = await self._run_single(config_a)
            result_b = await self._run_single(config_b)
            
            results_a.append(result_a)
            results_b.append(result_b)
        
        return {
            'config_a': results_a,
            'config_b': results_b
        }