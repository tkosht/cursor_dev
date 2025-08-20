# AMS 要件定義・基本設計レビュー（2025-08-18）

## 1. 目的と対象
- 対象: `app/ams/` Article Market Simulator (AMS)
- 目的: 記事コンテンツを多面的に分析し、対象読者・技術深度・感情的影響などを推定し、（将来的に）ペルソナ評価・ネットワーク効果シミュレーションに拡張可能な基盤を提供する。

## 2. 上位規約の準拠
- 参照: `docs/01.requirements/ai_agent_execution_rules.md`
- 遵守事項（抜粋）:
  - 実行前知識ロード・セキュリティ絶対・チェックリスト駆動・TDD
  - 統合/E2Eではモック禁止（実LLM使用）
  - 完了条件は受入（ATDC）で担保

## 3. 機能要件（現状コード・テストからの抽出）
- 分析（AnalysisAgent）
  - 入力: 記事本文（テキスト）
  - 出力: 次を含む JSON 相当の辞書
    - content: 主題/副題/トピック/ドメイン/タイプ/キー・メッセージ
    - structure: 行数/段落数/コードブロック有無 等（決定的）
    - sentiment: overall/score/emotional_tones 等（LLM）
    - readability: 文数/平均文長/難易度/推定読了時間（決定的）
    - keywords: 主要/副次/フレーズ/専門語/トレンド（LLM）
    - target_audience: 主要読者/セグメント/知識要件/年齢帯/レベル/興味（LLM）
    - technical_depth: レベル/概念/前提/コード例/実装可能性/理論-実践（LLM）
    - emotional_impact: 主要感情/感情遷移/動機/ストレス/ポジ要因/CTA 強度（LLM）
    - metadata: 解析時刻/所要秒数/次元数/エラー一覧
- LLM 選択
  - `config/llm_selector.py` に基づき、利用可能キーから最適モデルを選択
  - 既定: Gemini (`gemini-2.5-flash`)
- 設定
  - `AMSConfig` に LLM/Simulation/Visualization/Performance を内包し、`.env` から読込
  - TEST_MODE 依存は廃止（実 LLM 前提）

## 4. 非機能要件（抽出）
- セキュリティ: `.env` 非公開、キー秘匿
- 可観測性: ログ（INFO/DEBUG 等）、エラー伝播
- 性能/コスト: 低コストモデル優先、タイムアウト/リトライは将来的考慮
- テスト: 統合テストは実 LLM を使用。ユニットは I/O 境界でのモックを許容

## 5. 基本設計（現状準拠）
- 層構造
  - core: `interfaces.py`（Protocol）, `base.py`（基本実装）, `types.py`（型）
  - config: `config.py`（.env読込）, `llm_selector.py`（モデル選択）
  - utils: `llm_factory.py`（LLM生成）, `json_parser.py` 等
  - agents: `analyzer.py`（MVP中核）、将来的に `evaluator.py`/`reporter.py` 等
- 依存の流れ
  - tests → agents/utils → config → env
  - agents → utils.llm_factory → langchain_* 実LLM
- 実行経路（MVP）
  1) `AnalysisAgent.analyze(text)`
  2) 並列で 8 次元解析（LLM/非LLM混在）
  3) 解析結果dictに `metadata` 付与

## 6. 差分と課題
- 差分: TEST_MODE と DummyLLM 依存が存在 → 本リビューで廃止済み
- 警告: Pydantic v1 形式 validator の非推奨警告（置換必要）
- テスト全体の実行時間: 一部タイムアウト傾向 → 粒度別/選別実行の整理が必要

## 7. 受入基準（MVP）
- 実 LLM で `tests/integration/test_llm_connection.py` が通る
- `AnalysisAgent` の決定的（構造/可読性）テストが通る
- `.env` の GOOGLE_API_KEY 前提で失敗しない
- TEST_MODE なしでユニット/一部統合が安定動作
