# dev-flow 進捗管理機能設計書

## 概要
dag-debug-enhancedと統一性のある進捗管理・再開機能を実装し、開発ワークフローの中断・再開を可能にする。

## 設計原則

### 1. 階層的コンテキスト管理（dag-debug-enhancedとの統一）
```yaml
context_management:
  hierarchical_preservation:
    # グローバル不変情報
    global_immutable:
      - task_definition         # タスクの定義
      - branch_name            # 作業ブランチ
      - checklist_path         # チェックリストファイル
      - workflow_configuration  # ワークフロー設定
    
    # フェーズレベル情報
    phase_level:
      phase1_context:
        - test_files_created    # 作成したテストファイル
        - implementation_files  # 実装ファイル
        - checklist_progress   # チェックリスト進捗
        - review_comments      # レビューコメント
      
      phase2_context:
        - debug_history        # デバッグ履歴
        - error_analysis       # エラー解析結果
        - test_improvements    # テスト改善内容
        - knowledge_updates    # 更新したナレッジ
      
      phase3_context:
        - ci_requirements      # CI/CD要件
        - test_results         # テスト実行結果
        - validation_status    # 検証状態
        - final_adjustments    # 最終調整内容
    
    # ステップレベル詳細
    step_level:
      - current_step_id      # 現在のステップID
      - step_status          # ステップ状態
      - partial_results      # 部分的な結果
      - next_actions         # 次のアクション
```

### 2. 状態永続化フォーマット
```yaml
state_persistence:
  file_format:
    location: ".claude/progress/{task_name}_{timestamp}.yaml"
    
    structure:
      metadata:
        task_name: string
        task_description: string    # ユーザーが指定したタスクの説明
        created_at: timestamp
        last_updated: timestamp
        command_args: object        # 全てのコマンドライン引数
        
      execution_state:
        current_phase: 1|2|3
        current_step: string
        status: "in_progress"|"paused"|"completed"|"failed"
        
      phase_states:
        phase1:
          status: string
          completed_steps: []
          pending_steps: []
          artifacts:
            branch_name: string
            test_files: []
            implementation_files: []
            pr_url: string
            
        phase2:
          status: string
          completed_steps: []
          pending_steps: []
          artifacts:
            debug_sessions: []
            fixed_issues: []
            test_improvements: []
            knowledge_updates: []
            
        phase3:
          status: string
          completed_steps: []
          pending_steps: []
          artifacts:
            ci_checks: []
            test_results: {}
            final_commits: []
            
      recovery_data:
        last_successful_action: string
        rollback_points: []
        temporary_files: []
```

### 3. リカバリープロトコル
```yaml
recovery_protocol:
  auto_detection:
    # 既存の進捗ファイルを自動検出
    - scan: ".claude/progress/"
    - match: "task_name pattern"
    - prompt: "既存の進捗を検出しました。続きから再開しますか？"
    
  recovery_steps:
    validate_state:
      - verify_branch_exists
      - check_file_integrity
      - validate_checklist_state
      
    restore_context:
      - load_global_context
      - restore_phase_context
      - reconstruct_step_state
      
    resume_execution:
      - determine_resume_point
      - replay_necessary_setup
      - continue_from_last_step
      
  failure_handling:
    corruption_detected:
      - create_backup
      - attempt_partial_recovery
      - offer_fresh_start
      
    missing_dependencies:
      - identify_missing_items
      - suggest_recovery_actions
      - provide_manual_options
```

### 4. 進捗追跡メカニズム
```yaml
progress_tracking:
  real_time_updates:
    # 各アクション後に自動保存
    trigger_events:
      - step_completed
      - error_occurred
      - user_intervention
      - phase_transition
      
    update_strategy:
      - atomic_writes      # アトミックな書き込み
      - versioning        # バージョン管理
      - compression       # 古い進捗の圧縮
      
  reporting:
    status_command: "/dev-flow --status"
    output_format:
      current_location: "Phase X, Step Y"
      completion_percentage: XX%
      estimated_remaining: "X steps"
      recent_actions: []
      next_steps: []
```

