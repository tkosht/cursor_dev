---
meta:
  name: "Development_Flow_Management_Command"
  version: "1.0.0"
  purpose: >
    開発タスクを3つのフェーズ（初期開発、デバッグ、GitHub Actions対応）で
    体系的に実行するワークフロー管理コマンド。
    テストドリブン・チェックリストドリブンでの設計・実装から
    プルリクエスト発行までを一貫して管理する。

execution_model:
  core_flow: |
    Phase1: 初期開発
    → ブランチ作成とテストドリブン開発
    → チェックリストベースの設計・実装
    → レビューと進捗更新
    → プルリクエスト発行
    
    Phase2: デバッグ
    → テストケース・チェックリストのレビュー反映
    → エラー解析とデバッグ（/dag-debug-enhanced活用）
    → テストの妥当性検証と改善
    → 進捗・ナレッジ更新とコミット
    
    Phase3: GitHub Actions対応
    → CI/CD設定の把握とテスト実行（/dag-debug-enhanced活用）
    → 全テストのチェックリストドリブン実行
    → 進捗管理と知識更新
    → 最終コミット・プッシュ

    Phase4: ナレッジの記録
    → チェックリストドリブン実行
    → Phase1～3 で得られた知見を適切にserena, cognee に記録（/dag-debug-enhanced活用）
    → 最終コミット・プッシュ

