# Active Context

## Current Focus

### Testing Infrastructure Improvements

1. Async Testing Framework
   - pytest-asyncio configuration optimized
   - Event loop management improved
   - Warning handling streamlined

2. Mock Implementation
   - Async context manager patterns established
   - Error scenario handling improved
   - Multiple notification testing implemented

3. Test Coverage
   - Current coverage: 92%
   - Missing coverage: 252-255, 263-266, 297-299, 307-309 in app/query_monitor.py

## Recent Changes

### Testing Framework
- Replaced custom event loop with event_loop_policy
- Implemented proper async context manager mocking
- Added explicit test configuration in pytest.ini

### Error Handling
- Improved error notification testing
- Added multiple message verification
- Enhanced error scenario coverage
- Implemented QueryExecutionError for better error handling
- Updated error propagation in main function

### 2024-03-10: エラーハンドリングの改善
- QueryExecutionErrorの追加と実装
  - クライアントエラーの適切な処理
  - エラー伝播の改善
- テストケースの強化
  - エラーケースのテスト改善
  - 例外処理のテストケース追加
- コードフォーマットの修正
  - blackによる自動フォーマット
  - 空白行の整理

## Next Steps

1. Coverage Improvements
   - Investigate uncovered lines in query_monitor.py
   - Add tests for edge cases
   - Document coverage exceptions

2. Warning Resolution
   - Review remaining RuntimeWarnings
   - Consider additional warning filters
   - Update documentation for known warnings

3. Test Maintenance
   - Regular review of test patterns
   - Update mock implementations as needed
   - Monitor pytest-asyncio updates

## Active Decisions

1. Testing Strategy
   - Use pytest-asyncio for all async tests
   - Maintain high coverage requirements
   - Document all test patterns

2. Mock Implementation
   - Prefer AsyncMock over custom implementations
   - Use explicit context manager setup
   - Maintain clear fixture dependencies

3. Configuration Management
   - Centralize test configuration in pytest.ini
   - Document all warning suppressions
   - Keep test organization consistent

## Current Work Status
- エラーハンドリングの改善が完了
- すべてのテストが正常にパス（20テスト）
- コードカバレッジ92%を維持

## Next Steps
- 未カバーの行の調査とテスト追加
- エラーハンドリングのドキュメント更新

## 今後の改善ポイント

### エラーハンドリングの強化
1. エラー通知の失敗時
   - 現状：エラー通知の失敗が上位に伝播されない
   - 影響：エラーが発生しても管理者に通知されない
   - 改善案：SlackNotificationErrorを上位に伝播

2. HTTPエラーの詳細処理
   - 現状：HTTPエラーの詳細（ステータスコードなど）が失われる
   - 影響：エラーの原因特定が困難
   - 改善案：ステータスコードとエラーメッセージの詳細な記録

3. セッション管理
   - 現状：セッションクローズ時のエラーが無視される
   - 影響：リソースの解放が確実に行われない可能性
   - 改善案：try-finallyブロックでの確実なリソース解放

4. メイン関数のエラー伝播
   - 現状：エラーがログに記録されるだけ
   - 影響：アプリケーションの終了コードが適切に設定されない
   - 改善案：適切な終了コードの設定とエラー伝播

### テストカバレッジの向上
1. 未カバーの行
   - 現状：252-255, 263-266, 297-299, 307-309行目が未カバー
   - 影響：エッジケースの動作が不明確
   - 改善案：エッジケースのテストケース追加

2. テストケースの拡充
   - 現状：基本的なエラーケースのみ
   - 影響：複雑なエラーケースの検証が不足
   - 改善案：リトライロジック、パフォーマンステストの追加

### ロギングの改善
1. エラーログの詳細化
   - 現状：基本的なエラー情報のみ
   - 影響：トラブルシューティングが困難
   - 改善案：スタックトレース、コンテキスト情報の追加

2. トレース情報
   - 現状：処理の流れが追跡しにくい
   - 影響：問題の特定が困難
   - 改善案：処理フローのトレースログ追加

## 改善の優先順位
1. 高優先度
   - エラー通知の失敗時の処理
   - HTTPエラーの詳細処理
   - メイン関数のエラー伝播

2. 中優先度
   - セッション管理の改善
   - エラーログの詳細化
   - テストカバレッジの向上

3. 低優先度
   - トレース情報の追加
   - テストケースの拡充
   - パフォーマンステストの追加

## 注意事項
- 現状の実装でも基本的な機能は正常に動作
- 改善は運用性と保守性の向上が目的
- 優先順位に応じて段階的に改善を実施
