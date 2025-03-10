import asyncio
import json
import os
from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
import pytest_asyncio
from slack_sdk.errors import SlackApiError

from app.query_monitor import (
    QueryExecutionError,
    QueryMonitor,
    SlackNotificationError,
    main,
)


@pytest.fixture(scope="session")
def event_loop_policy():
    """イベントループポリシーの設定"""
    return asyncio.get_event_loop_policy()


@pytest_asyncio.fixture
async def mock_response():
    """レスポンスのモック"""
    response = AsyncMock()
    response.status = 200
    response.json.return_value = {"answer": "テスト結果"}
    response.raise_for_status = AsyncMock()
    return response


@pytest_asyncio.fixture
async def mock_session(mock_response):
    """セッションのモック"""
    session = AsyncMock(spec=aiohttp.ClientSession)
    
    # 非同期コンテキストマネージャーの正しい実装
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
    with patch.dict(os.environ, {
        "SLACK_TOKEN": "test-token",
        "DIFY_API_KEY": "test-dify-key"
    }):
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
                "channel": "test-channel"
            }
        ]
    }


@pytest_asyncio.fixture
async def monitor(mock_queries, mock_slack_client, mock_session):
    """QueryMonitorインスタンスの作成"""
    with patch("builtins.open", create=True) as mock_open, \
         patch("app.query_monitor.WebClient", return_value=mock_slack_client), \
         patch("app.query_monitor.aiohttp.ClientSession", return_value=mock_session):
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_queries)
        monitor = QueryMonitor(
            dify_api_key="test-dify-key",
            slack_token="test-token",
            slack_channel="test-channel",
            slack_client=mock_slack_client,
            session=mock_session
        )
        yield monitor


@pytest.mark.asyncio
async def test_init_success(monitor):
    """初期化の成功テスト"""
    assert monitor.dify_api_key == "test-dify-key"
    assert monitor.slack_channel == "test-channel"
    assert len(monitor.queries) == 1


@pytest.mark.asyncio
async def test_init_missing_env():
    """環境変数不足時の初期化テスト"""
    with pytest.raises(ValueError, match="All parameters are required"):
        QueryMonitor("", "", "")


@pytest.mark.asyncio
async def test_process_query_success(monitor, mock_slack_client, mock_session, mock_response):
    """クエリ実行成功のテスト"""
    # モックの設定
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test_channel")

    # アサーション
    mock_session.post.assert_called_once()
    mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_execution_error(monitor, mock_slack_client, mock_session):
    """クエリ実行エラーのテスト"""
    # モックの設定
    mock_session.post.side_effect = aiohttp.ClientError("APIエラー")
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test_channel")

    # アサーション
    assert mock_slack_client.chat_postMessage.call_count == 2
    calls = mock_slack_client.chat_postMessage.call_args_list
    assert calls[0].kwargs["channel"] == "errors"
    assert calls[1].kwargs["channel"] == "test_channel"


@pytest.mark.asyncio
async def test_process_query_notification_error(monitor, mock_slack_client, mock_session):
    """Slack通知エラーのテスト"""
    # モックの設定
    mock_response = MagicMock()
    mock_response.json.return_value = {"answer": "テスト結果"}
    mock_session.post.return_value = mock_response
    mock_slack_client.chat_postMessage.side_effect = SlackApiError("error", {"error": "test_error"})

    # テスト実行とアサーション
    with pytest.raises(SlackNotificationError):
        await monitor.process_query("test_query", "test_channel")


