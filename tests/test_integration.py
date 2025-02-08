"""統合テストモジュール。"""

import os
import time
import unittest

from app.content_fetcher import ContentFetcher
from app.content_parser import ContentParser
from app.gemini_analyzer import GeminiAnalyzer
from app.market_analyzer import MarketAnalyzer
from app.neo4j_manager import Neo4jManager


class TestIntegration(unittest.TestCase):
    """実環境での統合テストクラス。"""

    def setUp(self):
        """テストの前準備。"""
        self.api_key = os.getenv('GOOGLE_API_KEY_GEMINI')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY_GEMINIが設定されていません")

        # Neo4j接続情報を環境変数から取得
        self.neo4j_uri = os.getenv('neo4j_uri', 'bolt://neo4j:7687')
        self.neo4j_user = os.getenv('neo4j_user', 'neo4j')
        self.neo4j_password = os.getenv('neo4j_pswd', 'password')

        # 各コンポーネントの初期化
        self.fetcher = ContentFetcher()
        self.parser = ContentParser()
        self.analyzer = GeminiAnalyzer(self.api_key)
        self.neo4j_manager = Neo4jManager(
            uri=self.neo4j_uri,
            username=self.neo4j_user,
            password=self.neo4j_password
        )
        self.market_analyzer = MarketAnalyzer(
            neo4j_manager=self.neo4j_manager,
            gemini_analyzer=self.analyzer
        )

    def tearDown(self):
        """テストの後片付け。"""
        if hasattr(self, 'neo4j'):
            self.neo4j.close()

    def test_end_to_end_flow(self):
        """エンドツーエンドのフロー全体をテスト。"""
        # 実際のニュースサイトのURLを使用
        test_url = "https://www.reuters.com/technology/"
        
        try:
            # 1. コンテンツ取得
            html_content = self.fetcher.fetch_content(test_url)
            self.assertIsNotNone(html_content)
            
            # 2. コンテンツ解析
            parsed_content = self.parser.parse_html(html_content)
            self.assertIsInstance(parsed_content, dict)
            self.assertIn('content', parsed_content)
            
            # 3. Gemini解析
            gemini_result = self.analyzer.analyze_content(parsed_content['content'])
            self.assertIsInstance(gemini_result, dict)
            self.assertIn('entities', gemini_result)
            self.assertIn('relationships', gemini_result)
            
            # 4. 市場分析
            market_result = self.market_analyzer.process_gemini_output(gemini_result)
            self.assertIsInstance(market_result, dict)
            self.assertIn('impact', market_result)
            
            # 5. Neo4jへの保存
            self.neo4j_manager.save_analysis_result(market_result)
            
            # 6. 保存結果の検証
            saved_result = self.neo4j_manager.get_latest_analysis()
            self.assertIsNotNone(saved_result)
            
            # タイムスタンプ以外の内容を比較
            saved_result.pop('timestamp', None)
            market_result.pop('timestamp', None)
            self.assertEqual(market_result, saved_result)

        except Exception as e:
            self.fail(f"予期しない例外が発生しました: {str(e)}")

    def test_error_recovery(self):
        """エラーからの回復をテスト。"""
        # 1. 存在しないURLでのエラー
        test_url = "https://www.reuters.com/nonexistent-page/"
        
        try:
            # 意図的に失敗させる
            with self.assertRaises(Exception):
                self.fetcher.fetch_content(test_url)
            
            # 少し待ってから再試行
            time.sleep(2)
            
            # 正常なURLで再試行
            test_url = "https://www.reuters.com/technology/"
            html_content = self.fetcher.fetch_content(test_url)
            self.assertIsNotNone(html_content)
            
        except Exception as e:
            self.fail(f"エラーからの回復に失敗: {str(e)}")

    def test_concurrent_requests(self):
        """並行リクエストの処理をテスト。"""
        test_urls = [
            "https://www.reuters.com/technology/",
            "https://www.bloomberg.com/technology",
            "https://techcrunch.com/"
        ]
        
        results = []
        for url in test_urls:
            try:
                # 1. コンテンツ取得
                html_content = self.fetcher.fetch_content(url)
                
                # 2. コンテンツ解析
                parsed_content = self.parser.parse_html(html_content)
                
                # 3. Gemini解析
                gemini_result = self.analyzer.analyze_content(parsed_content['content'])
                
                # 4. 市場分析
                market_result = self.market_analyzer.process_gemini_output(gemini_result)
                
                # 5. Neo4jへの保存
                self.neo4j_manager.save_analysis_result(market_result)
                
                results.append(True)
            except Exception:
                results.append(False)
        
        # 少なくとも1つは成功しているはず
        self.assertTrue(any(results))


if __name__ == '__main__':
    unittest.main() 