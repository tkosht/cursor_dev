"""GeminiAnalyzerのテストモジュール。"""

import json
import os
import pytest
from app.gemini_analyzer import GeminiAnalyzer

def test_init_with_valid_api_key():
    """有効なAPIキーでの初期化テスト。"""
    api_key = os.getenv("GOOGLE_API_KEY_GEMINI")
    analyzer = GeminiAnalyzer(api_key=api_key)
    assert analyzer.api_key == api_key

def test_init_with_empty_api_key():
    """空のAPIキーでの初期化テスト。"""
    with pytest.raises(ValueError) as exc_info:
        GeminiAnalyzer(api_key="")
    assert "APIキーが指定されておらず" in str(exc_info.value)

def test_analyze_content_with_valid_input():
    """有効な入力での解析テスト。"""
    analyzer = GeminiAnalyzer()
    content = {
        "title": "テスト記事",
        "content": "これはテストコンテンツです。市場分析に関する情報が含まれています。",
        "url": "https://example.com/test"
    }
    result = analyzer.analyze_content(content)
    
    # 必須フィールドの存在確認
    assert "market_impact" in result
    assert "trends" in result
    assert "entities" in result
    assert "relationships" in result
    
    # 値の型と範囲の確認
    assert isinstance(result["market_impact"], float)
    assert 0 <= result["market_impact"] <= 1
    assert isinstance(result["trends"], list)
    assert isinstance(result["entities"], list)
    assert isinstance(result["relationships"], list)

def test_analyze_content_with_invalid_input():
    """不正な入力での解析テスト。"""
    analyzer = GeminiAnalyzer()
    invalid_content = {"invalid": "data"}
    
    with pytest.raises(ValueError) as exc_info:
        analyzer.analyze_content(invalid_content)
    assert "Invalid content format" in str(exc_info.value)

def test_parse_response_with_valid_json():
    """有効なJSONレスポンスのパースのテスト。"""
    analyzer = GeminiAnalyzer()
    valid_response = {
        "market_impact": 0.8,
        "trends": ["trend1", "trend2"],
        "entities": [{"name": "Company1", "type": "COMPANY", "description": "desc"}],
        "relationships": [{"source": "Company1", "target": "Company2", "type": "INFLUENCES", "strength": 0.7}]
    }
    response = json.dumps(valid_response)
    result = analyzer._parse_response(response)
    assert result == valid_response

def test_parse_response_with_invalid_json():
    """不正なJSONレスポンスのパースのテスト。"""
    analyzer = GeminiAnalyzer()
    invalid_response = "invalid json"
    
    with pytest.raises(ValueError) as exc_info:
        analyzer._parse_response(invalid_response)
    assert "Invalid JSON format" in str(exc_info.value)

def test_validate_json_result_with_missing_fields():
    """必須フィールドが欠けているJSONの検証テスト。"""
    analyzer = GeminiAnalyzer()
    invalid_result = {
        "market_impact": 0.8,
        "trends": ["trend1"]
        # entities と relationships が欠けている
    }
    
    with pytest.raises(ValueError) as exc_info:
        analyzer._validate_json_result(invalid_result)
    assert "必須フィールド" in str(exc_info.value)

def test_validate_json_result_with_invalid_impact_score():
    """不正な影響度スコアを持つJSONの検証テスト。"""
    analyzer = GeminiAnalyzer()
    invalid_result = {
        "market_impact": 1.5,  # 範囲外の値
        "trends": ["trend1"],
        "entities": [],
        "relationships": []
    }
    
    with pytest.raises(ValueError) as exc_info:
        analyzer._validate_json_result(invalid_result)
    assert "Impact score must be between 0 and 1" in str(exc_info.value) 