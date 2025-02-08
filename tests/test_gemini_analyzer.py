"""GeminiAnalyzerのテストモジュール。"""

import json
from unittest.mock import patch

import pytest

from app.exceptions import GeminiError, ValidationError
from app.gemini_analyzer import GeminiAnalyzer


@pytest.fixture
def gemini_analyzer():
    """GeminiAnalyzerのインスタンスを生成するフィクスチャ。"""
    return GeminiAnalyzer(api_key="test_api_key")


def test_init_with_empty_api_key():
    """空のAPIキーでの初期化をテストする。"""
    with pytest.raises(ValidationError):
        GeminiAnalyzer(api_key="")


def test_analyze_content_with_valid_input(gemini_analyzer):
    """有効な入力でのコンテンツ分析をテストする。"""
    content = {
        "title": "テストタイトル",
        "content": "テストコンテンツ",
        "date": "2025-01-11",
        "url": "https://example.com"
    }

    mock_response = {
        "entities": [
            {"id": "1", "name": "テスト", "type": "TEST"}
        ],
        "relationships": [
            {"source": "1", "target": "2", "type": "RELATED_TO"}
        ],
        "impact_scores": {
            "1": 0.8,
            "2": 0.6
        }
    }

    with patch.object(gemini_analyzer, '_call_gemini_api') as mock_call:
        mock_call.return_value = json.dumps(mock_response)
        result = gemini_analyzer.analyze_content(content)

        assert isinstance(result, dict)
        assert "entities" in result
        assert "relationships" in result
        assert "impact_scores" in result
        assert len(result["entities"]) == 1
        assert len(result["relationships"]) == 1
        assert len(result["impact_scores"]) == 2


def test_analyze_content_with_invalid_input(gemini_analyzer):
    """無効な入力でのコンテンツ分析をテストする。"""
    invalid_content = {
        "title": "",
        "content": "",
        "date": "invalid_date",
        "url": "invalid_url"
    }

    with pytest.raises(ValidationError):
        gemini_analyzer.analyze_content(invalid_content)


def test_parse_response_with_valid_json(gemini_analyzer):
    """有効なJSONレスポンスの解析をテストする。"""
    valid_json = {
        "entities": [
            {"id": "1", "name": "エンティティ1", "type": "TYPE1"}
        ],
        "relationships": [
            {"source": "1", "target": "2", "type": "RELATED_TO"}
        ],
        "impact_scores": {
            "1": 0.8,
            "2": 0.6
        }
    }

    result = gemini_analyzer._parse_response(json.dumps(valid_json))
    assert isinstance(result, dict)
    assert "entities" in result
    assert "relationships" in result
    assert "impact_scores" in result


def test_parse_response_with_invalid_json(gemini_analyzer):
    """無効なJSONレスポンスの解析をテストする。"""
    invalid_json = "invalid json string"
    with pytest.raises(GeminiError):
        gemini_analyzer._parse_response(invalid_json)


def test_validate_json_result_with_missing_fields(gemini_analyzer):
    """必須フィールドが欠けているJSONの検証をテストする。"""
    invalid_json = {
        "entities": [],
        # relationshipsが欠けている
        "impact_scores": {}
    }

    with pytest.raises(ValidationError):
        gemini_analyzer._validate_json_result(invalid_json)


def test_validate_json_result_with_invalid_impact_score(gemini_analyzer):
    """無効なインパクトスコアを含むJSONの検証をテストする。"""
    invalid_json = {
        "entities": [
            {"id": "1", "name": "エンティティ1", "type": "TYPE1"}
        ],
        "relationships": [
            {"source": "1", "target": "2", "type": "RELATED_TO"}
        ],
        "impact_scores": {
            "1": 1.5,  # スコアが1.0を超えている
            "2": -0.5  # スコアが0.0未満
        }
    }

    with pytest.raises(ValidationError):
        gemini_analyzer._validate_json_result(invalid_json)


def test_analyze_content_with_api_error(gemini_analyzer):
    """APIエラー時の処理をテストする。"""
    content = {
        "title": "テストタイトル",
        "content": "テストコンテンツ",
        "date": "2025-01-11",
        "url": "https://example.com"
    }

    with patch.object(gemini_analyzer, '_call_gemini_api') as mock_call:
        mock_call.side_effect = GeminiError("APIエラー")
        with pytest.raises(GeminiError):
            gemini_analyzer.analyze_content(content)


