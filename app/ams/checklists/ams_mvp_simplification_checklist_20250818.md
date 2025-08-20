# AMS MVP シンプル化・完成チェックリスト（2025-08-18）

- [x] 要件・基本設計のレビュー（`docs/01.requirements/ai_agent_execution_rules.md` 準拠）
- [x] TEST_MODE と DummyLLM の依存を廃止（`utils/llm_factory.py`, `config.py`, テスト修正）
- [x] 実 LLM 接続統合テスト `tests/integration/test_llm_connection.py` をパス
- [x] 決定的ユニットテスト（`core/base.py`/`interfaces.py` 周辺）をパス
- [x] ターゲットオーディエンス分析の年齢分布を正規化しテスト安定化
- [ ] Pydantic の非推奨 validator を `@field_validator` へ移行
- [ ] `utils/json_parser.py` のJSON抽出を堅牢化
- [ ] `ruff`/`black`/`mypy` 実行と残課題のゼロ化
- [ ] 追加統合テスト（`analyzer`の軽量ケース）を選別実行
- [ ] ドキュメント整備（本チェックリスト・MVP詳細設計・レビュー記録）

実行ログ（進捗メモ）
- 2025-08-18: TEST_MODE 廃止・接続テスト pass・core ユニット pass・demographics 正規化修正