phases:
  phase1_initial_development:
    name: "初期開発フェーズ"
    steps:
      - name: "ブランチ作成"
        actions:
          - "git checkout -b feature/[機能名] または task/[タスク名]"
          - "ブランチ作成の確認と作業開始準備"
      
      - name: "テストドリブン開発"
        actions:
          - "要件に基づくテストケースの作成"
          - "失敗するテストの確認"
          - "最小限の実装でテストを通す"
          - "リファクタリング"
      
      - name: "チェックリストドリブン設計・実装"
        actions:
          - "チェックリスト作成（checklists/配下）"
          - "各項目の実装と確認"
          - "進捗の記録"
      
      - name: "レビュー"
        actions:
          - "テストケースの妥当性確認"
          - "チェックリスト項目の網羅性確認"
          - "コードレビュー自己チェック"
      
      - name: "進捗更新"
        actions:
          - "progress/*.mdファイルの更新"
          - "ナレッジの記録（memory-bank/）"
      
      - name: "プルリクエスト発行"
        actions:
          - "git add -A && git commit -m 'feat: [機能説明]'"
          - "git push origin [ブランチ名]"
          - "gh pr create --title '[タイトル]' --body '[説明]'"

  phase2_debug:
    name: "デバッグフェーズ"
    steps:
      - name: "レビュー結果反映"
        actions:
          - "テストケースの改善"
          - "チェックリスト項目の追加・修正"
          - "実装の調整"
      
      - name: "テスト実施とエラー解析"
        protocol: "/dag-debug-enhanced"
        actions:
          - "全テストスイートの実行"
          - "エラー発生時の適切な解析"
          - "根本原因の特定"
          - "修正案の実装と検証"
      
      - name: "テスト妥当性検証"
        protocol: "/dag-debug-enhanced"
        actions:
          - "要件定義との整合性確認"
          - "基本設計との照合"
          - "テストケースの改善"
          - "カバレッジの確認"
      
      - name: "進捗管理"
        actions:
          - task_tracking:
              - "実施完了項目のリスト化"
              - "未完了項目の明確化"
              - "直近の課題と次ステップの特定"
      
      - name: "知識更新"
        actions:
          - "*.mdファイルへの追記"
          - "mcp__serena__write_memoryでの記録"
          - "cogneeへの知識追加"
          - "追加すべきルールの文書化"
      
      - name: "コミット＆プッシュ"
        actions:
          - "git add -A"
          - "git commit -m 'fix: [修正内容]'"
          - "git push origin [ブランチ名]"
          - "プルリクエストの自動更新確認"

  phase3_github_actions:
    name: "GitHub Actions対応フェーズ"
    steps:
      - name: "CI/CD設定把握"
        actions:
          - ".github/workflows/ci.ymlの内容確認"
          - "実行されるテスト・リンターの把握"
          - "必要な環境変数の確認"
      
      - name: "チェックリストドリブン実行"
        actions:
          - "CI/CDチェックリスト作成"
          - "各検証項目の実行"
            - "リンター（ruff, black, mypy等）"
            - "ユニットテスト"
            - "統合テスト"
            - "E2Eテスト"
            - "カバレッジ確認"
      
      - name: "全テスト確認"
        actions:
          - "ローカルでのCI同等テスト実行"
          - "エラー・警告の解消"
          - "パフォーマンス確認"
      
      - name: "進捗管理"
        actions:
          - task_tracking:
              - "CI/CD要件の達成状況"
              - "残課題の明確化"
              - "次アクションの定義"
      
      - name: "最終更新"
        actions:
          - "進捗状況ドキュメント更新"
          - "ナレッジ・ルールの更新"
          - "README等の更新（必要に応じて）"
      
      - name: "最終コミット＆プッシュ"
        actions:
          - "git add -A"
          - "git commit -m 'chore: CI/CD対応完了'"
          - "git push origin [ブランチ名]"
          - "プルリクエストの最終確認"
          - "マージ準備完了の確認"

  phase4_knowledge_recording:
    name: "ナレッジ記録フェーズ"
    steps:
      - name: "ナレッジ収集・整理"
        actions:
          - "Phase1-3で生成された知見の収集"
          - "実装パターンの抽出"
          - "デバッグ手法の整理"
          - "ベストプラクティスの特定"
      
      - name: "チェックリストベースのナレッジ記録"
        actions:
          - "ナレッジ記録チェックリスト作成（checklists/knowledge_recording.md）"
          - checklist_items:
              - "実装パターン記録"
              - "エラー解決パターン記録"
              - "パフォーマンス改善手法記録"
              - "セキュリティ考慮事項記録"
              - "テスト戦略記録"
      
      - name: "Serena統合ナレッジ記録"
        protocol: "/dag-debug-enhanced"
        actions:
          - "mcp__serena__write_memory でのパターン記録"
            - "implementation_patterns: 実装パターンとその効果"
            - "debug_solutions: デバッグ解決策と根本原因"
            - "optimization_techniques: 最適化手法と測定結果"
          - "mcp__serena__find_symbol での既存ナレッジとの関連付け"
          - "mcp__serena__get_symbols_overview での体系的整理"
      
      - name: "Cognee知識ベース更新"
        protocol: "/dag-debug-enhanced"
        actions:
          - "cogneeへの構造化知識の追加"
            - "問題カテゴリと解決策のマッピング"
            - "アンチパターンの記録"
            - "推奨アプローチの文書化"
          - "関連する既存知識との紐付け"
          - "検索可能な形式での保存"
      
      - name: "ドキュメント生成"
        actions:
          - "memory-bank/[タスク名]_learnings.md の作成"
          - "docs/patterns/[パターン名].md の作成"
          - "README.md への重要な知見の追加"
          - "CHANGELOG.md への学習事項の記載"
      
      - name: "知識の検証と品質保証"
        actions:
          - "記録したナレッジの正確性確認"
          - "再現可能性の検証"
          - "他のプロジェクトへの適用可能性評価"
          - "既存ナレッジとの矛盾チェック"
      
      - name: "最終コミット＆プッシュ"
        actions:
          - "git add memory-bank/ docs/patterns/ checklists/"
          - "git commit -m 'docs: ナレッジとパターンの記録'"
          - "git push origin [ブランチ名]"
          - "プルリクエストへのナレッジサマリー追加"

verification_requirements:
  phase1_checks:
    - "ブランチが正しく作成されているか"
    - "テストファーストアプローチが守られているか"
    - "チェックリストが作成・更新されているか"
    - "進捗が記録されているか"
    - "プルリクエストが適切に作成されているか"
  
  phase2_checks:
    - "全テストが通過しているか"
    - "エラー解析が適切に実施されているか"
    - "テストの妥当性が検証されているか"
    - "ナレッジが更新されているか"
    - "コミットメッセージが適切か"
  
  phase3_checks:
    - "CI/CDの全項目をクリアしているか"
    - "ローカルでCI相当のテストが通るか"
    - "ドキュメントが最新化されているか"
    - "プルリクエストがマージ可能な状態か"
  
  phase4_checks:
    - "全フェーズの知見が適切に収集されているか"
    - "ナレッジがSerenaとCogneeに記録されているか"
    - "ドキュメントが生成・更新されているか"
    - "知識の品質と再現性が検証されているか"
    - "他プロジェクトへの適用可能性が評価されているか"

