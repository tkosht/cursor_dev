"""
実在するIRサイトを使用した統合テスト

実際のIRサイトに対してクローリングを行い、データ抽出をテストします。
"""

import asyncio
import logging
from typing import Dict, Optional

import pytest
from aiohttp import ClientError

from app.crawlers.adaptive import AdaptiveCrawler
from app.llm.manager import LLMManager

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class IRSiteLocator:
    """IRサイトの特定を行うクラス"""

    def __init__(self, llm_manager: Optional[LLMManager] = None):
        """初期化
        
        Args:
            llm_manager: LLMマネージャー（省略時は新規作成）
        """
        self.llm_manager = llm_manager or LLMManager()
        self.base_urls = {
            "6758": "https://www.sony.com/ja/",  # ソニーグループ
            "7974": "https://www.nintendo.co.jp/",  # 任天堂
            "3382": "https://www.7andi.com/",  # セブン&アイ
            "8697": "https://www.jpx.co.jp/"  # JPX
        }

    async def find_ir_page(self, company_code: str) -> str:
        """IRページのURLを特定

        Args:
            company_code: 企業コード

        Returns:
            str: IRページのURL

        Raises:
            ValueError: IRページが見つからない場合
        """
        base_url = self.base_urls.get(company_code)
        if not base_url:
            raise ValueError(f"企業コード {company_code} の基本URLが未定義です")

        # IRページの候補を探索（実際の実装ではLLMを使用して動的に特定）
        ir_paths = [
            "ir/",
            "IR/",
            "investor/",
            "investors/",
            "ja/ir/",
            "corporate/ir/",
            "SonyInfo/IR/"
        ]

        for path in ir_paths:
            url = f"{base_url.rstrip('/')}/{path}"
            try:
                async with AdaptiveCrawler(company_code) as crawler:
                    # ページの存在確認
                    await crawler._fetch_page(url)
                    return url
            except Exception as e:
                logger.debug(f"URL {url} の確認に失敗: {str(e)}")
                continue

        raise ValueError(f"企業コード {company_code} のIRページが見つかりません")


@pytest.fixture
def ir_site_locator():
    """IRSiteLocatorのフィクスチャ"""
    return IRSiteLocator()


@pytest.fixture
def adaptive_crawler():
    """AdaptiveCrawlerのフィクスチャ"""
    return AdaptiveCrawler(
        company_code="6758",  # ソニーグループ
        retry_delay=1.0,  # 1秒待機
        max_concurrent=2,  # 同時接続数制限
        timeout_total=30,
        timeout_connect=10,
        timeout_read=20,
        max_retries=3
    )


@pytest.mark.asyncio
async def test_sony_ir_site(adaptive_crawler, ir_site_locator):
    """ソニーグループのIRサイトテスト"""
    target_data = {
        "revenue": "売上高",
        "operating_profit": "営業利益",
        "net_income": "親会社株主に帰属する当期純利益"
    }
    
    try:
        # IRページを動的に特定
        ir_url = await ir_site_locator.find_ir_page("6758")
        
        async with adaptive_crawler:
            data = await adaptive_crawler.crawl(ir_url, target_data)
            
            # データの検証
            assert isinstance(data, dict)
            assert all(key in data for key in target_data.keys())
            assert all(isinstance(value, str) for value in data.values())
            assert all("円" in value for value in data.values())
        
    except Exception as e:
        logger.error(f"ソニーグループサイトのクロール失敗: {str(e)}")
        raise


@pytest.mark.asyncio
async def test_nintendo_ir_site(adaptive_crawler, ir_site_locator):
    """任天堂のIRサイトテスト"""
    target_data = {
        "revenue": "売上高",
        "operating_profit": "営業利益",
        "net_income": "親会社株主に帰属する当期純利益"
    }
    
    try:
        # IRページを動的に特定
        ir_url = await ir_site_locator.find_ir_page("7974")
        
        async with adaptive_crawler:
            data = await adaptive_crawler.crawl(ir_url, target_data)
            
            # データの検証
            assert isinstance(data, dict)
            assert all(key in data for key in target_data.keys())
            assert all(isinstance(value, str) for value in data.values())
            assert all("円" in value for value in data.values())
        
    except Exception as e:
        logger.error(f"任天堂サイトのクロール失敗: {str(e)}")
        raise


@pytest.mark.asyncio
async def test_seven_and_i_ir_site(adaptive_crawler, ir_site_locator):
    """セブン&アイ・ホールディングスのIRサイトテスト"""
    target_data = {
        "revenue": "営業収益",
        "operating_profit": "営業利益",
        "net_income": "親会社株主に帰属する当期純利益"
    }
    
    try:
        # IRページを動的に特定
        ir_url = await ir_site_locator.find_ir_page("3382")
        
        async with adaptive_crawler:
            data = await adaptive_crawler.crawl(ir_url, target_data)
            
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
    
    async with adaptive_crawler:
        with pytest.raises(ClientError):
            await adaptive_crawler.crawl(url, target_data)


@pytest.mark.asyncio
async def test_rate_limit_handling(adaptive_crawler, ir_site_locator):
    """レート制限のテスト"""
    target_data = {
        "revenue": "売上高",
        "operating_profit": "営業利益"
    }
    
    try:
        # IRページを動的に特定
        ir_url = await ir_site_locator.find_ir_page("7974")
        
        async with adaptive_crawler:
            # 3回連続でリクエスト
            for _ in range(3):
                await adaptive_crawler.crawl(ir_url, target_data)
                await asyncio.sleep(1)  # 1秒待機
            
    except ClientError as e:
        if e.status == 429:  # Too Many Requests
            logger.info("レート制限が正しく検出されました")
        else:
            raise 