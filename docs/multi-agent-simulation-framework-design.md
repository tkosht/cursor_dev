# Generalized Multi-Agent Simulation Framework Design

## Overview

This document describes a highly abstracted, extensible multi-agent simulation framework designed for real-time market simulations with visualization capabilities. The framework minimizes change points through plugin architecture and event-driven design patterns.

## Core Architecture Principles

### 1. Separation of Concerns

- **Core Engine**: Abstract simulation mechanics, event handling, time management
- **Domain Plugins**: Market-specific logic, behaviors, and rules
- **Visualization Layer**: Real-time streaming and rendering pipeline
- **Data Layer**: Optimized structures for streaming and analysis

### 2. Extension Through Composition

- Plugin-based architecture for simulation types
- Event-driven communication between components
- Interface-based contracts for clean abstractions
- Dependency injection for flexible configuration

## Core Components

### A. Abstract Base Classes and Interfaces

```python
# Core simulation entities
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime
import asyncio
from enum import Enum

T = TypeVar('T')

class SimulationEvent:
    """Base event class for all simulation events"""
    timestamp: datetime
    source_id: str
    event_type: str
    payload: Dict[str, Any]

class IAgent(ABC):
    """Abstract base for all simulation agents"""
    
    @property
    @abstractmethod
    def agent_id(self) -> str:
        pass
    
    @abstractmethod
    async def perceive(self, environment: 'IEnvironment', events: List[SimulationEvent]) -> None:
        """Process incoming events and update internal state"""
        pass
    
    @abstractmethod
    async def decide(self) -> List['IAction']:
        """Make decisions based on current state"""
        pass
    
    @abstractmethod
    async def act(self, environment: 'IEnvironment') -> List[SimulationEvent]:
        """Execute actions and return resulting events"""
        pass

class IAction(ABC):
    """Abstract base for agent actions"""
    
    @abstractmethod
    def validate(self, agent: IAgent, environment: 'IEnvironment') -> bool:
        """Check if action is valid in current context"""
        pass
    
    @abstractmethod
    async def execute(self, agent: IAgent, environment: 'IEnvironment') -> List[SimulationEvent]:
        """Execute the action and return events"""
        pass

class IEnvironment(ABC):
    """Abstract simulation environment"""
    
    @abstractmethod
    async def update(self, timestep: float) -> List[SimulationEvent]:
        """Update environment state"""
        pass
    
    @abstractmethod
    def get_state(self, agent_id: str) -> Dict[str, Any]:
        """Get observable state for an agent"""
        pass
    
    @abstractmethod
    async def apply_action(self, action: IAction, agent: IAgent) -> List[SimulationEvent]:
        """Apply an agent action to the environment"""
        pass

class ISimulationPlugin(ABC):
    """Base interface for simulation type plugins"""
    
    @abstractmethod
    def create_agents(self, config: Dict[str, Any]) -> List[IAgent]:
        """Factory method for creating domain-specific agents"""
        pass
    
    @abstractmethod
    def create_environment(self, config: Dict[str, Any]) -> IEnvironment:
        """Factory method for creating domain-specific environment"""
        pass
    
    @abstractmethod
    def get_metrics_definitions(self) -> Dict[str, Any]:
        """Define domain-specific metrics"""
        pass
```

### B. Event-Driven Architecture