def test_analyze_content_with_timeout(gemini_analyzer):
    """タイムアウト時の処理をテストする。"""
    content = {
        "title": "テストタイトル",
        "content": "テストコンテンツ",
        "date": "2025-01-11",
        "url": "https://example.com"
    }

    with patch.object(gemini_analyzer, '_call_gemini_api') as mock_call:
        mock_call.side_effect = TimeoutError("タイムアウト")
        with pytest.raises(GeminiError):
            gemini_analyzer.analyze_content(content)


def test_analyze_content_with_retry(gemini_analyzer):
    """リトライ処理をテストする。"""
    content = {
        "title": "テストタイトル",
        "content": "テストコンテンツ",
        "date": "2025-01-11",
        "url": "https://example.com"
    }

    mock_response = {
        "entities": [],
        "relationships": [],
        "impact_scores": {}
    }

    with patch.object(gemini_analyzer, '_call_gemini_api') as mock_call:
        mock_call.side_effect = [
            GeminiError("一時的なエラー"),
            GeminiError("一時的なエラー"),
            json.dumps(mock_response)
        ]
        
        result = gemini_analyzer.analyze_content(content)
        assert isinstance(result, dict)
        assert mock_call.call_count == 3


def test_validate_json_result_with_invalid_trends(gemini_analyzer):
    """無効なトレンド情報を含むJSONの検証をテストする。"""
    invalid_json = {
        "entities": [
            {"id": "1", "name": "エンティティ1", "type": "TYPE1"}
        ],
        "relationships": [
            {"source": "1", "target": "2", "type": "RELATED_TO"}
        ],
        "impact_scores": {
            "1": 0.8,
            "2": 0.6
        },
        "trends": "invalid"  # trendsが文字列（配列であるべき）
    }

    with pytest.raises(ValidationError):
        gemini_analyzer._validate_json_result(invalid_json)


def test_validate_json_result_with_invalid_entities(gemini_analyzer):
    """無効なエンティティ情報を含むJSONの検証をテストする。"""
    invalid_json = {
        "entities": [
            {"name": "エンティティ1", "type": "TYPE1"}  # idが欠けている
        ],
        "relationships": [],
        "impact_scores": {}
    }

    with pytest.raises(ValidationError):
        gemini_analyzer._validate_json_result(invalid_json)


def test_validate_json_result_with_invalid_relationships(gemini_analyzer):
    """無効なリレーションシップ情報を含むJSONの検証をテストする。"""
    invalid_json = {
        "entities": [
            {"id": "1", "name": "エンティティ1", "type": "TYPE1"}
        ],
        "relationships": [
            {"source": "1", "type": "RELATED_TO"}  # targetが欠けている
        ],
        "impact_scores": {
            "1": 0.8
        }
    }

    with pytest.raises(ValidationError):
        gemini_analyzer._validate_json_result(invalid_json)


def test_analyze_content_with_empty_content(gemini_analyzer):
    """空のコンテンツでの分析をテストする。"""
    empty_content = {
        "title": "",
        "content": "",
        "date": "",
        "url": ""
    }

    with pytest.raises(ValidationError):
        gemini_analyzer.analyze_content(empty_content)


def test_analyze_content_with_long_content(gemini_analyzer):
    """長いコンテンツでの分析をテストする。"""
    long_content = {
        "title": "テストタイトル",
        "content": "a" * 10000,  # 10000文字の長いコンテンツ
        "date": "2025-01-11",
        "url": "https://example.com"
    }

    mock_response = {
        "entities": [],
        "relationships": [],
        "impact_scores": {}
    }

    with patch.object(gemini_analyzer, '_call_gemini_api') as mock_call:
        mock_call.return_value = json.dumps(mock_response)
        result = gemini_analyzer.analyze_content(long_content)
        assert isinstance(result, dict)


def test_analyze_content_with_special_characters(gemini_analyzer):
    """特殊文字を含むコンテンツでの分析をテストする。"""
    special_content = {
        "title": "テスト!@#$%^&*()",
        "content": "特殊文字!@#$%^&*()",
        "date": "2025-01-11",
        "url": "https://example.com"
    }

    mock_response = {
        "entities": [],
        "relationships": [],
        "impact_scores": {}
    }

    with patch.object(gemini_analyzer, '_call_gemini_api') as mock_call:
        mock_call.return_value = json.dumps(mock_response)
        result = gemini_analyzer.analyze_content(special_content)
        assert isinstance(result, dict) 