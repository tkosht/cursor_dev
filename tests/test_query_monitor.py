import asyncio
import json
import os
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import aiohttp
import pytest
import pytest_asyncio
from slack_sdk.errors import SlackApiError

from app.query_monitor import (
    QueryExecutionError,
    QueryMonitor,
    execute_all_queries,
    load_config,
    main,
)


@pytest.fixture(scope="session")
def event_loop_policy():
    """イベントループポリシーの設定"""
    return asyncio.get_event_loop_policy()


@pytest.fixture(scope="function")
def event_loop():
    """Create and cleanup event loop for each test"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def mock_response():
    """APIレスポンスのモック"""
    mock = AsyncMock()
    mock.status = 200
    mock.json.return_value = {"answer": "テスト結果"}
    return mock


@pytest.fixture
def mock_session(mock_response):
    """セッションのモック"""
    session = AsyncMock(spec=aiohttp.ClientSession)
    cm = AsyncMock()
    cm.__aenter__.return_value = mock_response
    cm.__aexit__.return_value = None
    session.post.return_value = cm
    return session


@pytest_asyncio.fixture
async def mock_slack_client():
    """Slackクライアントのモック"""
    client = AsyncMock()
    client.token = "test-token"
    client.chat_postMessage = AsyncMock(return_value={"ok": True})
    return client


@pytest.fixture
def mock_env():
    """環境変数のモック"""
    with patch.dict(
        os.environ,
        {"SLACK_TOKEN": "test-token", "DIFY_API_KEY": "[API_KEY_REDACTED]"},
    ):
        yield


@pytest.fixture
def mock_queries():
    """クエリ設定のモック"""
    return {
        "queries": [
            {
                "name": "test_query",
                "description": "テストクエリ",
                "query": "テストクエリの内容",
                "channel": "test-channel",
            }
        ]
    }


@pytest_asyncio.fixture
async def monitor(mock_queries, mock_slack_client, mock_session):
    """QueryMonitorインスタンスの作成"""
    with (
        patch("builtins.open", create=True) as mock_open,
        patch("app.query_monitor.WebClient", return_value=mock_slack_client),
        patch(
            "app.query_monitor.aiohttp.ClientSession",
            return_value=mock_session,
        ),
    ):
        mock_open.return_value.__enter__.return_value.read.return_value = (
            json.dumps(mock_queries)
        )
        monitor = QueryMonitor(
            dify_api_key="[API_KEY_REDACTED]",
            slack_token="test-token",
            slack_channel="test-channel",
            slack_client=mock_slack_client,
            session=mock_session,
        )
        yield monitor
        # セッションのクリーンアップ
        if not monitor._session.closed:
            await monitor._session.close()


@pytest.mark.asyncio
async def test_init_success(monitor):
    """初期化の成功テスト"""
    assert monitor.dify_api_key == "test-dify-key"
    assert monitor.slack_channel == "test-channel"
    assert len(monitor.queries) == 1


@pytest.mark.asyncio
async def test_init_missing_env():
    """必須パラメータが不足している場合のテスト"""
    with pytest.raises(ValueError, match="All parameters are required"):
        QueryMonitor("", "", "")


@pytest.mark.asyncio
async def test_process_query_success(
    monitor, mock_slack_client, mock_session, mock_response
):
    """クエリ実行成功のテスト"""
    # モックの設定
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test_channel")

    # アサーション
    mock_session.post.assert_called_once()
    mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_execution_error(
    monitor, mock_slack_client, mock_session
):
    """クエリ実行エラーのテスト"""
    mock_session.post.side_effect = aiohttp.ClientError("APIエラー")
    
    with pytest.raises(
        QueryExecutionError,
        match="Failed to execute query after 3 attempts: APIエラー"
    ):
        await monitor.process_query("test_query", "test_channel")


@pytest.mark.asyncio
async def test_process_query_notification_error(
    monitor, mock_slack_client, mock_session
):
    """通知エラーのテスト"""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"answer": "テスト回答"}
    mock_session.post.return_value.__aenter__.return_value = mock_response
    mock_slack_client.chat_postMessage.side_effect = SlackApiError(
        "error", {"error": "channel_not_found"}
    )
    
    await monitor.process_query("test_query", "test-channel")
    
    mock_slack_client.chat_postMessage.assert_called_once()
    assert mock_slack_client.chat_postMessage.call_args[1]["channel"] == "test-channel"


@pytest.mark.asyncio
async def test_process_query_empty_result(mock_session, mock_slack_client):
    """空の結果のテスト"""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"answer": ""}
    mock_session.post.return_value.__aenter__.return_value = mock_response
    mock_slack_client.chat_postMessage.return_value = {"ok": True}
    
    monitor = QueryMonitor(
        dify_api_key="[API_KEY_REDACTED]",
        slack_token="test-slack-token",
        slack_channel="test-channel",
        session=mock_session,
        slack_client=mock_slack_client
    )
    
    await monitor.process_query("test_query", "test_channel")
    
    mock_slack_client.chat_postMessage.assert_called_once()
    call_args = mock_slack_client.chat_postMessage.call_args[1]
    assert "結果が空です" in call_args["blocks"][1]["text"]["text"]


@pytest.mark.asyncio
async def test_process_query_invalid_json(
    monitor, mock_slack_client, mock_session
):
    """無効なJSONレスポンスのテスト"""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.side_effect = aiohttp.ContentTypeError(
        request_info=MagicMock(real_url="http://test.com"),
        history=()
    )
    mock_response.text.return_value = "invalid json"
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    with pytest.raises(
        QueryExecutionError,
        match="Failed to execute query: 200, invalid json"
    ):
        await monitor.process_query("test_query", "test-channel")


@pytest.mark.asyncio
async def test_process_query_timeout(monitor, mock_slack_client, mock_session):
    """タイムアウトを処理するテスト"""
    mock_session.post.side_effect = aiohttp.ClientError("Request timed out")
    
    with pytest.raises(
        QueryExecutionError,
        match="Failed to execute query after 3 attempts: Request timed out"
    ):
        await monitor.process_query("テストクエリ", "テストチャンネル")


@pytest.mark.asyncio
async def test_process_query_connection_error(
    monitor, mock_slack_client, mock_session
):
    """接続エラーを処理するテスト"""
    mock_session.post.side_effect = aiohttp.ClientConnectionError("Connection failed")
    
    with pytest.raises(
        QueryExecutionError,
        match="Failed to execute query after 3 attempts: Connection failed"
    ):
        await monitor.process_query("test_query", "test_channel")


@pytest.mark.asyncio
async def test_process_query_http_error(
    monitor, mock_slack_client, mock_session, mock_response
):
    """HTTPエラーを処理するテスト"""
    # モックの設定
    mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info=MagicMock(), history=(), status=500
    )
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test_channel")

    # アサーション
    mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_execute_query_success(monitor, mock_session, mock_response):
    """クエリ実行成功のテスト"""
    # テスト実行
    result = await monitor.execute_query("test_query")

    # アサーション
    assert result == {"answer": "テスト結果"}
    mock_session.post.assert_called_once_with(
        f"{monitor.dify_host}/v1/chat-messages",
        headers={
            "Authorization": "Bearer test-dify-key",
            "Content-Type": "application/json"
        },
        json={
            "inputs": {},
            "query": "test_query",
            "response_mode": "blocking",
            "conversation_id": "",
            "user": "query_monitor"
        },
        timeout=ANY
    )


@pytest.mark.asyncio
async def test_execute_query_streaming(monitor, mock_session, mock_response):
    """ストリーミングモードでのクエリ実行テスト"""
    # モックの設定
    mock_response.json.return_value = {"answer": "ストリーミング結果"}
    
    # テスト実行
    result = await monitor.execute_query("test_query", response_mode="streaming")

    # アサーション
    assert result == {"answer": "ストリーミング結果"}
    mock_session.post.assert_called_once_with(
        f"{monitor.dify_host}/v1/chat-messages",
        headers={
            "Authorization": "Bearer test-dify-key",
            "Content-Type": "application/json"
        },
        json={
            "inputs": {},
            "query": "test_query",
            "response_mode": "streaming",
            "conversation_id": "",
            "user": "query_monitor"
        },
        timeout=ANY
    )


@pytest.mark.asyncio
async def test_execute_query_failure(monitor, mock_session):
    """クエリ実行失敗のテスト"""
    # モックの設定
    mock_session.post.side_effect = aiohttp.ClientError("APIエラー")

    # テスト実行とアサーション
    with pytest.raises(QueryExecutionError):
        await monitor.execute_query("test_query")


@pytest.mark.asyncio
async def test_send_error_notification_success(monitor, mock_slack_client):
    """エラー通知成功のテスト"""
    # モックの設定
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor._send_error_notification("テストエラー", "エラーメッセージ")

    # アサーション
    mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_send_error_notification_failure(monitor, mock_slack_client):
    """エラー通知失敗のテスト"""
    # モックの設定
    mock_slack_client.chat_postMessage.side_effect = SlackApiError(
        "error", {"error": "test_error"}
    )

    # テスト実行
    await monitor._send_error_notification("テストエラー", "エラーメッセージ")

    # アサーション
    mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_load_queries_file_not_found(monitor):
    """クエリ設定ファイルが見つからない場合のテスト"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            monitor._load_queries()


