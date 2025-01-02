"""
AdaptiveCrawlerのテスト

目的：
- 企業の財務情報・ニュースを収集するクローラーのテスト
- 特にIRサイトからの決算情報、プレスリリース、適時開示情報の取得をテスト
- 実際の外部接続を使用して、本番環境に近い状態でテスト
"""

import logging
import os
from typing import Any, Dict, Optional

import pytest
import pytest_asyncio

from app.crawlers.adaptive import AdaptiveCrawler
from app.llm.manager import LLMManager

# ログ設定
logger = logging.getLogger(__name__)

# テスト用の企業コード
TEST_COMPANY_CODE = "7203"  # トヨタ自動車


@pytest_asyncio.fixture
async def llm_manager():
    """LLMManagerのフィクスチャ"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")
    
    manager = LLMManager(
        model_name="gemini-2.0-flash-exp",
        temperature=0.1,
        api_key=api_key
    )
    return manager


@pytest_asyncio.fixture
async def crawler(llm_manager):
    """AdaptiveCrawlerのフィクスチャ"""
    return AdaptiveCrawler(llm_manager=llm_manager)


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_crawl_success(crawler):
    """実際のURLを使用したクロールテスト"""
    target_fields = ["title", "date", "content"]
    
    result = await crawler.crawl_ir_info(
        company_code=TEST_COMPANY_CODE,
        target_fields=target_fields
    )
    
    # 基本的な検証
    assert isinstance(result, dict)
    assert all(field in result for field in target_fields)
    
    # データの形式と内容を検証
    # タイトルの検証
    assert len(result["title"]) >= 3
    assert len(result["title"]) <= 200
    assert any(keyword in result["title"].lower() for keyword in ["決算", "ir", "投資家", "financial"])
    
    # 日付の検証
    assert len(result["date"]) == 10  # YYYY-MM-DD
    
    # コンテンツの検証
    assert len(result["content"]) >= 50
    assert any(keyword in result["content"].lower() for keyword in ["業績", "売上", "利益", "revenue", "profit"])


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_crawl_with_retry(crawler):
    """リトライ機能のテスト"""
    target_fields = ["title", "date", "content"]
    
    # 無効な企業コードでテスト
    result = await crawler.crawl_ir_info(
        company_code="invalid_code",
        target_fields=target_fields
    )
    assert result is None


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_adaptive_extraction(crawler):
    """アダプティブな抽出機能のテスト"""
    target_fields = ["title", "date", "content"]
    
    result = await crawler.crawl_ir_info(
        company_code=TEST_COMPANY_CODE,
        target_fields=target_fields
    )
    
    assert isinstance(result, dict)
    assert all(field in result for field in target_fields)
    assert len(result["content"]) >= 50