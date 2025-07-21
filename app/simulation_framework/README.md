# Generalized Multi-Agent Simulation Framework

A highly abstracted, extensible framework for building various types of market simulations with real-time visualization capabilities. This framework provides a plugin-based architecture that minimizes change points and enables easy customization for different simulation scenarios.

## Features

### Core Architecture

- **Plugin-Based Design**: Easily extend the framework for different market scenarios
- **Event-Driven Architecture**: Efficient real-time updates and communication
- **Abstract Base Classes**: Clean interfaces for agents, actions, and environments
- **Parallel Processing**: Support for both parallel and sequential agent processing
- **Real-Time Visualization**: Built-in WebSocket server for streaming simulation data

### Key Components

1. **Core Abstractions** (`core.py`)
   - `IAgent`: Base interface for all simulation agents
   - `IAction`: Base interface for agent actions
   - `IEnvironment`: Base interface for simulation environments
   - `ISimulationPlugin`: Base interface for simulation type plugins

2. **Simulation Engine** (`engine.py`)
   - `SimulationEngine`: Main orchestrator for running simulations
   - `SimulationController`: Advanced control features (A/B testing, parameter sweeps)
   - Time management with configurable tick rates and time scaling
   - Metrics collection and aggregation

3. **Visualization System** (`visualization.py`)
   - `VisualizationBridge`: Connects simulation to visualization layer
   - `VisualizationServer`: WebSocket server for real-time data streaming
   - `DataExporter`: Export simulation results to JSON/CSV
   - Optimized data structures for efficient streaming

4. **Built-in Plugins**
   - `ProductLaunchPlugin`: Simulates new product market entry
   - `PricingStrategyPlugin`: Simulates competitive pricing dynamics

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd simulation_framework

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```
asyncio
websockets
numpy
matplotlib
dataclasses
typing
json
logging
```

## Quick Start

### Basic Usage

```python
import asyncio
from simulation_framework import SimulationEngine
from simulation_framework.plugins import ProductLaunchPlugin

async def run_simulation():
    # Configuration
    config = {
        'tick_rate': 0.1,  # 100ms per tick
        'time_scale': 10.0,  # 10x speed
        'num_consumers': 1000,
        'marketing_budget': 1000000
    }
    
    # Create and run simulation
    plugin = ProductLaunchPlugin()
    engine = SimulationEngine(plugin, config)
    
    # Run for 30 simulated days
    final_state = await engine.run(duration=720)
    
    # Get metrics
    metrics = engine.get_metrics()
    print(f"Final adoption rate: {metrics['adoption_rate']['current']:.2%}")

asyncio.run(run_simulation())
```

### Real-Time Visualization

```python
from simulation_framework import VisualizationBridge, VisualizationServer

async def run_with_visualization():
    # Setup simulation
    plugin = PricingStrategyPlugin()
    engine = SimulationEngine(plugin, config)
    
    # Setup visualization
    bridge = VisualizationBridge(engine)
    server = VisualizationServer(bridge, port=8765)
    
    # Run both concurrently
    await asyncio.gather(
        engine.run(duration=300),
        server.start()
    )
```

Connect to `ws://localhost:8765` to receive real-time updates.

## Creating Custom Plugins

### Plugin Structure

```python
from simulation_framework.core import ISimulationPlugin, IAgent, IEnvironment

class MyCustomPlugin(ISimulationPlugin):
    def get_plugin_info(self) -> Dict[str, Any]:
        return {
            'name': 'My Custom Simulation',
            'version': '1.0.0',
            'description': 'Description of your simulation'
        }
    
    def create_agents(self, config: Dict[str, Any]) -> List[IAgent]:
        # Create your custom agents
        agents = []
        for i in range(config.get('num_agents', 100)):
            agents.append(MyCustomAgent(f"agent_{i}"))
        return agents
    
    def create_environment(self, config: Dict[str, Any]) -> IEnvironment:
        # Create your custom environment
        return MyCustomEnvironment(config)
    
    def get_metrics_definitions(self) -> Dict[str, Any]:
        # Define custom metrics
        return {
            'my_metric': {
                'calculator': self._calculate_my_metric,
                'aggregator': lambda x: sum(x) / len(x) if x else 0
            }
        }
```

