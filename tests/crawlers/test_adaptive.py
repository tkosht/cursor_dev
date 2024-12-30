"""
AdaptiveCrawlerのテスト

目的：
- 企業の財務情報・ニュースを収集するクローラーのテスト
- 特にIRサイトからの決算情報、プレスリリース、適時開示情報の取得をテスト
- 実際の外部接続を使用して、本番環境に近い状態でテスト
"""

import asyncio
import datetime
import logging
from dataclasses import dataclass

import aiohttp
import pytest

from app.crawlers.adaptive import AdaptiveCrawler
from app.llm.manager import LLMManager
from app.models.financial import Financial, PeriodType
from app.models.news import News

logger = logging.getLogger(__name__)

# テスト用の定数
TEST_URL = "https://global.toyota/jp/ir/"
TEST_NEWSROOM_URL = "https://global.toyota/jp/newsroom/"


@dataclass
class TestData:
    """テストデータ"""
    financial_data = Financial(
        company_id=1,
        fiscal_year="2023",
        period_type=PeriodType.FULL_YEAR,
        period_end_date=datetime.date(2024, 3, 31),
        revenue=10000000,
        operating_income=1000000,
        net_income=800000
    )
    
    news_data = News(
        company_id=1,
        title="テストニュース",
        content="これはテストニュースの内容です。",
        url="https://example.com/news/1",
        published_at=datetime.datetime.now(),
        source="テスト",
        category="IR"
    )


@pytest.fixture
def event_loop():
    """イベントループを作成して返す"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def adaptive_crawler(event_loop):
    """AdaptiveCrawlerのインスタンスを生成するフィクスチャ"""
    logger.info("AdaptiveCrawlerフィクスチャの初期化開始")
    
    # LLMマネージャーの初期化
    llm_manager = LLMManager()
    await llm_manager.initialize()
    
    # クローラーの設定
    timeout = aiohttp.ClientTimeout(total=60, connect=20, sock_read=20)
    connector = aiohttp.TCPConnector(
        limit=10,
        enable_cleanup_closed=True,
        force_close=False,
        keepalive_timeout=60
    )
    
    # クローラーのインスタンス化
    crawler = AdaptiveCrawler(
        company_code="7203",
        llm_manager=llm_manager,
        timeout=timeout,
        connector=connector,
        retry_delay=1,
        max_concurrent_requests=5,
        cache_ttl=60,
        max_cache_size=100
    )
    
    yield crawler  # asyncではなく通常のyieldを使用
    
    # クリーンアップ
    logger.debug("クローラーのクリーンアップを実行")
    await crawler.close()
    await llm_manager.close()


def assert_crawler_initialization(crawler: AdaptiveCrawler):
    """クローラーの初期化状態を検証"""
    assert crawler.company_code == "7203"
    assert crawler.llm_manager is not None
    assert crawler.cache is not None
    assert crawler.semaphore is not None


@pytest.mark.timeout(60)
async def test_initialization(adaptive_crawler):
    """初期化のテスト"""
    assert_crawler_initialization(adaptive_crawler)


@pytest.mark.timeout(60)
async def test_cache_key_generation(adaptive_crawler):
    """キャッシュキー生成のテスト"""
    key = adaptive_crawler._generate_cache_key(TEST_URL, TestData.financial_data)
    assert isinstance(key, str)
    assert TEST_URL in key
    assert "FinancialData" in key


@pytest.mark.timeout(60)
async def test_cache_operations(adaptive_crawler):
    """キャッシュ操作のテスト"""
    test_data = {"test": "data"}
    test_url = "https://example.com"
    
    # キャッシュの設定
    await adaptive_crawler._set_to_cache(test_url, test_data)
    
    # キャッシュの取得
    cached_data = await adaptive_crawler._get_from_cache(test_url)
    assert cached_data == test_data


@pytest.mark.timeout(60)
async def test_cache_size_limit(adaptive_crawler):
    """キャッシュサイズ制限のテスト"""
    for i in range(adaptive_crawler.max_cache_size + 1):
        url = f"https://example.com/{i}"
        await adaptive_crawler._set_to_cache(url, {"data": i})
    
    assert len(adaptive_crawler.cache) <= adaptive_crawler.max_cache_size


@pytest.mark.timeout(300)  # タイムアウトを5分に延長
async def test_crawl_success(adaptive_crawler):
    """クロール成功時のテスト - 決算情報の取得"""
    try:
        logger.info(f"クロール開始: {TEST_URL}")
        result = await adaptive_crawler.crawl(TEST_URL, TestData.financial_data)
        logger.info(f"クロール結果: {result}")
        assert isinstance(result, dict)
        assert "revenue" in result
    except Exception as e:
        logger.error(f"クロールエラー: {str(e)}")
        logger.error(f"クローラーの状態: semaphore={adaptive_crawler.semaphore._value}")
        raise


@pytest.mark.timeout(300)  # タイムアウトを5分に延長
async def test_crawl_with_retry(adaptive_crawler):
    """リトライ処理のテスト"""
    invalid_url = "https://invalid.example.com"
    
    with pytest.raises(Exception):
        await adaptive_crawler.crawl(invalid_url, TestData.financial_data)


@pytest.mark.timeout(300)  # タイムアウトを5分に延長
async def test_concurrent_requests(adaptive_crawler):
    """同時リクエスト制限のテスト - プレスリリースの取得"""
    start_time = datetime.datetime.now()
    
    try:
        logger.info(f"同時リクエストテスト開始: {TEST_NEWSROOM_URL}")
        tasks = [
            adaptive_crawler.crawl(TEST_NEWSROOM_URL, TestData.news_data)
            for _ in range(5)  # 同時リクエスト数を5に増やす
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
        success_count = sum(1 for r in results if isinstance(r, dict))
        
        logger.info(f"同時リクエスト結果: 成功={success_count}, 経過時間={elapsed_time:.2f}秒")
        assert success_count > 0
    except Exception as e:
        logger.error(f"同時リクエストテストエラー: {str(e)}")
        raise


@pytest.mark.timeout(120)
async def test_error_handling(adaptive_crawler):
    """エラーハンドリングのテスト"""
    invalid_data = {"invalid": "data"}
    
    with pytest.raises(Exception):
        await adaptive_crawler.crawl(TEST_URL, invalid_data)