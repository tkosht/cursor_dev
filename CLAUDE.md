# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status Overview

**Project**: New Development Project  
**Status**: 🚀 Initial Setup Complete  
**Coverage**: TBD  
**Tests**: Basic structure ready  
**Quality**: Fresh start with quality standards  

## Common Commands

### Development Environment
```bash
# Start development environment (Docker-based)
make                    # Start containers and install dependencies
make install           # Install poetry and claudecode
make bash              # Access container shell
make clean             # Clean logs, poetry, npm, and containers

# Python environment
poetry shell           # Activate virtual environment
poetry install         # Install dependencies
poetry add <package>   # Add new dependency
```

### Testing and Quality
```bash
# Testing
pytest                 # Run all tests with coverage
pytest -v             # Verbose test output
pytest tests/unit/    # Run only unit tests
pytest tests/integration/  # Run integration tests
pytest tests/e2e/     # Run end-to-end tests
pytest -k "test_name" # Run specific test by name

# Quality checks (REQUIRED before commits)
python scripts/quality_gate_check.py  # Comprehensive quality gate
black app/            # Format code (79 char line length)
flake8 app/           # Lint code (max complexity: 10)
mypy app/ --ignore-missing-imports    # Type checking

# Coverage report
pytest --cov=app --cov-report=html   # Generate HTML coverage report
```

## High-Level Architecture

### Project Structure
```
app/
├── __init__.py           # Package initialization
└── main.py               # Application entry point

tests/                    # Test suite
├── conftest.py          # Pytest configuration
├── unit/                # Unit tests
│   └── test_main.py     # Basic test example
├── integration/         # Integration tests
└── e2e/                # End-to-end tests

backup/                  # Previous project backup
├── a2a_prototype_backup/
└── tests_backup/
```

### Key Technologies
- **Python**: 3.10-3.12
- **Testing**: Pytest with coverage
- **Quality**: Black, Flake8, MyPy
- **Environment**: Docker with VSCode Dev Container
- **Package Manager**: Poetry

## Critical Development Rules

### 🔒 Security Rules (ABSOLUTE VIOLATIONS)
```bash
# NEVER execute these commands:
cat .env                    # ❌ Displays secrets
echo $API_KEY              # ❌ Exposes API keys
grep -r "API" .env         # ❌ Searches secrets
printenv | grep KEY        # ❌ Shows environment secrets

# Safe alternatives:
ls -la .env*               # ✅ Check file existence
[ -f .env ] && echo "exists" # ✅ Verify without display
wc -l .env                 # ✅ Count lines only
```

### 📊 Quality Standards
| Metric | Requirement | Current Status |
|--------|------------|----------------|
| Coverage | ≥85% overall, ≥50% per file | 70.5% ⚠️ |
| Tests | 100% passing | 99.3% (1 failing) ⚠️ |
| Flake8 | 0 violations | 34 violations ⚠️ |
| MyPy | 0 errors | TBD |
| Black | Formatted | Required |

### 🔄 Development Process
1. **Think First**: Use `<thinking/>` tags for reasoning
2. **Search Smart**: Check existing code/issues before implementing
3. **File Safety**: Verify directories exist before file creation
4. **Edit > Create**: Modify existing files rather than creating new ones
5. **Quality Gate**: Run `python scripts/quality_gate_check.py` before commits

### 📝 Git Workflow
```bash
# Branch naming
feature/<issue>-<description>  # New features
fix/<issue>-<description>      # Bug fixes
docs/<issue>-<description>     # Documentation

# Commit format (Conventional Commits)
feat: add new agent skill      # New feature
fix: resolve API timeout       # Bug fix
docs: update setup guide       # Documentation
test: add unit tests          # Testing
refactor: simplify logic      # Code improvement

# Verification commands
git status | cat              # Objective status check
git diff | cat                # Review changes
git log --oneline -5          # Recent history
```

### 🤖 AI-Specific Guidelines

#### Error Handling Excellence
- **SAFETY_FILTER**: Handle Gemini safety blocks gracefully
- **API_KEY_INVALID**: Clear error messages without exposing keys
- **Rate Limits**: Implement exponential backoff
- **Timeouts**: Set reasonable limits (30s default)

#### Analysis Quality Rules
1. **Question Everything**: "Is this implementation appropriate?"
2. **Root Cause Focus**: Don't blame external factors first
3. **Transparent Process**: Show reasoning clearly
4. **Own Mistakes**: Take responsibility and provide fixes
5. **Know Limits**: Suggest alternatives when tools fail

### 📚 Memory Bank Structure
```
memory-bank/
├── Core Context (Always Load)
│   ├── projectbrief.md         # Project mission
│   ├── activeContext.md        # Current focus
│   ├── progress.md             # Status tracking
│   └── rules.md                # Project rules
├── Knowledge Base
│   ├── *_lessons_learned.md    # Past learnings
│   ├── debugging_best_practices.md
│   └── security_incident_knowledge.md
└── research/                    # Investigation results
```

### ⚡ Performance Patterns
- **Async First**: Use async/await for I/O operations
- **Batch Operations**: Group related API calls
- **Error Recovery**: Implement retry with backoff
- **Resource Cleanup**: Always close connections/files
- **Logging**: DEBUG for details, INFO for milestones

### 🎯 Current Priorities
1. **Define Project Goals**: Determine the new project's purpose
2. **Setup Development**: Configure environment and dependencies
3. **Implement Features**: Build core functionality
4. **Maintain Quality**: Follow established standards from day one

### 📋 Project Context
- **Status**: Fresh start ready for new development
- **Previous Work**: A2A protocol research (backed up)
- **Environment**: Docker-based development ready
- **Standards**: Quality gates and rules in place
- **Rule Hierarchy**: rules.mdc → core.mdc → project.mdc