"""
CompanyCrawlerの統合テスト
"""

from datetime import date, datetime

import pytest
import requests
from sqlalchemy import select

from app.crawlers.company import CompanyCrawler
from app.models.company import Company
from app.models.financial import Financial
from app.models.news import News


def test_company_crawler_integration(
    mock_server,
    mock_config_file,
    test_db_session,
    mock_company_response,
    mock_financial_response,
    mock_news_response,
):
    """CompanyCrawlerの統合テスト"""
    # モックレスポンスの設定
    mock_server.set_responses(
        {
            "/company/": mock_company_response,
            "/ir/library/result.html": mock_financial_response,
            "/ir/news/": mock_news_response,
        }
    )

    # クローラーの実行
    crawler = CompanyCrawler("9843", session=test_db_session)
    crawler.crawl()

    # 1. 企業情報の検証
    company_stmt = select(Company).where(Company.company_code == "9843")
    company = test_db_session.scalars(company_stmt).first()
    assert company is not None
    assert company.name == "ニトリホールディングス"
    assert company.established_date == date(1972, 3, 1)
    assert company.description == "家具・インテリア用品の企画・販売"
    assert company.website_url == mock_server.url
    assert company.stock_exchange == "東証プライム"
    assert company.industry == "小売業"

    # 2. 財務情報の検証
    financial_stmt = select(Financial).where(Financial.company_id == company.id)
    financials = test_db_session.scalars(financial_stmt).all()
    assert len(financials) == 2

    # 2023年度の財務情報
    financial_2023 = next(f for f in financials if f.fiscal_year == "2023")
    assert financial_2023.period_type == "通期"
    assert financial_2023.revenue == 800_000_000_000
    assert financial_2023.operating_income == 120_000_000_000
    assert financial_2023.period_end_date == date(2024, 3, 31)

    # 2022年度の財務情報
    financial_2022 = next(f for f in financials if f.fiscal_year == "2022")
    assert financial_2022.period_type == "通期"
    assert financial_2022.revenue == 750_000_000_000
    assert financial_2022.operating_income == 110_000_000_000
    assert financial_2022.period_end_date == date(2023, 3, 31)

    # 3. ニュース情報の検証
    news_stmt = select(News).where(News.company_id == company.id)
    news_list = test_db_session.scalars(news_stmt).all()
    assert len(news_list) == 2

    # 最新のニュース
    latest_news = next(n for n in news_list if n.published_at == datetime(2023, 12, 25))
    assert latest_news.title == "2024年2月期 第3四半期決算説明資料"
    assert latest_news.url == f"{mock_server.url}/ir/news/2023/001.html"
    assert latest_news.source == "IR情報"
    assert latest_news.category == "プレスリリース"

    # 2番目のニュース
    second_news = next(n for n in news_list if n.published_at == datetime(2023, 12, 20))
    assert second_news.title == "新規出店に関するお知らせ"
    assert second_news.url == f"{mock_server.url}/ir/news/2023/002.html"
    assert second_news.source == "IR情報"
    assert second_news.category == "プレスリリース"


def test_company_crawler_invalid_company_code(mock_config_file, test_db_session):
    """存在しない企業コードでのテスト"""
    with pytest.raises(ValueError) as exc_info:
        CompanyCrawler("9999", session=test_db_session)
    assert "企業コード 9999 の設定が見つかりません" in str(exc_info.value)


def test_company_crawler_invalid_response(
    mock_server, mock_config_file, test_db_session
):
    """不正なレスポンスでのテスト"""
    # 不正なHTMLを返すように設定
    mock_server.set_responses(
        {
            "/company/": '<html><body><div class="company-info">Invalid HTML</div></body></html>'
        }
    )

    crawler = CompanyCrawler("9843", session=test_db_session)
    with pytest.raises(ValueError) as exc_info:
        crawler.crawl()
    assert "設立日が見つかりません" in str(exc_info.value)


def test_company_crawler_not_found(mock_server, mock_config_file, test_db_session):
    """404エラーでのテスト"""
    # レスポンスを設定しない（404エラーになる）
    mock_server.clear_responses()  # 全てのレスポンスをクリア

    crawler = CompanyCrawler("9843", session=test_db_session)
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        crawler.crawl()
    assert "404" in str(exc_info.value)
