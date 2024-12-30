"""
実在するIRサイトを使用した統合テスト

実際のIRサイトに対してクローリングを行い、データ抽出をテストします。
"""

import asyncio
import logging
from typing import Dict, Any

import pytest
from aiohttp import ClientError

from app.crawlers.adaptive import AdaptiveCrawler
from app.llm.manager import LLMManager

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@pytest.fixture
async def adaptive_crawler():
    """AdaptiveCrawlerのフィクスチャ"""
    crawler = AdaptiveCrawler(
        company_code="7203",  # トヨタ自動車
        retry_delay=1.0,  # 1秒待機
        max_concurrent=2,  # 同時接続数制限
        timeout_total=30,
        timeout_connect=10,
        timeout_read=20,
        max_retries=3
    )
    try:
        await crawler.__aenter__()
        yield crawler
    finally:
        await crawler.__aexit__(None, None, None)


@pytest.mark.asyncio
async def test_jpx_ir_site(adaptive_crawler):
    """JPX（日本取引所グループ）のIRサイトテスト"""
    target_data = {
        "revenue": "営業収益",
        "operating_profit": "営業利益",
        "net_income": "親会社株主に帰属する当期純利益"
    }
    
    base_url = "https://www.jpx.co.jp/corporate/investor-relations"
    url = f"{base_url}/financial-statements/index.html"
    
    try:
        data = await adaptive_crawler.crawl(url, target_data)
        
        # データの検証
        assert isinstance(data, dict)
        assert all(key in data for key in target_data.keys())
        assert all(isinstance(value, str) for value in data.values())
        assert all("円" in value for value in data.values())
        
    except Exception as e:
        logger.error(f"JPXサイトのクロール失敗: {str(e)}")
        raise


@pytest.mark.asyncio
async def test_nintendo_ir_site(adaptive_crawler):
    """任天堂のIRサイトテスト"""
    target_data = {
        "revenue": "売上高",
        "operating_profit": "営業利益",
        "net_income": "親会社株主に帰属する当期純利益"
    }
    
    url = "https://www.nintendo.co.jp/ir/finance/index.html"
    
    try:
        data = await adaptive_crawler.crawl(url, target_data)
        
        # データの検証
        assert isinstance(data, dict)
        assert all(key in data for key in target_data.keys())
        assert all(isinstance(value, str) for value in data.values())
        assert all("円" in value for value in data.values())
        
    except Exception as e:
        logger.error(f"任天堂サイトのクロール失敗: {str(e)}")
        raise


@pytest.mark.asyncio
async def test_seven_and_i_ir_site(adaptive_crawler):
    """セブン&アイ・ホールディングスのIRサイトテスト"""
    target_data = {
        "revenue": "営業収益",
        "operating_profit": "営業利益",
        "net_income": "親会社株主に帰属する当期純利益"
    }
    
    url = "https://www.7andi.com/ir/library/bs.html"
    
    try:
        data = await adaptive_crawler.crawl(url, target_data)
        
        # データの検証
        assert isinstance(data, dict)
        assert all(key in data for key in target_data.keys())
        assert all(isinstance(value, str) for value in data.values())
        assert all("円" in value for value in data.values())
        
    except Exception as e:
        logger.error(f"セブン&アイサイトのクロール失敗: {str(e)}")
        raise


@pytest.mark.asyncio
async def test_error_handling(adaptive_crawler):
    """エラーハンドリングのテスト"""
    target_data = {"test": "test"}
    
    # 存在しないURLでテスト
    url = "https://www.example.com/nonexistent"
    
    with pytest.raises(ClientError):
        await adaptive_crawler.crawl(url, target_data)


@pytest.mark.asyncio
async def test_rate_limit_handling(adaptive_crawler):
    """レート制限のテスト"""
    target_data = {
        "revenue": "売上高",
        "operating_profit": "営業利益"
    }
    
    # 同じURLに対して複数回リクエスト
    url = "https://www.nintendo.co.jp/ir/finance/index.html"
    
    try:
        # 3回連続でリクエスト
        for _ in range(3):
            await adaptive_crawler.crawl(url, target_data)
            await asyncio.sleep(1)  # 1秒待機
            
    except ClientError as e:
        if e.status == 429:  # Too Many Requests
            logger.info("レート制限が正しく検出されました")
        else:
            raise
""" 