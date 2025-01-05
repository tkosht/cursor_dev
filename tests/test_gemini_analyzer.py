"""GeminiAnalyzerのテストモジュール。"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from app.gemini_analyzer import GeminiAnalyzer
from datetime import datetime

@pytest.fixture
def mock_env():
    """環境変数をモックするフィクスチャ。"""
    with patch.dict(os.environ, {"GOOGLE_API_KEY_GEMINI": "test_api_key"}):
        yield

@pytest.fixture
def analyzer():
    """GeminiAnalyzerのインスタンスを生成するフィクスチャ。"""
    return GeminiAnalyzer(api_key="test_api_key")

@pytest.fixture
def valid_content():
    """有効なコンテンツデータを生成するフィクスチャ。"""
    return {
        'title': 'テスト記事',
        'content': 'これはテストコンテンツです。',
        'date': datetime.now(),
        'url': 'https://example.com/test'
    }

@pytest.fixture
def valid_api_response():
    """有効なAPI応答を生成するフィクスチャ。"""
    return json.dumps({
        'entities': [
            {
                'id': 'company1',
                'type': 'Company',
                'name': 'テスト株式会社',
                'description': 'テスト企業の説明'
            }
        ],
        'relationships': [
            {
                'source_id': 'company1',
                'target_id': 'product1',
                'type': 'PRODUCES',
                'strength': 0.8,
                'description': '主力製品'
            }
        ],
        'impact_scores': {
            'company1': 0.75
        },
        'summary': 'テスト企業に関する市場分析結果'
    })

def test_init_no_api_key():
    """APIキーが指定されていない場合のテスト。"""
    with pytest.raises(ValueError) as exc_info:
        GeminiAnalyzer(api_key="")
    assert "API key is required" in str(exc_info.value)

def test_analyze_content_success(analyzer, valid_content, valid_api_response):
    """analyze_content()の正常系テスト。"""
    with patch.object(analyzer._model, 'generate_content') as mock_generate:
        mock_response = MagicMock()
        mock_response.text = valid_api_response
        mock_generate.return_value = mock_response

        result = analyzer.analyze_content(valid_content)

        assert 'entities' in result
        assert 'relationships' in result
        assert 'impact_scores' in result
        assert 'summary' in result
        assert result['entities'][0]['name'] == 'テスト株式会社'
        assert result['impact_scores']['company1'] == 0.75

def test_analyze_content_empty_input(analyzer):
    """空の入力に対するテスト。"""
    with pytest.raises(ValueError) as exc_info:
        analyzer.analyze_content({})
    assert "Invalid content format" in str(exc_info.value)

def test_analyze_content_api_error(analyzer, valid_content):
    """API呼び出しエラー時のテスト。"""
    with patch.object(analyzer._model, 'generate_content') as mock_generate:
        mock_generate.side_effect = Exception("API error")

        with pytest.raises(RuntimeError) as exc_info:
            analyzer.analyze_content(valid_content)
        assert "Failed to analyze content" in str(exc_info.value)

def test_construct_prompt(analyzer, valid_content):
    """_construct_prompt()のテスト。"""
    prompt = analyzer._construct_prompt(valid_content)

    assert valid_content['title'] in prompt
    assert valid_content['content'] in prompt
    assert valid_content['url'] in prompt
    assert valid_content['date'].isoformat() in prompt

def test_construct_prompt_no_date(analyzer, valid_content):
    """日付なしの場合の_construct_prompt()のテスト。"""
    content_without_date = valid_content.copy()
    del content_without_date['date']

    prompt = analyzer._construct_prompt(content_without_date)

    assert 'Unknown' in prompt
    assert content_without_date['title'] in prompt
    assert content_without_date['content'] in prompt

def test_parse_response_invalid_score(analyzer):
    """不正なスコア値を含むレスポンスのテスト。"""
    invalid_response = json.dumps({
        'entities': [],
        'relationships': [],
        'impact_scores': {'test': 1.5},  # 範囲外の値
        'summary': 'test'
    })

    with pytest.raises(ValueError) as exc_info:
        analyzer._parse_response(invalid_response)
    assert "Impact score must be between 0 and 1" in str(exc_info.value)

def test_parse_response_empty(analyzer):
    """空のレスポンスのテスト。"""
    with pytest.raises(ValueError) as exc_info:
        analyzer._parse_response("")
    assert "Invalid JSON format" in str(exc_info.value) 