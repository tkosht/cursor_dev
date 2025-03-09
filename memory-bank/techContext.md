# 技術コンテキスト

## 開発環境
1. Python環境
   - Python 3.10以上
   - Poetryによる依存関係管理
   - 仮想環境: /.venv

2. 開発ツール
   - VSCode Dev Container
   - Git
   - pytest

## 主要ライブラリ
1. Slack SDK
   - WebClient
   - エラーハンドリング
   - レート制限対応

2. requests
   - HTTP通信
   - リトライ機能
   - タイムアウト設定

3. logging
   - ログローテーション
   - ログレベル管理
   - ファイル出力

## 設定管理
1. 環境変数
   - SLACK_TOKEN
   - DIFY_API_KEY

2. 設定ファイル
   - queries.json
   - ログ設定

## テスト環境
1. テストフレームワーク
   - pytest
   - unittest.mock
   - MagicMock

2. テストカバレッジ
   - 現在: 80%
   - 目標: 90%以上

## デプロイメント
1. 実行環境
   - cronによる定期実行
   - ログディレクトリ管理

2. 監視
   - ログ監視
   - エラー通知

## Testing Framework

### pytest-asyncio Configuration

```ini
[pytest]
asyncio_mode = strict
asyncio_default_fixture_loop_scope = function

filterwarnings =
    ignore::RuntimeWarning:app.query_monitor
```

### Key Testing Patterns

#### Async Context Manager Mocking

```python
@pytest_asyncio.fixture
async def mock_session(mock_response):
    session = AsyncMock(spec=aiohttp.ClientSession)
    cm = AsyncMock()
    cm.__aenter__.return_value = mock_response
    cm.__aexit__.return_value = None
    session.post.return_value = cm
    return session
```

#### Event Loop Management

```python
@pytest.fixture(scope="session")
def event_loop_policy():
    """イベントループポリシーの設定"""
    return asyncio.get_event_loop_policy()
```

### Best Practices

1. Event Loop Configuration
   - Use `event_loop_policy` instead of custom `event_loop` fixture
   - Set explicit loop scope in pytest.ini
   - Avoid manual loop creation/cleanup

2. Async Mock Setup
   - Use `AsyncMock` for async context managers
   - Set `__aenter__` and `__aexit__` explicitly
   - Specify return values for async methods

3. Error Handling
   - Test both success and error paths
   - Verify error notifications
   - Check multiple message scenarios

4. Warning Management
   - Configure warning filters in pytest.ini
   - Handle RuntimeWarnings appropriately
   - Document known warning patterns

## Known Issues and Solutions

### Async Context Manager Issues

1. Problem: AttributeError: __aenter__
   Solution: Proper async context manager implementation
   ```python
   cm = AsyncMock()
   cm.__aenter__.return_value = mock_response
   cm.__aexit__.return_value = None
   ```

2. Problem: Multiple message assertions
   Solution: Use call_args_list for verification
   ```python
   assert mock_client.call_count == 2
   calls = mock_client.call_args_list
   assert calls[0].kwargs["channel"] == "errors"
   ```

### Event Loop Warnings

1. Problem: Deprecated event loop fixture
   Solution: Use event_loop_policy fixture
   ```python
   @pytest.fixture(scope="session")
   def event_loop_policy():
       return asyncio.get_event_loop_policy()
   ```

2. Problem: Unset loop scope
   Solution: Configure in pytest.ini
   ```ini
   asyncio_default_fixture_loop_scope = function
   ```

## Dependencies

- pytest-asyncio: ^0.25.3
- pytest: ^8.3.4
- pytest-cov: ^6.0.0
