"""
実在するIRサイトを使用した統合テスト

実際のIRサイトに対してクローリングを行い、以下の機能をテストします：
1. 動的なIRページの探索
2. サイト構造の変更への適応
3. データ抽出の正確性
"""

import asyncio
import logging
from typing import Optional
from unittest.mock import patch
from urllib.parse import urljoin

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
            "6758": "https://www.sony.com/ja/SonyInfo/",  # ソニーグループ
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

        try:
            async with AdaptiveCrawler(company_code) as crawler:
                # サイト構造を解析
                structure = await crawler.analyze_site_structure(base_url)
                
                # LLMを使用してIRページのリンクを特定
                prompt = (
                    "以下のサイト構造から、IR（投資家情報）ページへのリンクを特定してください。\n"
                    "リンクのhref属性値のみを返してください。\n\n"
                    f"サイト構造: {structure}\n"
                )
                
                ir_link = await self.llm_manager.llm.generate(prompt)
                if not ir_link:
                    raise ValueError("IRページのリンクが見つかりません")

                # 相対パスを絶対パスに変換
                ir_url = urljoin(base_url, ir_link.strip())
                
                # IRページの存在確認
                response = await crawler._fetch_page(ir_url)
                if response.status != 200:
                    raise ValueError("IRページにアクセスできません")

                return ir_url

        except Exception as e:
            logger.error(f"IRページの探索に失敗: {str(e)}")
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
async def test_dynamic_ir_page_discovery(adaptive_crawler, ir_site_locator):
    """動的なIRページ探索のテスト"""
    company_codes = ["6758", "7974", "3382"]  # テスト対象の企業
    
    for code in company_codes:
        try:
            # IRページを動的に特定
            ir_url = await ir_site_locator.find_ir_page(code)
            
            # URLの形式を確認
            assert "ir" in ir_url.lower() or "investor" in ir_url.lower()
            assert ir_url.startswith("https://")
            
            # ページの取得を確認
            async with adaptive_crawler as crawler:
                response = await crawler._fetch_page(ir_url)
                assert response.status == 200
                
                # コンテンツの妥当性を確認
                content = await response.text()
                assert any(keyword in content.lower() for keyword in ["ir", "investor", "投資家"])
                
                # サイト構造の解析を確認
                structure = await crawler.analyze_site_structure(ir_url)
                assert structure is not None
                assert "navigation" in structure
                assert "main_content" in structure
            
        except Exception as e:
            logger.error(f"企業コード {code} のテスト失敗: {str(e)}")
            raise


@pytest.mark.asyncio
async def test_adaptive_data_extraction(adaptive_crawler, ir_site_locator):
    """適応的なデータ抽出のテスト"""
    target_data = {
        "revenue": "売上高",
        "operating_profit": "営業利益",
        "net_income": "親会社株主に帰属する当期純利益"
    }
    
    try:
        # IRページを動的に特定
        ir_url = await ir_site_locator.find_ir_page("6758")
        
        async with adaptive_crawler as crawler:
            # サイト構造を解析
            structure = await crawler.analyze_site_structure(ir_url)
            
            # データ抽出
            data = await crawler.extract_data(ir_url, target_data)
            
            # データの検証
            assert isinstance(data, dict)
            assert all(key in data for key in target_data.keys())
            assert all(isinstance(value, str) for value in data.values())
            assert all("円" in value for value in data.values())
            
            # 抽出したデータがサイト構造と整合していることを確認
            for key, value in data.items():
                assert value in structure["main_content"]
        
    except Exception as e:
        logger.error(f"データ抽出テスト失敗: {str(e)}")
        raise


@pytest.mark.asyncio
async def test_site_structure_adaptation(adaptive_crawler, ir_site_locator):
    """サイト構造の変更への適応テスト"""
    try:
        # IRページを動的に特定
        ir_url = await ir_site_locator.find_ir_page("6758")
        
        async with adaptive_crawler as crawler:
            # オリジナルの構造を解析
            original_structure = await crawler.analyze_site_structure(ir_url)
            
            # 構造を変更（HTMLの一部を変更）して新しい構造を作成
            modified_structure = {
                **original_structure,
                "main_content": original_structure["main_content"].replace(
                    "売上高", "連結売上高"
                ).replace(
                    "営業利益", "連結営業利益"
                )
            }
            
            # 変更後の構造でもデータを抽出できることを確認
            target_data = {
                "revenue": "連結売上高",
                "operating_profit": "連結営業利益"
            }
            
            # モック化された構造を使用してデータを抽出
            with patch.object(crawler, 'analyze_site_structure', return_value=modified_structure):
                data = await crawler.extract_data(ir_url, target_data)
            
            # データの検証
            assert isinstance(data, dict)
            assert all(key in data for key in target_data.keys())
            assert all(isinstance(value, str) for value in data.values())
            assert all("円" in value for value in data.values())
        
    except Exception as e:
        logger.error(f"構造適応テスト失敗: {str(e)}")
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


@pytest.mark.asyncio
async def test_dynamic_url_exploration(adaptive_crawler, ir_site_locator):
    """動的URL探索のテスト"""
    company_code = "6758"  # ソニーグループ
    
    async with adaptive_crawler as crawler:
        # IRページの動的探索
        ir_url = await ir_site_locator.find_ir_page(company_code)
        
        # URLの形式を確認
        assert "ir" in ir_url.lower() or "investor" in ir_url.lower()
        assert ir_url.startswith("https://")
        
        # ページの取得を確認
        response = await crawler._fetch_page(ir_url)
        assert response.status == 200
        
        # コンテンツの妥当性を確認
        content = await response.text()
        assert any(keyword in content.lower() for keyword in ["ir", "investor", "投資家"]) 