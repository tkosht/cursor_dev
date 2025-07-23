# Article Market Simulator (AMS)

A dynamic multi-agent system for simulating and evaluating market reactions to articles through virtual personas.

## Overview

AMS uses LangGraph and LLMs to dynamically generate diverse personas and simulate their reactions to articles, providing valuable insights about potential market reception.

## Architecture

### Core Components

1. **Core Interfaces** (`src/core/`)
   - `IAgent`: Base interface for all agents
   - `IEnvironment`: Simulation environment interface
   - `IAction`: Agent action interface
   - `IPlugin`: Plugin system interface
   - `ISimulation`: Main simulation controller interface

2. **Agent System** (`src/agents/`)
   - **OrchestratorAgent**: Main control agent using LangGraph
   - **AnalysisAgent**: Article analysis (Level 0 context analysis)
   - **PersonaGenerator**: Dynamic 6-layer persona generation
   - **EvaluationAgent**: Persona-based article evaluation
   - **AggregatorAgent**: Result aggregation and scoring
   - **ReporterAgent**: Report generation

3. **Plugin Architecture** (`src/plugins/`)
   - Extensible plugin system for different simulation types
   - Default plugins: Article evaluation, Product launch, Pricing strategy

4. **Visualization** (`src/visualization/`)
   - Real-time WebSocket-based visualization
   - Network graphs, time series, heatmaps
   - Differential updates for performance

## Key Features

- **Dynamic Persona Generation**: No fixed personas - dynamically generated based on article content
- **6-Layer Hierarchical Generation**: From context analysis to fine-grained micro-behaviors
- **Parallel Processing**: Uses LangGraph's Send API for concurrent persona evaluation
- **Real-time Visualization**: WebSocket streaming of simulation progress
- **Plugin Architecture**: Easily extensible for new simulation types
- **LLM Provider Flexibility**: Supports Gemini, OpenAI, Anthropic

## Installation

```bash
# Clone the repository
cd app/ams

# Install dependencies
pip install -e .

# Copy environment configuration
cp .env.example .env
# Edit .env with your API keys
```

## Quick Start

```python
from ams import ArticleMarketSimulator

# Initialize simulator
simulator = ArticleMarketSimulator()

# Configure simulation
config = {
    "article_content": "Your article text here...",
    "population_size": 50,
    "simulation_steps": 10,
    "llm_provider": "gemini"
}

# Run simulation
results = await simulator.run(config)

# Access results
print(results.final_report)
print(results.persona_evaluations)
print(results.aggregated_scores)
```

## Development

### Project Structure

```
app/ams/
├── src/
│   ├── core/           # Core interfaces and base classes
│   ├── agents/         # LangGraph agents
│   ├── plugins/        # Plugin implementations
│   ├── config/         # Configuration management
│   ├── visualization/  # Real-time visualization
│   └── utils/          # Utility functions
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── e2e/           # End-to-end tests
├── docs/              # Documentation
├── examples/          # Example usage
└── pyproject.toml     # Project configuration
```

### Testing

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test markers
pytest -m "unit"  # Unit tests only
pytest -m "integration"  # Integration tests (requires valid API key)

# Run specific test modules
pytest tests/integration/test_llm_connection.py -v
pytest tests/unit/test_llm_transparency.py -v
```

### Development Workflow

1. **Feature Branch**: Always work on feature branches
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Test-Driven Development**: Write tests first
   - Start with unit tests for new components
   - Add integration tests for agent interactions
   - Include e2e tests for full workflows

3. **Code Quality**: Run quality checks before committing
   ```bash
   black src tests
   ruff check src tests
   mypy src
   ```

## Performance Requirements

- Generate 50 personas in 10 seconds
- Complete 50 personas/10 timesteps simulation in 60 seconds
- Real-time visualization updates
- Support for parallel processing

## Configuration

See `.env.example` for all configuration options:

- LLM provider settings (Gemini, OpenAI, Anthropic)
- Performance tuning (max personas, workers, timeouts)
- WebSocket server configuration
- Caching and profiling options

## License

[License information here]

## Contributing

[Contributing guidelines here]