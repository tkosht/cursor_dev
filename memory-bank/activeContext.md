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
