"""Unit tests for Nitori crawler."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.crawler.nitori import NitoriCrawler
from app.parser.llm_parser import LLMParser


def test_nitori_crawler_init():
    """Test NitoriCrawler initialization."""
    storage_dir = Path("test_data")
    crawler = NitoriCrawler(storage_dir=storage_dir)
    
    assert crawler.base_url == "https://www.nitorihd.co.jp"
    assert crawler.storage_dir == storage_dir
    assert crawler.ir_url == "https://www.nitorihd.co.jp/ir/"
    assert crawler.company_info_url == "https://www.nitorihd.co.jp/company/about/"


@patch("app.crawler.nitori.LLMParser")
def test_get_company_info(mock_llm_parser, mock_playwright):
    """Test getting company information."""
    # LLMParserのモックを設定
    mock_parser = MagicMock()
    mock_parser.parse.return_value = {
        "extracted_data": {
            "設立": "1972年3月",
            "資本金": "13,370百万円",
            "従業員数": "45,000名",
            "事業内容": "家具・インテリア用品の販売",
            "本社所在地": "札幌市北区"
        },
        "confidence": 0.95
    }
    mock_llm_parser.return_value = mock_parser
    
    crawler = NitoriCrawler()
    with crawler:
        company_info = crawler._get_company_info()
    
    assert company_info["name"] == "株式会社ニトリホールディングス"
    assert company_info["company_profile"]["設立"] == "1972年3月"
    assert company_info["company_profile"]["資本金"] == "13,370百万円"
    assert company_info["confidence"] == 0.95


def test_llm_parser(mock_openai):
    """Test LLM parser."""
    # OpenAIクライアントのモック
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content="""
{
    "extracted_data": {
        "設立": "1972年3月",
        "資本金": "13,370百万円"
    },
    "confidence": 0.95
}
"""
                )
            )
        ]
    )
    mock_openai.return_value = mock_client
    
    parser = LLMParser(api_key="test_key")
    parser.client = mock_client  # 直接クライアントを置き換え
    
    # テスト用のHTML
    html_content = """
    <html>
        <body>
            <div class="company-info">
                <dl>
                    <dt>設立</dt>
                    <dd>1972年3月</dd>
                    <dt>資本金</dt>
                    <dd>13,370百万円</dd>
                </dl>
            </div>
        </body>
    </html>
    """
    
    # 期待するフィールド
    expected_fields = {
        "設立": "会社の設立日",
        "資本金": "会社の資本金額"
    }
    
    # パース実行
    result = parser.parse(html_content, "company_info", expected_fields)
    
    assert result is not None
    assert result["extracted_data"]["設立"] == "1972年3月"
    assert result["extracted_data"]["資本金"] == "13,370百万円"
    assert result["confidence"] == 0.95


def test_llm_parser_validation():
    """Test LLM parser validation."""
    parser = LLMParser(api_key="test_key")
    
    # 不正なデータ構造
    invalid_data = {
        "data": {
            "設立": "1972年3月"
        }
    }
    
    expected_fields = {
        "設立": "会社の設立日"
    }
    
    # バリデーション実行
    assert not parser._validate_parsed_data(invalid_data, expected_fields)
    
    # 不正な信頼度
    invalid_confidence = {
        "extracted_data": {
            "設立": "1972年3月"
        },
        "confidence": 2.0
    }
    
    assert not parser._validate_parsed_data(invalid_confidence, expected_fields)
