"""ContentFetcherのテストモジュール。"""

import unittest
from unittest.mock import Mock, patch

import requests

from app.content_fetcher import ContentFetcher


class TestContentFetcher(unittest.TestCase):
    """ContentFetcherのテストクラス。"""

    def setUp(self):
        """テストの前準備。"""
        self.fetcher = ContentFetcher(timeout=5)
        self.test_url = "https://example.com"
        self.test_content = "<html><head><title>Test Page</title></head><body>Test content</body></html>"

    def test_fetch_content_success(self):
        """正常系: コンテンツの取得が成功するケース。"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = self.test_content
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = self.fetcher.fetch_content(self.test_url)

            self.assertEqual(result['url'], self.test_url)
            self.assertEqual(result['content'], self.test_content)
            self.assertEqual(result['title'], 'Test Page')
            mock_get.assert_called_once_with(self.test_url, timeout=5)

    def test_fetch_content_invalid_url(self):
        """異常系: 不正なURLが指定された場合。"""
        invalid_urls = [
            "",
            "not_a_url",
            "http://.com",
            "ftp://example.com"  # HTTPSのみサポート
        ]

        for url in invalid_urls:
            with self.assertRaises(ValueError):
                self.fetcher.fetch_content(url)

    def test_fetch_content_request_error(self):
        """異常系: リクエストエラーが発生した場合。"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")

            with self.assertRaises(requests.RequestException):
                self.fetcher.fetch_content(self.test_url)

    def test_fetch_content_timeout(self):
        """異常系: タイムアウトが発生した場合。"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.Timeout("Request timed out")

            with self.assertRaises(requests.Timeout):
                self.fetcher.fetch_content(self.test_url)

    def test_fetch_content_http_error(self):
        """異常系: HTTPエラーが発生した場合。"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
            mock_get.return_value = mock_response

            with self.assertRaises(requests.HTTPError):
                self.fetcher.fetch_content(self.test_url)

    def test_get_metrics(self):
        """メトリクス取得機能のテスト。"""
        # 正常系のリクエストを実行
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = self.test_content
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            self.fetcher.fetch_content(self.test_url)

        # メトリクスを取得して検証
        metrics = self.fetcher.get_metrics()
        self.assertIn('content_fetch', metrics)
        self.assertIsInstance(metrics['content_fetch']['success'], int)
        self.assertIsInstance(metrics['content_fetch']['error'], int)
        self.assertIsInstance(metrics['content_fetch']['total_time'], float)

    def test_fetch_content_no_title(self):
        """正常系: タイトルが存在しないコンテンツの取得。"""
        content_without_title = "<html><body>No title here</body></html>"
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = content_without_title
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = self.fetcher.fetch_content(self.test_url)

            self.assertEqual(result['url'], self.test_url)
            self.assertEqual(result['content'], content_without_title)
            self.assertEqual(result['title'], '')

    def test_fetch_content_malformed_title(self):
        """正常系: 不正な形式のタイトルを含むコンテンツの取得。"""
        malformed_content = "<html><head><title>Test</title><title>Duplicate</title></head><body>Test</body></html>"
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = malformed_content
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = self.fetcher.fetch_content(self.test_url)

            self.assertEqual(result['url'], self.test_url)
            self.assertEqual(result['content'], malformed_content)
            self.assertEqual(result['title'], 'Test') 