"""MarketAnalyzerのテストモジュール"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from app.market_analyzer import MarketAnalyzer


class TestMarketAnalyzer(unittest.TestCase):
    """MarketAnalyzerクラスのテストケース"""

    def setUp(self):
        """テストの前準備"""
        self.analyzer = MarketAnalyzer()
        self.sample_data = {
            'title': 'テストニュース',
            'content': 'AIによる市場分析の進展について',
            'url': 'https://example.com/news/1',
            'published_at': '2024-01-01T00:00:00'
        }
        self.sample_entities = [
            {
                'id': 'entity_0',
                'name': 'AI企業X',
                'type': 'COMPANY',
                'description': 'AI技術を開発する企業',
                'properties': {
                    'importance': 0.8,
                    'category': 'Technology',
                    'source': 'news'
                }
            },
            {
                'id': 'entity_1',
                'name': '市場分析ツール',
                'type': 'PRODUCT',
                'description': 'AIを活用した市場分析ツール',
                'properties': {
                    'importance': 0.6,
                    'category': 'Software',
                    'source': 'news'
                }
            }
        ]
        self.sample_relationships = [
            {
                'source': 'entity_0',
                'target': 'entity_1',
                'type': 'DEVELOPS',
                'strength': 0.7,
                'description': '開発関係'
            }
        ]
        self.sample_trends = ['AI市場分析', 'デジタルトランスフォーメーション']

    def test_analyze(self):
        """analyze メソッドのテスト"""
        with patch.object(self.analyzer.gemini, 'analyze_content') as mock_analyze:
            # モックの戻り値を設定
            mock_analyze.return_value = {
                'entities': self.sample_entities,
                'relationships': self.sample_relationships,
                'trends': self.sample_trends,
                'market_impact': 0.7,
                'technology_impact': 0.8,
                'social_impact': 0.6
            }

            # 分析を実行
            result = self.analyzer.analyze(self.sample_data)

            # 結果の検証
            self.assertIsInstance(result, dict)
            self.assertIn('entities', result)
            self.assertIn('relationships', result)
            self.assertIn('impact_scores', result)
            self.assertIn('trends', result)
            self.assertEqual(result['source_url'], self.sample_data['url'])
            self.assertTrue(isinstance(result['analyzed_at'], str))

    def test_calculate_trend_factor(self):
        """_calculate_trend_factor メソッドのテスト"""
        trend = 'AI市場分析'
        factor = self.analyzer._calculate_trend_factor(
            trend,
            self.sample_entities,
            self.sample_relationships
        )
        self.assertIsInstance(factor, float)
        self.assertGreaterEqual(factor, 0.0)
        self.assertLessEqual(factor, 1.0)

    def test_calculate_company_factor(self):
        """_calculate_company_factor メソッドのテスト"""
        trend = 'AI'
        factor = self.analyzer._calculate_company_factor(
            trend,
            self.sample_entities
        )
        self.assertIsInstance(factor, float)
        self.assertGreaterEqual(factor, 0.0)
        self.assertLessEqual(factor, 1.0)

    def test_calculate_market_factor(self):
        """_calculate_market_factor メソッドのテスト"""
        trend = 'AI市場分析'
        factor = self.analyzer._calculate_market_factor(
            trend,
            self.sample_relationships
        )
        self.assertIsInstance(factor, float)
        self.assertGreaterEqual(factor, 0.0)
        self.assertLessEqual(factor, 1.0)

    def test_find_related_entities(self):
        """_find_related_entities メソッドのテスト"""
        trend = 'AI'
        related = self.analyzer._find_related_entities(
            trend,
            self.sample_entities
        )
        self.assertIsInstance(related, list)
        self.assertTrue(all(isinstance(id_, str) for id_ in related))
        self.assertGreater(len(related), 0)

    def test_calculate_market_impact(self):
        """_calculate_market_impact メソッドのテスト"""
        trend = 'AI市場分析'
        impact = self.analyzer._calculate_market_impact(
            trend,
            self.sample_entities,
            self.sample_relationships
        )
        self.assertIsInstance(impact, float)
        self.assertGreaterEqual(impact, 0.0)
        self.assertLessEqual(impact, 1.0)

    def test_calculate_impact_scores(self):
        """_calculate_impact_scores メソッドのテスト"""
        output = {
            'market_impact': 0.7,
            'technology_impact': 0.8,
            'social_impact': 0.6
        }
        trends = [
            {
                'name': 'AI市場分析',
                'importance': 0.8
            }
        ]
        scores = self.analyzer._calculate_impact_scores(
            output,
            self.sample_entities,
            self.sample_relationships,
            trends
        )
        self.assertIsInstance(scores, dict)
        self.assertIn('market_impact', scores)
        self.assertIn('technology_impact', scores)
        self.assertIn('social_impact', scores)
        for score in scores.values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    def test_calculate_impact_score_with_invalid_input(self):
        """_calculate_impact_score メソッドの無効な入力のテスト"""
        # 文字列の場合
        self.assertEqual(self.analyzer._calculate_impact_score('invalid'), 0.5)
        # Noneの場合
        self.assertEqual(self.analyzer._calculate_impact_score(None), 0.5)
        # 範囲外の値の場合
        self.assertEqual(self.analyzer._calculate_impact_score(1.5), 1.0)
        self.assertEqual(self.analyzer._calculate_impact_score(-0.5), 0.0)

    def test_analyze_with_invalid_input(self):
        """analyze メソッドの無効な入力のテスト"""
        invalid_data = {
            'title': 'テスト',
            # 必須フィールドの欠落
        }
        with self.assertRaises(Exception):
            self.analyzer.analyze(invalid_data)

    def test_process_gemini_output_with_invalid_input(self):
        """process_gemini_output メソッドの無効な入力のテスト"""
        # 辞書以外の入力
        with self.assertRaises(ValueError):
            self.analyzer.process_gemini_output([])
        
        # 必須フィールドが欠落した辞書
        with self.assertRaises(Exception):
            self.analyzer.process_gemini_output({})


if __name__ == '__main__':
    unittest.main() 