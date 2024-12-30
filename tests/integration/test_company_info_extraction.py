"""
企業情報抽出の統合テスト

実際のURLを使用して、企業情報が正しく抽出できることを確認します。
"""

import pytest
from sqlalchemy.orm import Session

from app.llm.manager import LLMManager
from app.models.company import Company
from app.site_analyzer import URLAnalyzer


@pytest.mark.asyncio
async def test_real_company_info_extraction(db_session: Session):
    """実際のURLから企業情報を抽出できることを確認"""
    # テスト対象の企業URL
    test_urls = [
        "https://www.example.com/",  # テスト用サイト
    ]

    # 実際のLLMManagerを使用
    analyzer = URLAnalyzer(llm_manager=LLMManager())

    for url in test_urls:
        # 1. URLの内容を分析
        result = await analyzer.analyze(url)

        assert result is not None
        assert "error" not in result
        assert "llm_response" in result

        # 2. 分析結果から企業情報を抽出できることを確認
        analysis = result["llm_response"]
        assert isinstance(analysis, dict)

        # 基本的な企業情報が含まれていることを確認
        required_fields = ["company_name", "business_description", "industry"]
        for field in required_fields:
            assert field in analysis
            assert analysis[field] is not None
            assert len(analysis[field]) > 0

        # 3. 抽出した情報でCompanyモデルが作成できることを確認
        company = Company(
            name=analysis["company_name"],
            description=analysis["business_description"],
            industry=analysis["industry"],
            website_url=url,
        )

        # DBに保存できることを確認
        db_session.add(company)
        db_session.flush()  # IDを生成するためにflush

        # 保存した情報が取得できることを確認
        db_session.refresh(company)  # 最新の状態を取得
        assert company.id is not None
        assert company.name == analysis["company_name"]
        assert company.description == analysis["business_description"]
        assert company.industry == analysis["industry"]
        assert company.website_url == url

        db_session.commit()


@pytest.mark.asyncio
async def test_company_info_extraction_error_handling():
    """企業情報抽出時のエラーハンドリングを確認"""
    # 存在しないURLでテスト
    invalid_url = "https://this-url-does-not-exist.example.com"

    analyzer = URLAnalyzer(llm_manager=LLMManager())
    result = await analyzer.analyze(invalid_url)

    assert result is not None
    assert "error" in result
    assert result["relevance_score"] == 0.0
    assert result["category"] == "error"
    assert result["confidence"] == 0.0
    assert result["processing_time"] == 0.0
    assert result["llm_response"] == {}


@pytest.mark.asyncio
async def test_company_info_extraction_rate_limit():
    """レート制限時の挙動を確認"""
    # 短時間で複数回リクエストを送信
    url = "https://www.example.com"
    analyzer = URLAnalyzer(llm_manager=LLMManager())

    results = []
    for _ in range(5):  # 5回連続でリクエスト
        result = await analyzer.analyze(url)
        results.append(result)

    # 少なくとも1つのレスポンスにエラーが含まれていることを確認
    assert any("error" in result for result in results)
