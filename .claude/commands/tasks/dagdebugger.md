meta:
  name: "DAG_Debugger_MetaPrompt"
  version: "0.9.3"
  purpose: >
    複雑・高難度なエラー解析／デバッグを、DAG（木）探索として
    トライ＆エラーで葉まで掘り下げ、効率的にバックトラック・枝刈りしながら遂行する。
    直近変更箇所が原因と推定される場合は、環境前提確認などの低価値分岐を抑制し高速化する。
  requirements: >
    $ARGUMENTS

io:
  inputs:
    - name: problem_context
      desc: 発生しているエラー/症状/ログ/コード断片/直近の編集内容など
    - name: constraints
      desc: 時間/コスト/トークン/利用可能ツール/禁止操作など
    - name: goal_definition
      desc: 解決条件・再現条件・期待される正常動作
    - name: tools
      desc: 呼び出し可能な関数・API・シェル・テストランナー等の仕様
    - name: history
      desc: これまでの試行・既知の原因・既に否定された仮説
  outputs:
    - name: final_fix
      desc: 修正案/パッチ/設定変更/コマンド等の具体的手段
    - name: proof_of_fix
      desc: 再現テスト、ログ、検証結果（Before/After）とその根拠
    - name: decision_trace
      desc: DAG探索の要約（主要分岐・剪定理由・スコアリング結果）

state:
  global_state_schema:
    FRONTIER:  # 展開待ちノード集合
      - node_id
    CLOSED:    # 展開済みノード（確定/棄却）
      - node_id
    SUSPECT_RECENT_EDIT: boolean  # 直近編集が原因かの推定フラグ
    BUDGET:
      token: {max: {{token_budget}}, used: 0}
      tool_calls: {max: {{tool_call_budget}}, used: 0}
      depth: {max: {{max_depth}}, current: 0}
    HEURISTICS:
      recent_edit_weight: 0.6
      impact_weight: 0.25
      severity_weight: 0.15
    LOG: []  # 主要な判断・スコアリング・剪定理由の記録
  node_schema:
    id: auto
    parent: node_id | null
    hypothesis: string          # 原因仮説（Why）
    plan: string                # 何を検証するか（How）
    required_tools: [string]
    expected_signal: string     # 合否判定の観測項目/ログ/テスト結果
    result: string | null       # 実行後の観測結果
    score:
      suspicion: float          # 仮説の有望度（0-1）
      cost_estimate: float      # 予想コスト（小さいほど良い）
      priority: float           # suspicion / cost 等から算出
    status: {OPEN|EXPANDED|PROVED|REJECTED|PRUNED}

algorithms:
  main_loop: |
    1. 初期化:
       - SUSPECT_RECENT_EDIT を推定する:
         * 直近コミット/編集内容から差分行数・影響範囲を評価する（ツール get_git_diff 等）
         * 症状発生時刻とコミット時刻の近さを考慮
         * Heuristicスコア > θ_recent の場合 True
       - ルートノードを生成（全体的なエラー仮説クラス）
       - FRONTIER ← {root}
    2. while FRONTIER が空でない and 目標未達:
       a. node ← SelectNode(FRONTIER):
          * priority 最大のノードを選択（best-first）
       b. Expand(node):
          * HypothesisRefinement(node)
          * 子ノード群を生成（分岐）
          * 各子について ScoreNode(child)
          * Prune(child) で低優先度/冗長枝を削除
          * 可用予算内でテスト/検証の実行をスケジューリング
       c. Execute & Evaluate:
          * 必要ならツールを実行、結果記録
          * expected_signal と result を比較し、PROVED/REJECTED を決定
       d. Update State:
          * node を CLOSED に移動
          * 新規 OPEN 子ノードを FRONTIER に追加
          * BUDGET を更新し、閾値超過なら graceful degrade:
            - 分岐幅縮小、depth制限、より強い剪定
    3. Termination:
       - final_fix が得られたら停止
       - 予算切れや探索打ち切り条件時は、現状最有力仮説と次手順を提案
  node_scoring_formula: |
    suspicion = f_recent_edit * recent_edit_weight
                + f_code_impact * impact_weight
                + f_error_severity * severity_weight
    cost_estimate = normalized(estimated_time + tool_call_cost + token_cost)
    priority = suspicion / (1 + cost_estimate)
  pruning_policy: |
    - SUSPECT_RECENT_EDIT == True の場合:
      * envチェック・依存パッケージ全洗い出し等の「広すぎる枝」を初期フェーズで抑制
      * 代わりに差分行付近の関数/モジュール/設定項目に集中
    - 既に否定された前提を再利用する枝は剪定
    - 類似仮説（テキスト類似度 > τ_sim）の重複枝はまとめて代表一本に統合
    - priority < τ_priority の枝は保持しない
    - 深さ > max_depth の枝は打ち切り（要約生成で別戦略に切替）
  selection_strategy: |
    SelectNode(FRONTIER):
      - best-first (優先度順)
      - 時々（p=ε）で探査的に2-3番手を選び、局所最適回避（ε-greedy）
  backtrack_strategy: |
    - REJECTED/PRUNED された親ノードの兄弟枝を再評価
    - 任意のタイミングで priority 再計算（新情報反映）
  stopping_conditions: |
    - 合理的な修正案が得られ、再現テストでPass
    - 予算上限を超過しそうな場合は、現状の最有力仮説セットと推奨次ステップを出力
    - ユーザが中断/終了を指示

