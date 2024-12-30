"""
実際のURLに対するクロール機能のインテグレーションテスト
"""
import pytest

from app.crawlers.url_collector import URLCollector
from app.errors.url_analysis_errors import NetworkError, RateLimitError
from app.metrics.url_analysis_metrics import URLAnalysisMetrics
from app.site_analyzer import URLAnalyzer


class TestURLCrawler:
    """URLクローラーの統合テスト"""

    @pytest.fixture
    def url_collector(self) -> URLCollector:
        """URLコレクターのフィクスチャ"""
        return URLCollector(max_concurrent_requests=3, request_timeout=10.0)

    @pytest.fixture
    def url_analyzer(self) -> URLAnalyzer:
        """URLアナライザーのフィクスチャ"""
        return URLAnalyzer(request_timeout=10.0)

    @pytest.fixture
    def metrics(self) -> URLAnalysisMetrics:
        """メトリクス収集のフィクスチャ"""
        return URLAnalysisMetrics()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_crawl_corporate_website(
        self,
        url_collector: URLCollector,
        url_analyzer: URLAnalyzer,
        metrics: URLAnalysisMetrics,
    ):
        """企業Webサイトのクロールテスト"""
        # テスト対象のURL
        base_url = "https://www.accenture.com/jp-ja/"

        try:
            # サイトマップからURLを収集
            urls = await url_collector.collect_from_sitemap(base_url)
            assert len(urls) > 0, "サイトマップからURLを取得できませんでした"

            # 収集したURLの分析（最大3件まで）
            for url in urls[:3]:  # 処理数を3件に制限
                result = await url_analyzer.analyze(url)
                metrics.record_url_processing(
                    url=url,
                    result=result,
                    processing_time=result.get("processing_time", 0.0),
                    llm_latency=result.get("llm_latency", 0.0),
                )

            # メトリクスの確認
            assert metrics.processed_urls > 0, "URLが処理されていません"
            assert metrics.error_count == 0, "エラーが発生しています"

        except NetworkError as e:
            pytest.skip(f"ネットワークエラーが発生しました: {str(e)}")
        except RateLimitError as e:
            pytest.skip(f"レート制限に達しました: {str(e)}")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_crawl_navigation_links(
        self,
        url_collector: URLCollector,
        url_analyzer: URLAnalyzer,
        metrics: URLAnalysisMetrics,
    ):
        """ナビゲーションリンクのクロールテスト"""
        # テスト対象のURL
        base_url = "https://www.accenture.com/jp-ja/about/company-index"

        try:
            # ナビゲーションからURLを収集
            urls = await url_collector.collect_from_navigation(base_url)
            assert len(urls) > 0, "ナビゲーションからURLを取得できませんでした"

            # 収集したURLの分析（最大2件まで）
            for url in urls[:2]:  # 処理数を2件に制限
                result = await url_analyzer.analyze(url)
                metrics.record_url_processing(
                    url=url,
                    result=result,
                    processing_time=result.get("processing_time", 0.0),
                    llm_latency=result.get("llm_latency", 0.0),
                )

            # メトリクスの確認
            assert metrics.processed_urls > 0, "URLが処理されていません"
            assert metrics.error_count == 0, "エラーが発生しています"

        except NetworkError as e:
            pytest.skip(f"ネットワークエラーが発生しました: {str(e)}")
        except RateLimitError as e:
            pytest.skip(f"レート制限に達しました: {str(e)}")

    @pytest.mark.asyncio
    @pytest.mark.timeout(20)
    async def test_error_handling_invalid_url(
        self,
        url_collector: URLCollector,
        url_analyzer: URLAnalyzer,
        metrics: URLAnalysisMetrics,
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
                llm_latency=result.get("llm_latency", 0.0),
            )
        except NetworkError as e:
            assert e.status_code == 404, "404エラーが発生すべきです"
            metrics.record_error(invalid_url, e)

        # エラーメトリクスの確認
        assert metrics.error_count > 0, "エラーが記録されていません"

    @pytest.mark.asyncio
    @pytest.mark.timeout(20)
    async def test_robots_txt_handling(self, url_collector: URLCollector):
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
