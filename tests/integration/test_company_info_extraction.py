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
        "https://www.sony.com/ja/",  # ソニー
        "https://www.toyota.co.jp/",  # トヨタ自動車
        "https://www.nintendo.co.jp/"  # 任天堂
    ]
    
    analyzer = URLAnalyzer(llm_manager=LLMManager())
    
    for url in test_urls:
        # 1. URLの内容を分析
        result = await analyzer.analyze(url)
        
        assert result is not None
        assert "error" not in result
        assert "analysis" in result
        
        # 2. 分析結果から企業情報を抽出できることを確認
        analysis = result["analysis"]
        assert isinstance(analysis, dict)
        
        # 基本的な企業情報が含まれていることを確認
        required_fields = [
            "company_name",
            "business_description",
            "industry"
        ]
        for field in required_fields:
            assert field in analysis
            assert analysis[field] is not None
            assert len(analysis[field]) > 0

        # 3. 抽出した情報でCompanyモデルが作成できることを確認
        company = Company(
            name=analysis["company_name"],
            description=analysis["business_description"],
            industry=analysis["industry"],
            website_url=url
        )
        
        # DBに保存できることを確認
        db_session.add(company)
        db_session.commit()
        
        # 保存した情報が取得できることを確認
        saved_company = db_session.query(Company).filter_by(
            name=analysis["company_name"]
        ).first()
        
        assert saved_company is not None
        assert saved_company.name == analysis["company_name"]
        assert saved_company.description == analysis["business_description"]
        assert saved_company.industry == analysis["industry"]
        assert saved_company.website_url == url


@pytest.mark.asyncio
async def test_company_info_extraction_error_handling():
    """企業情報抽出時のエラーハンドリングを確認"""
    # 存在しないURLでテスト
    invalid_url = "https://this-url-does-not-exist.example.com"
    
    analyzer = URLAnalyzer(llm_manager=LLMManager())
    result = await analyzer.analyze(invalid_url)
    
    assert result is not None
    assert "error" in result
    assert result["url"] == invalid_url
    assert result["llm_latency"] == 0.0
    assert result["processing_time"] > 0.0


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