"""ContentFetcherのテストモジュール。"""

import os
from pathlib import Path
import pytest
import responses
from unittest.mock import mock_open, patch
import requests

from app.content_fetcher import ContentFetcher


@pytest.fixture
def content_fetcher():
    return ContentFetcher()


@responses.activate
def test_fetch_html_success(content_fetcher):
    """fetch_html()の正常系テスト"""
    test_url = "https://example.com"
    test_html = "<html><body>Test content</body></html>"
    responses.add(
        responses.GET,
        test_url,
        body=test_html,
        status=200,
        content_type="text/html"
    )

    result = content_fetcher.fetch_html(test_url)
    assert result == test_html


@responses.activate
def test_fetch_html_404(content_fetcher):
    """fetch_html()の404エラー処理テスト"""
    test_url = "https://example.com/not-found"
    responses.add(
        responses.GET,
        test_url,
        status=404
    )

    with pytest.raises(ConnectionError) as exc_info:
        content_fetcher.fetch_html(test_url)
    assert "404" in str(exc_info.value)


@responses.activate
def test_fetch_html_timeout(content_fetcher):
    """fetch_html()のタイムアウト処理テスト"""
    test_url = "https://example.com/timeout"
    responses.add(
        responses.GET,
        test_url,
        body=requests.exceptions.Timeout()
    )

    with pytest.raises(TimeoutError):
        content_fetcher.fetch_html(test_url)


def test_fetch_html_empty_url(content_fetcher):
    """fetch_html()の空URL処理テスト"""
    with pytest.raises(ValueError) as exc_info:
        content_fetcher.fetch_html("")
    assert "URL" in str(exc_info.value)


def test_fetch_from_file_success(content_fetcher):
    """fetch_from_file()の正常系テスト"""
    test_content = "<html><body>Test content from file</body></html>"
    test_path = "test.html"

    with patch("builtins.open", mock_open(read_data=test_content)):
        result = content_fetcher.fetch_from_file(test_path)
        assert result == test_content


def test_fetch_from_file_not_found(content_fetcher):
    """fetch_from_file()のファイル未存在テスト"""
    test_path = "non_existent.html"

    with pytest.raises(FileNotFoundError):
        content_fetcher.fetch_from_file(test_path)


def test_verify_response_success(content_fetcher):
    """_verify_response()のステータスコード判定テスト"""
    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code

    assert content_fetcher._verify_response(MockResponse(200)) is True
    assert content_fetcher._verify_response(MockResponse(299)) is True
    assert content_fetcher._verify_response(MockResponse(404)) is False
    assert content_fetcher._verify_response(MockResponse(500)) is False 