@pytest.mark.asyncio
async def test_load_queries_invalid_json(monitor):
    """無効なJSONファイルの場合のテスト"""
    with patch("builtins.open", create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = (
            "invalid json"
        )
        with pytest.raises(json.JSONDecodeError):
            monitor._load_queries()


@pytest.mark.asyncio
async def test_main_success(
    mock_env, mock_queries, mock_slack_client, mock_session, mock_response
):
    """メイン関数成功のテスト"""
    with (
        patch("builtins.open", create=True) as mock_open,
        patch("app.query_monitor.WebClient", return_value=mock_slack_client),
        patch(
            "app.query_monitor.aiohttp.ClientSession",
            return_value=mock_session,
        ),
        patch.dict(
            os.environ,
            {
                "DIFY_API_KEY": "[API_KEY_REDACTED]",
                "SLACK_TOKEN": "test-token",
            },
        ),
    ):
        mock_open.return_value.__enter__.return_value.read.return_value = (
            json.dumps(mock_queries)
        )
        mock_slack_client.chat_postMessage.return_value = {"ok": True}

        # テスト実行
        await main()

        # アサーション
        mock_session.post.assert_called_once()
        mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_main_missing_env():
    """メイン関数環境変数不足のテスト"""
    with (
        patch("app.query_monitor.WebClient"),
        patch("app.query_monitor.aiohttp.ClientSession"),
        patch("app.query_monitor.load_environment"),
        patch.dict(os.environ, {}, clear=True),
    ):
        with pytest.raises(ValueError, match="Required environment variables are not set"):
            await main()


@pytest.mark.asyncio
async def test_main_error_handling(
    mock_env, mock_queries, mock_slack_client, mock_session
):
    """メイン関数のエラーハンドリングテスト"""
    with (
        patch("builtins.open", create=True) as mock_open,
        patch("app.query_monitor.WebClient", return_value=mock_slack_client),
        patch(
            "app.query_monitor.aiohttp.ClientSession",
            return_value=mock_session,
        ),
        patch.dict(
            os.environ,
            {
                "DIFY_API_KEY": "[API_KEY_REDACTED]",
                "SLACK_TOKEN": "test-token",
            },
        ),
    ):
        mock_open.return_value.__enter__.return_value.read.return_value = (
            json.dumps(mock_queries)
        )
        mock_session.post.side_effect = aiohttp.ClientError("予期せぬエラー")
        mock_slack_client.chat_postMessage.return_value = {"ok": True}

        with pytest.raises(
            QueryExecutionError,
            match="Failed to execute query after 3 attempts: 予期せぬエラー"
        ):
            await main()


@pytest.mark.asyncio
async def test_main_application_error(
    mock_env, mock_queries, mock_slack_client, mock_session
):
    """アプリケーションエラーのテスト"""
    with (
        patch("builtins.open", create=True) as mock_open,
        patch("app.query_monitor.WebClient", return_value=mock_slack_client),
        patch(
            "app.query_monitor.aiohttp.ClientSession",
            return_value=mock_session,
        ),
        patch.dict(
            os.environ,
            {
                "DIFY_API_KEY": "[API_KEY_REDACTED]",
                "SLACK_TOKEN": "test-token",
            },
        ),
    ):
        mock_open.return_value.__enter__.return_value.read.return_value = (
            json.dumps(mock_queries)
        )
        mock_session.post.side_effect = QueryExecutionError("アプリケーションエラー")
        mock_slack_client.chat_postMessage.side_effect = SlackApiError(
            "error", {"error": "invalid_auth"}
        )

        with pytest.raises(
            QueryExecutionError,
            match="アプリケーションエラー"
        ):
            await main()


@pytest.mark.asyncio
async def test_custom_dify_host(mock_session, mock_slack_client):
    """カスタムDifyホストのテスト"""
    custom_host = "https://custom.dify.example.com"
    monitor = QueryMonitor(
        dify_api_key="[API_KEY_REDACTED]",
        slack_token="test-slack-token",
        slack_channel="test-channel",
        dify_host=custom_host,
        session=mock_session,
        slack_client=mock_slack_client
    )
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"answer": "テスト回答"}
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    await monitor.process_query("test_query", "test_channel")
    
    mock_session.post.assert_called_once_with(
        f"{custom_host}/v1/chat-messages",
        headers={
            "Authorization": "Bearer test-dify-key",
            "Content-Type": "application/json"
        },
        json={
            "inputs": {},
            "query": "test_query",
            "response_mode": "blocking",
            "conversation_id": "",
            "user": "query_monitor"
        },
        timeout=ANY
    )


