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
   - Current coverage: 95%
   - Missing coverage: 254-259, 269, 307-308 in app/query_monitor.py

## Recent Changes

### Testing Framework
- Replaced custom event loop with event_loop_policy
- Implemented proper async context manager mocking
- Added explicit test configuration in pytest.ini

### Error Handling
- Improved error notification testing
- Added multiple message verification
- Enhanced error scenario coverage

### 2024-03-10: Difyホスト設定の柔軟化
- カスタムDifyホストの設定をサポート
  - 環境変数 `DIFY_HOST` による設定が可能
  - デフォルト値: https://api.dify.ai
- テストカバレッジの追加
  - カスタムホスト設定のテストケース追加
  - 既存テストへの影響なし

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
- Difyホスト設定の柔軟化が完了
- すべてのテストが正常にパス（20テスト）
- コードカバレッジ95%を維持

## Next Steps
- 環境変数のドキュメント更新
- カスタムホスト設定のユーザーガイド追加
