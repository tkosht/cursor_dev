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

    def test_extract_entities(self):
        """_extract_entities メソッドのテスト
        
        必要性：
        - エンティティ抽出の正確性確認
        - IDとプロパティの検証
        
        十分性：
        - 必須フィールドの存在確認
        - プロパティの型チェック
        - エンティティの一意性確認
        """
        raw_entities = [
            {
                'name': 'テスト企業A',
                'type': 'COMPANY',
                'description': 'テスト用企業A',
                'properties': {
                    'importance': 0.8,
                    'category': 'Test'
                }
            },
            {
                'name': 'テスト製品X',
                'type': 'PRODUCT',
                'description': 'テスト用製品X',
                'properties': {
                    'importance': 0.6,
                    'category': 'Test'
                }
            }
        ]
        
        result = self.analyzer._extract_entities(raw_entities)
        
        # 結果の検証
        self.assertEqual(len(result), 2)
        for entity in result:
            self.assertIn('id', entity)
            self.assertIn('name', entity)
            self.assertIn('type', entity)
            self.assertIn('description', entity)
            self.assertIn('properties', entity)
            self.assertIsInstance(entity['properties'], dict)
            self.assertIsInstance(entity['properties'].get('importance'), float)

    def test_extract_entities_with_invalid_input(self):
        """_extract_entities メソッドの無効な入力のテスト
        
        必要性：
        - エラー処理の確認
        - 無効なデータの除外確認
        
        十分性：
        - 必須フィールド欠落の処理
        - 無効な型の処理
        - エラーメッセージの確認
        """
        # 無効なエンティティを含むリスト
        invalid_entities = [
            {},  # 空辞書
            {'name': 'Invalid'},  # 必須フィールド欠落
            None,  # None
            {  # 無効な型のプロパティ
                'name': 'Test',
                'type': 'TEST',
                'description': 'Test',
                'properties': 'invalid'
            }
        ]
        
        result = self.analyzer._extract_entities(invalid_entities)
        self.assertEqual(len(result), 0)

    def test_detect_relationships(self):
        """_detect_relationships メソッドのテスト
        
        必要性：
        - リレーションシップ検出の正確性確認
        - IDマッピングの検証
        
        十分性：
        - 必須フィールドの存在確認
        - プロパティの型チェック
        - 関係の方向性確認
        """
        name_to_id = {
            'テスト企業A': 'entity_0',
            'テスト製品X': 'entity_1'
        }
        
        raw_relationships = [
            {
                'source': 'テスト企業A',
                'target': 'テスト製品X',
                'type': 'DEVELOPS',
                'strength': 0.7,
                'description': 'テスト用関係'
            }
        ]
        
        result = self.analyzer._detect_relationships(raw_relationships, name_to_id)
        
        # 結果の検証
        self.assertEqual(len(result), 1)
        rel = result[0]
        self.assertEqual(rel['source'], 'entity_0')
        self.assertEqual(rel['target'], 'entity_1')
        self.assertEqual(rel['type'], 'DEVELOPS')
        self.assertIsInstance(rel['strength'], float)
        self.assertIn('description', rel)

    def test_detect_relationships_with_invalid_input(self):
        """_detect_relationships メソッドの無効な入力のテスト
        
        必要性：
        - エラー処理の確認
        - 無効なデータの除外確認
        
        十分性：
        - 必須フィールド欠落の処理
        - 存在しないエンティティの処理
        - 無効な型の処理
        """
        name_to_id = {'テスト企業A': 'entity_0'}
        
        # 無効なリレーションシップを含むリスト
        invalid_relationships = [
            {},  # 空辞書
            {  # 必須フィールド欠落
                'source': 'テスト企業A'
            },
            None,  # None
            {  # 存在しないエンティティ
                'source': '存在しない企業',
                'target': 'テスト企業A',
                'type': 'TEST'
            },
            {  # 無効な型のプロパティ
                'source': 'テスト企業A',
                'target': 'テスト企業A',
                'type': 'TEST',
                'strength': 'invalid'
            }
        ]
        
        result = self.analyzer._detect_relationships(invalid_relationships, name_to_id)
        self.assertEqual(len(result), 0)

    def test_analyze_trends_detailed(self):
        """_analyze_trends メソッドの詳細テスト
        
        必要性：
        - トレンド分析の正確性確認
        - 重要度計算の検証
        - 関連エンティティの検出確認
        
        十分性：
        - 複数トレンドの処理
        - 重要度の順序確認
        - 関連情報の正確性
        """
        raw_trends = ['AI技術', 'デジタル化', '市場動向']
        entities = [
            {
                'id': 'entity_0',
                'name': 'AI企業X',
                'type': 'COMPANY',
                'description': 'AI技術を開発する企業',
                'properties': {'importance': 0.8}
            },
            {
                'id': 'entity_1',
                'name': 'デジタルソリューション',
                'type': 'PRODUCT',
                'description': 'デジタル化支援ツール',
                'properties': {'importance': 0.6}
            }
        ]
        relationships = [
            {
                'source': 'entity_0',
                'target': 'entity_1',
                'type': 'DEVELOPS',
                'strength': 0.7
            }
        ]
        
        result = self.analyzer._analyze_trends(raw_trends, entities, relationships)
        
        # 結果の検証
        self.assertEqual(len(result), 3)
        self.assertTrue(all(isinstance(trend, dict) for trend in result))
        self.assertTrue(all('importance' in trend for trend in result))
        self.assertTrue(all('related_entities' in trend for trend in result))
        self.assertTrue(all('market_impact' in trend for trend in result))
        
        # 重要度でソートされていることを確認
        importances = [trend['importance'] for trend in result]
        self.assertEqual(importances, sorted(importances, reverse=True))

    def test_analyze_trends_with_empty_input(self):
        """_analyze_trends メソッドの空入力テスト
        
        必要性：
        - エッジケースの処理確認
        - 空データの処理検証
        
        十分性：
        - 空リストの処理
        - デフォルト値の確認
        """
        result = self.analyzer._analyze_trends([], [], [])
        self.assertEqual(result, [])
        
        result = self.analyzer._analyze_trends(['テストトレンド'], [], [])
        self.assertEqual(len(result), 1)
        self.assertLessEqual(result[0]['importance'], 0.5)
        self.assertEqual(result[0]['related_entities'], [])

    def test_analyze_trends_with_invalid_input(self):
        """_analyze_trends メソッドの無効な入力テスト
        
        必要性：
        - エラー処理の確認
        - 無効データの処理検証
        
        十分性：
        - 無効な型の処理
        - エラー時のデフォルト値
        """
        # 無効なエンティティ
        invalid_entities = [{'invalid': 'data'}]
        # 無効なリレーションシップ
        invalid_relationships = [{'invalid': 'data'}]
        
        result = self.analyzer._analyze_trends(
            ['テストトレンド'],
            invalid_entities,
            invalid_relationships
        )
        
        self.assertEqual(len(result), 1)
        trend = result[0]
        self.assertEqual(trend['name'], 'テストトレンド')
        self.assertGreaterEqual(trend['importance'], 0.0)
        self.assertLessEqual(trend['importance'], 1.0)
        self.assertEqual(trend['related_entities'], [])
        self.assertEqual(trend['market_impact'], 0.0)

    def test_calculate_novelty_factor(self):
        """_calculate_novelty_factor メソッドのテスト
        
        必要性：
        - 新規性評価の確認
        - スコア計算の検証
        
        十分性：
        - 異なるトレンドの評価
        - スコア範囲の確認
        """
        # 新しいトレンド
        factor1 = self.analyzer._calculate_novelty_factor('新技術XYZ')
        self.assertGreaterEqual(factor1, 0.0)
        self.assertLessEqual(factor1, 1.0)
        
        # 一般的なトレンド
        factor2 = self.analyzer._calculate_novelty_factor('AI')
        self.assertGreaterEqual(factor2, 0.0)
        self.assertLessEqual(factor2, 1.0)
        
        # 空文字列
        factor3 = self.analyzer._calculate_novelty_factor('')
        self.assertEqual(factor3, 0.0)


if __name__ == '__main__':
    unittest.main() 