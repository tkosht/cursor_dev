# AMS Test Review and Execution Checklist (2025-08-17)

## Scope
- AMS (app/ams/) subproject tests review, alignment with requirements/design, and execution.

## Pre-flight (Mandatory)
- [ ] Confirm knowledge loaded per `docs/01.requirements/ai_agent_execution_rules.md`
- [ ] Ensure on task branch `task/ams-test-review-20250817`
- [ ] Security check: No secrets printed; `.env` not displayed
- [ ] Environment: Poetry available; Python 3.11+

## Requirements/Design Traceability Updates
- [x] Add traceability notes to integration tests
  - [x] `tests/integration/test_orchestrator_integration.py`
  - [x] `tests/integration/test_small_scale_integration.py`
  - [x] `tests/integration/test_llm_connection.py`
- [x] Add traceability notes to key unit tests
  - [x] `tests/unit/test_target_audience_analyzer.py`
- [ ] Spot-check other unit tests for traceability headers

## Test Environment Readiness
- [ ] Verify `.env` or `.env.test` exists without exposing content
- [ ] Ensure one of `GOOGLE_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` is set (skip if not)
- [ ] Set `TEST_MODE=true` for controlled behavior

## Install and Lint
- [ ] `cd app/ams && poetry install`
- [ ] `poetry run ruff check .`
- [ ] `poetry run black --check .`
- [ ] `poetry run mypy src`

## Test Execution
- [ ] Unit tests fast subset: `poetry run pytest -q tests/unit -k 'not llm and not reporter'`
- [ ] Full unit tests (LLM): `poetry run pytest -q tests/unit`
- [ ] Integration (non-LLM-heavy first): `poetry run pytest -q tests/integration -k 'orchestrator_integration'`
- [ ] Integration (LLM connection): `poetry run pytest -q tests/integration/test_llm_connection.py`
- [ ] Small scale end-to-end (may be slow): `poetry run pytest -q tests/integration/test_small_scale_integration.py`

## Failure Handling (DAG)
- [ ] Capture first failing test file/node
- [ ] Identify failure class: CONFIG | NETWORK | SCHEMA | ASSERTION | PERFORMANCE | TIMEOUT
- [ ] For CONFIG: verify provider+API key env, defaults, `config.py` validation
- [ ] For NETWORK: retry once, consider marking `flaky` if intermittent
- [ ] For SCHEMA: align types between `src` and tests, update parser if needed
- [ ] For ASSERTION: verify requirement mapping; adjust code or test accordingly
- [ ] For PERFORMANCE/TIMEOUT: use lightweight mode flags (`force_lightweight=True`) where available

## Post-Execution
- [ ] Save pytest output to `app/ams/test_results/`
- [ ] Summarize failures and create follow-up tasks
- [ ] Commit with Conventional Commit message

## Notes
- Integration/E2E tests use REAL LLM per policy; may skip without API keys.
- Avoid printing secrets; only high-level status in logs.
