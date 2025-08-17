# AI Agent 実行ルール統合ドキュメント

## 目的
AI Agent（Serena/Cognee 含む）による開発・タスク遂行を、再現性と品質をもって実行するための統合ルール、手順、チェックリストを定義する。

## 最上位プロトコル
- 参照源: `CLAUDE.md`
- 原則:
  - 事前知識ロードは絶対（`smart_knowledge_load()`、必要に応じ `comprehensive_knowledge_load()`）
  - セキュリティ絶対（秘密情報の露出禁止。検知パターンは即停止）
  - 価値評価5点チェック（Security / User value / Long-term / Fact-based / Knowledge / Alternatives）
  - チェックリスト駆動実行（CDTE）
  - TDD（Red-Green-Refactor）、ATDC（受け入れテスト駆動完了）
  - 完了整合性（背景/継続タスクが残る間は未完了）

## 実行チェックリスト（do_task 統合）
- /mandatory_rules の実行（必須ルール確認）
- ブランチ切替（`main/master` 以外、`feature/*|fix/*|docs/*|task/*`）
- タスク戦略・実行計画の精緻化（DAG前提）
- レビュー観点のチェックリスト化（受入基準/検証手順）
- タスク実行（必要に応じサブエージェント委譲、適切なコンテキスト移送）
- 実行結果レビュー（事実ベース評価）
- コミット/プッシュ/PR（WHY重視、PRにテスト計画）
- 注: 実行中に承認が必須な場合は中断して質問

## 知識ロードプロトコル
- 出典: `memory-bank/00-core/knowledge_loading_functions.md`
- 手順: 日付確立 → MCP選択（Serena/Cognee）→ 選択MCPでドメイン知識ロード → 完全性検証 → 実行
- `smart_knowledge_load()`:
  - セッション継続/必須ルール/ドメイン検索を高速読み込み
- `comprehensive_knowledge_load()`:
  - Local → Cognee → Web の3層で網羅

## MCP 選択（Serena vs Cognee）
- Serena: コード/設定/プロジェクト文脈（編集・依存・構造・制約・記録）
- Cognee: パターン/原則/横断知識（設計・再利用・テンプレ）
- ハイブリッド: Cogneeで戦略 → Serenaで実装
- 発見→昇格: Serenaで記録 → Cogneeにパターン昇格

## 開発ワークフロー
- 出典: `memory-bank/00-core/development_workflow.md`
- 流れ: 要件定義（Cognee検索）→ 設計レビュー → TDD実装 → セルフレビュー → 自動品質チェック → ピア/批判的レビュー → マージ → 振り返りとナレッジ記録
- 成果物: 要件/受け入れテスト仕様/リスク評価/チェックリスト/品質ログ

## 主要チェックリスト（抜粋）
- 事前
  - ルール確認、重複実装確認、設計妥当性、TDD準備、ブランチ確認（main禁止）
- 実装
  - 配置/命名/設定外出し、エラー分類、最小Doc、既存パターン準拠
- 完了
  - すべてのテスト/ゲート通過、背景/継続タスク完了、ドキュメント更新、PR

## テスト/品質/セキュリティ
- テスト構成
  - 単体: `tests/unit/`、統合: `tests/integration/`、E2E: `tests/e2e/`
  - モック禁止（統合/E2E）、実呼び出し推奨（CI外部3-5回まで）
- 品質ゲート（例）
  - 型/静的解析、Lint、カバレッジ閾値、セキュリティ（bandit/safety）、複雑度
- セキュリティ絶対
  - `.env`/キー露出禁止。秘密は環境変数で管理。入力バリデーション必須

## ブランチ/コミット/PR
- ブランチ: `feature/*`/`fix/*`/`docs/*`/`task/*`（main直コミット禁止）
- コミット: Conventional Commits、WHY重視、品質ゲート前に実行
- PR: 変更要約とテスト計画、全コミット/差分を俯瞰、URL共有

