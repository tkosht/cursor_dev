"""
企業クローラーのテスト

このモジュールは、企業クローラーの機能をテストします。
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

from app.crawler.company import CompanyCrawler
from app.models.company import Company
from app.models.financial import Financial, PeriodType
from app.models.news import News


@pytest.fixture
def mock_response():
    """
    モックレスポンスを作成します。
    """
    response = MagicMock(spec=requests.Response)
    response.text = "<html><body>Test content</body></html>"
    response.status_code = 200
    return response


def test_crawl_company(session, mock_response):
    """
    企業情報のクロールをテストします。
    """
    with patch('app.crawler.base.requests.request', return_value=mock_response):
        crawler = CompanyCrawler("9843", session=session)
        crawler.crawl()

        # 企業情報が保存されていることを確認
        company = session.query(Company).filter_by(company_code="9843").first()
        assert company is not None
        assert company.name == "ニトリホールディングス"
        assert company.name_en == "Nitori Holdings Co., Ltd."
        assert company.established_date == datetime(1972, 3, 3).date()

        # 財務情報が保存されていることを確認
        financial = session.query(Financial).filter_by(company_id=company.id).first()
        assert financial is not None
        assert financial.fiscal_year == "2023年度"
        assert financial.period_type == PeriodType.FULL_YEAR
        assert financial.revenue == 1000000000

        # ニュースが保存されていることを確認
        news = session.query(News).filter_by(company_id=company.id).first()
        assert news is not None
        assert news.title == "2024年2月期 第3四半期決算短信〔IFRS〕（連結）"
        assert news.source == "適時開示"


def test_parse_company(session, mock_response):
    """
    企業情報のパースをテストします。
    """
    crawler = CompanyCrawler("9843", session=session)
    data = crawler.parse_company(mock_response)

    assert data["company_code"] == "9843"
    assert data["name"] == "ニトリホールディングス"
    assert data["name_en"] == "Nitori Holdings Co., Ltd."
    assert data["established_date"] == datetime(1972, 3, 3).date()
    assert data["stock_exchange"] == "東証プライム"
    assert data["industry"] == "小売業"


def test_parse_financial(session, mock_response):
    """
    財務情報のパースをテストします。
    """
    crawler = CompanyCrawler("9843", session=session)
    data_list = crawler.parse_financial(mock_response)

    assert len(data_list) == 1
    data = data_list[0]
    assert data["fiscal_year"] == "2023年度"
    assert data["period_type"] == PeriodType.FULL_YEAR
    assert data["period_end_date"] == datetime(2024, 2, 20).date()
    assert data["revenue"] == 1000000000
    assert data["operating_income"] == 100000000


def test_parse_news(session, mock_response):
    """
    ニュースのパースをテストします。
    """
    crawler = CompanyCrawler("9843", session=session)
    data_list = crawler.parse_news(mock_response)

    assert len(data_list) == 1
    data = data_list[0]
    assert data["title"] == "2024年2月期 第3四半期決算短信〔IFRS〕（連結）"
    assert data["source"] == "適時開示"
    assert data["category"] == "決算情報"
    assert data["published_at"] == datetime(2024, 1, 4, 15, 0)


def test_request_error(session):
    """
    リクエストエラーのハンドリングをテスト��ます。
    """
    with patch('app.crawler.base.requests.request', side_effect=requests.RequestException):
        crawler = CompanyCrawler("9843", session=session)
        with pytest.raises(requests.RequestException):
            crawler.crawl()

        # データが保存されていないことを確認
        company = session.query(Company).filter_by(company_code="9843").first()
        assert company is None 