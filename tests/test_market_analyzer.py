"""MarketAnalyzerのテストモジュール。"""

import pytest
from app.market_analyzer import MarketAnalyzer

@pytest.fixture
def analyzer():
    """MarketAnalyzerのインスタンスを生成するフィクスチャ。"""
    return MarketAnalyzer()

@pytest.fixture
def sample_gemini_result():
    """テスト用のGemini解析結果を生成するフィクスチャ。"""
    return {
        "impact_score": 0.8,
        "entities": [
            {
                "name": "テスト企業",
                "type": "COMPANY",
                "description": "テスト企業の説明"
            },
            {
                "name": "テスト製品",
                "type": "PRODUCT",
                "description": "テスト製品の説明"
            }
        ],
        "relationships": [
            {
                "source": "テスト企業",
                "target": "競合企業",
                "type": "COMPETES",
                "description": "市場で競合している"
            }
        ],
        "trends": ["トレンド1", "トレンド2"]
    }

def test_process_gemini_output_success(analyzer, sample_gemini_result):
    """process_gemini_output()が正常に動作することをテスト。"""
    result = analyzer.process_gemini_output(sample_gemini_result)
    assert len(result["entities"]) == 2
    assert len(result["relationships"]) == 1
    assert result["impact"] == 0.8
    assert len(result["trends"]) == 2

def test_process_gemini_output_invalid_input(analyzer):
    """process_gemini_output()が不正な入力を適切に処理できることをテスト。"""
    with pytest.raises(ValueError) as exc_info:
        analyzer.process_gemini_output("invalid")
    assert "辞書形式ではありません" in str(exc_info.value)

def test_extract_entities_success(analyzer, sample_gemini_result):
    """_extract_entities()が正常に動作することをテスト。"""
    entities = analyzer._extract_entities(sample_gemini_result)
    assert len(entities) == 2
    assert entities[0]["name"] == "テスト企業"
    assert entities[0]["type"] == "COMPANY"
    assert entities[1]["name"] == "テスト製品"
    assert entities[1]["type"] == "PRODUCT"

def test_extract_entities_invalid_type(analyzer):
    """_extract_entities()が不正なエンティティタイプを適切に処理できることをテスト。"""
    result = {
        "entities": [
            {
                "name": "テスト",
                "type": "INVALID_TYPE",
                "description": "説明"
            }
        ]
    }
    entities = analyzer._extract_entities(result)
    assert len(entities) == 0

def test_extract_entities_missing_fields(analyzer):
    """_extract_entities()が必須フィールド欠落を適切に処理できることをテスト。"""
    result = {
        "entities": [
            {
                "name": "テスト"  # descriptionとtypeが欠落
            }
        ]
    }
    entities = analyzer._extract_entities(result)
    assert len(entities) == 0

def test_detect_relationships_success(analyzer, sample_gemini_result):
    """_detect_relationships()が正常に動作することをテスト。"""
    relationships = analyzer._detect_relationships(sample_gemini_result)
    assert len(relationships) == 1
    assert relationships[0]["source"] == "テスト企業"
    assert relationships[0]["target"] == "競合企業"
    assert relationships[0]["type"] == "COMPETES"

def test_detect_relationships_invalid_type(analyzer):
    """_detect_relationships()が不正な関係タイプを適切に処理できることをテスト。"""
    result = {
        "relationships": [
            {
                "source": "A",
                "target": "B",
                "type": "INVALID_TYPE",
                "description": "説明"
            }
        ]
    }
    relationships = analyzer._detect_relationships(result)
    assert len(relationships) == 0

def test_detect_relationships_missing_fields(analyzer):
    """_detect_relationships()が必須フィールド欠落を適切に処理できることをテスト。"""
    result = {
        "relationships": [
            {
                "source": "A",
                "target": "B"  # typeとdescriptionが欠落
            }
        ]
    }
    relationships = analyzer._detect_relationships(result)
    assert len(relationships) == 0

def test_calculate_impact_score_success(analyzer, sample_gemini_result):
    """_calculate_impact_score()が正常に動作することをテスト。"""
    impact = analyzer._calculate_impact_score(sample_gemini_result)
    assert impact == 0.8

def test_calculate_impact_score_invalid_type(analyzer):
    """_calculate_impact_score()が不正なスコアタイプを適切に処理できることをテスト。"""
    result = {"impact_score": "invalid"}
    with pytest.raises(ValueError) as exc_info:
        analyzer._calculate_impact_score(result)
    assert "数値ではありません" in str(exc_info.value)

def test_calculate_impact_score_out_of_range(analyzer):
    """_calculate_impact_score()が範囲外のスコアを適切に処理できることをテスト。"""
    result = {"impact_score": 1.5}
    with pytest.raises(ValueError) as exc_info:
        analyzer._calculate_impact_score(result)
    assert "範囲外です" in str(exc_info.value) 