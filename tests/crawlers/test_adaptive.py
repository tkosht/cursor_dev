"""
AdaptiveCrawlerのテスト

目的：
- 企業の財務情報・ニュースを収集するクローラーのテスト
- 特にIRサイトからの決算情報、プレスリリース、適時開示情報の取得をテスト
- 実際の外部接続を使用して、本番環境に近い状態でテスト
"""

import asyncio
import os

import pytest
import pytest_asyncio

from app.crawlers.adaptive import AdaptiveCrawler
from app.llm.manager import LLMManager


@pytest_asyncio.fixture
async def llm_manager():
    api_key = os.getenv("GOOGLE_API_KEY_GEMINI")
    if not api_key:
        pytest.skip("GOOGLE_API_KEY_GEMINI not set")
    
    manager = LLMManager()
    await manager.load_model("gemini-2.0-flash-exp", api_key)
    return manager


@pytest_asyncio.fixture
async def crawler(llm_manager):
    crawler = AdaptiveCrawler(
        company_code="7203",  # トヨタ自動車のコード
        llm_manager=llm_manager,
        max_concurrent=2
    )
    async with crawler as c:
        yield c
    await crawler.close()


@pytest.mark.asyncio
async def test_crawl_success(crawler):
    """実際のIRサイトからのデータ取得テスト"""
    # IRサイトのURLを動的に取得
    ir_urls = await crawler.get_ir_urls()
    assert ir_urls, "IR URLsの取得に失敗しました"
    assert "financial_results" in ir_urls, "決算情報のURLが見つかりません"
    
    url = ir_urls["financial_results"]
    target_data = {
        "revenue": "売上収益",
        "operating_income": "営業利益"
    }
    
    result = await crawler.crawl(url, target_data)
    assert result is not None
    assert isinstance(result, dict)
    assert "revenue" in result
    assert "operating_income" in result


@pytest.mark.asyncio
async def test_crawl_invalid_url(crawler):
    """無効なURLの場合のエラーハンドリングテスト"""
    url = "https://invalid-url.example.com"
    target_data = {"revenue": "売上高"}
    
    with pytest.raises(Exception):
        await crawler.crawl(url, target_data)


@pytest.mark.asyncio
async def test_concurrent_requests(crawler):
    """同時リクエスト制限のテスト"""
    # IRサイトのURLを動的に取得
    ir_urls = await crawler.get_ir_urls()
    assert ir_urls, "IR URLsの取得に失敗しました"
    assert "financial_results" in ir_urls, "決算情報のURLが見つかりません"
    
    url = ir_urls["financial_results"]
    target_data = {
        "title": "四半期報告書",
        "date": "提出日"
    }
    
    tasks = [
        crawler.crawl(url, target_data)
        for _ in range(3)
    ]
    
    results = await asyncio.gather(*tasks)
    assert all(isinstance(r, dict) for r in results)
    assert all("title" in r for r in results)
    assert all("date" in r for r in results)