"""
企業モデルのテスト

このモジュールは、企業モデルの機能をテストします。
"""

from datetime import date

import pytest

from app.models.company import Company


def test_create_company(session, sample_company):
    """企業の作成をテストします。"""
    assert sample_company.id is not None
    assert sample_company.company_code == "9843"
    assert sample_company.name == "ニトリホールディングス"
    assert sample_company.established_date == date(1972, 3, 3)


def test_company_to_dict(sample_company):
    """企業モデルの辞書変換をテストします。"""
    data = sample_company.to_dict()
    assert data["company_code"] == "9843"
    assert data["name"] == "ニトリホールディングス"
    assert data["industry"] == "小売業"


def test_company_from_dict(session):
    """辞書からの企業モデル作成をテストします。"""
    data = {
        "company_code": "7203",
        "name": "トヨタ自動車",
        "name_en": "TOYOTA MOTOR CORPORATION",
        "established_date": date(1937, 8, 28),
        "industry": "輸送用機器"
    }
    company = Company.from_dict(data)
    session.add(company)
    session.commit()

    assert company.id is not None
    assert company.company_code == "7203"
    assert company.name == "トヨタ自動車"


def test_company_update(sample_company):
    """企業情報の更新をテストします。"""
    data = {
        "name_en": "Nitori Holdings Corporation",
        "representative_position": "代表取締役社長"
    }
    sample_company.update(data)

    assert sample_company.name_en == "Nitori Holdings Corporation"
    assert sample_company.representative_position == "代表取締役社長"
    # 更新されていないフィールドは元の値のまま
    assert sample_company.company_code == "9843"


def test_company_relationships(session, sample_company, sample_financial, sample_news):
    """企業モデルのリレーションシップをテストします。"""
    # 財務情報の関連付けを確認
    assert len(sample_company.financials) == 1
    financial = sample_company.financials[0]
    assert financial.fiscal_year == "2023年度"
    assert financial.revenue == 1000000000

    # ニュースの関連付けを確認
    assert len(sample_company.news) == 1
    news = sample_company.news[0]
    assert news.title == "2024年2月期 第3四半期決算短信〔IFRS〕（連結）"
    assert news.source == "適時開示"


def test_company_unique_code(session):
    """企業コードの一意性制約をテストします。"""
    company1 = Company(
        company_code="1111",
        name="テスト企業1"
    )
    session.add(company1)
    session.commit()

    # 同じ企業コードで別の企業を作成
    company2 = Company(
        company_code="1111",
        name="テスト企業2"
    )
    session.add(company2)
    
    with pytest.raises(Exception):  # SQLAlchemyの具体的な例外クラスは環境依存
        session.commit() 