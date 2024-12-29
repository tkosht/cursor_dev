"""
実際の企業サイトを使用した統合テスト
"""
import asyncio
import logging
import sys

import pytest

from app.errors.url_analysis_errors import (
    NetworkError,
    RateLimitError,
    URLAnalysisError,
)
from app.llm.manager import LLMManager
from app.metrics.url_analysis_metrics import URLAnalysisMetrics
from app.site_analyzer import SiteAnalyzer

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# すべてのロガーのレベルをDEBUGに設定
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.DEBUG)

# テスト対象の企業サイト
TARGET_SITES = [
    "https://www.accenture.com/jp-ja",  # アクセンチュア（日本）
    "https://www.softbank.jp/",         # ソフトバンク
    "https://www.toyota.co.jp/",        # トヨタ自動車
]

# エラーテスト用のサイト
ERROR_TEST_SITES = [
    "https://nonexistent.example.com",           # 存在しないドメイン
    "https://www.google.com/nonexistent-page",   # 404エラー
    "https://api.github.com/rate-limit",         # レート制限テスト
]


@pytest.fixture
def metrics() -> URLAnalysisMetrics:
    """メトリクス収集のフィクスチャ"""
    return URLAnalysisMetrics()


@pytest.mark.asyncio
async def test_real_site_analysis(metrics: URLAnalysisMetrics):
    """
    実際の企業サイトで情報抽出をテスト
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting test_real_site_analysis")
    
    llm_manager = LLMManager()
    logger.info("LLMManager initialized")
    
    for base_url in TARGET_SITES:
        logger.info(f"\n=== Starting analysis of {base_url} ===")
        
        async with SiteAnalyzer(llm_manager) as analyzer:
            try:
                logger.info("Initialized SiteAnalyzer")
                
                # サイト構造の解析
                logger.info("Starting site structure analysis")
                start_time = asyncio.get_event_loop().time()
                result = await analyzer.analyze_site_structure(base_url)
                end_time = asyncio.get_event_loop().time()
                logger.info("Completed site structure analysis")

                # メトリクスの記録
                processing_time = end_time - start_time
                metrics.record_url_processing(
                    url=base_url,
                    result=result,
                    processing_time=processing_time,
                    llm_latency=analyzer.get_llm_latency()
                )
                
                # 結果の検証
                assert result is not None, f"Result should not be None for {base_url}"
                assert "sitemap" in result, "Result should contain sitemap"
                assert "navigation" in result, "Result should contain navigation"
                assert "relevant_pages" in result, "Result should contain relevant_pages"
                
                # 結果の表示
                logger.info("\nSitemap URLs:")
                for url in result["sitemap"][:3]:
                    logger.info(f"- {url}")
                    assert url.startswith("http"), f"Invalid URL format: {url}"
                
                logger.info("\nRelevant Pages:")
                for page in result["relevant_pages"][:2]:
                    logger.info(f"\nURL: {page['url']}")
                    logger.info(f"Type: {page['page_type']}")
                    logger.info(f"Relevance Score: {page['relevance_score']:.2f}")
                    assert 0 <= page["relevance_score"] <= 1, f"Invalid relevance score: {page['relevance_score']}"
                
            except Exception as e:
                logger.error(f"Error analyzing {base_url}: {str(e)}", exc_info=True)
                metrics.record_error(base_url, e)
                raise  # テスト失敗として扱う

    # メトリクスの検証
    assert metrics.processed_urls > 0, "No URLs were processed"
    assert metrics.error_count == 0, "Errors occurred during processing"


@pytest.mark.asyncio
async def test_error_handling(metrics: URLAnalysisMetrics):
    """
    エラーケースのテスト
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting test_error_handling")
    
    llm_manager = LLMManager()
    
    async with SiteAnalyzer(llm_manager) as analyzer:
        for url in ERROR_TEST_SITES:
            logger.info(f"\n=== Testing error handling for {url} ===")
            
            try:
                start_time = asyncio.get_event_loop().time()
                result = await analyzer.analyze_site_structure(url)
                end_time = asyncio.get_event_loop().time()
                
                # メトリクスの記録
                processing_time = end_time - start_time
                metrics.record_url_processing(
                    url=url,
                    result=result,
                    processing_time=processing_time,
                    llm_latency=analyzer.get_llm_latency()
                )
                
                # 存在しないサイトの場合
                if "nonexistent" in url:
                    assert result is None or len(result["sitemap"]) == 0, \
                        "Should handle nonexistent domain gracefully"
                
                # 404エラーの場合
                elif "nonexistent-page" in url:
                    assert result is None or len(result["relevant_pages"]) == 0, \
                        "Should handle 404 error gracefully"
                
                # レート制限の場合
                elif "rate-limit" in url:
                    assert result is not None, \
                        "Should handle rate limiting with retries"
                
            except (NetworkError, RateLimitError, URLAnalysisError) as e:
                logger.error(f"Error testing {url}: {str(e)}", exc_info=True)
                metrics.record_error(url, e)
                # エラーケースのテストなので、例外は記録するが再送出はしない
                continue

    # エラーメトリクスの検証
    assert metrics.error_count > 0, "No errors were recorded for error test cases"


@pytest.mark.asyncio
async def test_robots_txt_handling():
    """
    robots.txtの処理テスト
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting test_robots_txt_handling")
    
    llm_manager = LLMManager()
    
    async with SiteAnalyzer(llm_manager) as analyzer:
        for base_url in TARGET_SITES:
            logger.info(f"\n=== Testing robots.txt for {base_url} ===")
            
            try:
                # robots.txtの取得と解析
                robots_txt_url = f"{base_url}/robots.txt"
                robots_data = await analyzer._fetch_robots_txt(robots_txt_url)
                
                # 結果の検証
                assert robots_data is not None, f"Failed to get robots.txt from {base_url}"
                assert isinstance(robots_data, str), "robots.txt data should be a string"
                
                # サイトマップの検証
                sitemap_urls = await analyzer._get_sitemaps_from_robots(base_url)
                if sitemap_urls:
                    for sitemap_url in sitemap_urls:
                        assert sitemap_url.startswith("http"), f"Invalid sitemap URL: {sitemap_url}"
                
                logger.info(f"Successfully processed robots.txt for {base_url}")
                
            except Exception as e:
                logger.error(f"Error processing robots.txt for {base_url}: {str(e)}", exc_info=True)
                raise  # robots.txtの処理エラーはテスト失敗として扱う


if __name__ == "__main__":
    asyncio.run(test_real_site_analysis()) 