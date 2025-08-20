# AMS コードレビュー記録 (2025-08-18)

## スコープ
- `app/ams/src` 全体の設計簡素化方針適合性
- TEST_MODE/DummyLLM 廃止の影響
- 実LLM前提の安定性

## 主要観点と所見
- 設計一貫性: Pydanticモデル中心。`AgentState`等の外部共通型を導入せず、AMS内部の `EvaluationResult`/`PersonaAttributes` 等で統一 → OK
- LLM統合: `utils/llm_factory.py` は実LLMのみ。`config.llm_selector`と連動 → OK
- 例外/フォールバック: `TargetAudienceAnalyzer._analyze_demographics` に正規化を追加し、LLM応答変動で落ちないよう改善 → OK
- 環境依存: `.env` のキー前提。`.env`の露出なし → OK
- 非推奨警告: `@validator`(v1形式)は将来`@field_validator`へ移行必要 → TODO
- テストポリシー: 統合は実LLM、単体は決定的・I/O境界でのモックのみ → OK

## 変更提案（小）
- Pydantic v2移行: `@field_validator`/`ConfigDict`へ（警告解消）
- `json_parser.py` のJSON抽出強化（トリプルバックティックや前後説明テキストの頑健化）
- `llm_factory` のタイムアウト/リトライ（要件次第）

## リスク
- 実LLMのレイテンシ/コスト変動による統合テストの時間・安定性

## 結論
- シンプル化方針（YAGNI/DRY）に適合。AMSは単独実行可能な構成となっており、余計な互換層を持たない。
