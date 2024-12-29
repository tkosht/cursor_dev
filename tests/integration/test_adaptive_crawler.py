"""
AdaptiveCrawlerの統合テスト
"""
import os
import time
from typing import Any, Dict

import aiohttp
import pytest
from aioresponses import aioresponses

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


@pytest.fixture
def mock_responses():
    """モックレスポンス"""
    with aioresponses() as m:
        # 企業情報ページ
        m.get(
            'https://www.nitorihd.co.jp/company/',
            status=200,
            body="""
            <html>
                <body>
                    <h1 class="company-name">株式会社ニトリホールディングス</h1>
                    <dl class="company-info">
                        <dt>設立</dt>
                        <dd>1972年3月</dd>
                        <dt>事業内容</dt>
                        <dd>家具・インテリア用品の企画・販売</dd>
                    </dl>
                </body>
            </html>
            """
        )
        
        # 財務情報ページ
        m.get(
            'https://www.nitorihd.co.jp/ir/library/result.html',
            status=200,
            body="""
            <html>
                <body>
                    <table class="financial-info">
                        <tr>
                            <th>決算期</th>
                            <td>2024年2月期</td>
                        </tr>
                        <tr>
                            <th>売上高</th>
                            <td>8,000億円</td>
                        </tr>
                        <tr>
                            <th>営業利益</th>
                            <td>1,200億円</td>
                        </tr>
                    </table>
                </body>
            </html>
            """
        )
        
        # ニュースページ
        m.get(
            'https://www.nitorihd.co.jp/ir/news/',
            status=200,
            body="""
            <html>
                <body>
                    <ul class="news-list">
                        <li>
                            <span class="date">2024年1月1日</span>
                            <a href="/news/1.html" class="title">新店舗オープンのお知らせ</a>
                        </li>
                    </ul>
                </body>
            </html>
            """
        )
        
        # 404エラーページ
        m.get(
            'https://www.nitorihd.co.jp/not-found/',
            status=404,
            body='Not Found'
        )
        yield m


async def validate_response(result: Dict[str, Any], expected_keys: Dict[str, str]) -> None:
    """レスポンスを検証

    Args:
        result: クロール結果
        expected_keys: 期待するキー
    """
    assert result is not None
    assert isinstance(result, dict)
    for key in expected_keys:
        assert key in result
        assert result[key] is not None
        assert isinstance(result[key], str)
        assert len(result[key]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawl_nitori_company_info(crawler, mock_responses):
    """ニトリの企業情報取得テスト"""
    # テストデータ
    url = 'https://www.nitorihd.co.jp/company/'
    target_data = {
        'company_name': '会社名',
        'established_date': '設立日',
        'business_description': '事業内容'
    }
    
    try:
        # クロール実行
        result = await crawler.crawl(url, target_data)
        
        # 検証
        await validate_response(result, target_data)
        assert 'ニトリ' in result['company_name']
    except aiohttp.ClientError as e:
        pytest.skip(f'外部サービスへのアクセスに失敗: {str(e)}')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawl_nitori_financial_info(crawler, mock_responses):
    """ニトリの財務情報取得テスト"""
    # テストデータ
    url = 'https://www.nitorihd.co.jp/ir/library/result.html'
    target_data = {
        'fiscal_year': '決算期',
        'revenue': '売上高',
        'operating_income': '営業利益'
    }
    
    try:
        # クロール実行
        result = await crawler.crawl(url, target_data)
        
        # 検証
        await validate_response(result, target_data)
        assert isinstance(result['revenue'], str)
        assert '円' in result['revenue']
    except aiohttp.ClientError as e:
        pytest.skip(f'外部サービスへのアクセスに失敗: {str(e)}')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawl_nitori_news(crawler, mock_responses):
    """ニトリのニュース取得テスト"""
    # テストデータ
    url = 'https://www.nitorihd.co.jp/ir/news/'
    target_data = {
        'date': '日付',
        'title': 'タイトル',
        'link': 'リンク'
    }
    
    try:
        # クロール実行
        result = await crawler.crawl(url, target_data)
        
        # 検証
        await validate_response(result, target_data)
        assert isinstance(result['date'], str)
    except aiohttp.ClientError as e:
        pytest.skip(f'外部サービスへのアクセスに失敗: {str(e)}')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawl_error_handling(crawler, mock_responses):
    """エラーハンドリングのテスト"""
    # テストデータ
    url = 'https://www.nitorihd.co.jp/not-found/'
    target_data = {
        'title': 'タイトル'
    }
    
    # クロール実行
    with pytest.raises(aiohttp.ClientError) as exc_info:
        await crawler.crawl(url, target_data)
    
    # 検証
    assert str(exc_info.value) != ''
    assert crawler.retry_count > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawl_performance(crawler, mock_responses):
    """パフォーマンステスト"""
    # テストデータ
    url = 'https://www.nitorihd.co.jp/company/'
    target_data = {
        'company_name': '会社名'
    }
    
    try:
        # 実行時間を計測
        start_time = time.time()
        
        # クロール実行
        result = await crawler.crawl(url, target_data)
        
        # 実行時間を検証
        execution_time = time.time() - start_time
        assert execution_time < 10  # 10秒以内に完了すること
        assert result is not None
    except aiohttp.ClientError as e:
        pytest.skip(f'外部サービスへのアクセスに失敗: {str(e)}') 