"""
AdaptiveCrawlerの統合テスト
"""
import os
import time

import pytest

from app.crawlers.adaptive import AdaptiveCrawler
from app.llm.manager import LLMManager


@pytest.fixture
def llm_manager():
    """LLMマネージャーのインスタンス"""
    api_key = os.getenv('GEMINI_API_KEY', 'dummy-key')
    manager = LLMManager()
    manager.load_model('gemini-2.0-flash-exp', api_key)
    return manager


@pytest.fixture
def crawler(llm_manager):
    """クローラーのインスタンス"""
    return AdaptiveCrawler(
        company_code='9843',
        llm_manager=llm_manager,
        max_retries=3,
        retry_delay=0.1
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawl_nitori_company_info(crawler):
    """ニトリの企業情報取得テスト"""
    # テストデータ
    url = 'https://www.nitorihd.co.jp/company/'
    target_data = {
        'company_name': '会社名',
        'established_date': '設立日',
        'business_description': '事業内容'
    }
    
    # クロール実行
    result = await crawler.crawl(url, target_data)
    
    # 検証
    assert result is not None
    assert isinstance(result, dict)
    assert 'company_name' in result
    assert 'established_date' in result
    assert 'business_description' in result
    assert 'ニトリ' in result['company_name']


@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawl_nitori_financial_info(crawler):
    """ニトリの財務情報取得テスト"""
    # テストデータ
    url = 'https://www.nitorihd.co.jp/ir/library/result.html'
    target_data = {
        'fiscal_year': '決算期',
        'revenue': '売上高',
        'operating_income': '営業利益'
    }
    
    # クロール実行
    result = await crawler.crawl(url, target_data)
    
    # 検証
    assert result is not None
    assert isinstance(result, dict)
    assert 'fiscal_year' in result
    assert 'revenue' in result
    assert 'operating_income' in result
    assert isinstance(result['revenue'], str)
    assert '円' in result['revenue']


@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawl_nitori_news(crawler):
    """ニトリのニュース取得テスト"""
    # テストデータ
    url = 'https://www.nitorihd.co.jp/ir/news/'
    target_data = {
        'date': '日付',
        'title': 'タイトル',
        'link': 'リンク'
    }
    
    # クロール実行
    result = await crawler.crawl(url, target_data)
    
    # 検証
    assert result is not None
    assert isinstance(result, dict)
    assert 'date' in result
    assert 'title' in result
    assert 'link' in result
    assert isinstance(result['date'], str)
    assert len(result['title']) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawl_error_handling(crawler):
    """エラーハンドリングのテスト"""
    # テストデータ
    url = 'https://www.nitorihd.co.jp/not-found/'
    target_data = {
        'title': 'タイトル'
    }
    
    # クロール実行
    with pytest.raises(Exception) as exc_info:
        await crawler.crawl(url, target_data)
    
    # 検証
    assert str(exc_info.value) != ''
    assert crawler.retry_count > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawl_performance(crawler):
    """パフォーマンステスト"""
    # テストデータ
    url = 'https://www.nitorihd.co.jp/company/'
    target_data = {
        'company_name': '会社名'
    }
    
    # 実行時間を計測
    start_time = time.time()
    
    # クロール実行
    result = await crawler.crawl(url, target_data)
    
    # 実行時間を検証
    execution_time = time.time() - start_time
    assert execution_time < 10  # 10秒以内に完了すること
    assert result is not None 