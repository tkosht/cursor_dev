# Essential Commands Reference

## Work Management Protocol (MANDATORY for all tasks)
```bash
git branch --show-current                   # Check current branch
git checkout -b docs/[content-type]         # Documentation updates
git checkout -b task/[management-type]      # Workflow/process tasks
git checkout -b feature/[functionality]     # New features
git checkout -b fix/[issue-description]     # Bug fixes
git status && git add . && git commit -m "descriptive message"  # Commit workflow
gh pr create --title "Title" --body "Description"  # Create pull request
```

## Development
```bash
poetry install && poetry shell
uvicorn app.a2a_mvp.server.app:app --reload
```

## Testing
```bash
pytest tests/unit/test_skills/test_task_skills.py -v
pytest --cov=app --cov-report=html
```

## Quality
```bash
flake8 app/ tests/ --statistics
black app/ tests/ --check --diff
mypy app/ --show-error-codes
```

## TDD Cycle (Red-Green-Refactor)
1. Write failing test first
2. Minimal implementation 
3. Refactor for quality

## Docker
```bash
make              # Start environment
make bash         # Access container
make clean        # Clean up
```

## Progress Recording (Required)
```bash
ls memory-bank/06-project/progress/           # View all progress files
echo "📋 Rules: memory-bank/09-meta/progress_recording_mandatory_rules.md"
echo "✅ Checklist: memory-bank/09-meta/session_start_checklist.md"
```

## Cognee Strategic Utilization (Knowledge Management)
```bash
mcp__cognee__cognify_status                 # Status check
mcp__cognee__search "query" GRAPH_COMPLETION # Strategic search
mcp__cognee__cognee_add_developer_rules     # Load core knowledge

# Emergency & optimization  
mcp__cognee__prune && sleep 5               # Emergency reset
time mcp__cognee__search "test" CHUNKS      # Performance test
```

## Enhanced Integrated Knowledge Access
```bash
cat memory-bank/02-organization/ai_coordination_comprehensive_guide.md  # Complete AI coordination
cat memory-bank/04-quality/enhanced_review_process_framework.md         # Complete review process
```