```python
class EventBus:
    """Central event distribution system"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[SimulationEvent] = []
        self._stream_handlers: List[Callable] = []
    
    async def publish(self, event: SimulationEvent) -> None:
        """Publish event to all subscribers"""
        self._event_history.append(event)
        
        # Notify specific subscribers
        if event.event_type in self._subscribers:
            for handler in self._subscribers[event.event_type]:
                await handler(event)
        
        # Notify stream handlers for real-time visualization
        for handler in self._stream_handlers:
            await handler(event)
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to specific event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def add_stream_handler(self, handler: Callable) -> None:
        """Add handler for real-time event streaming"""
        self._stream_handlers.append(handler)

class SimulationClock:
    """Manages simulation time and scheduling"""
    
    def __init__(self, tick_rate: float = 0.1):
        self.current_time: float = 0.0
        self.tick_rate = tick_rate
        self.scheduled_events: List[Tuple[float, SimulationEvent]] = []
    
    async def advance(self) -> List[SimulationEvent]:
        """Advance simulation time and return due events"""
        self.current_time += self.tick_rate
        
        due_events = []
        remaining_events = []
        
        for scheduled_time, event in self.scheduled_events:
            if scheduled_time <= self.current_time:
                due_events.append(event)
            else:
                remaining_events.append((scheduled_time, event))
        
        self.scheduled_events = remaining_events
        return due_events
    
    def schedule_event(self, event: SimulationEvent, delay: float) -> None:
        """Schedule future event"""
        scheduled_time = self.current_time + delay
        self.scheduled_events.append((scheduled_time, event))
        self.scheduled_events.sort(key=lambda x: x[0])
```

### C. Core Simulation Engine

```python
class SimulationEngine:
    """Main simulation orchestrator"""
    
    def __init__(self, plugin: ISimulationPlugin, config: Dict[str, Any]):
        self.plugin = plugin
        self.config = config
        self.event_bus = EventBus()
        self.clock = SimulationClock(config.get('tick_rate', 0.1))
        
        # Initialize components
        self.agents = plugin.create_agents(config)
        self.environment = plugin.create_environment(config)
        
        # State management
        self.is_running = False
        self.simulation_state = SimulationState()
    
    async def run(self, duration: Optional[float] = None) -> None:
        """Run simulation for specified duration or indefinitely"""
        self.is_running = True
        start_time = self.clock.current_time
        
        while self.is_running:
            # Check duration limit
            if duration and (self.clock.current_time - start_time) >= duration:
                break
            
            # Execute simulation cycle
            await self._simulation_cycle()
            
            # Allow for real-time delays if configured
            if self.config.get('real_time', False):
                await asyncio.sleep(self.clock.tick_rate)
    
    async def _simulation_cycle(self) -> None:
        """Single simulation cycle"""
        # 1. Advance time and get scheduled events
        scheduled_events = await self.clock.advance()
        
        # 2. Update environment
        env_events = await self.environment.update(self.clock.tick_rate)
        
        # 3. Publish all events
        all_events = scheduled_events + env_events
        for event in all_events:
            await self.event_bus.publish(event)
        
        # 4. Agent perception-decision-action cycle
        for agent in self.agents:
            # Perceive
            agent_state = self.environment.get_state(agent.agent_id)
            await agent.perceive(self.environment, all_events)
            
            # Decide
            actions = await agent.decide()
            
            # Act
            for action in actions:
                if action.validate(agent, self.environment):
                    action_events = await self.environment.apply_action(action, agent)
                    for event in action_events:
                        await self.event_bus.publish(event)
        
        # 5. Update metrics
        await self._update_metrics()
    
    async def _update_metrics(self) -> None:
        """Calculate and stream current metrics"""
        metrics = self.plugin.get_metrics_definitions()
        current_metrics = {}
        
        # Calculate domain-specific metrics
        for metric_name, metric_def in metrics.items():
            calculator = metric_def.get('calculator')
            if calculator:
                current_metrics[metric_name] = await calculator(
                    self.agents, 
                    self.environment, 
                    self.event_bus._event_history
                )
        
        # Publish metrics event
        metrics_event = SimulationEvent(
            timestamp=datetime.now(),
            source_id='simulation_engine',
            event_type='metrics_update',
            payload=current_metrics
        )
        await self.event_bus.publish(metrics_event)
```

### D. Data Structures for Streaming

