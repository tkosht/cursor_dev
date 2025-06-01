# A2A MVP - Task Management Agent

A practical implementation of Google's A2A (Agent-to-Agent) Protocol using Test-Driven Development approach.

## Features

- ✅ Full CRUD operations for task management
- ✅ A2A protocol compliant
- ✅ RESTful API with FastAPI
- ✅ CLI client for easy interaction
- ✅ 81% test coverage
- ✅ Modular architecture for MVP development

## Quick Start

### Prerequisites

- Python 3.10+
- Poetry (for dependency management)

### Installation

```bash
# Clone the repository
cd /home/devuser/workspace

# Install dependencies
poetry install
```

### Running the Server

```bash
# Activate virtual environment
poetry shell

# Start the A2A server
python -m app.a2a_mvp.server.app
```

The server will start at `http://localhost:8000`

### Using the CLI Client

```bash
# Get agent information
python -m app.a2a_mvp.client.cli info

# Create a task
python -m app.a2a_mvp.client.cli create "Buy groceries" -d "Milk and bread"

# List all tasks
python -m app.a2a_mvp.client.cli list

# Toggle task completion
python -m app.a2a_mvp.client.cli toggle <task_id>

# Update a task
python -m app.a2a_mvp.client.cli update <task_id> --title "New title"

# Delete a task
python -m app.a2a_mvp.client.cli delete <task_id>
```

## API Reference

### GET /
Returns the agent card with capabilities and skills.

### POST /task
Execute task operations.

Request body:
```json
{
  "action": "create|get|list|update|delete|toggle|clear",
  "task_id": "optional-for-some-actions",
  "data": {
    "title": "Task title",
    "description": "Optional description",
    "completed": false
  }
}
```

### POST /a2a/message
Handle A2A protocol messages.

## Architecture

```
├── core/               # Core types and exceptions
├── storage/           # Storage abstraction and implementations
├── skills/            # Business logic skills
├── agents/            # A2A agent implementations
├── server/            # FastAPI server
└── client/            # CLI client
```

## Testing

```bash
# Run all tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=app.a2a_mvp --cov-report=html

# Run specific test module
pytest tests/unit/test_agents/ -v
```

## Development

This project follows Test-Driven Development (TDD) principles:

1. Write tests first
2. Implement minimal code to pass tests
3. Refactor while keeping tests green

## Extending for MVP

The modular architecture allows easy extension:

- **Storage**: Replace `InMemoryStorage` with database implementation
- **Skills**: Add new business logic skills
- **Agents**: Implement additional agents for different domains
- **API**: Add authentication, WebSocket support, etc.

## License

This is a sample implementation for educational purposes.