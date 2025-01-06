"""MarketAnalyzerのテスト"""

from unittest.mock import patch

import pytest

from app.market_analyzer import MarketAnalyzer


@pytest.fixture
def market_analyzer():
    """MarketAnalyzerのインスタンスを生成"""
    return MarketAnalyzer()


def test_analyze_success(market_analyzer):
    """analyze()が正常に動作することをテスト。"""
    # モックデータ
    input_data = {
        'title': 'Test Title',
        'content': 'Test Content',
        'url': 'http://example.com',
        'published_at': '2024-01-01T00:00:00'
    }
    
    gemini_result = {
        'entities': [{'name': 'Company A', 'type': 'COMPANY'}],
        'relationships': [{'type': 'COMPETES', 'source': 'Company A', 'target': 'Company B'}],
        'market_impact': 0.8,
        'trends': ['AI sector growth']
    }
    
    # GeminiAnalyzerのモック
    with patch.object(market_analyzer.gemini, 'analyze_content', return_value=gemini_result):
        # テスト実行
        result = market_analyzer.analyze(input_data)
        
        # 検証
        assert result['entities'] == [{'name': 'Company A', 'type': 'COMPANY', 'description': '', 'properties': {}}]
        assert result['relationships'] == [{
            'type': 'COMPETES',
            'source': 'Company A',
            'target': 'Company B',
            'description': '',
            'properties': {}
        }]
        assert result['impact_scores']['market_impact'] == 0.8
        assert result['source_url'] == 'http://example.com'
        assert isinstance(result['analyzed_at'], str)


def test_analyze_error(market_analyzer):
    """analyze()がエラーを適切に処理できることをテスト。"""
    # モックデータ
    input_data = {
        'title': 'Test Title',
        'content': 'Test Content',
        'url': 'http://example.com',
        'published_at': '2024-01-01T00:00:00'
    }
    
    # GeminiAnalyzerのモックでエラーを発生させる
    with patch.object(market_analyzer.gemini, 'analyze_content', side_effect=ValueError("テストエラー")):
        # テスト実行と検証
        with pytest.raises(ValueError) as exc_info:
            market_analyzer.analyze(input_data)
        assert "テストエラー" in str(exc_info.value)


def test_process_gemini_output_success(market_analyzer):
    """process_gemini_output()が正常に動作することをテスト。"""
    result = {
        "market_impact": 0.8,
        "trends": ["AI sector growth"],
        "entities": [{"name": "Company A", "type": "COMPANY"}],
        "relationships": [{"type": "COMPETES", "source": "Company A", "target": "Company B"}]
    }
    processed = market_analyzer.process_gemini_output(result)
    assert processed["impact"] == 0.8


def test_process_gemini_output_invalid_input(market_analyzer):
    """process_gemini_output()が不正な入力を適切に処理できることをテスト。"""
    with pytest.raises(ValueError) as exc_info:
        market_analyzer.process_gemini_output("invalid")
    assert "辞書形式ではありません" in str(exc_info.value)


def test_extract_entities_success(market_analyzer):
    """_extract_entities()が正常に動作することをテスト。"""
    result = {
        "entities": [
            {"name": "Company A", "type": "COMPANY"},
            {"name": "Product X", "type": "PRODUCT"}
        ]
    }
    entities = market_analyzer._extract_entities(result)
    assert len(entities) == 2
    assert entities[0]["name"] == "Company A"
    assert entities[0]["type"] == "COMPANY"


def test_extract_entities_invalid_type(market_analyzer):
    """_extract_entities()が不正な型のentitiesを処理できることをテスト。"""
    result = {"entities": "invalid"}
    with pytest.raises(ValueError) as exc_info:
        market_analyzer._extract_entities(result)
    assert "リスト形式ではありません" in str(exc_info.value)


def test_extract_entities_missing_fields(market_analyzer):
    """_extract_entities()が必須フィールドの欠けたentitiesを処理できることをテスト。"""
    result = {"entities": [{"name": "Company A"}]}
    with pytest.raises(ValueError) as exc_info:
        market_analyzer._extract_entities(result)
    assert "必須フィールドが欠けています" in str(exc_info.value)


def test_detect_relationships_success(market_analyzer):
    """_detect_relationships()が正常に動作することをテスト。"""
    result = {
        "relationships": [
            {
                "type": "COMPETES",
                "source": "Company A",
                "target": "Company B"
            }
        ]
    }
    relationships = market_analyzer._detect_relationships(result)
    assert len(relationships) == 1
    assert relationships[0]["type"] == "COMPETES"
    assert relationships[0]["source"] == "Company A"
    assert relationships[0]["target"] == "Company B"


def test_detect_relationships_invalid_type(market_analyzer):
    """_detect_relationships()が不正な型のrelationshipsを処理できることをテスト。"""
    result = {"relationships": "invalid"}
    with pytest.raises(ValueError) as exc_info:
        market_analyzer._detect_relationships(result)
    assert "リスト形式ではありません" in str(exc_info.value)


def test_detect_relationships_missing_fields(market_analyzer):
    """_detect_relationships()が必須フィールドの欠けたrelationshipsを処理できることをテスト。"""
    result = {"relationships": [{"type": "COMPETES"}]}
    with pytest.raises(ValueError) as exc_info:
        market_analyzer._detect_relationships(result)
    assert "必須フィールドが欠けています" in str(exc_info.value)


def test_calculate_impact_score_success(market_analyzer):
    """_calculate_impact_score()が正常に動作することをテスト。"""
    result = {
        "market_impact": 0.8,
        "trends": [],
        "entities": [],
        "relationships": []
    }
    impact = market_analyzer._calculate_impact_score(result)
    assert impact == 0.8


def test_calculate_impact_score_invalid_type(market_analyzer):
    """_calculate_impact_score()が不正な型のimpact_scoreを処理できることをテスト。"""
    result = {
        "market_impact": "invalid",
        "trends": [],
        "entities": [],
        "relationships": []
    }
    with pytest.raises(ValueError) as exc_info:
        market_analyzer._calculate_impact_score(result)
    assert "market_impactが数値ではありません" in str(exc_info.value)


def test_calculate_impact_score_out_of_range(market_analyzer):
    """_calculate_impact_score()が範囲外のimpact_scoreを処理できることをテスト。"""
    result = {
        "market_impact": 1.5,
        "trends": [],
        "entities": [],
        "relationships": []
    }
    with pytest.raises(ValueError) as exc_info:
        market_analyzer._calculate_impact_score(result)
    assert "market_impactは0から1の範囲である必要があります" in str(exc_info.value)


def test_validate_score_type_success(market_analyzer):
    """_validate_score_type()が正常に動作することをテスト。"""
    assert market_analyzer._validate_score_type(0.5) == 0.5
    assert market_analyzer._validate_score_type("0.5") == 0.5
    assert market_analyzer._validate_score_type({"market_impact": 0.5}) == 0.5


def test_validate_score_range_success(market_analyzer):
    """_validate_score_range()が正常に動作することをテスト。"""
    market_analyzer._validate_score_range(0.0)
    market_analyzer._validate_score_range(0.5)
    market_analyzer._validate_score_range(1.0)


def test_validate_score_range_error(market_analyzer):
    """_validate_score_range()が範囲外の値を適切に処理できることをテスト。"""
    with pytest.raises(ValueError) as exc_info:
        market_analyzer._validate_score_range(1.5)
    assert "market_impactは0から1の範囲である必要があります" in str(exc_info.value) 