"""
企業情報抽出の統合テスト

実際のURLを使用して、企業情報が正しく抽出できることを確認します。
"""

import pytest
from sqlalchemy.orm import Session

from app.extraction.manager import ExtractionManager
from app.models.company import Company


@pytest.mark.asyncio
async def test_real_company_info_extraction(db_session: Session):
    """実際のURLから企業情報を抽出できることを確認"""
    # テスト対象の企業URL
    test_urls = [
        "https://www.example.com/",  # テスト用サイト
    ]

    # セレクターの設定
    selectors = {
        "name": "h1.company-name",
        "description": "div.company-description",
        "established": "table tr:contains('設立')",
    }

    extractor = ExtractionManager()

    for url in test_urls:
        # 1. 企業情報を抽出
        company_info = await extractor.extract_company_info(url, selectors)

        assert company_info is not None
        assert "name" in company_info
        assert "description" in company_info

        # 2. 財務情報を抽出
        financial_selectors = {
            "table": "table.financial-info",
            "rows": "tr",
        }
        financials = await extractor.extract_financial_info(url, financial_selectors)

        assert isinstance(financials, list)
        if financials:  # 財務情報が存在する場合
            for financial in financials:
                assert "fiscal_year" in financial
                assert "revenue" in financial
                assert "operating_income" in financial
                assert "net_income" in financial

        # 3. 抽出した情報でCompanyモデルが作成できることを確認
        company = Company(
            name=company_info["name"],
            description=company_info["description"],
            established_date=company_info.get("established_date"),
            website_url=url,
        )

        # DBに保存できることを確認
        db_session.add(company)
        db_session.flush()  # IDを生成するためにflush

        # 保存した情報が取得できることを確認
        db_session.refresh(company)  # 最新の状態を取得
        assert company.id is not None
        assert company.name == company_info["name"]
        assert company.description == company_info["description"]
        assert company.website_url == url

        db_session.commit()


@pytest.mark.asyncio
async def test_company_info_extraction_error_handling():
    """企業情報抽出時のエラーハンドリングを確認"""
    # 存在しないURLでテスト
    invalid_url = "https://this-url-does-not-exist.example.com"
    selectors = {"name": "h1.company-name"}

    extractor = ExtractionManager()
    with pytest.raises(Exception) as exc_info:
        await extractor.extract_company_info(invalid_url, selectors)

    assert "ExtractionError" in str(exc_info.type)


@pytest.mark.asyncio
async def test_company_info_validation():
    """企業情報の検証スコア計算を確認"""
    extractor = ExtractionManager()

    # テストデータ
    extracted_data = {
        "name": "テスト株式会社",
        "description": "テスト事業の説明",
        "established_date": "2020-01-01",
        "invalid_field": "不正なフィールド",
    }

    expected_schema = {
        "name": str,
        "description": str,
        "established_date": str,
        "stock_exchange": str,  # 存在しないフィールド
    }

    # 検証スコアの計算
    score = extractor.calculate_validation_score(extracted_data, expected_schema)

    # 3/4のフィールドが正しい型なので、スコアは0.75になるはず
    assert score == 0.75


@pytest.mark.asyncio
async def test_financial_info_validation():
    """財務情報の検証を確認"""
    extractor = ExtractionManager()

    # テストデータ
    extracted_data = {
        "fiscal_year": "2023",
        "revenue": 1000000000,
        "operating_income": 100000000,
        "net_income": "not_a_number",  # 不正な値
    }

    expected_schema = {
        "fiscal_year": str,
        "revenue": float,
        "operating_income": float,
        "net_income": float,
    }

    # 検証スコアの計算
    score = extractor.calculate_validation_score(extracted_data, expected_schema)

    # 3/4のフィールドが正しい型なので、スコアは0.75になるはず
    assert score == 0.75
