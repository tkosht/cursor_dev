# タスク完了整合性ルール（必須遵守）

## KEYWORDS: task-completion, integrity, background-tasks, continuation-tasks, completion-criteria, mandatory-rule
## DOMAIN: meta-process|task-management|completion-verification
## PRIORITY: MANDATORY
## WHEN: 全タスク完了判断時、継続プロセス実行時、完了報告前
## NAVIGATION: CLAUDE.md → PRE_TASK_PROTOCOL → task completion verification → this file

## RULE: 継続中・バックグラウンドタスクが完了するまで、メインタスクは「未完了」とする

## ABSOLUTE COMPLETION CRITERIA (絶対完了基準)

### 🚨 MANDATORY RULE: 継続タスク完了原則
```bash
COMPLETION_DEFINITION=(
    "COMPLETE = ALL tasks including background/continuation tasks finished"
    "INCOMPLETE = ANY task still running, pending, or in progress"
    "NO_PARTIAL_COMPLETION = Cannot claim completion with active background tasks"
    "VERIFICATION_REQUIRED = All completion claims must be verified"
)

# 完了判断フロー
COMPLETION_VERIFICATION_FLOW=(
    "1. Main task status check"
    "2. Background task status check" 
    "3. Continuation task status check"
    "4. External dependency completion check"
    "5. ALL must be COMPLETE before claiming completion"
)
```

### 📋 Background Task Categories (バックグラウンドタスク分類)
```bash
BACKGROUND_TASK_TYPES=(
    "Cognee operations (cognify, search indexing)"
    "Database operations (setup, migration, backup)"
    "File system operations (large file processing)"
    "Network operations (downloads, uploads, API calls)"
    "Build processes (compilation, testing, deployment)"
    "Async operations (queued tasks, scheduled jobs)"
)

# 各タイプの完了確認方法
VERIFICATION_METHODS=(
    "Cognee: mcp__cognee__cognify_status + search test"
    "Database: Connection test + query execution"  
    "File system: File existence + integrity check"
    "Network: Response validation + error checking"
    "Build: Exit code + output verification"
    "Async: Queue status + job completion status"
)
```

### ⏳ Continuation Task Monitoring (継続タスク監視)
```bash
CONTINUATION_MONITORING_PROTOCOL=(
    "NEVER claim completion while tasks are 'in progress'"
    "NEVER assume background tasks will complete successfully"
    "ALWAYS verify completion before final status report"
    "ALWAYS provide estimated completion time if known"
    "ALWAYS offer alternative approaches if tasks fail"
)

# 監視実装例
function verify_all_tasks_complete() {
    local incomplete_tasks=()
    
    # Cognee check
    if ! mcp__cognee__search "test" CHUNKS >/dev/null 2>&1; then
        incomplete_tasks+=("Cognee restoration")
    fi
    
    # Background processes check
    if pgrep -f "background_process" >/dev/null; then
        incomplete_tasks+=("Background processes")
    fi
    
    # Async task check
    if [ -f "/tmp/async_tasks_running" ]; then
        incomplete_tasks+=("Async operations")
    fi
    
    if [ ${#incomplete_tasks[@]} -eq 0 ]; then
        echo "✅ ALL TASKS COMPLETE"
        return 0
    else
        echo "⏳ INCOMPLETE TASKS: ${incomplete_tasks[*]}"
        return 1
    fi
}
```

## VIOLATION CONSEQUENCES (違反時の結果)

### 🚨 False Completion Reporting (偽完了報告)
```bash
FALSE_COMPLETION_VIOLATIONS=(
    "Claiming 'complete' while background tasks running"
    "Ignoring continuation task status"
    "Assuming 'probably completed' without verification"
    "Reporting partial completion as full completion"
)

VIOLATION_CONSEQUENCES=(
    "IMMEDIATE task status downgrade to 'IN_PROGRESS'"
    "MANDATORY re-verification of all task components"
    "ADDITIONAL monitoring until true completion"
    "DOCUMENTATION of violation for process improvement"
)
```

### 📋 Recovery Process (復旧プロセス)
```bash
VIOLATION_RECOVERY_STEPS=(
    "1. ACKNOWLEDGE: Admit incomplete status immediately"
    "2. IDENTIFY: List all incomplete/continuing tasks"
    "3. MONITOR: Set up proper monitoring for each task"
    "4. VERIFY: Confirm completion of each component"
    "5. REPORT: Provide verified completion status only"
)
```

## IMPLEMENTATION GUIDELINES (実装ガイドライン)

### ✅ Correct Completion Reporting
```bash
# CORRECT examples
echo "⏳ Task in progress: Main functionality complete, Cognee restoration continuing"
echo "⏳ Estimated completion: 15 minutes (database restoration)"
echo "✅ ALL TASKS COMPLETE: Main + background + continuation tasks verified"

# INCORRECT examples  
echo "✅ Task complete" # while background tasks running
echo "✅ Mostly complete" # partial completion claim
echo "✅ Complete (except for...)" # conditional completion
```

### 🔄 Monitoring Implementation
```bash
# Continuous monitoring pattern
while ! verify_all_tasks_complete; do
    echo "⏳ Waiting for task completion..."
    sleep 30
    # Provide progress updates
    check_background_task_progress
done
echo "✅ TRUE COMPLETION: All tasks verified complete"
```

### 📊 Progress Reporting Standards
```bash
PROGRESS_REPORTING_STANDARDS=(
    "SPECIFIC: List exact tasks and their status"
    "HONEST: Never overstate completion percentage"
    "ACTIONABLE: Provide next steps or estimated times"
    "VERIFIABLE: Include verification methods used"
    "COMPLETE: Cover all task components"
)
```

## RELATED VIOLATIONS (関連違反)

### 常見的完了報告違反パターン
1. **背景任務無視**: バックグラウンドタスクを完了報告から除外
2. **推測的完了**: 「たぶん完了した」based on assumptions
3. **部分完了誤報**: 一部完了を全体完了として報告
4. **時間圧力妥協**: 緊急時に完了基準を下げる
5. **技術的回避**: 困難なタスクを「実装済み」として迂回

## ENFORCEMENT PROTOCOL (強制実行プロトコル)

### 🔒 Mandatory Checks Before Completion Claims
```bash
PRE_COMPLETION_CHECKLIST=(
    "[ ] Main task verification complete"
    "[ ] Background task status checked"  
    "[ ] Continuation task status confirmed"
    "[ ] External dependencies verified"
    "[ ] Error conditions handled"
    "[ ] Rollback procedures available"
    "[ ] Documentation updated"
    "[ ] Next steps identified"
)

# Only after ALL items checked: completion claim allowed
```

## RELATED:
- memory-bank/00-core/user_authorization_mandatory.md (Value assessment framework)
- memory-bank/09-meta/progress_recording_mandatory_rules.md (Progress recording standards)
- memory-bank/01-cognee/cognee_reconstruction_successful_procedure.md (45-minute completion protocol)

---

**CRITICAL**: このルールは「利便性 vs 正確性」の誤判断を防ぐための必須ルールです。