```python
@dataclass
class StreamableState:
    """Optimized state representation for streaming"""
    timestamp: float
    agent_states: Dict[str, Dict[str, Any]]  # Flattened for efficiency
    environment_snapshot: Dict[str, Any]
    metrics: Dict[str, float]
    
    def to_json(self) -> str:
        """Fast JSON serialization"""
        return json.dumps({
            'timestamp': self.timestamp,
            'agents': self.agent_states,
            'environment': self.environment_snapshot,
            'metrics': self.metrics
        })

class SimulationDataStream:
    """Manages data streaming for visualization"""
    
    def __init__(self, buffer_size: int = 1000):
        self.buffer = deque(maxlen=buffer_size)
        self.subscribers: List[Callable] = []
    
    async def push(self, state: StreamableState) -> None:
        """Add state to stream and notify subscribers"""
        self.buffer.append(state)
        
        # Notify all visualization subscribers
        for subscriber in self.subscribers:
            await subscriber(state)
    
    def get_buffer(self, n: Optional[int] = None) -> List[StreamableState]:
        """Get last n states from buffer"""
        if n is None:
            return list(self.buffer)
        return list(itertools.islice(self.buffer, max(0, len(self.buffer) - n), len(self.buffer)))

class VisualizationBridge:
    """Bridge between simulation and visualization layer"""
    
    def __init__(self, engine: SimulationEngine):
        self.engine = engine
        self.data_stream = SimulationDataStream()
        
        # Register as event handler
        engine.event_bus.add_stream_handler(self._handle_event)
    
    async def _handle_event(self, event: SimulationEvent) -> None:
        """Convert events to streamable format"""
        if event.event_type == 'metrics_update':
            # Create streamable state
            state = StreamableState(
                timestamp=self.engine.clock.current_time,
                agent_states=self._collect_agent_states(),
                environment_snapshot=self._get_environment_snapshot(),
                metrics=event.payload
            )
            await self.data_stream.push(state)
    
    def _collect_agent_states(self) -> Dict[str, Dict[str, Any]]:
        """Collect current agent states"""
        return {
            agent.agent_id: agent.get_observable_state()
            for agent in self.engine.agents
        }
    
    def _get_environment_snapshot(self) -> Dict[str, Any]:
        """Get environment snapshot"""
        return self.engine.environment.get_snapshot()
```

## Plugin Architecture Examples

### Example 1: Article Market Simulation Plugin

```python
class ArticleMarketPlugin(ISimulationPlugin):
    """Plugin for article/content market simulation"""
    
    def create_agents(self, config: Dict[str, Any]) -> List[IAgent]:
        agents = []
        
        # Create readers
        for i in range(config.get('num_readers', 100)):
            agents.append(ReaderAgent(
                agent_id=f'reader_{i}',
                preferences=self._generate_preferences(),
                influence_network=self._generate_network()
            ))
        
        # Create content creators
        for i in range(config.get('num_creators', 10)):
            agents.append(ContentCreatorAgent(
                agent_id=f'creator_{i}',
                expertise=self._generate_expertise()
            ))
        
        # Create influencers
        for i in range(config.get('num_influencers', 5)):
            agents.append(InfluencerAgent(
                agent_id=f'influencer_{i}',
                reach=self._generate_reach()
            ))
        
        return agents
    
    def create_environment(self, config: Dict[str, Any]) -> IEnvironment:
        return ContentMarketEnvironment(
            viral_threshold=config.get('viral_threshold', 0.1),
            decay_rate=config.get('decay_rate', 0.05)
        )
    
    def get_metrics_definitions(self) -> Dict[str, Any]:
        return {
            'content_reach': {
                'calculator': self._calculate_reach,
                'aggregation': 'sum'
            },
            'engagement_rate': {
                'calculator': self._calculate_engagement,
                'aggregation': 'average'
            },
            'viral_coefficient': {
                'calculator': self._calculate_viral_coefficient,
                'aggregation': 'max'
            }
        }
```

### Example 2: Product Launch Simulation Plugin