## Serena 運用（本リポ文脈）
- 出典: `serena_project_knowledge.md`, `serena_memory_dynamic_prompt_loading.md`, `serena_memory_mcp_usage_strategy.md`
- 役割: プロジェクト構造/制約/品質標準/CI/環境/コマンド/メトリクスの一次情報源
- 動的プロンプト: Cogneeテンプレ → Serena文脈でマージ → 実行（変数置換、制約注入、安全・品質適用）

## Cognee 運用（パターン中核）
- 出典: `cognee_core_patterns.md`, `essential_patterns_cognee.md`
- 役割: 横断パターン、設計原則、チェックリスト、実行モデル（並列/トークン最適化）
- 重要パターン: 事前知識ロード、MCP選択、DAG分解、順次思考、知識記録、品質ゲート

## マルチエージェント協調
- 役割例: Orchestrator / Serena Analyst / Sequential Thinker / Fix Validator
- 通信: 上下/水平チャンネル（検証済み知見・仮説・割当の明確化）
- 並列: 上位N仮説の同時検証、早期打ち切り、学びの集約

### マルチエージェント協調 具体ルール（強化）

- 役割分担（必須）
  - Orchestrator: DAG管理・サブエージェント割当・戦略統合
  - Serena Analyst: セマンティック解析・依存関係/構造把握・実装制約の適用
  - Sequential Thinker: 段階的推論・仮説設計・並列探索の設計
  - Fix Validator: テスト実行・回帰検証・性能/セキュリティ検証

- タスク分解と割当（必須）
  - DAG分解: ノードごとに「仮説生成→検証計画→実行→観測→解釈」
  - 並列探索: 上位3仮説の並列実行。最初の確証を採用し未確証枝は中断

- 通信プロトコル（検証ベース、必須）
  - メッセージID付与→送信→ACK受領確認→タイムアウトでエスカレーション
  - チャンネル定義: upward（validated findings/new hypotheses）、downward（search targets/assumptions）、lateral（shared patterns/correlated insights）
  - 推測・集合主張禁止: 「全員稼働中」等は個別確認がない限り禁止
  - 実装参照: `ai_coordination_comprehensive_guide.md`（verified_ai_communication, verify_ai_worker_status）

- 状態同期（必須）
  - 共有状態ファイル: `/tmp/ai_agent_coordination_state`
  - 原子的更新（テンポラリ→置換）と新鮮度チェック（10分超は警告）

- タイムアウト/エスカレーション（必須）
  - 既定: TASK_TIMEOUT=300s、STATUS_CHECK_INTERVAL=60s、ESCALATION_THRESHOLD=2
  - 無応答時は即座に再送→再無応答で人間監督へエスカレーション

- 品質メトリクス（推奨→将来必須）
  - Response Rate / Avg Response Time / False Status Reports / Verification Success / Timeout Incidents

- コンプライアンスチェックリスト（協調タスク）
  - Before: 共有状態稼働/通信設定/タイムアウト有効/役割確定/検証手順周知
  - During: 定期状態確認/推測排除/通信失敗の即検出/エスカレーション準備
  - After: 最終状態確認/通信品質メトリクス記録/学びのナレッジ反映/次回改善点反映

参照: `cognee_core_patterns.md`（Multi-Agent Coordination, DAG/Parallel, Communication）、`memory-bank/02-organization/ai_coordination_comprehensive_guide.md`

---

## DAG 実行モデル（do_task / dag-debug-enhanced / dagdebugger 統合）

### 目的
曖昧・未知の解決策を持つ高難易度タスクを、DAG分解しながら動的に枝刈り/拡張し、サブエージェント協調で探索・検証・確定する。

