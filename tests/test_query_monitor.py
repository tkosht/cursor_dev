import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import requests
from slack_sdk.errors import SlackApiError

from app.query_monitor import (
    QueryExecutionError,
    QueryMonitor,
    SlackNotificationError,
    main,
)


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


@pytest.fixture
def mock_slack_client():
    """Slackクライアントのモック"""
    mock = AsyncMock()
    mock.token = "test-token"
    mock.chat_postMessage = AsyncMock()
    return mock


@pytest.fixture
def mock_session():
    """セッションのモック"""
    mock = MagicMock()
    mock.post = AsyncMock()
    return mock


@pytest.fixture
def monitor(mock_queries, mock_slack_client, mock_session):
    """QueryMonitorインスタンスの作成"""
    with patch("builtins.open", create=True) as mock_open, \
         patch("app.query_monitor.WebClient", return_value=mock_slack_client), \
         patch("app.query_monitor.requests.Session", return_value=mock_session):
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_queries)
        return QueryMonitor(
            dify_api_key="test-dify-key",
            slack_token="test-token",
            slack_channel="test-channel",
            slack_client=mock_slack_client,
            session=mock_session
        )


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
async def test_process_query_success(monitor, mock_slack_client, mock_session):
    """クエリ実行成功のテスト"""
    # モックの設定
    mock_response = MagicMock()
    mock_response.json.return_value = {"answer": "テスト結果"}
    mock_session.post.return_value = mock_response
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
    mock_session.post.side_effect = requests.exceptions.RequestException("APIエラー")
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test_channel")

    # アサーション
    mock_slack_client.chat_postMessage.assert_called_once()


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
    mock_session.post.side_effect = requests.exceptions.Timeout("Request timed out")
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test_channel")

    # アサーション
    mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_connection_error(monitor, mock_slack_client, mock_session):
    """接続エラーを処理するテスト"""
    # モックの設定
    mock_session.post.side_effect = requests.exceptions.ConnectionError("Connection failed")
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test_channel")

    # アサーション
    mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_http_error(monitor, mock_slack_client, mock_session):
    """HTTPエラーを処理するテスト"""
    # モックの設定
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP Error")
    mock_session.post.return_value = mock_response
    mock_slack_client.chat_postMessage.return_value = {"ok": True}

    # テスト実行
    await monitor.process_query("test_query", "test_channel")

    # アサーション
    mock_slack_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_execute_query_success(monitor, mock_session):
    """クエリ実行成功のテスト"""
    # モックの設定
    mock_response = MagicMock()
    mock_response.json.return_value = {"answer": "テスト結果"}
    mock_session.post.return_value = mock_response

    # テスト実行
    result = await monitor.execute_query("test_query")

    # アサーション
    assert result == {"answer": "テスト結果"}
    mock_session.post.assert_called_once()


@pytest.mark.asyncio
async def test_execute_query_failure(monitor, mock_session):
    """クエリ実行失敗のテスト"""
    # モックの設定
    mock_session.post.side_effect = requests.exceptions.RequestException("APIエラー")

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
async def test_main_success(mock_env, mock_queries, mock_slack_client, mock_session):
    """メイン関数成功のテスト"""
    with patch("builtins.open", create=True) as mock_open, \
         patch("app.query_monitor.WebClient", return_value=mock_slack_client), \
         patch("app.query_monitor.requests.Session", return_value=mock_session), \
         patch.dict(os.environ, {
             "DIFY_API_KEY": "test-api-key",
             "SLACK_TOKEN": "test-token",
             "SLACK_CHANNEL": "test-channel"
         }):
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_queries)
        mock_response = MagicMock()
        mock_response.json.return_value = {"answer": "テスト結果"}
        mock_session.post.return_value = mock_response
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
         patch("app.query_monitor.requests.Session", return_value=mock_session):
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_queries)
        mock_session.post.side_effect = Exception("予期せぬエラー")

        # テスト実行
        with pytest.raises(Exception):
            await main() 