```python
class ProductLaunchPlugin(ISimulationPlugin):
    """Plugin for product launch market simulation"""
    
    def create_agents(self, config: Dict[str, Any]) -> List[IAgent]:
        agents = []
        
        # Create consumers with adoption curves
        for segment in config.get('consumer_segments', []):
            for i in range(segment['size']):
                agents.append(ConsumerAgent(
                    agent_id=f'consumer_{segment["name"]}_{i}',
                    adoption_threshold=segment['adoption_threshold'],
                    budget=self._sample_budget(segment),
                    social_influence=segment.get('social_influence', 0.5)
                ))
        
        # Create competitors
        for i in range(config.get('num_competitors', 3)):
            agents.append(CompetitorAgent(
                agent_id=f'competitor_{i}',
                market_share=config.get('initial_market_share', {}).get(i, 0.1),
                response_strategy=config.get('competitor_strategies', ['aggressive'])[i]
            ))
        
        # Create the launching company
        agents.append(LaunchingCompanyAgent(
            agent_id='launching_company',
            marketing_budget=config.get('marketing_budget', 1000000),
            pricing_strategy=config.get('pricing_strategy', 'penetration')
        ))
        
        return agents
    
    def create_environment(self, config: Dict[str, Any]) -> IEnvironment:
        return MarketEnvironment(
            market_size=config.get('market_size', 1000000),
            growth_rate=config.get('market_growth_rate', 0.05),
            seasonality=config.get('seasonality_factors', {})
        )
```

### Example 3: Pricing Strategy Simulation Plugin

```python
class PricingStrategyPlugin(ISimulationPlugin):
    """Plugin for dynamic pricing strategy simulation"""
    
    def create_agents(self, config: Dict[str, Any]) -> List[IAgent]:
        agents = []
        
        # Create price-sensitive customers
        elasticity_segments = config.get('elasticity_segments', [
            {'name': 'price_sensitive', 'elasticity': -2.0, 'size': 40},
            {'name': 'moderate', 'elasticity': -1.0, 'size': 40},
            {'name': 'premium', 'elasticity': -0.5, 'size': 20}
        ])
        
        for segment in elasticity_segments:
            for i in range(segment['size']):
                agents.append(PriceSensitiveCustomerAgent(
                    agent_id=f'customer_{segment["name"]}_{i}',
                    price_elasticity=segment['elasticity'],
                    reference_price=config.get('initial_price', 100),
                    purchase_frequency=self._sample_frequency()
                ))
        
        # Create competing retailers
        for i in range(config.get('num_retailers', 5)):
            agents.append(RetailerAgent(
                agent_id=f'retailer_{i}',
                pricing_algorithm=config.get('pricing_algorithms', ['rule_based'])[i],
                inventory_capacity=config.get('inventory_capacity', 1000),
                cost_structure=self._generate_cost_structure()
            ))
        
        return agents
```

## Real-Time Visualization Integration

```python
class VisualizationServer:
    """WebSocket server for real-time visualization"""
    
    def __init__(self, bridge: VisualizationBridge, port: int = 8765):
        self.bridge = bridge
        self.port = port
        self.clients: Set[websocket.WebSocketServerProtocol] = set()
        
        # Subscribe to data stream
        bridge.data_stream.subscribers.append(self._broadcast_state)
    
    async def _broadcast_state(self, state: StreamableState) -> None:
        """Broadcast state to all connected clients"""
        if self.clients:
            message = state.to_json()
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
    
    async def handle_client(self, websocket, path):
        """Handle new client connection"""
        self.clients.add(websocket)
        try:
            # Send initial state
            buffer = self.bridge.data_stream.get_buffer(100)
            for state in buffer:
                await websocket.send(state.to_json())
            
            # Keep connection alive
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
    
    async def start(self):
        """Start WebSocket server"""
        async with websockets.serve(self.handle_client, "localhost", self.port):
            await asyncio.Future()  # Run forever
```

## Usage Example

