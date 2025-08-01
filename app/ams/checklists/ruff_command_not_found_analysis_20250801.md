# Ruff Command Not Found Error Analysis Checklist - 2025-08-01

## Problem Summary
GitHub Actions CI failing with: "Command not found: ruff" after successful dependency installation

## Error Details
```
Run poetry run ruff check app/ tests/
Command not found: ruff
Error: Process completed with exit code 1.
```

## Context
- install dependencies step passed successfully
- Changed from `--with dev,test` to `--with dev` (merged test into dev)
- Local environment works fine

## Analysis Checklist

### 1. Dependency Declaration Analysis
- [x] Check if ruff is in pyproject.toml [tool.poetry.group.dev.dependencies] - FOUND
- [x] Verify ruff version specification - ">=0.3.0"
- [x] Check for any conditional dependencies - None
- [x] Confirm no typos in dependency name - Correct

### 2. Poetry Lock File Verification
- [x] Check if ruff is in poetry.lock - FOUND
- [x] Verify ruff is associated with dev group - Confirmed
- [x] Check for any platform-specific restrictions - None
- [x] Confirm lock file is up to date - Confirmed

### 3. CI Environment Analysis
- [x] Verify Poetry virtual environment activation - Issue found
- [x] Check Poetry install command output - Not in correct directory
- [x] Verify Python version compatibility - OK
- [x] Check working directory in CI - **ROOT CAUSE: Missing working-directory**

### 4. Local Environment Testing
- [x] Test `poetry run ruff --version` locally - Works (0.12.5)
- [x] Verify ruff installation with `poetry show ruff` - Installed
- [x] Check virtual environment path - Correct
- [x] Compare local vs CI environment - CI runs from root, not app/ams

### 5. Potential Root Causes
- [ ] H1: Ruff not properly declared in dependencies - REJECTED
- [ ] H2: Poetry cache issue in CI - REJECTED
- [ ] H3: Virtual environment not activated - REJECTED
- [x] H4: Working directory issue - **CONFIRMED**
- [ ] H5: Poetry version incompatibility - REJECTED

### 6. Solution Options
- [ ] Option 1: Explicit ruff installation in CI - NOT NEEDED
- [ ] Option 2: Clear Poetry cache and reinstall - NOT NEEDED
- [ ] Option 3: Pin Poetry version in CI - NOT NEEDED
- [ ] Option 4: Use different command syntax - NOT NEEDED
- [x] Option 5: Set working-directory in CI - **IMPLEMENTED**

### 7. Implementation Steps
- [x] Identify exact root cause - Working directory mismatch
- [x] Choose appropriate solution - Add working-directory to CI
- [x] Implement fix - Added defaults.run.working-directory
- [x] Test locally - Commands work with correct paths
- [x] Update CI configuration - Updated all paths

### 8. Verification Steps
- [x] Local Poetry install test - Success
- [x] Local ruff execution test - Success
- [x] Unit tests still passing - 106/106 passing
- [x] No regression in functionality - Confirmed

## Solution Summary

The root cause was that GitHub Actions was running Poetry commands from the repository root,
but pyproject.toml and poetry.lock are located in app/ams/. The Poetry virtual environment
was created in app/ams/.venv, so commands couldn't find the installed packages.

**Solution**: Added `defaults.run.working-directory: app/ams` to the CI job configuration
and updated all paths to be relative to app/ams/ directory.

## DAG Debug Tree

```
Root: Command not found: ruff
├── H1: Dependency Declaration Issue
│   ├── Not in dev dependencies
│   ├── Wrong group assignment
│   └── Syntax error in pyproject.toml
├── H2: Poetry Lock Sync Issue
│   ├── Lock file out of sync
│   ├── Platform-specific exclusion
│   └── Cache corruption
├── H3: Virtual Environment Issue
│   ├── Not activated properly
│   ├── Wrong Python version
│   └── Path not in PATH
├── H4: CI-specific Issue
│   ├── Different Poetry behavior
│   ├── Cache problem
│   └── Installation incomplete
└── H5: Recent Changes Impact
    ├── Group merge affected ruff
    ├── Dependencies conflict
    └── Installation order issue
```

## Investigation Commands
```bash
# Check local ruff installation
poetry show ruff
poetry run ruff --version
poetry run which ruff

# Check dependency declaration
grep -n "ruff" pyproject.toml
grep -n "ruff" poetry.lock

# Check Poetry environment
poetry env info
poetry config --list
```