task_tracking_template:
  structure: |
    ## タスク進捗状況
    
    ### 完了項目
    - [ ] 項目1
    - [ ] 項目2
    
    ### 未完了項目
    - [ ] 項目3
    - [ ] 項目4
    
    ### 直近の課題
    - 課題1: [詳細]
    - 課題2: [詳細]
    
    ### 次のステップ
    1. [アクション1]
    2. [アクション2]

knowledge_update_locations:
  markdown_files:
    - "progress/[日付]_[タスク名]_progress.md"
    - "docs/implementation_notes.md"
    - "checklists/[タスク名]_checklist.md"
    - "memory-bank/[タスク名]_learnings.md"
    - "docs/patterns/[パターン名].md"
  
  serena_memories:
    - "[タスク名]_implementation_knowledge"
    - "[タスク名]_debug_patterns"
    - "[タスク名]_best_practices"
    - "[タスク名]_optimization_techniques"
    - "[タスク名]_antipatterns"
  
  cognee_entries:
    - "implementation_patterns"
    - "debug_solutions"
    - "ci_cd_learnings"
    - "performance_optimizations"
    - "security_considerations"

state_management:
  context_preservation:
    global_immutable:
      - task_definition         # タスクの定義
      - task_description       # ユーザーが指定したタスクの説明
      - branch_name            # 作業ブランチ
      - checklist_path         # チェックリストファイル
      - workflow_configuration  # ワークフロー設定
    
    phase_level:
      phase1_context:
        - test_files_created    # 作成したテストファイル
        - implementation_files  # 実装ファイル
        - checklist_progress   # チェックリスト進捗
        - review_comments      # レビューコメント
        - pr_url              # プルリクエストURL
      
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
      
      phase4_context:
        - collected_insights   # 収集した知見
        - pattern_catalog      # パターンカタログ
        - serena_records       # Serena記録内容
        - cognee_entries       # Cognee登録内容
        - documentation_paths  # 生成したドキュメントパス
    
    step_level:
      - current_step_id        # 現在のステップID
      - step_status           # ステップ状態
      - partial_results       # 部分的な結果
      - next_actions          # 次のアクション

progress_persistence:
  file_format:
    location: ".claude/progress/{task_name}_{timestamp}.yaml"
    naming_convention: |
      # タスク名から安全なファイル名を生成
      task_name = task_description.lower()
        .replace(" ", "_")
        .replace(/[^a-z0-9_]/g, "")
        .substring(0, 30)
      timestamp = YYYYMMDD_HHMMSS
    
    schema:
      metadata:
        task_name: string
        task_description: string
        created_at: timestamp
        last_updated: timestamp
        command_args: object
        
      execution_state:
        current_phase: 1|2|3|4
        current_step: string
        status: "in_progress"|"paused"|"completed"|"failed"
        
      phase_states:
        phase1:
          status: "pending"|"in_progress"|"completed"|"skipped"
          completed_steps: []
          pending_steps: []
          artifacts:
            branch_name: string
            test_files: []
            implementation_files: []
            pr_url: string
            
        phase2:
          status: "pending"|"in_progress"|"completed"|"skipped"
          completed_steps: []
          pending_steps: []
          artifacts:
            debug_sessions: []
            fixed_issues: []
            test_improvements: []
            knowledge_updates: []
            
        phase3:
          status: "pending"|"in_progress"|"completed"|"skipped"
          completed_steps: []
          pending_steps: []
          artifacts:
            ci_checks: []
            test_results: {}
            final_commits: []
            
        phase4:
          status: "pending"|"in_progress"|"completed"|"skipped"
          completed_steps: []
          pending_steps: []
          artifacts:
            collected_patterns: []
            serena_memories: []
            cognee_entries: []
            generated_docs: []
            verification_results: {}
            
      recovery_data:
        last_successful_action: string
        rollback_points: []
        temporary_files: []
  
  auto_save_triggers:
    - step_completed
    - phase_transition
    - error_occurred
    - user_interruption
    - checkpoint_reached

