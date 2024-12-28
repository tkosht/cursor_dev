"""
財務情報モデルのテスト

このモジュールは、財務情報モデルの機能をテストします。
"""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.financial import Financial


def test_create_financial(session, sample_financial):
    """財務情報の作成をテストします。"""
    assert sample_financial.id is not None
    assert sample_financial.fiscal_year == "2023年度"
    assert sample_financial.period_type == PeriodType.FULL_YEAR
    assert sample_financial.revenue == 1000000000


def test_financial_to_dict(sample_financial):
    """財務情報モデルの辞書変換をテストします。"""
    data = sample_financial.to_dict()
    assert data["fiscal_year"] == "2023年度"
    assert data["revenue"] == 1000000000
    assert data["operating_income"] == 100000000


def test_financial_from_dict(session, sample_company):
    """辞書からの財務情報モデル作成をテストします。"""
    data = {
        "company_id": sample_company.id,
        "fiscal_year": "2023Q3",
        "period_type": PeriodType.QUARTER,
        "period_end_date": date(2023, 11, 20),
        "revenue": 500000000,
        "operating_income": 50000000
    }
    financial = Financial.from_dict(data)
    session.add(financial)
    session.commit()

    assert financial.id is not None
    assert financial.fiscal_year == "2023Q3"
    assert financial.revenue == 500000000


def test_financial_update(sample_financial):
    """財務情報の更新をテストします。"""
    data = {
        "revenue": 1100000000,
        "operating_income": 110000000
    }
    sample_financial.update(data)

    assert sample_financial.revenue == 1100000000
    assert sample_financial.operating_income == 110000000
    # 更新されていないフィールドは元の値のまま
    assert sample_financial.fiscal_year == "2023年度"


def test_financial_relationship(session, sample_financial):
    """財務情報モデルのリレーションシップをテストします。"""
    company = sample_financial.company
    assert company is not None
    assert company.name == "ニトリホールディングス"
    assert company.company_code == "9843"


def test_invalid_period_type(session, sample_company):
    """無効な決算期間種類をテストします。"""
    # None値の指定（nullable=Falseのため）
    financial = Financial(
        company_id=sample_company.id,
        fiscal_year="2023年度",
        period_type=None,  # None値は許可されない
        period_end_date=date(2024, 2, 20)
    )
    session.add(financial)
    
    # コミット時にエラーが発生することを確認
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
    
    # 無効な値の指定
    with pytest.raises(ValueError):
        PeriodType("invalid_type") 