"""MarketAnalyzerのテストモジュール。"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from app.exceptions import MarketAnalysisError, ValidationError
from app.gemini_analyzer import GeminiAnalyzer
from app.market_analyzer import MarketAnalyzer
from app.neo4j_manager import Neo4jManager


class TestMarketAnalyzer(unittest.TestCase):
    """MarketAnalyzerのテストクラス。"""

    def setUp(self):
        """テストの前準備。"""
        self.neo4j_manager = MagicMock(spec=Neo4jManager)
        self.gemini_analyzer = MagicMock(spec=GeminiAnalyzer)
        self.analyzer = MarketAnalyzer(
            neo4j_manager=self.neo4j_manager,
            gemini_analyzer=self.gemini_analyzer
        )

    def test_init_validation(self):
        """初期化時の引数検証をテスト。"""
        with self.assertRaises(ValidationError):
            MarketAnalyzer(neo4j_manager=None, gemini_analyzer=self.gemini_analyzer)
        
        with self.assertRaises(ValidationError):
            MarketAnalyzer(neo4j_manager=self.neo4j_manager, gemini_analyzer=None)

    def test_analyze_content_success(self):
        """コンテンツ分析が成功することを確認。"""
        # モックの設定
        content = "テスト用コンテンツ"
        analysis_result = {
            'entities': ['企業A', '製品X'],
            'relationships': ['企業Aが製品Xを発表']
        }
        self.gemini_analyzer.analyze_content.return_value = analysis_result
        self.neo4j_manager.create_content_node.return_value = "content-123"
        self.neo4j_manager.create_entity_node.side_effect = ["entity-1", "entity-2"]
        self.neo4j_manager.create_relationship.return_value = "rel-1"

        # テスト実行
        result = self.analyzer.analyze_content(content)

        # 検証
        self.assertIsInstance(result, dict)
        self.assertEqual(result['content_id'], "content-123")
        self.assertEqual(result['entities'], ['企業A', '製品X'])
        self.assertEqual(result['relationships'], ['企業Aが製品Xを発表'])

    def test_analyze_content_validation(self):
        """コンテンツのバリデーションをテスト。"""
        invalid_inputs = [None, "", 123, [], {}]
        for invalid_input in invalid_inputs:
            with self.assertRaises(ValidationError):
                self.analyzer.analyze_content(invalid_input)

    def test_get_market_trends(self):
        """市場トレンド取得をテスト。"""
        # モックの設定
        expected_trends = [
            {
                'title': 'トレンド1',
                'url': 'http://example.com/1',
                'published_at': '2025-01-01T00:00:00',
                'market_impact': 0.8
            }
        ]
        self.neo4j_manager.execute_query.return_value = expected_trends

        # テスト実行
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31)
        result = self.analyzer.get_market_trends(start_date, end_date)

        # 検証
        self.assertEqual(result, expected_trends)
        self.neo4j_manager.execute_query.assert_called_once()

    def test_get_entity_relationships(self):
        """エンティティ関係取得をテスト。"""
        # モックの設定
        expected_relationships = [
            {
                'source': '企業A',
                'target': '企業B',
                'type': 'COMPETES_WITH',
                'strength': 0.7
            }
        ]
        self.neo4j_manager.execute_query.return_value = expected_relationships

        # テスト実行
        result = self.analyzer.get_entity_relationships('企業A')

        # 検証
        self.assertEqual(result, expected_relationships)
        self.neo4j_manager.execute_query.assert_called_once()

    def test_get_metrics(self):
        """メトリクス取得をテスト。"""
        expected_metrics = {
            'entity_count': 10,
            'relationship_count': 5
        }
        self.analyzer._monitor.get_metrics.return_value = expected_metrics
        result = self.analyzer.get_metrics()
        self.assertEqual(result, expected_metrics)


if __name__ == '__main__':
    unittest.main() 