recovery_mechanism:
  auto_detection:
    scan_directory: ".claude/progress/"
    detection_logic: |
      1. ディレクトリ内の*.yamlファイルをスキャン
      2. status != "completed" のファイルを抽出
      3. 最新のタイムスタンプを持つファイルを優先
      4. ユーザーに再開の確認を求める
    
  recovery_steps:
    validate_state:
      - verify_branch: "git branch --show-current でブランチ確認"
      - check_files: "進捗ファイルに記録されたファイルの存在確認"
      - validate_checklist: "チェックリストファイルの整合性確認"
      
    restore_context:
      - load_metadata: "タスク情報の復元"
      - restore_phase_state: "フェーズ状態の復元"
      - reconstruct_progress: "進捗状況の再構築"
      
    resume_execution:
      - determine_resume_point: "中断したステップを特定"
      - display_context: "現在の状態をユーザーに表示"
      - continue_workflow: "ワークフローを継続"
  
  error_handling:
    file_corruption:
      action: "バックアップ作成後、部分復旧を試行"
      fallback: "新規開始のオプションを提示"
      
    missing_dependencies:
      action: "不足しているファイル・設定を特定"
      recovery: "手動での復旧手順を提示"

usage:
  command: "/dev-flow <task_description> [options]"
  
  options:
    - name: "--phase"
      value: "PHASE"
      description: "特定フェーズから開始 (1/2/3/4)"
      default: "1"
    
    - name: "--skip-pr"
      description: "プルリクエスト作成をスキップ"
      type: "flag"
    
    - name: "--dry-run"
      description: "ドライランモード（実際の変更を行わない）"
      type: "flag"
    
    - name: "--verbose"
      description: "詳細出力モード"
      type: "flag"
    
    - name: "--checklist"
      value: "PATH"
      description: "既存チェックリストを使用"
      type: "path"
    
    - name: "--resume"
      description: "最新の進捗から自動的に再開"
      type: "flag"
      conflicts_with: ["--phase", "--reset"]
    
    - name: "--resume-from"
      value: "PROGRESS_FILE"
      description: "指定した進捗ファイルから再開"
      type: "path"
      conflicts_with: ["--resume", "--reset"]
    
    - name: "--status"
      description: "現在の進捗状態を表示"
      type: "flag"
      conflicts_with: ["--resume", "--reset"]
    
    - name: "--reset"
      description: "進捗をリセットして最初から開始"
      type: "flag"
      conflicts_with: ["--resume", "--resume-from", "--status"]
    
    - name: "--list-progress"
      description: "保存されている進捗ファイル一覧を表示"
      type: "flag"
      standalone: true
  
  examples:
    - description: "新機能開発の完全フロー実行"
      command: '/dev-flow "ユーザー認証機能の追加"'
      expected_behavior: "Phase1から開始し、4つのフェーズすべてを実行"
    
    - description: "デバッグフェーズから開始"
      command: '/dev-flow "既存バグの修正" --phase 2'
      expected_behavior: "Phase2から開始し、テスト実行とデバッグを実施"
    
    - description: "チェックリスト指定での実行"
      command: '/dev-flow "API統合" --checklist checklists/api_integration.md'
      expected_behavior: "指定されたチェックリストを使用して実行"
    
    - description: "ドライランでの確認"
      command: '/dev-flow "データベース移行" --dry-run --verbose'
      expected_behavior: "実際の変更なしで実行計画を詳細表示"
    
    - description: "PRなしでの実行"
      command: '/dev-flow "内部リファクタリング" --skip-pr'
      expected_behavior: "プルリクエスト作成をスキップして実行"
    
    - description: "CI/CD対応のみ実行"
      command: '/dev-flow "CI修正" --phase 3'
      expected_behavior: "Phase3のGitHub Actions対応のみを実行"
    
    - description: "ナレッジ記録のみ実行"
      command: '/dev-flow "完了タスクの知見記録" --phase 4'
      expected_behavior: "Phase4のナレッジ記録のみを実行"
    
    - description: "中断したタスクの再開"
      command: '/dev-flow --resume'
      expected_behavior: |
        最新の進捗ファイルを自動検出し、中断した箇所から再開
        保存されたコンテキストとタスク説明を復元
    
    - description: "進捗状態の確認"
      command: '/dev-flow --status'
      expected_behavior: |
        現在のタスク、フェーズ、ステップ、完了率を表示
        次のアクションと最近の作業内容を確認
    
    - description: "進捗一覧の表示"
      command: '/dev-flow --list-progress'
      expected_behavior: |
        保存されている全ての進捗ファイルをリスト表示
        各タスクの説明、状態、最終更新日時を確認
    
    - description: "特定の進捗ファイルから再開"
      command: '/dev-flow --resume-from .claude/progress/api_impl_20250803_143000.yaml'
      expected_behavior: "指定された進捗ファイルから作業を再開"

