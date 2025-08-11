---
meta:
  name: "Enhanced_DAG_Debugger_with_Serena_Sequential_Runner"
  version: "1.0.0"
  deprecated: true
  supersedes:
    - path: "tasks/dag-debug-enhanced.md"
      version: "2.0.0"
  note: |
    このテンプレートは `tasks/dag-debug-enhanced.md` (v2.0.0) に置き換えられました。
    可能な限り最新のテンプレートを使用してください。
  purpose: >
    超高難度のデバッグ・問題解決を、Serenaのセマンティック理解と
    Sequential Thinkingの段階的推論を組み合わせたDAG探索で遂行。
    厳密な検証基準と回帰テストにより、確実な問題解決を保証する。

execution_model:
  core_flow: |
    1. 初期診断フェーズ (Sequential Thinking)
       → 問題の症状を段階的に分析し、初期仮説群を生成
    
    2. DAG探索フェーズ (DAG + Serena)
       → 各ノードでSerenaのセマンティック分析を実行
       → Sequential Thinkingで思考過程を記録
       → 分岐をサブエージェントで分析実行
    
    3. 検証・確定フェーズ (All Tools)
       → 修正案の実装と全テストスイートの実行
       → デグレード確認と証跡の生成

verification_requirements:
  mandatory_checks:
    - name: "Initial State Capture"
      desc: "問題発生時の完全な状態スナップショット"
      tools: ["mcp__serena__list_dir", "git status", "test results"]
    
    - name: "Root Cause Validation"
      desc: "特定した原因の再現可能な証明"
      criteria:
        - "問題を確実に再現できる最小限のテストケース"
        - "修正により問題が解消することの証明"
        - "他の機能への影響がないことの確認"
    
    - name: "Regression Test Suite"
      desc: "既存機能の動作保証"
      steps:
        - "関連モジュールの全テスト実行"
        - "統合テストの実行"
        - "パフォーマンステスト（必要に応じて）"

node_execution_template:
  structure:
    hypothesis_generation: |
      # Serenaのセマンティック分析を使用
      1. mcp__serena__find_symbol で関連シンボルを特定
      2. mcp__serena__find_referencing_symbols で影響範囲を調査
      3. mcp__serena__get_symbols_overview で全体構造を把握
    
    verification_plan: |
      # Sequential Thinkingで段階的検証
      1. 前提条件の確認
      2. 仮説に基づくテスト設計
      3. 期待される観測結果の定義
      4. 実際の検証実行
      5. 結果の解釈と次ステップ決定
    
    scoring_algorithm: |
      suspicion_score = weighted_sum([
        recent_change_correlation: 0.4,
        code_complexity: 0.2,
        error_pattern_match: 0.3,
        historical_bug_density: 0.1
      ])
      
      cost_estimate = weighted_sum([
        execution_time: 0.3,
        token_usage: 0.3,
        tool_calls: 0.2,
        cognitive_load: 0.2
      ])
      
      priority = (suspicion_score * urgency_factor) / (1 + cost_estimate)

enhanced_features:
  serena_integration:
    - semantic_diff_analysis: |
        # 直近の変更を意味的に分析
        1. git diffの取得
        2. 変更されたシンボルの特定
        3. 依存関係グラフの生成
        4. 影響範囲の推定
    
    - intelligent_search: |
        # コードベース全体から関連箇所を効率的に検索
        - mcp__serena__search_for_pattern で症状関連パターンを検索
        - 発見したパターンから新たな仮説を生成
  
  sequential_thinking_integration:
    - thought_chain_management: |
        # 各ノードの思考プロセスを保存・活用
        - 成功した推論パスの記録
        - 失敗した仮説とその理由の保存
        - 類似問題への知識の転用
    
    - parallel_exploration: |
        # 複数の有望な仮説を並行探索
        - トップ3仮説を同時に検証開始
        - 最初に確定的な結果が出た枝を採用
        - 他の枝の部分的成果も活用

strict_validation_protocol:
  pre_fix_validation:
    - capture_baseline: "現在の全テスト結果を記録"
    - identify_affected_tests: "修正が影響する可能性のあるテストを特定"
    - create_reproduction_test: "問題を確実に再現するテストを作成"
  
  post_fix_validation:
    - verify_fix: "再現テストが成功することを確認"
    - run_unit_tests: "関連ユニットテストの実行"
    - run_integration_tests: "統合テストの実行"
    - performance_check: "パフォーマンス劣化がないことを確認"
    - security_scan: "セキュリティ脆弱性の確認（該当する場合）"
  
  documentation_requirements:
    - root_cause_explanation: "問題の根本原因の詳細な説明"
    - fix_rationale: "修正方法の選択理由"
    - test_coverage: "追加/修正されたテストの説明"
    - rollback_plan: "問題発生時の切り戻し手順"

usage_command: |
  /dag-debug-enhanced <problem_description> [options]
  
  Options:
    --max-depth N         # DAG探索の最大深さ (default: 8)
    --time-limit MINUTES  # 実行時間制限 (default: 30)
    --parallel-width N    # 並行探索する仮説数 (default: 3)
    --test-mode          # ドライランモード（実際の修正は行わない）
    --verbose            # 詳細な思考プロセスを表示
    --focus AREA         # 特定領域に集中 (frontend/backend/db/infra)
    
  Examples:
    # 本番環境のメモリリーク調査
    /dag-debug-enhanced "production memory leak in user service" --focus backend
    
    # フロントエンドのレンダリング問題
    /dag-debug-enhanced "React component not updating after state change" --parallel-width 5
    
    # 複雑な統合問題
    /dag-debug-enhanced "API timeout after recent deployment" --verbose --time-limit 60

  Migration:
    このテンプレートは非推奨です。`tasks/dag-debug-enhanced.md` を参照してください。

output_format:
  summary:
    problem_statement: string
    root_cause: string
    fix_applied: string
    validation_results:
      reproduction_test: {status, details}
      unit_tests: {passed, failed, skipped}
      integration_tests: {passed, failed, skipped}
      regression_tests: {passed, failed, skipped}
      performance_impact: {metrics, comparison}
  
  detailed_report:
    dag_exploration_trace: [nodes_visited, pruning_decisions]
    thought_process_log: [sequential_thinking_steps]
    code_changes: [files, diffs, rationale]
    test_additions: [new_tests, coverage_improvement]
    
  actionable_items:
    immediate_actions: []
    follow_up_tasks: []
    monitoring_recommendations: []
    documentation_updates: []