@pytest.mark.asyncio
async def test_process_query_empty_result(monitor, mock_slack_client, mock_session):
    """空の結果を処理するテスト"""
    # モックの設定
    mock_response = MagicMock()
    mock_response.json.return_value = {"answer": ""}
    mock_session.post.return_value = mock_response
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test_channel")

    # アサーション
    mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_invalid_json(monitor, mock_slack_client, mock_session):
    """無効なJSONレスポンスを処理するテスト"""
    # モックの設定
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_session.post.return_value = mock_response
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test_channel")

    # アサーション
    mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_timeout(monitor, mock_slack_client, mock_session):
    """タイムアウトを処理するテスト"""
    # モックの設定
    mock_session.post.side_effect = aiohttp.ClientTimeout("Request timed out")
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test_channel")

    # アサーション
    mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_connection_error(monitor, mock_slack_client, mock_session):
    """接続エラーを処理するテスト"""
    # モックの設定
    mock_session.post.side_effect = aiohttp.ClientConnectionError("Connection failed")
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test_channel")

    # アサーション
    assert mock_slack_client.chat_postMessage.call_count == 2
    calls = mock_slack_client.chat_postMessage.call_args_list
    assert calls[0].kwargs["channel"] == "errors"
    assert calls[1].kwargs["channel"] == "test_channel"


@pytest.mark.asyncio
async def test_process_query_http_error(monitor, mock_slack_client, mock_session, mock_response):
    """HTTPエラーを処理するテスト"""
    # モックの設定
    mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info=MagicMock(),
        history=(),
        status=500
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
    mock_session.post.assert_called_once()


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
    mock_slack_client.chat_postMessage.side_effect = SlackApiError("error", {"error": "test_error"})

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
        mock_open.return_value.__enter__.return_value.read.return_value = "invalid json"
        with pytest.raises(json.JSONDecodeError):
            monitor._load_queries()


@pytest.mark.asyncio
async def test_main_success(mock_env, mock_queries, mock_slack_client, mock_session, mock_response):
    """メイン関数成功のテスト"""
    with patch("builtins.open", create=True) as mock_open, \
         patch("app.query_monitor.WebClient", return_value=mock_slack_client), \
         patch("app.query_monitor.aiohttp.ClientSession", return_value=mock_session), \
         patch.dict(os.environ, {
             "DIFY_API_KEY": "test-api-key",
             "SLACK_TOKEN": "test-token",
             "SLACK_CHANNEL": "test-channel"
         }):
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_queries)
        mock_slack_client.chat_postMessage.return_value = {"ok": True}

        # テスト実行
        await main()

        # アサーション
        mock_session.post.assert_called_once()
        mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_main_missing_env():
    """メイン関数環境変数不足のテスト"""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Required environment variables are not set"):
            await main()


@pytest.mark.asyncio
async def test_main_error_handling(mock_env, mock_queries, mock_slack_client, mock_session):
    """メイン関数エラーハンドリングのテスト"""
    with patch("builtins.open", create=True) as mock_open, \
         patch("app.query_monitor.WebClient", return_value=mock_slack_client), \
         patch("app.query_monitor.aiohttp.ClientSession", return_value=mock_session):
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_queries)
        mock_session.post.side_effect = Exception("予期せぬエラー")

        # テスト実行
        with pytest.raises(Exception):
            await main()


@pytest.mark.asyncio
async def test_custom_dify_host(mock_env, mock_slack_client, mock_session, mock_response):
    """カスタムDifyホストのテスト"""
    with patch.dict(os.environ, {
        "DIFY_API_KEY": "test-dify-key",
        "SLACK_TOKEN": "test-token",
        "DIFY_HOST": "https://custom.dify.example.com"
    }):
        monitor = QueryMonitor(
            dify_api_key="test-dify-key",
            slack_token="test-token",
            slack_channel="test-channel",
            slack_client=mock_slack_client,
            session=mock_session
        )
        await monitor.execute_query("test_query")
        
        # カスタムホストが使用されていることを確認
        mock_session.post.assert_called_once_with(
            "https://custom.dify.example.com/v1/completion-messages",
            headers={"Authorization": "Bearer test-dify-key", "Content-Type": "application/json"},
            json={"query": "test_query"},
            timeout=mock.ANY
        ) 