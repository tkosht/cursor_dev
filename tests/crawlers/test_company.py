"""CompanyCrawlerのテストモジュール"""
from unittest.mock import Mock, patch

import pytest

from app.config.crawler import CompanyConfig
from app.crawlers.company import CompanyCrawler


@pytest.fixture
def company_config():
    """企業設定のフィクスチャ"""
    return CompanyConfig(company_code="9843", base_url="https://www.nitorihd.co.jp")


@pytest.fixture
def crawler(company_config):
    """クローラーのフィクスチャ"""
    with patch("app.crawlers.company.get_company_config") as mock_get_config:
        mock_get_config.return_value = company_config
        crawler = CompanyCrawler(company_code="9843")
        yield crawler


def test_init(crawler, company_config):
    """初期化のテスト"""
    assert crawler.company_code == "9843"
    assert crawler.config == company_config


def test_init_invalid_company_code():
    """無効な企業コードでの初期化テスト"""
    with patch("app.crawlers.company.get_company_config") as mock_get_config:
        mock_get_config.return_value = None
        with pytest.raises(ValueError) as exc_info:
            CompanyCrawler(company_code="0000")
        assert "企業コード 0000 の設定が見つかりません" in str(exc_info.value)


@patch("app.crawlers.base.BaseCrawler._make_request")
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
        mock_news_response,
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
    mock_request.assert_any_call(
        f"{crawler.config.base_url}{crawler.config.company_info_path}"
    )
    mock_request.assert_any_call(
        f"{crawler.config.base_url}{crawler.config.financial_info_path}"
    )
    mock_request.assert_any_call(
        f"{crawler.config.base_url}{crawler.config.news_info_path}"
    )
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

    assert result["company_code"] == "9843"
    assert result["name"] == "ニトリホールディングス"
    assert result["established_date"].strftime("%Y-%m-%d") == "1972-03-01"
    assert "家具・インテリア用品の販売" in result["description"]


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
    assert results[0]["fiscal_year"] == "2023"
    assert results[0]["revenue"] == 100_000_000_000
    assert results[0]["operating_income"] == 10_000_000_000


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
    assert results[0]["title"] == "決算発表"
    assert results[0]["published_at"].strftime("%Y-%m-%d") == "2023-12-25"
    assert results[0]["url"] == "https://www.nitorihd.co.jp/ir/news/2023/1225.html"