@pytest.mark.asyncio
async def test_process_query_empty_result_warning(
    monitor, mock_slack_client, mock_session
):
    """空の結果の警告テスト"""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"answer": ""}
    mock_session.post.return_value.__aenter__.return_value = mock_response
    mock_slack_client.chat_postMessage.return_value = {"ok": True}
    
    await monitor.process_query("test_query", "test_channel")
    
    mock_slack_client.chat_postMessage.assert_called_once()
    call_args = mock_slack_client.chat_postMessage.call_args[1]
    assert "警告" in call_args["blocks"][0]["text"]["text"]


@pytest.mark.asyncio
async def test_process_query_success_notification(
    monitor, mock_slack_client, mock_session, mock_response
):
    """成功時の通知テスト"""
    # モックの設定
    mock_response.json.return_value = {"answer": "テスト成功"}
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test-channel")

    # アサーション
    mock_slack_client.chat_postMessage.assert_called_once_with(
        channel="test-channel",
        blocks=[
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "✅ クエリ実行結果"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "テスト成功"},
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": "ステータス: success"}],
            },
            {"type": "divider"},
        ],
        text="テスト成功",
    )


@pytest.mark.asyncio
async def test_process_query_unexpected_error(
    monitor, mock_slack_client, mock_session
):
    """予期せぬエラーのテスト"""
    # モックの設定
    mock_session.post.side_effect = ValueError("予期せぬエラー")
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行とアサーション
    with pytest.raises(ValueError, match="予期せぬエラー"):
        await monitor.process_query("test_query", "test_channel")


