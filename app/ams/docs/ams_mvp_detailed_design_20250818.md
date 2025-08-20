# AMS MVP 詳細設計（2025-08-18）

## 1. スコープ
- 最小: `AnalysisAgent` による 8 次元分析の安定提供
- LLM 接続: 環境変数からモデル自動選択（Gemini 既定）
- テスト: 実 LLM 統合テスト（接続/自然応答）、決定的ユニット（構造/可読性）

## 2. コンポーネント
- `core/`
  - `interfaces.py`: `IAgent`, `IEnvironment`, `IAction`, `ISimulation` などの Protocol
  - `base.py`: 上記の基本実装（MVPでは Environment/Simulation の最小機能のみ使用）
  - `types.py`: `PersonaAttributes` 等の Pydantic モデル（型の集中管理）
- `config/`
  - `config.py`: `.env` 読込, `AMSConfig`, `LLMConfig` 等
  - `llm_selector.py`: `TaskType` に応じたモデル選択
- `utils/`
  - `llm_factory.py`: 実 LLM 生成（Gemini/OpenAI/Anthropic）。TEST_MODE 排除。
  - `json_parser.py`: LLM 応答の JSON 抽出（将来は厳格化）
- `agents/`
  - `analyzer.py`: 分析の中核。非LLM（構造/可読性）と LLM 分析の統合

## 3. データフロー
1) 入力 `article_content: str`
2) `AnalysisAgent.analyze()` で次を並列実行
   - 非LLM: `_analyze_structure`, `_analyze_readability`
   - LLM: `_analyze_content`, `_analyze_sentiment`, `_analyze_keywords`, `_analyze_target_audience`, `_analyze_technical_depth`, `_analyze_emotional_impact`
3) 結果を集約し `metadata` 追加

## 4. 設定/環境
- 必須環境変数（いずれか）: `GOOGLE_API_KEY` | `OPENAI_API_KEY` | `ANTHROPIC_API_KEY`
- 既定: `LLM_PROVIDER` 未指定 → キー存在から自動推定（Gemini優先）
- タイムアウト: `LLMConfig.timeout`（初期値 60s）

## 5. 例外/エラー
- LLM 応答の JSON 解析失敗時: エラーを `metadata.errors` に登録し、他次元は継続
- キー未設定時: 設定生成時に `ValueError`（起動前に検知）。統合テストは skip

## 6. 実装簡素化ポリシー
- TEST_MODE/DummyLLM 依存の撤廃（常に実 LLM）
- LLM 呼び出し統一: `utils.llm_factory.create_llm()`
- プロンプトは最小限・JSON応答を志向、解析側で安全抽出

## 7. テスト設計
- ユニット: 決定的（構造/可読性）、`config`/`llm_selector` のロジック確認
- 統合: `tests/integration/test_llm_connection.py` を必須
- 実行順: ユニット迅速 → 接続統合 → 必要に応じ追加統合

## 8. 将来拡張（MVP外）
- `evaluator.py` によるペルソナ評価（実LLM）
- レポート生成/ネットワーク効果シミュレーション
- Pydantic v2 への完全移行（`@field_validator`）
