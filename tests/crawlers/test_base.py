"""BaseCrawlerのテストモジュール"""
from unittest.mock import Mock, patch

import pytest
from requests.exceptions import RequestException

from app.crawlers.base import BaseCrawler


class DummyCrawler(BaseCrawler):
    """テスト用クローラークラス"""
    def crawl(self) -> None:
        """クロール処理の実装"""
        pass


@pytest.fixture
def crawler():
    """クローラーのフィクスチャ"""
    return DummyCrawler()


def test_init_with_default_values(crawler):
    """デフォルト値での初期化テスト"""
    assert crawler.session is None
    assert crawler.timeout == 30
    assert crawler.max_retries == 3
    assert 'User-Agent' in crawler.headers


def test_init_with_custom_values():
    """カスタム値での初期化テスト"""
    session = Mock()
    headers = {'User-Agent': 'TestBot'}
    crawler = DummyCrawler(
        session=session,
        headers=headers,
        timeout=60,
        max_retries=5
    )
    
    assert crawler.session == session
    assert crawler.headers == headers
    assert crawler.timeout == 60
    assert crawler.max_retries == 5


@patch('requests.request')
def test_make_request_success(mock_request, crawler):
    """リクエスト成功時のテスト"""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_request.return_value = mock_response
    
    url = 'http://example.com'
    response = crawler._make_request(url)
    
    assert response == mock_response
    mock_request.assert_called_once_with(
        'GET',
        url,
        headers=crawler.headers,
        timeout=crawler.timeout
    )


@patch('requests.request')
def test_make_request_retry(mock_request, crawler):
    """リクエストリトライのテスト"""
    mock_request.side_effect = [
        RequestException(),
        RequestException(),
        Mock()  # 3回目で成功
    ]
    
    crawler._make_request('http://example.com')
    assert mock_request.call_count == 3


@patch('requests.request')
def test_make_request_max_retries_exceeded(mock_request, crawler):
    """最大リトライ���数超過時のテスト"""
    mock_request.side_effect = RequestException()
    
    with pytest.raises(RequestException):
        crawler._make_request('http://example.com')
    
    assert mock_request.call_count == crawler.max_retries


def test_save_without_session(crawler):
    """セッションなしでの保存テスト"""
    data = Mock()
    crawler.save(data)  # エラーを発生させずに処理を完了すること


def test_save_with_session():
    """セッションありでの保存テスト"""
    session = Mock()
    crawler = DummyCrawler(session=session)
    data = Mock()
    
    crawler.save(data)
    
    session.add.assert_called_once_with(data)
    session.commit.assert_called_once()


def test_save_with_error():
    """保存エラー時のテスト"""
    session = Mock()
    session.commit.side_effect = Exception()
    crawler = DummyCrawler(session=session)
    data = Mock()
    
    with pytest.raises(Exception):
        crawler.save(data)
    
    session.rollback.assert_called_once() 