@pytest.mark.asyncio
async def test_load_config_success(mock_env):
    """load_config関数のテスト"""
    with (
        patch("app.query_monitor.load_environment") as mock_load_env,
        patch.dict(
            os.environ,
            {
                "DIFY_API_KEY": "[API_KEY_REDACTED]",
                "SLACK_TOKEN": "test-token",
                "DIFY_HOST": "http://test-host",
                "REQUEST_TIMEOUT": "120",
            },
        ),
    ):
        mock_load_env.return_value = None

        # load_config関数を実行
        dify_api_key, slack_token, dify_host, request_timeout = load_config()

        # 戻り値の確認
        assert dify_api_key == "test-api-key"
        assert slack_token == "test-token"
        assert dify_host == "http://test-host"
        assert request_timeout == 120

        # load_environmentが呼び出されたことを確認
        mock_load_env.assert_called_once()


@pytest.mark.asyncio
async def test_load_config_missing_env():
    """load_config関数の必須環境変数不足のテスト"""
    with (
        patch("app.query_monitor.load_environment"),
        patch.dict(os.environ, {}, clear=True),
    ):
        with pytest.raises(ValueError, match="Required environment variables are not set"):
            load_config()


@pytest.mark.asyncio
async def test_execute_all_queries_success(monitor, mock_slack_client, mock_session, mock_response):
    """execute_all_queries関数の成功テスト"""
    # モックの設定
    mock_response.json.return_value = {"answer": "テスト結果"}
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await execute_all_queries(monitor)

    # アサーション
    mock_session.post.assert_called()
    mock_slack_client.chat_postMessage.assert_called()