output_format:
  phase_summary:
    phase_name: string
    status: "completed" | "in_progress" | "failed"
    completed_steps: []
    remaining_steps: []
    issues_encountered: []
    
  final_report:
    overall_status: string
    branch_name: string
    pr_url: string
    test_results:
      unit_tests: {passed, failed, total}
      integration_tests: {passed, failed, total}
      coverage: percentage
    knowledge_updates:
      markdown_files: []
      serena_memories: []
      cognee_entries: []
    next_actions: []

checklist_integration:
  auto_create: true
  template_location: "checklists/templates/dev_flow_template.md"
  update_frequency: "after_each_step"
  tracking_format: |
    - [x] 完了項目
    - [ ] 未完了項目
    - [~] 進行中項目

error_handling:
  phase1_errors:
    branch_conflict: "既存ブランチとの競合を解決"
    test_creation_failure: "テストテンプレートの提供"
    
  phase2_errors:
    test_failure: "/dag-debug-enhanced プロトコルで解析"
    coverage_drop: "追加テストケースの提案"
    
  phase3_errors:
    ci_failure: "ローカル再現と修正"
    merge_conflict: "競合解決の支援"
    
  phase4_errors:
    knowledge_conflict: "既存ナレッジとの矛盾を検出・解決"
    serena_write_failure: "代替記録方法の提供とリトライ"
    documentation_generation_failure: "手動テンプレートの提供"

success_criteria:
  phase1:
    - "適切なブランチでの作業"
    - "テストファースト開発の実践"
    - "チェックリストの完全性"
    - "プルリクエストの作成"
    
  phase2:
    - "全テストの通過"
    - "適切なエラー解析と修正"
    - "知識の体系的な記録"
    - "継続的な進捗更新"
    
  phase3:
    - "CI/CD全項目のクリア"
    - "ドキュメントの最新化"
    - "マージ可能な状態の達成"
    - "知識ベースへの貢献"
    
  phase4:
    - "全フェーズの知見の体系的収集"
    - "SerenaとCogneeへの適切な記録"
    - "再利用可能なパターンの文書化"
    - "知識の品質と一貫性の確保"
    - "他プロジェクトへの適用性の確立"
  
  progress_management:
    - "進捗ファイルの自動保存が機能"
    - "中断・再開が正確に動作"
    - "コンテキストの完全な復元"
    - "エラー時の適切なリカバリー"
    - "複数タスクの並行管理が可能"

progress_status_format:
  display_template: |
    ================================
    📋 タスク: {task_description}
    📍 現在位置: Phase {current_phase} - {phase_name}
    📌 ステップ: {current_step} ({completed_steps}/{total_steps})
    📊 進捗: {completion_percentage}% 完了
    
    ✅ 最近の完了項目:
    {recent_completions}
    
    🔄 次のアクション:
    {next_actions}
    
    ⏱️ 最終更新: {last_updated}
    ================================

progress_list_format:
  display_template: |
    ================================
    📂 保存されている進捗ファイル
    ================================
    ID | タスク名 | タスク説明 | 最終更新 | 状態
    ---|---------|-----------|----------|-----
    {progress_entries}
    ================================
    
    💡 ヒント: /dev-flow --resume で最新タスクを再開
    　　　　　 /dev-flow --resume-from [ID].yaml で特定タスクを再開
---