"""エンドツーエンドテストモジュール"""

import os
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from app.content_fetcher import ContentFetcher
from app.content_parser import ContentParser
from app.exceptions import ContentFetchError, ContentParseError, DatabaseError
from app.gemini_analyzer import GeminiAnalyzer
from app.market_analyzer import MarketAnalyzer
from app.neo4j_manager import Neo4jManager


class TestEndToEnd(unittest.TestCase):
    """エンドツーエンドテスト"""

    def setUp(self):
        """テストの前準備"""
        # 環境変数の確認
        required_vars = {
            'NEO4J_USER': os.getenv('neo4j_user'),
            'NEO4J_PASSWORD': os.getenv('neo4j_pswd'),
            'NEO4J_URI': os.getenv('neo4j_uri', 'bolt://neo4j:7687'),
            'GOOGLE_API_KEY_GEMINI': os.getenv('GOOGLE_API_KEY_GEMINI')
        }

        missing_vars = [key for key, value in required_vars.items() if not value]
        if missing_vars:
            self.skipTest(f"Missing required environment variables: {', '.join(missing_vars)}")

        # コンポーネントの初期化
        self.content_fetcher = ContentFetcher()
        self.content_parser = ContentParser()
        self.gemini_analyzer = GeminiAnalyzer(api_key=required_vars['GOOGLE_API_KEY_GEMINI'])
        self.neo4j_manager = Neo4jManager(
            uri=required_vars['NEO4J_URI'],
            username=required_vars['NEO4J_USER'],
            password=required_vars['NEO4J_PASSWORD']
        )
        self.market_analyzer = MarketAnalyzer(
            neo4j_manager=self.neo4j_manager,
            gemini_analyzer=self.gemini_analyzer
        )

        # 実際のニュースサイトのURL
        self.test_urls = [
            'https://www.reuters.com/technology/',
            'https://www.bloomberg.com/technology',
            'https://techcrunch.com/'
        ]

    def tearDown(self):
        """テストの後片付け"""
        try:
            # テストで作成したデータを削除
            self.neo4j_manager.execute_query("""
                MATCH (n)
                WHERE n.source = 'test'
                DETACH DELETE n
            """)
        finally:
            self.neo4j_manager.close()

    def test_full_workflow(self):
        """完全なワークフローのテスト"""
        try:
            # 1. コンテンツの取得と解析
            html_content = self.content_fetcher.fetch_content(self.test_urls[0])
            self.assertIsNotNone(html_content)
            
            parsed_content = self.content_parser.parse_html(html_content)
            self.assertIsInstance(parsed_content, dict)
            self.assertIn('title', parsed_content)
            self.assertIn('content', parsed_content)

            # 2. Geminiによる分析
            gemini_result = self.gemini_analyzer.analyze_content(parsed_content)
            self.assertIsInstance(gemini_result, dict)
            self.assertIn('market_impact', gemini_result)
            self.assertIn('trends', gemini_result)
            self.assertIn('entities', gemini_result)
            self.assertIn('relationships', gemini_result)

            # 3. 市場分析
            market_result = self.market_analyzer.analyze(parsed_content, gemini_result)
            self.assertIsInstance(market_result, dict)
            self.assertIn('entities', market_result)
            self.assertIn('relationships', market_result)
            self.assertIn('impact_scores', market_result)
            self.assertIn('trends', market_result)

            # 4. 分析結果の保存と検証
            analysis_data = {
                'entities': market_result['entities'],
                'relationships': market_result['relationships'],
                'impact_scores': market_result['impact_scores'],
                'source_url': self.test_urls[0],
                'analyzed_at': datetime.now().isoformat()
            }
            success = self.neo4j_manager.store_analysis(analysis_data)
            self.assertTrue(success)

            # 保存したデータの検証
            stored_data = self.neo4j_manager.get_analysis_by_url(self.test_urls[0])
            self.assertIsNotNone(stored_data)
            self.assertEqual(len(stored_data['entities']), len(market_result['entities']))

        except Exception as e:
            self.fail(f"Workflow test failed: {str(e)}")

    def test_error_recovery(self):
        """エラー回復のテスト"""
        try:
            # 1. 存在しないURLでのエラー処理
            invalid_url = 'https://www.reuters.com/nonexistent-page/'
            with self.assertRaises(ContentFetchError):
                self.content_fetcher.fetch_content(invalid_url)

            # 2. 正常なURLでの処理を確認（回復確認）
            html_content = self.content_fetcher.fetch_content(self.test_urls[0])
            self.assertIsNotNone(html_content)

            # 3. 不正なHTMLでのエラー処理
            with self.assertRaises(ContentParseError):
                self.content_parser.parse_html("<invalid>html")

            # 4. 正常なHTMLでの処理を確認（回復確認）
            parsed_content = self.content_parser.parse_html(html_content)
            self.assertIsInstance(parsed_content, dict)

            # 5. データベースエラーからの回復
            with self.assertRaises(DatabaseError):
                self.neo4j_manager.execute_query("INVALID QUERY")

            # 6. 正常なクエリでの処理を確認（回復確認）
            result = self.neo4j_manager.execute_query("MATCH (n) RETURN count(n) as count")
            self.assertIsNotNone(result)

        except Exception as e:
            self.fail(f"Error recovery test failed: {str(e)}")

    def test_concurrent_workflow(self):
        """並行ワークフローのテスト"""
        def process_url(url):
            try:
                # 1. コンテンツ取得
                html_content = self.content_fetcher.fetch_content(url)
                
                # 2. コンテンツ解析
                parsed_content = self.content_parser.parse_html(html_content)
                
                # 3. Gemini分析
                gemini_result = self.gemini_analyzer.analyze_content(parsed_content)
                
                # 4. 市場分析
                market_result = self.market_analyzer.analyze(parsed_content, gemini_result)
                
                # 5. 結果保存
                analysis_data = {
                    'entities': market_result['entities'],
                    'relationships': market_result['relationships'],
                    'impact_scores': market_result['impact_scores'],
                    'source_url': url,
                    'analyzed_at': datetime.now().isoformat()
                }
                success = self.neo4j_manager.store_analysis(analysis_data)
                
                return success, url, None

            except Exception as e:
                return False, url, str(e)

        try:
            results = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_url = {
                    executor.submit(process_url, url): url 
                    for url in self.test_urls
                }
                
                for future in as_completed(future_to_url):
                    success, url, error = future.result()
                    results.append({
                        'url': url,
                        'success': success,
                        'error': error
                    })

            # 結果の検証
            self.assertEqual(len(results), len(self.test_urls))
            successful_results = [r for r in results if r['success']]
            self.assertGreater(len(successful_results), 0)

            # 保存されたデータの検証
            for result in successful_results:
                stored_data = self.neo4j_manager.get_analysis_by_url(result['url'])
                self.assertIsNotNone(stored_data)
                self.assertIn('entities', stored_data)
                self.assertIn('relationships', stored_data)

        except Exception as e:
            self.fail(f"Concurrent workflow test failed: {str(e)}")


if __name__ == '__main__':
    unittest.main() 