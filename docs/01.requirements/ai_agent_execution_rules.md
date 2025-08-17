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

## 参考ファイル一覧（主要）
- `.claude/commands/tasks/do_task.md`
- `CLAUDE.md`
- `memory-bank/00-core/{knowledge_loading_functions.md,development_workflow.md,task_completion_integrity_mandatory.md}`
- `serena_project_knowledge.md`, `serena_memory_dynamic_prompt_loading.md`, `serena_memory_mcp_usage_strategy.md`
- `cognee_core_patterns.md`, `essential_patterns_cognee.md`
