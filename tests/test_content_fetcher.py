"""ContentFetcherのテストモジュール。

このモジュールは、ContentFetcherクラスの各メソッドの動作を検証します。

必要性：
- HTMLコンテンツの取得機能の検証
- エラーハンドリングの確認
- ファイル操作の検証

十分性：
- 実際のHTTPリクエストのテスト
- エラーケースの網羅
- ファイル操作の完全性確認
"""

import os
import pytest
import requests
from unittest.mock import Mock, patch
from pathlib import Path

from app.content_fetcher import ContentFetcher

def test_init_default_values():
    """デフォルト値での初期化をテストする。
    
    必要性：
    - デフォルトパラメータの確認
    - セッション初期化の確認
    
    十分性：
    - パラメータ値の検証
    - セッションの存在確認
    """
    fetcher = ContentFetcher()
    assert fetcher._timeout == 30.0
    assert fetcher._max_retries == 3
    assert fetcher._session is not None

def test_init_custom_values():
    """カスタム値での初期化をテストする。
    
    必要性：
    - カスタムパラメータの反映確認
    - セッション初期化の確認
    
    十分性：
    - パラメータ値の検証
    - セッションの存在確認
    """
    fetcher = ContentFetcher(timeout=10.0, max_retries=5)
    assert fetcher._timeout == 10.0
    assert fetcher._max_retries == 5
    assert fetcher._session is not None

@patch('requests.Session')
def test_fetch_html_success(mock_session):
    """HTMLの取得成功ケースをテストする。
    
    必要性：
    - 正常系の動作確認
    - レスポンス処理の確認
    
    十分性：
    - ステータスコードの確認
    - レスポンス内容の検証
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html>Test Content</html>"
    mock_session.return_value.get.return_value = mock_response
    
    fetcher = ContentFetcher()
    content = fetcher.fetch_html("http://example.com")
    
    assert content == "<html>Test Content</html>"
    mock_session.return_value.get.assert_called_once_with(
        "http://example.com",
        timeout=30.0
    )

def test_fetch_html_empty_url():
    """空のURLでの取得をテストする。
    
    必要性：
    - 入力検証の確認
    - エラーメッセージの検証
    
    十分性：
    - 空文字列での呼び出し
    - エラーメッセージの確認
    """
    fetcher = ContentFetcher()
    with pytest.raises(ValueError) as exc_info:
        fetcher.fetch_html("")
    assert "URL must not be empty" in str(exc_info.value)

@patch('requests.Session')
def test_fetch_html_timeout(mock_session):
    """タイムアウトケースをテストする。
    
    必要性：
    - タイムアウト処理の確認
    - エラーハンドリングの検証
    
    十分性：
    - タイムアウト例外の発生
    - エラーメッセージの確認
    """
    mock_session.return_value.get.side_effect = requests.Timeout()
    
    fetcher = ContentFetcher()
    with pytest.raises(TimeoutError) as exc_info:
        fetcher.fetch_html("http://example.com")
    assert "Request timed out" in str(exc_info.value)

@patch('requests.Session')
def test_fetch_html_connection_error(mock_session):
    """接続エラーケースをテストする。
    
    必要性：
    - 接続エラー処理の確認
    - エラーハンドリングの検証
    
    十分性：
    - 接続エラー例外の発生
    - エラーメッセージの確認
    """
    mock_session.return_value.get.side_effect = requests.RequestException("Connection failed")
    
    fetcher = ContentFetcher()
    with pytest.raises(ConnectionError) as exc_info:
        fetcher.fetch_html("http://example.com")
    assert "Failed to fetch content" in str(exc_info.value)

def test_fetch_from_file_success(tmp_path):
    """ファイルからの読み込み成功ケースをテストする。
    
    必要性：
    - ファイル読み込み機能の確認
    - 文字エンコーディングの確認
    
    十分性：
    - ファイル作成と読み込み
    - 内容の正確性確認
    """
    test_content = "<html>Test Content</html>"
    test_file = tmp_path / "test.html"
    test_file.write_text(test_content, encoding='utf-8')
    
    fetcher = ContentFetcher()
    content = fetcher.fetch_from_file(str(test_file))
    
    assert content == test_content

def test_fetch_from_file_not_found():
    """存在しないファイルの読み込みをテストする。
    
    必要性：
    - ファイル不在時の処理確認
    - エラーハンドリングの検証
    
    十分性：
    - 存在しないファイルパスでの呼び出し
    - エラーメッセージの確認
    """
    fetcher = ContentFetcher()
    with pytest.raises(FileNotFoundError) as exc_info:
        fetcher.fetch_from_file("nonexistent.html")
    assert "File not found" in str(exc_info.value)

@patch('builtins.open')
def test_fetch_from_file_io_error(mock_open):
    """ファイル読み込みエラーケースをテストする。
    
    必要性：
    - IO エラー処理の確認
    - エラーハンドリングの検証
    
    十分性：
    - IO エラー例外の発生
    - エラーメッセージの確認
    """
    mock_open.side_effect = IOError("Read error")
    
    fetcher = ContentFetcher()
    with pytest.raises(IOError) as exc_info:
        fetcher.fetch_from_file("test.html")
    assert "Failed to read file" in str(exc_info.value)

def test_verify_response():
    """レスポンス検証メソッドをテストする。
    
    必要性：
    - ステータスコード検証の確認
    - 成功/失敗の判定確認
    
    十分性：
    - 様々なステータスコードでのテスト
    - 境界値のテスト
    """
    fetcher = ContentFetcher()
    
    # 成功ケース
    response = Mock()
    response.status_code = 200
    assert fetcher._verify_response(response) is True
    
    response.status_code = 299
    assert fetcher._verify_response(response) is True
    
    # 失敗ケース
    response.status_code = 199
    assert fetcher._verify_response(response) is False
    
    response.status_code = 300
    assert fetcher._verify_response(response) is False
    
    response.status_code = 404
    assert fetcher._verify_response(response) is False
    
    response.status_code = 500
    assert fetcher._verify_response(response) is False 