"""
Companyモデルの単体テスト
"""

import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.company import Company
from app.models.financial import Financial, PeriodType
from app.models.news import News


def test_create_company(db_session):
    """基本的な企業情報の作成テスト"""
    company = Company(
        company_code="1234",
        name="テスト株式会社",
        name_en="Test Corporation",
        description="テスト用の企業です",
        established_date=datetime.date(2000, 1, 1),
        website_url="https://example.com",
        stock_exchange="東証プライム",
        industry="情報・通信",
        headquarters_address="東京都千代田区",
        representative_name="テスト太郎",
        representative_position="代表取締役社長",
        employees_count="1000人"
    )

    db_session.add(company)
    db_session.commit()

    assert company.id is not None
    assert company.company_code == "1234"
    assert company.name == "テスト株式会社"
    assert company.created_at is not None
    assert company.updated_at is not None


def test_company_unique_code(db_session):
    """企業コードのユニーク制約テスト"""
    company1 = Company(
        company_code="1234",
        name="テスト株式会社1"
    )
    db_session.add(company1)
    db_session.commit()

    company2 = Company(
        company_code="1234",
        name="テスト株式会社2"
    )
    db_session.add(company2)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_company_required_fields(db_session):
    """必須フィールドの検証テスト"""
    company = Company(
        company_code="1234"
        # nameは必須だが指定しない
    )
    db_session.add(company)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_company_relationships(db_session):
    """リレーションシップのテスト"""
    company = Company(
        company_code="1234",
        name="テスト株式会社"
    )
    db_session.add(company)
    db_session.commit()

    # 初期状態では空のリスト
    assert len(company.financials) == 0
    assert len(company.news) == 0


def test_company_str_representation():
    """文字列表現のテスト"""
    company = Company(name="テスト株式会社")
    assert str(company) == "<Company(name=テスト株式会社)>"


def test_company_update(db_session):
    """企業情報の更新テスト"""
    company = Company(
        company_code="1234",
        name="テスト株式会社"
    )
    db_session.add(company)
    db_session.commit()

    # 情報を更新
    company.name = "更新後株式会社"
    company.industry = "製造業"
    db_session.commit()

    # 更新後の検証
    updated_company = db_session.query(Company).filter_by(company_code="1234").first()
    assert updated_company.name == "更新後株式会社"
    assert updated_company.industry == "製造業"
    assert updated_company.updated_at > updated_company.created_at


def test_company_delete(db_session):
    """企業情報の削除テスト"""
    company = Company(
        company_code="1234",
        name="テスト株式会社"
    )
    db_session.add(company)
    db_session.commit()

    # 削除
    db_session.delete(company)
    db_session.commit()

    # 削除の確認
    deleted_company = db_session.query(Company).filter_by(company_code="1234").first()
    assert deleted_company is None


def test_company_financial_relationship(db_session):
    """企業と財務情報のリレーションシップテスト"""
    # 企業を作成
    company = Company(
        company_code="1234",
        name="テスト株式会社"
    )
    db_session.add(company)
    db_session.commit()

    # 財務情報を追加
    financial = Financial(
        company_id=company.id,
        fiscal_year="2023",
        period_type=PeriodType.FULL_YEAR,
        period_end_date=datetime.date(2023, 12, 31),
        revenue=1000000000,
        operating_income=100000000,
        net_income=50000000
    )
    company.financials.append(financial)
    db_session.commit()

    # リレーションシップの確認
    assert len(company.financials) == 1
    assert company.financials[0].fiscal_year == "2023"
    assert company.financials[0].revenue == 1000000000

    # 企業を削除すると財務情報も削除される（cascade="all, delete-orphan"）
    db_session.delete(company)
    db_session.commit()

    # 財務情報も削除されていることを確認
    assert db_session.query(Financial).filter_by(company_id=company.id).first() is None


def test_company_news_relationship(db_session):
    """企業とニュースのリレーションシップテスト"""
    # 企業を作成
    company = Company(
        company_code="1234",
        name="テスト株式会社"
    )
    db_session.add(company)
    db_session.commit()

    # ニュースを追加
    news = News(
        company_id=company.id,
        title="テストニュース",
        content="これはテストニュースです",
        published_at=datetime.datetime(2023, 12, 31, 12, 0, 0),
        url="https://example.com/news/1",
        source="テストソース",
        category="プレスリリース"
    )
    company.news.append(news)
    db_session.commit()

    # リレーションシップの確認
    assert len(company.news) == 1
    assert company.news[0].title == "テストニュース"
    assert company.news[0].content == "これはテストニュースです"

    # 企業を削除するとニュースも削除される（cascade="all, delete-orphan"）
    db_session.delete(company)
    db_session.commit()

    # ニュースも削除されていることを確認
    assert db_session.query(News).filter_by(company_id=company.id).first() is None


def test_company_to_dict(db_session):
    """to_dictメソッドのテスト"""
    company = Company(
        company_code="1234",
        name="テスト株式会社",
        industry="情報・通信"
    )
    db_session.add(company)
    db_session.commit()

    company_dict = company.to_dict()
    assert company_dict["company_code"] == "1234"
    assert company_dict["name"] == "テスト株式会社"
    assert company_dict["industry"] == "情報・通信"
    assert "id" in company_dict
    assert "created_at" in company_dict
    assert "updated_at" in company_dict


def test_company_from_dict():
    """from_dictメソッドのテスト"""
    data = {
        "company_code": "1234",
        "name": "テスト株式会社",
        "industry": "情報・通信",
        "invalid_field": "この項目は無視される"
    }
    company = Company.from_dict(data)

    assert company.company_code == "1234"
    assert company.name == "テスト株式会社"
    assert company.industry == "情報・通信"
    assert not hasattr(company, "invalid_field")


def test_company_update_from_dict(db_session):
    """updateメソッドのテスト"""
    company = Company(
        company_code="1234",
        name="テスト株式会社",
        industry="情報・通信"
    )
    db_session.add(company)
    db_session.commit()

    update_data = {
        "name": "更新後株式会社",
        "industry": "製造業",
        "invalid_field": "この項目は無視される"
    }
    company.update(update_data)
    db_session.commit()

    assert company.name == "更新後株式会社"
    assert company.industry == "製造業"
    assert company.company_code == "1234"  # 更新されていないフィールド
    assert not hasattr(company, "invalid_field") 