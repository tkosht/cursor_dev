"""
企業情報クローラーのE2Eテスト

実際のWebサイトからのデータ取得をテストします。
"""

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.crawlers.company import CompanyCrawler
from app.models.base import Base
from app.models.company import Company
from app.models.financial import Financial
from app.models.news import News


@pytest.fixture(scope="module")
def db_session():
    """テスト用DBセッション"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_nitori_data_extraction(db_session: Session):
    """ニトリHDの企業情報取得テスト"""
    # クローラーの実行
    crawler = CompanyCrawler("9843", session=db_session)
    crawler.crawl()

    # 1. 企業情報の検証
    company_stmt = select(Company).where(Company.company_code == "9843")
    company = db_session.scalars(company_stmt).first()
    assert company is not None
    assert company.name == "ニトリホールディングス"
    assert company.stock_exchange == "東証プライム"
    assert company.industry == "小売業"

    # 2. 財務情報の検証
    financial_stmt = select(Financial).where(Financial.company_id == company.id)
    financials = db_session.scalars(financial_stmt).all()
    assert len(financials) > 0

    # 最新の財務情報を検証
    latest_financial = max(financials, key=lambda x: x.fiscal_year)
    assert latest_financial.period_type == "通期"
    assert latest_financial.revenue > 0
    assert latest_financial.operating_income > 0

    # 3. ニュース情報の検証
    news_stmt = select(News).where(News.company_id == company.id)
    news_list = db_session.scalars(news_stmt).all()
    assert len(news_list) > 0

    # 最新のニュースを検証
    latest_news = max(news_list, key=lambda x: x.published_at)
    assert latest_news.title
    assert latest_news.url.startswith("https://www.nitorihd.co.jp/")
    assert latest_news.source == "IR情報"


@pytest.mark.parametrize(
    "company_code,expected_name,expected_exchange",
    [
        ("9843", "ニトリホールディングス", "東証プライム"),
        ("7203", "トヨタ自動車", "東証プライム"),
        # 他の企業を追加予定
    ],
)
def test_multiple_companies(
    db_session: Session, company_code: str, expected_name: str, expected_exchange: str
):
    """複数の企業サイトでの動作確認"""
    # クローラーの実行
    crawler = CompanyCrawler(company_code, session=db_session)
    crawler.crawl()

    # 企業情報の検証
    company_stmt = select(Company).where(Company.company_code == company_code)
    company = db_session.scalars(company_stmt).first()
    assert company is not None
    assert company.name == expected_name
    assert company.stock_exchange == expected_exchange

    # 財務情報の存在確認
    financial_stmt = select(Financial).where(Financial.company_id == company.id)
    financials = db_session.scalars(financial_stmt).all()
    assert len(financials) > 0

    # ニュースの存在確認
    news_stmt = select(News).where(News.company_id == company.id)
    news_list = db_session.scalars(news_stmt).all()
    assert len(news_list) > 0
