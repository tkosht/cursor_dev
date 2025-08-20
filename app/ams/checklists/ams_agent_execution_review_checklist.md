# AMS AI Agent 実行・テスト完全達成チェックリスト

- [ ] 目的確認: すべてのテストが要件/基本設計に対比して正しく、全て PASSED（FAIL/ERROR/SKIP 0）

## 1. 準備（必須）
- [ ] `CLAUDE.md`/`ai_agent_execution_rules.md` の遵守確認
- [ ] 作業ブランチ確認（`main/master` 以外）
- [ ] 知識ロード（smart_knowledge_load）完了
- [ ] セキュリティ絶対（秘密漏えい防止）確認

## 2. 要件・設計ドキュメントの同期
- [ ] `docs/01.requirements/ai_agent_execution_rules.md` の要件を抽出
- [ ] `docs/02.basic_design/a2a_architecture.md` の設計意図を抽出
- [ ] `docs/03.detail_design/*` の実装指針を確認
- [ ] テスト観点に落とし込み（受入基準リスト化）

## 3. テストレビュー（TDD準拠）
- [ ] `app/ams/tests/unit/` のテストが要件/設計に整合
- [ ] `integration/` `e2e/` がモック禁止ルールを満たす
- [ ] 不適切な SKIP/xfail が存在しない
- [ ] 必要な不足テストの TODO を洗い出し

## 4. ベースライン実行
- [ ] `poetry run pytest -v` を実行
- [ ] 失敗/エラー/スキップ件数を記録
- [ ] 失敗テストの最小再現条件を確定

## 5. 修正ループ（Red→Green→Refactor）
- [ ] 根本原因を事実で特定
- [ ] 先にテスト（期待仕様）を固定/強化
- [ ] 実装を最小変更で修正
- [ ] 簡素化（同機能ならよりシンプル）を適用
- [ ] ログ/例外分類/戻り値を設計と一致させる
- [ ] 再実行して完全緑化（FAIL/ERROR/SKIP=0）

## 6. 回帰/デグレード確認（必須）
- [ ] 影響範囲テストを明示し再実行
- [ ] パフォーマンス・安定性に悪化がない

## 7. 品質ゲート
- [ ] `ruff check .` / `black --check .` / `mypy app/ams`
- [ ] カバレッジ確認（閾値があれば充足）

## 8. 完了/記録
- [ ] 変更点 WHY を含むコミット
- [ ] テスト計画含む PR 作成（必要時）
- [ ] 知見を `app/ams/docs/` に記録

---

### 実行ログ
- ベースライン: 未実施
- 最新実行結果: 未実施
- 修正サマリ: 未
- 残課題: 未
