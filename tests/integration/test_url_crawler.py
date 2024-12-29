"""
実際のURLに対するクロール機能のインテグレーションテスト
"""
import asyncio
from typing import List
from urllib.parse import urljoin

import pytest

from app.analyzer.url_analyzer import URLAnalyzer
from app.crawler.url_collector import URLCollector
from app.errors.url_analysis_errors import NetworkError, RateLimitError
from app.metrics.url_analysis_metrics import URLAnalysisMetrics


class TestURLCrawler:
    """URLクローラーの統合テスト"""

    @pytest.fixture
    async def url_collector(self) -> URLCollector:
        """URLコレクターのフィクスチャ"""
        collector = URLCollector(
            max_concurrent_requests=3,
            request_timeout=30.0
        )
        return collector

    @pytest.fixture
    async def url_analyzer(self) -> URLAnalyzer:
        """URLアナライザーのフィクスチャ"""
        analyzer = URLAnalyzer()
        return analyzer

    @pytest.fixture
    async def metrics(self) -> URLAnalysisMetrics:
        """メトリクス収集のフィクスチャ"""
        return URLAnalysisMetrics()

    @pytest.mark.asyncio
    async def test_crawl_corporate_website(
        self,
        url_collector: URLCollector,
        url_analyzer: URLAnalyzer,
        metrics: URLAnalysisMetrics
    ):
        """企業Webサイトのクロールテスト"""
        # テスト対象のURL
        base_url = "https://www.accenture.com/jp-ja/"
        
        try:
            # サイトマップからURLを収集
            urls = await url_collector.collect_from_sitemap(base_url)
            assert len(urls) > 0, "サイトマップからURLを取得できませんでした"

            # 収集したURLの分析
            for url in urls[:5]:  # テスト用に最初の5件のみ処理
                result = await url_analyzer.analyze(url)
                metrics.record_url_processing(
                    url=url,
                    result=result,
                    processing_time=result.get("processing_time", 0.0),
                    llm_latency=result.get("llm_latency", 0.0)
                )

            # メトリクスの確認
            assert metrics.processed_urls > 0, "URLが処理されていません"
            assert metrics.error_count == 0, "エラーが発生しています"

        except NetworkError as e:
            pytest.skip(f"ネットワークエラーが発生しました: {str(e)}")
        except RateLimitError as e:
            pytest.skip(f"レート制限に達しました: {str(e)}")

    @pytest.mark.asyncio
    async def test_crawl_navigation_links(
        self,
        url_collector: URLCollector,
        url_analyzer: URLAnalyzer,
        metrics: URLAnalysisMetrics
    ):
        """ナビゲーションリンクのクロールテスト"""
        # テスト対象のURL
        base_url = "https://www.accenture.com/jp-ja/about/company-index"
        
        try:
            # ナビゲーションからURLを収集
            urls = await url_collector.collect_from_navigation(base_url)
            assert len(urls) > 0, "ナビゲーションからURLを取得できませんでした"

            # 収集したURLの分析
            for url in urls[:3]:  # テスト用に最初の3件のみ処理
                result = await url_analyzer.analyze(url)
                metrics.record_url_processing(
                    url=url,
                    result=result,
                    processing_time=result.get("processing_time", 0.0),
                    llm_latency=result.get("llm_latency", 0.0)
                )

            # メトリクスの確認
            assert metrics.processed_urls > 0, "URLが処理されていません"
            assert metrics.error_count == 0, "エラーが発生しています"

        except NetworkError as e:
            pytest.skip(f"ネットワークエラーが発生しました: {str(e)}")
        except RateLimitError as e:
            pytest.skip(f"レート制限に達しました: {str(e)}")

    @pytest.mark.asyncio
    async def test_error_handling_invalid_url(
        self,
        url_collector: URLCollector,
        url_analyzer: URLAnalyzer,
        metrics: URLAnalysisMetrics
    ):
        """無効なURLのエラーハンドリングテスト"""
        # 無効なURL
        invalid_url = "https://www.accenture.com/jp-ja/invalid-page-that-does-not-exist"
        
        try:
            # URLの分析
            result = await url_analyzer.analyze(invalid_url)
            metrics.record_url_processing(
                url=invalid_url,
                result=result,
                processing_time=result.get("processing_time", 0.0),
                llm_latency=result.get("llm_latency", 0.0)
            )
        except NetworkError as e:
            assert e.status_code == 404, "404エラーが発生すべきです"
            metrics.record_error(invalid_url, e)

        # エラーメトリクスの確認
        assert metrics.error_count > 0, "エラーが記録されていません"

    @pytest.mark.asyncio
    async def test_robots_txt_handling(
        self,
        url_collector: URLCollector
    ):
        """robots.txtの処理テスト"""
        # テスト対象のURL
        base_url = "https://www.accenture.com/jp-ja/"
        
        try:
            # robots.txtの取得と解析
            sitemap_urls = await url_collector.get_sitemaps_from_robots(base_url)
            assert len(sitemap_urls) > 0, "robots.txtからサイトマップURLを取得できませんでした"

            # サイトマップの存在確認
            for sitemap_url in sitemap_urls:
                assert sitemap_url.startswith("http"), "無効なサイトマップURLです"

        except NetworkError as e:
            pytest.skip(f"robots.txtの取得に失敗しました: {str(e)}") 