### Custom Agent Implementation

```python
class MyCustomAgent(IAgent):
    async def perceive(self, environment: IEnvironment, events: List[SimulationEvent]):
        # Process events and update internal state
        for event in events:
            if event.event_type == "relevant_event":
                self.process_event(event)
    
    async def decide(self) -> List[IAction]:
        # Make decisions based on state
        if self.should_act():
            return [MyCustomAction()]
        return []
    
    async def act(self, environment: IEnvironment) -> List[SimulationEvent]:
        # Execute actions
        events = []
        for action in self._action_queue:
            events.extend(await action.execute(self, environment))
        return events
```

## Advanced Features

### Parameter Sweeps

```python
controller = SimulationController(engine)
results = await controller.run_parameter_sweep(
    parameter_name='marketing_budget',
    values=[100000, 500000, 1000000],
    base_config=config
)
```

### A/B Testing

```python
results = await controller.run_ab_test(
    config_a={'pricing_strategy': 'penetration'},
    config_b={'pricing_strategy': 'premium'},
    num_runs=10
)
```

### Event Handling

```python
# Subscribe to specific events
async def on_purchase(event: SimulationEvent):
    print(f"Purchase made: {event.payload}")

engine.event_bus.subscribe('product_purchased', on_purchase)
```

### Data Export

```python
from simulation_framework import DataExporter

exporter = DataExporter(bridge)
exporter.export_to_json('results.json')
exporter.export_metrics_to_csv('metrics.csv')
```

## Performance Optimization

### Parallel Agent Processing

```python
config = {
    'parallel_agents': True,  # Process agents in parallel
    'tick_rate': 0.1,
    'max_event_history': 10000  # Limit event history size
}
```

### Batch Event Processing

The framework automatically batches events for efficient processing and streaming.

### Custom Metrics Aggregation

```python
def custom_aggregator(values: List[float]) -> float:
    # Custom aggregation logic
    return np.percentile(values, 95) if values else 0

metrics_def = {
    'p95_response_time': {
        'calculator': calculate_response_time,
        'aggregator': custom_aggregator,
        'window_size': 1000
    }
}
```

## WebSocket API

The visualization server provides a WebSocket API for real-time data:

### Message Types

**From Server:**
```json
{
    "type": "state_update",
    "timestamp": 1234.5,
    "tick": 100,
    "data": {
        "agents": {...},
        "environment": {...},
        "metrics": {...},
        "events": {...}
    }
}
```

**To Server:**
```json
{
    "type": "control",
    "command": "pause",
    "params": {}
}
```

### Available Commands

- `pause`: Pause simulation
- `resume`: Resume simulation
- `stop`: Stop simulation
- `schedule_event`: Schedule a custom event

## Examples

See the `examples/` directory for comprehensive examples:

1. **Product Launch Simulation**: Market adoption dynamics
2. **Pricing Competition**: Multi-retailer pricing strategies
3. **Parameter Sweeps**: Finding optimal parameters
4. **A/B Testing**: Comparing strategies
5. **Real-time Visualization**: WebSocket integration

Run all examples:
```bash
python examples/usage_demo.py
```

## Architecture Benefits

1. **Minimal Change Points**: Core framework rarely needs modification
2. **Easy Extension**: Add new simulation types via plugins
3. **Real-time Capable**: Built for streaming and visualization
4. **Technology Agnostic**: Core abstractions work with any tech stack
5. **Performance Optimized**: Parallel processing and efficient data structures

## Future Extensions

- GraphQL API for more flexible queries
- Built-in machine learning integration
- Distributed simulation support
- Advanced visualization templates
- Plugin marketplace

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details