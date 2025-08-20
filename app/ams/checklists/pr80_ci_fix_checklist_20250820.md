# PR #80 CI Fix Checklist (2025-08-20)

- [x] ルール確認: `docs/01.requirements/ai_agent_execution_rules.md`
- [x] 失敗ジョブ特定: CI `test (3.10/3.11/3.12)` が失敗
- [x] エラーログ取得: 単一失敗は `tests/unit/test_target_audience_analyzer.py::test_psychographic_insights`（'motivations' 欠落）
- [x] ローカル再現（対象限定）: `pytest -k target_audience_analyzer -v` 実行
- [x] 修正実装: `src/agents/target_audience_analyzer.py` にキー正規化と型安全化を追加
- [x] フォーマット/リンタ: `ruff check` / `black --check`（AMS配下）
- [x] AMSユニットテスト（対象限定）: 7/7 PASS
- [ ] AMSユニットテスト（全体）: CIに委譲
- [ ] AMS統合テスト: CI別ジョブに委譲（APIキー前提）
- [x] コミット
- [x] プッシュ
