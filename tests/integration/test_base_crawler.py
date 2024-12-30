"""
BaseCrawlerクラスの統合テスト
"""

from unittest.mock import Mock, patch

import pytest
from requests.exceptions import RequestException
from sqlalchemy.orm import Session

from app.crawlers.base import BaseCrawler
from app.monitoring.monitor import CrawlerMonitor


class TestCrawler(BaseCrawler):
    """テスト用クローラークラス"""
    def _crawl(self) -> None:
        self._make_request("https://example.com")


@pytest.fixture
def mock_session():
    return Mock(spec=Session)


@pytest.fixture
def mock_monitor():
    return Mock(spec=CrawlerMonitor)


def test_crawler_initialization(mock_session, mock_monitor):
    """クローラーの初期化テスト"""
    crawler = TestCrawler(
        company_code="1234",
        session=mock_session,
        monitor=mock_monitor,
        timeout=60,
        max_retries=5
    )
    
    assert crawler.company_code == "1234"
    assert crawler.session == mock_session
    assert crawler.monitor == mock_monitor
    assert crawler.timeout == 60
    assert crawler.max_retries == 5
    assert "User-Agent" in crawler.headers


def test_crawler_monitoring(mock_session, mock_monitor):
    """モニタリング機能のテスト"""
    crawler = TestCrawler(
        company_code="1234",
        session=mock_session,
        monitor=mock_monitor
    )
    
    with patch.object(crawler, '_make_request') as mock_request:
        crawler.crawl()
        
        mock_monitor.start_crawler.assert_called_once_with("1234")
        mock_monitor.stop_crawler.assert_called_once_with("1234")
        mock_request.assert_called_once()


def test_request_retry_mechanism(mock_session, mock_monitor):
    """リクエストのリトライ機能テスト"""
    crawler = TestCrawler(
        company_code="1234",
        session=mock_session,
        monitor=mock_monitor,
        max_retries=3
    )
    
    with patch('requests.request') as mock_request:
        mock_request.side_effect = [
            RequestException("Network error"),
            RequestException("Timeout"),
            Mock(raise_for_status=Mock())  # 3回目で成功
        ]
        
        crawler.crawl()
        assert mock_request.call_count == 3
        mock_monitor.log_warning.assert_called()


def test_request_failure_handling(mock_session, mock_monitor):
    """リクエスト失敗時のエラーハンドリングテスト"""
    crawler = TestCrawler(
        company_code="1234",
        session=mock_session,
        monitor=mock_monitor,
        max_retries=2
    )
    
    with patch('requests.request') as mock_request:
        mock_request.side_effect = RequestException("Network error")
        
        with pytest.raises(RequestException):
            crawler.crawl()
        
        mock_monitor.log_error.assert_called_once()
        mock_monitor.stop_crawler.assert_called_once_with("1234", status="error")


def test_progress_update(mock_session, mock_monitor):
    """進捗更新機能のテスト"""
    crawler = TestCrawler(
        company_code="1234",
        session=mock_session,
        monitor=mock_monitor
    )
    
    crawler._update_progress(5, 10)
    mock_monitor.update_progress.assert_called_once_with("1234", 5, 10)


def test_data_saving(mock_session):
    """データ保存機能のテスト"""
    crawler = TestCrawler(session=mock_session)
    test_data = Mock()
    
    crawler.save(test_data)
    
    mock_session.add.assert_called_once_with(test_data)
    mock_session.commit.assert_called_once()


def test_data_saving_error_handling(mock_session):
    """データ保存エラー時のハンドリングテスト"""
    crawler = TestCrawler(session=mock_session)
    test_data = Mock()
    
    mock_session.commit.side_effect = Exception("Database error")
    
    with pytest.raises(Exception):
        crawler.save(test_data)
    
    mock_session.rollback.assert_called_once() 