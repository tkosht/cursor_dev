"""MarketAnalyzerのテストモジュール。"""

from datetime import datetime

import pytest

from app.market_analyzer import MarketAnalyzer


def test_init():
    """初期化のテスト。"""
    analyzer = MarketAnalyzer()
    assert hasattr(analyzer, 'gemini')
    assert hasattr(analyzer, 'logger')


def test_analyze_with_valid_input():
    """有効な入力での解析テスト。"""
    analyzer = MarketAnalyzer()
    data = {
        'title': 'テスト記事',
        'content': 'これはテストコンテンツです。市場分析に関する情報が含まれています。',
        'url': 'https://example.com/test',
        'published_at': datetime.now().isoformat()
    }
    
    result = analyzer.analyze(data)
    
    # 必須フィールドの存在確認
    assert 'entities' in result
    assert 'relationships' in result
    assert 'impact_scores' in result
    assert 'trends' in result
    assert 'source_url' in result
    assert 'analyzed_at' in result
    
    # 値の型と範囲の確認
    assert isinstance(result['entities'], list)
    assert isinstance(result['relationships'], list)
    assert isinstance(result['impact_scores'], dict)
    assert isinstance(result['trends'], list)
    assert isinstance(result['source_url'], str)
    assert isinstance(result['analyzed_at'], str)
    
    # impact_scoresの内容確認
    assert 'market_impact' in result['impact_scores']
    assert 'technology_impact' in result['impact_scores']
    assert 'social_impact' in result['impact_scores']
    assert all(0 <= score <= 1 for score in result['impact_scores'].values())


def test_analyze_with_invalid_input():
    """不正な入力での解析テスト。"""
    analyzer = MarketAnalyzer()
    invalid_data = {'invalid': 'data'}
    
    with pytest.raises(ValueError):
        analyzer.analyze(invalid_data)


def test_process_gemini_output_with_valid_data():
    """有効なGemini出力の処理テスト。"""
    analyzer = MarketAnalyzer()
    valid_output = {
        'entities': [
            {'name': 'Company1', 'type': 'COMPANY', 'description': 'desc1'},
            {'name': 'Product1', 'type': 'PRODUCT', 'description': 'desc2'}
        ],
        'relationships': [
            {
                'type': 'PRODUCES',
                'source': 'Company1',
                'target': 'Product1',
                'description': 'production'
            }
        ],
        'market_impact': 0.8,
        'technology_impact': 0.7,
        'social_impact': 0.6,
        'trends': ['trend1', 'trend2']
    }
    
    result = analyzer.process_gemini_output(valid_output)
    
    assert len(result['entities']) == 2
    assert len(result['relationships']) == 1
    assert result['impact_scores']['market_impact'] == 0.8
    assert len(result['trends']) == 2


def test_process_gemini_output_with_invalid_data():
    """不正なGemini出力の処理テスト。"""
    analyzer = MarketAnalyzer()
    invalid_output = "invalid"
    
    with pytest.raises(ValueError) as exc_info:
        analyzer.process_gemini_output(invalid_output)
    assert "辞書形式ではありません" in str(exc_info.value)


def test_extract_entities_with_valid_data():
    """有効なエンティティデータの抽出テスト。"""
    analyzer = MarketAnalyzer()
    valid_entities = [
        {'name': 'Company1', 'type': 'company', 'description': 'desc1'},
        {'name': 'Product1', 'type': 'product', 'description': 'desc2'}
    ]
    
    result = analyzer._extract_entities(valid_entities)
    
    assert len(result) == 2
    assert result[0]['type'] == 'COMPANY'  # 大文字に変換されていることを確認
    assert 'description' in result[0]
    assert 'properties' in result[0]


def test_extract_entities_with_invalid_data():
    """不正なエンティティデータの抽出テスト。"""
    analyzer = MarketAnalyzer()
    invalid_entities = [{'invalid': 'data'}]
    
    result = analyzer._extract_entities(invalid_entities)
    assert len(result) == 0


def test_detect_relationships_with_valid_data():
    """有効なリレーションシップデータの検出テスト。"""
    analyzer = MarketAnalyzer()
    valid_relationships = [
        {
            'type': 'influences',
            'source': 'Company1',
            'target': 'Market1',
            'description': 'strong influence'
        }
    ]
    name_to_id = {
        'Company1': 'entity_0',
        'Market1': 'entity_1'
    }

    result = analyzer._detect_relationships(valid_relationships, name_to_id)

    assert len(result) == 1
    assert result[0]['type'] == 'INFLUENCES'
    assert result[0]['source'] == 'entity_0'
    assert result[0]['target'] == 'entity_1'
    assert 'description' in result[0]
    assert 'timestamp' in result[0]


def test_detect_relationships_with_invalid_data():
    """不正なリレーションシップデータの検出テスト。"""
    analyzer = MarketAnalyzer()
    invalid_relationships = [{'invalid': 'data'}]
    name_to_id = {}

    result = analyzer._detect_relationships(invalid_relationships, name_to_id)
    assert len(result) == 0


def test_calculate_impact_score_with_valid_data():
    """有効な影響度スコアの計算テスト。"""
    analyzer = MarketAnalyzer()

    assert analyzer._calculate_impact_score(0.5) == 0.5
    assert round(analyzer._calculate_impact_score("0.7"), 1) == 0.7
    assert analyzer._calculate_impact_score(1.0) == 1.0
    assert analyzer._calculate_impact_score(0.0) == 0.0 