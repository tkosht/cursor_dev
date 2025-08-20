# PR #80 CI Fix Checklist (2025-08-20)

- [x] ルール確認: `docs/01.requirements/ai_agent_execution_rules.md`
- [x] 失敗ジョブ特定: CI `test (3.10/3.11/3.12)` が失敗
- [x] エラーログ取得: Ruff 895 errors (W293 など) により失敗
- [ ] ローカル再現: `poetry install` → `ruff check` 実行
- [ ] 自動修正: `ruff check . --fix` 実行
- [ ] フォーマット: `black .` 実行
- [ ] 型チェック: `mypy src/`
- [ ] app/ams ユニットテスト: `pytest -v tests/unit`
- [ ] app/ams 統合テスト: `pytest -v tests/integration`（環境キー未設定なら skip 記録）
- [ ] ルート tests 実行: `pytest -v` at repo root
- [ ] CI との整合確認（ワークフロー差分・失敗マスクの有無）
- [ ] コミット: fix(lint): ruff auto-fix + format + tests
- [ ] プッシュ
