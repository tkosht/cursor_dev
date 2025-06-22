# タスク完了整合性ルール（必須遵守） - 拡張版

## KEYWORDS: task-completion, integrity, background-tasks, continuation-tasks, completion-criteria, mandatory-rule, completion-drift-prevention
## DOMAIN: meta-process|task-management|completion-verification|quality-management
## PRIORITY: MANDATORY
## WHEN: 全タスク完了判断時、継続プロセス実行時、完了報告前、タスク開始時
## NAVIGATION: CLAUDE.md → PRE_TASK_PROTOCOL → task completion verification → this file

## RULE 1: 継続中・バックグラウンドタスクが完了するまで、メインタスクは「未完了」とする
## RULE 2: 完了条件ドリフト現象を防止し、初期完了基準を実行中に維持する

## ABSOLUTE COMPLETION CRITERIA (絶対完了基準)

### 🚨 MANDATORY RULE 1: 継続タスク完了原則
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

### 🚨 MANDATORY RULE 2: 完了条件ドリフト防止プロトコル
```bash
# CRITICAL: タスク開始時に完了条件を明確化・記録し、実行中の変更を厳格管理
COMPLETION_CONDITION_RULES=(
    "MUST: 最低限の動作要件 (これが満たされないと未完了)"
    "SHOULD: 品質要件 (通常期待される品質レベル)"
    "COULD: 理想的実装 (時間・リソース許せば実現)"
)

COMPLETION_DRIFT_PREVENTION=(
    "0. 完了条件事前定義: タスク開始前に必ず MUST/SHOULD/COULD を明確化"
    "1. 継続的条件参照: 実行中は定期的に初期完了条件を確認"
    "2. 変更管理厳格化: 完了条件変更時は明示的にユーザー承認を求める"
    "3. 品質劣化阻止: MUST条件の緩和は絶対禁止"
    "4. 受け入れテスト駆動: 完了条件を受け入れテストとして実装"
)

# ENFORCEMENT
NO_COMPLETION_WITHOUT_CRITERIA="完了条件が不明確なタスク実行は禁止"
DRIFT_DETECTION_MANDATORY="完了条件からの乖離を自動検出し警告"
USER_APPROVAL_REQUIRED="完了条件変更は必ずユーザー承認を得る"
```

### 📋 3段階完了条件管理 (階層化品質基準)
```bash
# MUST条件 (絶対必須 - 未達成時は未完了)
MUST_CONDITIONS=(
    "基本動作要件: 指定機能が正常動作する"
    "セキュリティ要件: セキュリティ問題が存在しない"
    "テスト合格: 関連テストが全て合格する"
    "品質ゲート: 最低品質基準をクリアする"
)

# SHOULD条件 (推奨レベル - 通常期待される品質)
SHOULD_CONDITIONS=(
    "コード品質: Clean Code原則準拠"
    "ドキュメント: 必要な説明・コメントが存在"
    "エラーハンドリング: 適切な例外処理"
    "パフォーマンス: 許容範囲内の実行時間"
)

# COULD条件 (理想的実装 - 余裕があれば実現)
COULD_CONDITIONS=(
    "最適化: パフォーマンス最適化"
    "拡張性: 将来の機能拡張を考慮"
    "ユーザビリティ: 使いやすさの向上"
    "イノベーション: 創造的な解決策"
)

# 完了判定基準
COMPLETION_CRITERIA=(
    "MUST条件: 100%達成必須 (1つでも未達成なら未完了)"
    "SHOULD条件: 80%以上達成推奨"
    "COULD条件: 達成すれば加点評価"
)
```

### 🎯 受け入れテスト駆動完了 (ATDC: Acceptance Test Driven Completion)
```bash
# 受け入れテスト必須作成ルール
ACCEPTANCE_TEST_RULES=(
    "事前定義: タスク開始前に受け入れテストを作成"
    "ユーザー合意: 受け入れテストについてユーザーと合意"
    "合格基準明確化: 各テストの合格条件を明確に定義"
    "継続的実行: 実装中は定期的にテストを実行"
    "完了条件統合: 受け入れテスト合格を完了の必要条件とする"
)

# 受け入れテストパターン
ACCEPTANCE_TEST_PATTERNS=(
    "機能テスト: 指定機能が期待通りに動作する"
    "品質テスト: コード品質基準を満たす"
    "統合テスト: 既存システムとの連携が正常"
    "ユーザビリティテスト: ユーザーが期待通りに使用できる"
    "パフォーマンステスト: 性能要件を満たす"
)

# テスト駆動完了プロセス
ATDC_PROCESS=(
    "Red: 受け入れテストを作成（最初は失敗状態）"
    "Green: 受け入れテストが合格する最小実装"
    "Refactor: 品質向上のためのリファクタリング"
    "Verify: 全受け入れテストの最終確認"
    "Complete: 受け入れテスト合格による完了宣言"
)
```

### 🔒 完了条件変更管理プロトコル
```bash
# 変更許可基準
CHANGE_APPROVAL_CRITERIA=(
    "MUST条件変更: ユーザー明示承認 + 理由文書化必須"
    "SHOULD条件変更: ユーザー承認推奨 + 理由説明"
    "COULD条件変更: 内部判断可能だが記録必須"
    "スコープ拡大: 必ずユーザー承認 + 影響評価"
)

# 変更記録フォーマット
CHANGE_RECORD_FORMAT=(
    "変更対象: [MUST/SHOULD/COULD] [具体的条件]"
    "変更理由: [技術的制約/要件変更/発見事項]"
    "影響評価: [品質影響/時間影響/リスク評価]"
    "承認状況: [ユーザー承認済み/内部判断/要承認]"
    "代替案: [他の実現方法/品質確保策]"
)

# 変更防止ルール
CHANGE_PREVENTION=(
    "MUST条件緩和禁止: セキュリティ・基本動作は絶対維持"
    "品質劣化阻止: 品質基準を下げる変更は禁止"
    "スコープクリープ注意: 要求の膨張を適切に管理"
    "時間プレッシャー回避: 急ぎを理由とした品質妥協禁止"
)
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