"""
ExtractionManagerのテスト

データ抽出機能の単体テストを実施します。
"""

from datetime import date
from typing import Any, Dict

import pytest

from app.errors.url_analysis_errors import ExtractionError
from app.extraction.manager import ExtractionManager


@pytest.mark.asyncio
async def test_extract_company_info():
    """企業情報抽出のテスト"""
    extractor = ExtractionManager()
    selectors = {
        "name": "h1.company-name",
        "description": "div.company-description",
        "established": "table tr:contains('設立')",
    }

    # モック用のHTMLコンテンツ
    html_content = """
    <html>
        <h1 class="company-name">テスト株式会社</h1>
        <div class="company-description">テスト事業の説明</div>
        <table>
            <tr>
                <th>設立</th>
                <td>2020年1月1日</td>
            </tr>
        </table>
    </html>
    """

    # _extract_company_infoメソッドのテスト
    result = extractor._extract_company_info(html_content, selectors)

    assert result is not None
    assert result["name"] == "テスト株式会社"
    assert result["description"] == "テスト事業の説明"
    assert result["established_date"] == date(2020, 1, 1)


@pytest.mark.asyncio
async def test_extract_financial_info():
    """財務情報抽出のテスト"""
    extractor = ExtractionManager()
    selectors = {
        "table": "table.financial-info",
        "rows": "tr",
    }

    # モック用のHTMLコンテンツ
    html_content = """
    <html>
        <table class="financial-info">
            <tr>
                <th>年度</th>
                <th>売上高</th>
                <th>営業利益</th>
                <th>純利益</th>
            </tr>
            <tr>
                <td>2023年度</td>
                <td>10億円</td>
                <td>1億円</td>
                <td>5000万円</td>
            </tr>
        </table>
    </html>
    """

    # _extract_financial_infoメソッドのテスト
    result = extractor._extract_financial_info(html_content, selectors)

    assert len(result) == 1
    financial = result[0]
    assert financial["fiscal_year"] == "2023"
    assert financial["revenue"] == 1_000_000_000
    assert financial["operating_income"] == 100_000_000
    assert financial["net_income"] == 50_000_000


@pytest.mark.asyncio
async def test_parse_amount():
    """金額パースのテスト"""
    extractor = ExtractionManager()

    # 正常系のテスト
    assert extractor._parse_amount("1,000,000円") == 1_000_000
    assert extractor._parse_amount("1億円") == 100_000_000
    assert extractor._parse_amount("1.5億円") == 150_000_000
    assert extractor._parse_amount("500百万円") == 500_000_000

    # 異常系のテスト
    assert extractor._parse_amount("不正な金額") is None
    assert extractor._parse_amount("") is None
    assert extractor._parse_amount("円") is None


@pytest.mark.asyncio
async def test_validation_score():
    """検証スコア計算のテスト"""
    extractor = ExtractionManager()

    # 完全一致のケース
    data1: Dict[str, Any] = {
        "name": "テスト",
        "value": 100,
    }
    schema1 = {
        "name": str,
        "value": int,
    }
    assert extractor.calculate_validation_score(data1, schema1) == 1.0

    # 部分一致のケース
    data2: Dict[str, Any] = {
        "name": "テスト",
        "value": "100",  # 型が異なる
    }
    schema2 = {
        "name": str,
        "value": int,
        "missing": str,  # 存在しないフィールド
    }
    assert extractor.calculate_validation_score(data2, schema2) == 1/3  # nameのみ一致

    # 空データのケース
    assert extractor.calculate_validation_score({}, {}) == 0.0
    assert extractor.calculate_validation_score(None, schema1) == 0.0
    assert extractor.calculate_validation_score(data1, None) == 0.0


@pytest.mark.asyncio
async def test_error_handling():
    """エラーハンドリングのテスト"""
    extractor = ExtractionManager(timeout=0.1)  # タイムアウトを短く設定

    # 存在しないURLへのアクセス
    with pytest.raises(ExtractionError) as exc_info:
        await extractor.extract_company_info(
            "https://invalid.example.com",
            {"name": "h1"}
        )
    assert "ExtractionError" in str(exc_info.type)

    # タイムアウトのテスト
    with pytest.raises(ExtractionError) as exc_info:
        await extractor.extract_company_info(
            "https://httpstat.us/200?sleep=5000",  # 5秒遅延
            {"name": "h1"}
        )
    assert "タイムアウト" in str(exc_info.value) 