### 状態モデル（Global State）
- FRONTIER: 展開待ちノード集合（node_id のリスト）
- CLOSED: 展開済みノード（確定/棄却）
- SUSPECT_RECENT_EDIT: 直近編集が原因か推定フラグ（bool）
- BUDGET:
  - token: {max, used}
  - tool_calls: {max, used}
  - depth: {max, current}
- HEURISTICS:
  - recent_edit_weight: 0.6
  - impact_weight: 0.25
  - severity_weight: 0.15
- LOG: 主要判断・スコア・剪定理由の記録

### ノードスキーマ（Node State）
- id: 自動採番
- parent: 親 node_id | null
- hypothesis: 原因仮説（Why）
- plan: 検証計画（How）
- required_tools: 使用ツール一覧
- expected_signal: 観測項目/合否判定基準
- result: 観測結果
- score:
  - suspicion: 有望度 0-1
  - cost_estimate: 予想コスト
  - priority: suspicion / (1 + cost_estimate) 等
- status: OPEN | EXPANDED | PROVED | REJECTED | PRUNED

### メインループ（Best-first + 動的更新）
1. 初期化
   - 直近差分・時系列から SUSPECT_RECENT_EDIT を推定
   - ルートノード生成（包括仮説）→ FRONTIER へ
2. while FRONTIER 非空 かつ 目標未達:
   - SelectNode: priority 最大を選択（ε-greedyで2-3番手選択を稀に採用）
   - Expand: 仮説精緻化→子ノード生成→スコア→剪定→実行スケジュール
   - Execute & Evaluate: 観測と expected_signal 照合 → PROVED/REJECTED
   - Update: CLOSED へ移動、子を FRONTIER に追加、BUDGET 更新
3. 終了条件
   - 再現テストPassの修正案確定／予算上限間近時は最有力仮説と次手順提示／ユーザ中断

### スコアリング/選択/剪定/バックトラック
- スコア式（例）
  - suspicion = recent_edit*0.6 + impact*0.25 + severity*0.15
  - cost_estimate = norm(time + tool + token)
  - priority = suspicion / (1 + cost_estimate)
- 剪定ポリシー
  - 直近編集が有力な場合、広域環境チェック等の低価値枝を初期抑制
  - 否定された前提再利用枝は剪定
  - 類似仮説は統合、priority が閾値未満は保持しない
  - 深さ超過時は打ち切り、要約提示で戦略切替
- バックトラック
  - REJECTED/PRUNED の兄弟枝再評価
  - 新情報で priority 再計算（動的DAG更新）

### ノード実行テンプレ（Serena × Sequential Thinking）
- 仮説生成（Serena）
  1. mcp__serena__find_symbol で関連シンボル特定
  2. mcp__serena__find_referencing_symbols で影響範囲把握
  3. mcp__serena__get_symbols_overview で全体構造把握
- 検証計画（Sequential Thinking）
  1. 前提確認 → 2. テスト設計 → 3. 期待観測定義 → 4. 実行 → 5. 解釈/次手
- サブエージェント起動規則（エージェント化）
  - 深いセマンティック解析: Serena Analyst
  - 複雑推論/並列探索設計: Sequential Thinker
  - 修正検証/回帰・性能/セキュリティ: Fix Validator
- 結果統合
  - ノード文脈を更新し、子へ主要所見を伝播（上/下/水平チャネル）

### 検証要件（Strict Validation Protocol）
- Pre-fix: ベースライン取得、影響テスト特定、最小再現テスト作成
- Post-fix: 修正確認、単体/統合テスト、性能確認、必要時セキュリティ走査
- ドキュメント: 根因説明、修正方針理由、追加テスト説明、ロールバック手順

### パラメータ/制御（実運用のダイヤル）
- max-depth（既定: 8）/ time-limit 分 / parallel-width（既定: 3）
- sub-agents（利用数上限）/ serena-depth（探索深度）
- 予算ガード: トークン/ツール/深さの上限に応じ粗粒度探索へ切替

