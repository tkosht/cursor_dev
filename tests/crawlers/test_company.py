"""CompanyCrawlerのテストモジュール"""
from unittest.mock import Mock, patch

import pytest

from app.crawlers.company import CompanyCrawler


@pytest.fixture
def crawler():
    """クローラーのフィクスチャ"""
    return CompanyCrawler(company_code="9843")


def test_init(crawler):
    """初期化のテスト"""
    assert crawler.company_code == "9843"
    assert crawler.base_url == "https://www.nitorihd.co.jp"


@patch('app.crawlers.base.BaseCrawler._make_request')
def test_crawl_success(mock_request, crawler):
    """クロール成功時のテスト"""
    # モックレスポンスの準備
    mock_company_response = Mock()
    mock_company_response.text = """
    <div class="company-info">
        <h1 class="company-name">ニトリホールディングス</h1>
        <table>
            <tr>
                <th>設立</th>
                <td>1972年3月1日</td>
            </tr>
            <tr>
                <th>事業内容</th>
                <td>家具・インテリア用品の販売</td>
            </tr>
        </table>
    </div>
    """
    
    mock_financial_response = Mock()
    mock_financial_response.text = """
    <table class="financial-table">
        <tr>
            <th>決算期</th>
            <th>売上高</th>
            <th>営業利益</th>
        </tr>
        <tr>
            <td>2023</td>
            <td>100,000百万円</td>
            <td>10,000百万円</td>
        </tr>
    </table>
    """
    
    mock_news_response = Mock()
    mock_news_response.text = """
    <ul class="news-list">
        <li>
            <span class="date">2023.12.25</span>
            <span class="title">決算発表</span>
            <a href="/ir/news/2023/1225.html">詳細</a>
        </li>
    </ul>
    """
    
    mock_request.side_effect = [
        mock_company_response,
        mock_financial_response,
        mock_news_response
    ]
    
    # セッションのモック
    session = Mock()
    company = Mock()
    company.id = 1
    session.add.return_value = None
    crawler.session = session
    
    # クロール実行
    crawler.crawl()
    
    # 各APIが正しく呼び出されたことを確認
    assert mock_request.call_count == 3
    session.add.assert_called()
    session.commit.assert_called()


def test_parse_company(crawler):
    """企業情報パースのテスト"""
    html = """
    <div class="company-info">
        <h1 class="company-name">ニトリホールディングス</h1>
        <table>
            <tr>
                <th>設立</th>
                <td>1972年3月1日</td>
            </tr>
            <tr>
                <th>事業内容</th>
                <td>家具・インテリア用品の販売</td>
            </tr>
        </table>
    </div>
    """
    response = Mock()
    response.text = html
    
    result = crawler.parse_company(response)
    
    assert result['company_code'] == "9843"
    assert result['name'] == "ニトリホールディングス"
    assert result['established_date'].strftime('%Y-%m-%d') == "1972-03-01"
    assert "家具・インテリア用品の販売" in result['description']


def test_parse_financial(crawler):
    """財務情報パースのテスト"""
    html = """
    <table class="financial-table">
        <tr>
            <th>決算期</th>
            <th>売上高</th>
            <th>営業利益</th>
        </tr>
        <tr>
            <td>2023</td>
            <td>100,000百万円</td>
            <td>10,000百万円</td>
        </tr>
    </table>
    """
    response = Mock()
    response.text = html
    
    results = crawler.parse_financial(response)
    
    assert len(results) == 1
    assert results[0]['fiscal_year'] == "2023"
    assert results[0]['revenue'] == 100_000_000_000
    assert results[0]['operating_income'] == 10_000_000_000


def test_parse_news(crawler):
    """ニュース情報パースのテスト"""
    html = """
    <ul class="news-list">
        <li>
            <span class="date">2023.12.25</span>
            <span class="title">決算発表</span>
            <a href="/ir/news/2023/1225.html">詳細</a>
        </li>
    </ul>
    """
    response = Mock()
    response.text = html
    
    results = crawler.parse_news(response)
    
    assert len(results) == 1
    assert results[0]['title'] == "決算発表"
    assert results[0]['published_at'].strftime('%Y-%m-%d') == "2023-12-25"
    assert results[0]['url'] == "https://www.nitorihd.co.jp/ir/news/2023/1225.html" 