```python
async def run_article_market_simulation():
    """Example: Running an article market simulation"""
    
    # Configuration
    config = {
        'tick_rate': 0.1,  # 100ms per tick
        'real_time': True,
        'num_readers': 1000,
        'num_creators': 20,
        'num_influencers': 10,
        'viral_threshold': 0.15,
        'decay_rate': 0.02
    }
    
    # Create simulation
    plugin = ArticleMarketPlugin()
    engine = SimulationEngine(plugin, config)
    
    # Setup visualization
    bridge = VisualizationBridge(engine)
    viz_server = VisualizationServer(bridge)
    
    # Custom event handlers
    async def log_viral_content(event: SimulationEvent):
        if event.event_type == 'content_viral':
            print(f"Content {event.payload['content_id']} went viral!")
    
    engine.event_bus.subscribe('content_viral', log_viral_content)
    
    # Run simulation and visualization server concurrently
    await asyncio.gather(
        engine.run(duration=3600),  # Run for 1 hour simulated time
        viz_server.start()
    )

# Run the simulation
if __name__ == "__main__":
    asyncio.run(run_article_market_simulation())
```

## Extension Points

### 1. Custom Agent Behaviors
- Override `perceive()`, `decide()`, and `act()` methods
- Implement domain-specific decision logic
- Add machine learning models for adaptive behavior

### 2. Environment Dynamics
- Implement custom physics/rules in `update()`
- Add external data feeds
- Create time-based market conditions

### 3. Metrics and Analytics
- Define custom metric calculators
- Add statistical analysis pipelines
- Implement A/B testing frameworks

### 4. Visualization Customization
- Create custom visualization renderers
- Add interactive controls via WebSocket
- Implement 3D visualizations

## Performance Optimization

### 1. Parallel Agent Processing
```python
async def parallel_agent_cycle(agents: List[IAgent], environment: IEnvironment):
    """Process agents in parallel for better performance"""
    tasks = []
    for agent in agents:
        tasks.append(agent_cycle(agent, environment))
    
    results = await asyncio.gather(*tasks)
    return results
```

### 2. Event Batching
```python
class BatchedEventBus(EventBus):
    """Batch events for efficient processing"""
    
    def __init__(self, batch_size: int = 100):
        super().__init__()
        self.batch_size = batch_size
        self.pending_events: List[SimulationEvent] = []
    
    async def publish(self, event: SimulationEvent) -> None:
        self.pending_events.append(event)
        
        if len(self.pending_events) >= self.batch_size:
            await self._flush_events()
    
    async def _flush_events(self) -> None:
        """Process all pending events in batch"""
        # Process events in batch for efficiency
        for event in self.pending_events:
            await super().publish(event)
        self.pending_events.clear()
```

## Integration Patterns

### 1. External Data Integration
```python
class DataFeedIntegration:
    """Integrate real-world data feeds"""
    
    async def fetch_market_data(self) -> Dict[str, Any]:
        """Fetch real market data"""
        # Integration with market data APIs
        pass
    
    async def inject_into_simulation(self, engine: SimulationEngine):
        """Inject real data into simulation"""
        data = await self.fetch_market_data()
        event = SimulationEvent(
            timestamp=datetime.now(),
            source_id='external_data',
            event_type='market_update',
            payload=data
        )
        await engine.event_bus.publish(event)
```

### 2. Machine Learning Integration
```python
class MLAgentBehavior:
    """ML-powered agent decision making"""
    
    def __init__(self, model_path: str):
        self.model = self.load_model(model_path)
    
    async def predict_action(self, state: Dict[str, Any]) -> IAction:
        """Use ML model to predict best action"""
        features = self.extract_features(state)
        prediction = self.model.predict(features)
        return self.map_to_action(prediction)
```

## Conclusion

This framework provides a flexible, extensible foundation for multi-agent market simulations with real-time visualization. The plugin architecture allows for easy customization while maintaining a clean separation of concerns. The event-driven design enables efficient real-time updates and visualization streaming.

Key benefits:
- Minimal change points through abstraction
- Easy extension via plugins
- Built-in support for real-time visualization
- Optimized data structures for streaming
- Clear integration patterns for various use cases

The framework can be adapted for any market simulation scenario by implementing appropriate plugins and customizing the visualization layer.