### フェイルセーフ/ガード
- 予算ガード: 使用量が上限の80%超で粗探索へ降格
- ループガード: 同一ノードを新情報なしで2回超再開したら強制剪定/新データ要求
- 曖昧性ガード: 重要情報が欠落し推定困難な場合は明確化質問

### 出力フォーマット（検証可能性の担保）
- Summary: problem_statement / root_cause / fix_applied / validation_results
- Detailed: dag_exploration_trace / thought_process_log / serena_analysis_results / sub_agent_contributions / code_changes / test_additions
- Actionables: immediate_actions / follow_up_tasks / monitoring / docs_updates

## エラー対応/回復
- 検出→分析→解決→予防（完全文脈取得、最小再現、根因特定、回帰テスト追加）
- リカバリ: バックオフ、フォールバック、安全モード、劣化ログ化

## パフォーマンス最適化
- 検索優先（Grep/Glob → 最小Read）、Serenaセマンティック活用
- 並列化（検索/読込/仮説検証のバッチ化）
- キャッシュ/テンプレ再利用、トークン節約

## 完了整合性（必須）
- 出典: `memory-bank/00-core/task_completion_integrity_mandatory.md`
- すべての背景/継続タスクが完了するまで未完了。
- MUST/SHOULD/COULD の完了条件を事前定義。ドリフト禁止（変更は承認必須）。
- 受け入れテスト（ATDC）を完了条件に統合。

---

## レビュー観点と結果（この変更での実施）

- マルチエージェント役割と責務が明確か: 補強済（役割ごとの責務を具体化）
- タスク分解/並列実行の規律が明確か: 補強済（DAG/トップ3並列/早期打ち切り）
- 通信が検証ベースか（ACK/Timeout/Escalation）: 補強済（ID付きACK/閾値/手順）
- 共有状態と新鮮度検証があるか: 補強済（原子的更新/10分警告）
- メトリクスと監査が定義されているか: 追加（応答率等の指標を明記）
- 推測禁止/集合主張禁止の運用規則があるか: 補強済（禁止と個別確認必須）
- チェックリスト駆動（Before/During/After）が整備されているか: 追加
- 参照先の一次情報リンクが十分か: 追加（具体ファイルを明記）

- DAG実行モデル（状態/ノード/アルゴリズム/剪定/ガード/出力）を明文化
- `do_task` チェックリストを統合し実務オペレーションを標準化

判定: 上記観点は全て満たすように補強/追記済み。

---

## マージ記録（ナレッジ更新履歴）

- 日付: 2025-08-17
- 変更概要:
  - マルチエージェント協調の具体ルールを強化（役割/通信ACK/共有状態/タイムアウト/メトリクス/チェックリスト）
  - レビュー観点を明文化し、本ドキュメントへレビュー結果を反映
  - 参照箇所（`cognee_core_patterns.md`, `memory-bank/02-organization/ai_coordination_comprehensive_guide.md`）を追記
  - `dag-debug-enhanced.md` / `dagdebugger.md` / `dagrunner.md` の指針を統合
  - 曖昧タスク向けのDAG動的更新・並列探索・フェイルセーフを体系化
- 期待効果:
  - 検証ベース協調の徹底、推測ベース連携の排除
  - 協調タスクの再現性・可観測性・早期異常検知の向上


## 参考ファイル一覧（主要）
- `.claude/commands/tasks/do_task.md`
- `CLAUDE.md`
- `memory-bank/00-core/{knowledge_loading_functions.md,development_workflow.md,task_completion_integrity_mandatory.md}`
- `serena_project_knowledge.md`, `serena_memory_dynamic_prompt_loading.md`, `serena_memory_mcp_usage_strategy.md`
- `cognee_core_patterns.md`, `essential_patterns_cognee.md`
- `.claude/commands/tasks/dag-debug-enhanced.md`
- `.claude/commands/tasks/dagdebugger.md`
- `.claude/commands/tasks/dagrunner.md`
