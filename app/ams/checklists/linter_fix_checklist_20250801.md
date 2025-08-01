# GitHub Actions Linter Fix Checklist - 2025-08-01

## Issue Summary
- **Ruff linter**: 353 errors (265 fixable automatically)
- **Black formatter**: 32 files need reformatting  
- **MyPy type checker**: Module path conflicts
- **CI Configuration**: Using flake8/isort in CI but ruff/black in project config

## Root Cause Analysis
1. Recent commit `def4123` introduced significant code changes with optimization work
2. CI workflow (`ci.yml`) uses `flake8` and `isort` but project config uses `ruff` and `black`
3. Code formatting and style violations from recent development work
4. MyPy module path conflicts due to package structure

## Systematic Fix Checklist

### Phase 1: Fix CI Configuration Mismatch
- [ ] **1.1** Update `.github/workflows/ci.yml` to use `ruff` instead of `flake8`
- [ ] **1.2** Update `.github/workflows/ci.yml` to use `black` instead of `isort` for formatting
- [ ] **1.3** Add `ruff` and other dev dependencies to CI workflow installation
- [ ] **1.4** Update linter command patterns in CI to match project configuration

### Phase 2: Fix Ruff Linting Issues (353 errors)
- [ ] **2.1** Run `ruff check --fix` to automatically fix 265 fixable issues
- [ ] **2.2** Manually fix remaining issues:
  - [ ] Remove unused imports (F401 errors)
  - [ ] Fix line length violations (E501 errors) 
  - [ ] Rename unused loop variables (B007 errors)
  - [ ] Fix list comprehension inefficiencies (C416 errors)
- [ ] **2.3** Verify all ruff issues are resolved: `ruff check src/ tests/`

### Phase 3: Fix Black Formatting Issues (32 files)
- [ ] **3.1** Run `black src/ tests/` to reformat all files
- [ ] **3.2** Verify formatting: `black --check src/ tests/`

### Phase 4: Fix MyPy Type Checking Issues  
- [ ] **4.1** Fix module path conflicts by using `--explicit-package-bases` flag
- [ ] **4.2** Update mypy configuration in `pyproject.toml` if needed
- [ ] **4.3** Verify type checking: `mypy src/ --ignore-missing-imports --explicit-package-bases`

### Phase 5: Update Project Configuration
- [ ] **5.1** Update `pyproject.toml` ruff configuration to fix deprecation warnings:
  - Move `select` to `lint.select`
- [ ] **5.2** Ensure all linting tool versions are compatible

### Phase 6: Regression Testing
- [ ] **6.1** Run all unit tests: `pytest tests/unit/ -v`
- [ ] **6.2** Run integration tests: `pytest tests/integration/ -v`
- [ ] **6.3** Verify test coverage hasn't degraded: `pytest --cov=src`
- [ ] **6.4** Run complete test suite: `pytest tests/ -v`

### Phase 7: Final Validation
- [ ] **7.1** Run all linters in sequence:
  - [ ] `ruff check src/ tests/`  
  - [ ] `black --check src/ tests/`
  - [ ] `mypy src/ --ignore-missing-imports --explicit-package-bases`
- [ ] **7.2** Simulate CI workflow locally to ensure all checks pass
- [ ] **7.3** Verify no functional regressions by running key integration tests

### Phase 8: Commit and Push  
- [ ] **8.1** Stage all changes: `git add .`
- [ ] **8.2** Create descriptive commit message documenting linter fixes
- [ ] **8.3** Commit changes: `git commit -m "fix: resolve GitHub Actions linter errors and warnings"`
- [ ] **8.4** Push to remote: `git push origin task/ams-development-status-check`

## Expected Outcomes
- All GitHub Actions linter checks pass
- No ruff linting errors (0/353 remaining)
- All files properly formatted with black
- MyPy type checking passes without module conflicts
- CI workflow uses correct linting tools matching project config
- No regression in test functionality or coverage

## Risk Mitigation
- Full test suite execution before committing
- Incremental fixes with verification at each phase
- Backup of current state via git commit history
- Real LLM API testing maintained (no mocking)

## Time Estimation
- Phase 1: 15 minutes (CI config updates)
- Phase 2: 30 minutes (ruff fixes) 
- Phase 3: 5 minutes (black formatting)
- Phase 4: 10 minutes (mypy fixes)
- Phase 5: 5 minutes (config updates)
- Phase 6: 20 minutes (regression testing)
- Phase 7: 10 minutes (final validation)
- Phase 8: 5 minutes (commit/push)
- **Total**: ~100 minutes

## Notes
- Follow mandatory rules: no mocking, fact-based approach, quality-first mindset
- Maintain all existing functionality while fixing style/formatting issues
- Document any unexpected issues discovered during the fix process