### 5. コマンドインターフェース拡張
```yaml
extended_commands:
  # 通常の新規実行
  - command: "/dev-flow <task_description> [options]"
    description: "新しいタスクを開始"
    example: '/dev-flow "ユーザー認証機能の実装"'
    
  # 続きから再開（task_descriptionは保存されたものを使用）
  - command: "/dev-flow --resume"
    description: "最新の進捗から自動的に再開"
    behavior: "保存されたtask_descriptionとコンテキストを復元"
    
  # 特定の進捗ファイルから再開
  - command: "/dev-flow --resume-from {progress_file}"
    description: "指定した進捗ファイルから再開"
    behavior: "進捗ファイルからtask_descriptionを含む全状態を復元"
    
  # 進捗状態の確認
  - command: "/dev-flow --status [task_name]"
    description: "現在の進捗状態を表示"
    output_includes:
      - task_description
      - current_phase_and_step
      - completion_percentage
    
  # 進捗のリセット
  - command: "/dev-flow --reset <task_description>"
    description: "指定したタスクの進捗をリセット"
    
  # 進捗の一覧表示
  - command: "/dev-flow --list-progress"
    description: "保存されている進捗ファイル一覧"
    output_format: "task_name | task_description | last_updated | status"
```

### 6. チェックリスト連携
```yaml
checklist_integration:
  sync_mechanism:
    # チェックリストの状態を進捗ファイルと同期
    - read_checklist_state
    - update_progress_file
    - mark_completed_items
    
  conflict_resolution:
    # チェックリストと進捗の不整合を解決
    - detect_discrepancies
    - prompt_user_decision
    - merge_states
```

### 7. 実装優先順位
1. **Phase 1**: 基本的な状態保存・読み込み機能
   - 進捗ファイルの作成・更新
   - 基本的な再開機能
   
2. **Phase 2**: 高度なリカバリー機能
   - エラー状態からの復旧
   - 部分的な状態復元
   
3. **Phase 3**: 統合機能
   - チェックリストとの完全同期
   - 複数タスクの並行管理

## 使用例

### 新規タスクの開始
```bash
# ユーザーの指示を引数として受け取る
/dev-flow "ユーザー認証機能の実装"

# オプション付き
/dev-flow "APIエンドポイントの追加" --phase 1 --checklist api_checklist.md
```

### 中断と再開
```bash
# 作業中に中断（進捗は自動保存される）
# ... 作業中断 ...

# 後で再開（task_descriptionは自動的に復元）
/dev-flow --resume

# 出力例:
# 📂 進捗を検出しました: "ユーザー認証機能の実装"
# 🔄 Phase 2, Step 3 から再開します
# ✅ コンテキスト復元完了
```

### 進捗の確認
```bash
/dev-flow --status

# 出力例:
# タスク: "ユーザー認証機能の実装"
# 現在位置: Phase 2 (デバッグ), Step 3/5
# 進捗: 65% 完了
# 最近のアクション:
#   - ✓ テストケースレビュー完了
#   - ✓ エラー解析実施
# 次のステップ:
#   - テスト妥当性検証
```

### 複数タスクの管理
```bash
# 進捗一覧の表示
/dev-flow --list-progress

# 出力例:
# ID | タスク名 | タスク説明 | 最終更新 | 状態
# 1  | auth_impl | ユーザー認証機能の実装 | 2025-08-03 10:30 | Phase2-進行中
# 2  | api_endpoints | APIエンドポイントの追加 | 2025-08-03 09:15 | Phase1-完了
# 3  | db_migration | データベース移行 | 2025-08-02 18:45 | Phase3-進行中
```

## 次のステップ
1. この設計に基づいてdev-flow.mcを更新
2. 進捗ファイルのスキーマ定義
3. リカバリーロジックの実装
4. テストケースの作成