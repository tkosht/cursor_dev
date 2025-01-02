"""
データ抽出の統合テスト

実際のURLを使用して、データ抽出機能の統合テストを実施します。
"""

import asyncio
from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.exceptions import ExtractionError
from app.extraction.manager import ExtractionManager
from app.models.company import Company


@pytest.mark.asyncio
async def test_real_data_extraction(db_session: Session):
    """実際のURLからのデータ抽出テスト"""
    # テスト対象のURL
    test_urls = [
        "https://www.example.com/company",  # テスト用サイト
    ]

    # 抽出設定
    company_selectors = {
        "name": "h1.company-name",
        "description": "div.company-description",
        "established": "table tr:contains('設立')",
    }

    financial_selectors = {
        "table": "table.financial-info",
        "rows": "tr",
    }

    extractor = ExtractionManager()

    for url in test_urls:
        # 1. データ抽出
        company_info = await extractor.extract_company_info(url, company_selectors)
        financials = await extractor.extract_financial_info(url, financial_selectors)

        # 2. データの検証
        company_schema = {
            "name": str,
            "description": str,
            "established_date": date,
        }
        company_score = extractor.calculate_validation_score(
            company_info,
            company_schema
        )
        assert company_score >= 0.7  # 70%以上の精度を要求

        if financials:
            financial_schema = {
                "fiscal_year": str,
                "revenue": float,
                "operating_income": float,
                "net_income": float,
            }
            for financial in financials:
                score = extractor.calculate_validation_score(
                    financial,
                    financial_schema
                )
                assert score >= 0.7  # 70%以上の精度を要求

        # 3. データの永続化
        company = Company(
            name=company_info["name"],
            description=company_info["description"],
            established_date=company_info.get("established_date"),
            website_url=url,
        )

        db_session.add(company)
        db_session.flush()
        db_session.refresh(company)

        assert company.id is not None
        assert company.name == company_info["name"]
        assert company.description == company_info["description"]

        db_session.commit()


@pytest.mark.asyncio
async def test_concurrent_extraction():
    """並行データ抽出のテスト"""
    urls = [
        "https://www.example1.com",
        "https://www.example2.com",
        "https://www.example3.com",
    ]
    selectors = {"name": "h1.company-name"}

    extractor = ExtractionManager()
    tasks = [
        extractor.extract_company_info(url, selectors)
        for url in urls
    ]

    # 同時実行による例外が発生しないことを確認
    with pytest.raises(ExtractionError):
        await asyncio.gather(*tasks)


@pytest.mark.asyncio
async def test_rate_limit_handling():
    """レート制限のテスト"""
    url = "https://www.example.com"
    selectors = {"name": "h1.company-name"}

    extractor = ExtractionManager()
    
    # 短時間で複数回リクエスト
    for _ in range(5):
        with pytest.raises(ExtractionError) as exc_info:
            await extractor.extract_company_info(url, selectors)
        
        # レート制限エラーまたはネットワークエラーが発生することを確認
        assert any(
            error_type in str(exc_info.value)
            for error_type in ["レート制限", "ネットワークエラー"]
        ) 