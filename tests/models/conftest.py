"""
モデルテストの共通設定

このモジュールは、モデルテストで使用する共通の設定やフィクスチャを提供します。
"""

from datetime import date, datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import Base, set_session
from app.models.company import Company
from app.models.financial import Financial, PeriodType
from app.models.news import News


@pytest.fixture(scope="function")
def engine():
    """
    テスト用のSQLiteインメモリデータベースエンジンを作成します。
    """
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="function")
def session(engine):
    """
    テスト用のデータベースセッションを作成します。
    """
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    set_session(session)
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_company(session):
    """
    テスト���のサンプル企業データを作成します。
    """
    company = Company(
        company_code="9843",
        name="ニトリホールディングス",
        name_en="Nitori Holdings Co., Ltd.",
        established_date=date(1972, 3, 3),
        description="家具・インテリア用品の企画・販売",
        headquarters_address="札幌市北区新琴似七条一丁目2番39号",
        representative_name="似鳥 昭雄",
        representative_position="代表取締役会長",
        website_url="https://www.nitorihd.co.jp/",
        stock_exchange="東証プライム",
        industry="小売業",
        employees_count="約45,000名（連結）"
    )
    session.add(company)
    session.commit()
    return company


@pytest.fixture
def sample_financial(session, sample_company):
    """
    テスト用のサンプル財務データを作成します。
    """
    financial = Financial(
        company_id=sample_company.id,
        fiscal_year="2023年度",
        period_type=PeriodType.FULL_YEAR,
        period_end_date=date(2024, 2, 20),
        revenue=1000000000,
        operating_income=100000000,
        ordinary_income=110000000,
        net_income=80000000,
        total_assets=2000000000,
        net_assets=1500000000,
        earnings_per_share=100.50,
        book_value_per_share=1500.75,
        dividend_per_share=50.00
    )
    session.add(financial)
    session.commit()
    return financial


@pytest.fixture
def sample_news(session, sample_company):
    """
    テスト用のサンプルニュースデータを作成します。
    """
    news = News(
        company_id=sample_company.id,
        title="2024年2月期 第3四半期決算短信〔IFRS〕（連結）",
        content="当第3四半期連結累計期間の営業収益は6,481億71百万円...",
        url="https://www.nitorihd.co.jp/ir/news/2024/20240104.pdf",
        published_at=datetime(2024, 1, 4, 15, 0, tzinfo=timezone.utc),
        source="適時開示",
        category="決算情報"
    )
    session.add(news)
    session.commit()
    return news 