@pytest.mark.asyncio
async def test_execute_all_queries_error(monitor, mock_slack_client, mock_session):
    """execute_all_queries関数のエラーテスト"""
    mock_session.post.side_effect = aiohttp.ClientError("APIエラー")
    
    with pytest.raises(
        QueryExecutionError,
        match="Failed to execute query after 3 attempts: APIエラー"
    ):
        await execute_all_queries(monitor)


@pytest.mark.asyncio
async def test_load_dotenv_success(mock_env, mock_queries, mock_slack_client, mock_session):
    """load_dotenvを使用した環境変数の読み込みテスト"""
    with (
        patch("builtins.open", create=True) as mock_open,
        patch("app.query_monitor.WebClient", return_value=mock_slack_client),
        patch("app.query_monitor.aiohttp.ClientSession", return_value=mock_session),
        patch("app.query_monitor.load_dotenv") as mock_load_dotenv,
    ):
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_queries)
        mock_load_dotenv.return_value = None

        # メイン関数を実行
        with patch.dict(os.environ, {"DIFY_API_KEY": "[API_KEY_REDACTED]", "SLACK_TOKEN": "test-token"}):
            await main()

        # load_dotenvが呼び出されたことを確認
        mock_load_dotenv.assert_called_once()


@pytest.mark.asyncio
async def test_session_property(mock_session):
    """sessionプロパティの初期化テスト"""
    # 一度モニターを作成して_sessionをNoneに設定
    request_timeout = 120
    monitor = QueryMonitor(
        dify_api_key="[API_KEY_REDACTED]",
        slack_token="test-token",
        slack_channel="test-channel",
        request_timeout=request_timeout
    )
    
    # _sessionをNoneに設定して新しいセッションが生成されるか確認
    monitor._session = None
    
    with (
        patch("aiohttp.ClientSession") as mock_client_session,
        patch("aiohttp.TCPConnector") as mock_connector,
        patch("aiohttp.ClientTimeout") as mock_timeout
    ):
        mock_connector.return_value = "mock_connector"
        mock_timeout.return_value = "mock_timeout"
        mock_client_session.return_value = mock_session
        
        # sessionプロパティを呼び出し
        session = monitor.session
        
        # セッションが新しく作成されたことを確認
        mock_timeout.assert_called_once_with(total=request_timeout)
        mock_connector.assert_called_once()
        mock_client_session.assert_called_once_with(
            timeout="mock_timeout",
            connector="mock_connector"
        )
        assert session == mock_session


@pytest.mark.asyncio
async def test_main_unexpected_error(
    mock_env, mock_queries, mock_slack_client, mock_session
):
    """予期せぬエラーのテスト"""
    with (
        patch("builtins.open", create=True) as mock_open,
        patch("app.query_monitor.WebClient", return_value=mock_slack_client),
        patch("app.query_monitor.aiohttp.ClientSession", return_value=mock_session),
        patch("app.query_monitor.load_environment") as mock_load_environment,
    ):
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_queries)
        mock_load_environment.return_value = None

        # 予期せぬエラーを発生させる
        mock_session.post.side_effect = Exception("Unexpected error")

        monitor = QueryMonitor(
            dify_api_key="[API_KEY_REDACTED]",
            slack_token="test-token",
            slack_channel="test-channel",
            slack_client=mock_slack_client,
            session=mock_session,
        )

        with pytest.raises(Exception, match="Unexpected error"):
            await monitor.process_query("test query", "test-channel")