policies:
  tool_use:
    rules:
      - 目的と無関係なツール呼び出しは禁止
      - 冪等でない操作は必ず dry-run 模式で先に検証
      - ログ/テスト結果は必ず state.LOG に記録し、次の判断に反映
  reasoning_log:
    include:
      - 選択した枝と理由
      - 剪定した枝と理由
      - スコア計算の根拠値（recent_edit_weight 等）
    redact:
      - 不要に長いトークン消費を避けるため、詳細ログは必要部分のみ要約
  hallucination_guard:
    - 事実/コマンド/設定値は常にソース（ログ/コード/ドキュメント）と突き合わせ
    - 不確実な場合は "仮説" と明示し、検証手順を伴わせる

templates:
  prompt_blocks:
    system: |
      あなたはDAG探索型デバッグエージェントである。
      以下のYAML仕様に従い、状態管理・分岐生成・検証・剪定・バックトラックを行い、
      最終的な修正案と検証証跡を提示せよ。
    user_context: |
      === Problem Context ===
      {{problem_context}}

      === Constraints ===
      {{constraints}}

      === Goal Definition ===
      {{goal_definition}}

      === Tools Spec ===
      {{tools}}

      === History / Tried ===
      {{history}}
    output_format: |
      必ず以下のJSONで返答:
      {
        "final_fix": "...",
        "proof_of_fix": "...",
        "decision_trace": "...",
        "next_actions_if_not_solved": "..."
      }
  node_generation: |
    # 子ノード生成テンプレ
    - hypothesis: >
        {{parent.hypothesis}} を細分化:
        仮説タイプ: {{type}}
        原因候補: {{candidate}}
      plan: >
        {{test_or_inspection_steps}}
      required_tools: [{{tool_list}}]
      expected_signal: "{{expected_observation}}"
  evaluation_block: |
    # 実行結果評価テンプレ
    input_node_id: {{node.id}}
    result_summary: "{{observed}}"
    decision: "{{PROVED|REJECTED|UNCERTAIN}}"
    rationale: "{{why}}"
  pruning_decision: |
    node_id: {{node.id}}
    reason: "{{duplication|low_priority|budget_limit|contradiction}}"

heuristics:
  suspect_recent_edit_rules:
    - if diff_lines <= 50 and error_appeared_after_commit_minutes <= 30: +0.4
    - if changed_files overlap error_stacktrace_modules: +0.3
    - if env/toolchain untouched for >30 days: +0.2
    - else: +0
  impact_rules:
    - core_function_touched? +0.3
    - config_flag_changed? +0.2
    - dependency_version_bump? +0.2
  severity_rules:
    - crash/panic/fatal? +0.3
    - silent_wrong_output? +0.2
    - performance_regression_only? +0.1

failsafes:
  budget_guard:
    - if token_usage > 0.8 * max: switch to coarse-grained search
    - if depth > max_depth: summarize open branches, ask user for narrowing
  loop_guard:
    - if same node reopened > 2 times without new info: force prune or require new data
  ambiguity_guard:
    - ask clarifying question if critical info is missing and cannot be inferred cheaply

usage_note: >
  - このYAMLは「メタプロンプト」であり、LLMにそのまま与える想定。
  - {{}} のプレースホルダを実際の入力で置換し、tools仕様を同梱する。
  - 実装側で FRONTIER/CLOSED などの状態を外部で保持し、毎ターン注入しても良い。
  - もしくはLLM側で簡易的にテキスト管理し、外部に同期する形でも良い。

