"""統合テストモジュール"""

import os
from datetime import datetime
from pathlib import Path

import pytest
from dotenv import load_dotenv

from app.content_fetcher import ContentFetcher
from app.content_parser import ContentParser
from app.gemini_analyzer import GeminiAnalyzer
from app.knowledge_repository import KnowledgeRepository
from app.market_analyzer import MarketAnalyzer
from app.neo4j_manager import Neo4jManager


@pytest.fixture(scope="session", autouse=True)
def setup_env():
    """テスト用の環境変数を設定するフィクスチャ"""
    # .env.testファイルを読み込む
    env_path = Path(__file__).parent.parent / '.env.test'
    if not env_path.exists():
        pytest.fail(".env.testファイルが見つかりません。テスト用の環境変数を設定してください。")
    
    load_dotenv(env_path)
    
    # 必須の環境変数をチェック
    required_vars = ['neo4j_user', 'neo4j_pswd', 'GOOGLE_API_KEY_GEMINI']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        pytest.fail(f"必須の環境変数が設定されていません: {', '.join(missing_vars)}")
    
    yield


def test_full_workflow():
    """エンドツーエンドの統合テスト
    
    以下のフローをテスト:
    1. HTMLコンテンツの取得
    2. コンテンツの解析
    3. Geminiによる分析
    4. 市場分析の実行
    5. Neo4jへの結果保存
    """
    try:
        # テスト用HTMLファイルの読み込み
        content_fetcher = ContentFetcher()
        html_content = content_fetcher.fetch_from_file('tests/data/sample.html')
        
        # HTMLの解析
        content_parser = ContentParser()
        parsed_content = content_parser.parse_html(html_content)
        assert parsed_content['title'], "タイトルの抽出に失敗しました"
        assert parsed_content['content'], "本文の抽出に失敗しました"
        
        # Geminiによる分析
        gemini = GeminiAnalyzer()
        gemini_result = gemini.analyze_content(parsed_content)
        assert isinstance(gemini_result, dict), "Gemini分析結果が不正な形式です"
        
        # 市場分析
        analyzer = MarketAnalyzer()
        market_result = analyzer.process_gemini_output(gemini_result)
        
        # 結果の検証
        assert isinstance(market_result, dict), "市場分析結果が不正な形式です"
        assert 'entities' in market_result, "分析結果にentitiesが含まれていません"
        assert 'relationships' in market_result, "分析結果にrelationshipsが含まれていません"
        assert 'impact_scores' in market_result, "分析結果にimpact_scoresが含まれていません"
        
        # Neo4jへの保存
        neo4j = Neo4jManager()
        repo = KnowledgeRepository(neo4j)
        
        try:
            success = repo.store_analysis({
                'entities': market_result['entities'],
                'relationships': market_result['relationships'],
                'impact_scores': market_result['impact_scores'],
                'source_url': parsed_content['url'],
                'analyzed_at': datetime.now().isoformat()
            })
            assert success, "分析結果の保存に失敗しました"
            
        finally:
            neo4j.close()
            
    except Exception as e:
        pytest.fail(f"統合テストが失敗しました: {str(e)}")


@pytest.mark.integration
def test_neo4j_connection():
    """Neo4jとの実接続テスト"""
    neo4j = None
    try:
        neo4j = Neo4jManager()
        
        # テストノードの作成
        test_node = {
            "name": "Test Entity",
            "type": "TEST",
            "description": "Test node for connection verification",
            "created_at": datetime.now().isoformat()
        }
        
        # ノードの作成
        node_id = neo4j.create_node(
            labels=["TestNode"],
            properties=test_node
        )
        assert node_id is not None, "ノードの作成に失敗しました"
        
        # ノードの検索
        found_node = neo4j.find_node(
            labels=["TestNode"],
            properties={"name": "Test Entity"}
        )
        assert found_node is not None, "作成したノードが見つかりません"
        assert found_node["type"] == "TEST", "ノードのプロパティが正しくありません"
        
    except Exception as e:
        pytest.fail(f"Neo4j接続テストが失敗しました: {str(e)}")
    
    finally:
        if neo4j:
            neo4j.close()


@pytest.mark.integration
def test_gemini_connection():
    """Gemini APIとの実接続テスト"""
    try:
        gemini = GeminiAnalyzer()
        
        # テストコンテンツの作成
        test_content = {
            "title": "AI Market Analysis",
            "content": """
            Recent developments in artificial intelligence have shown significant 
            market impact. Companies like OpenAI and Google are leading the way 
            in AI innovation, while Microsoft and Amazon are integrating AI 
            capabilities into their cloud services.
            """,
            "url": "https://example.com/ai-market-analysis",
            "published_at": datetime.now().isoformat()
        }
        
        # 分析実行
        result = gemini.analyze_content(test_content)
        
        # 結果の検証
        assert result is not None, "Gemini APIからのレスポンスが空です"
        assert isinstance(result, dict), "Gemini APIの結果が不正な形式です"
        assert 'market_impact' in result, "市場影響度が含まれていません"
        assert 'entities' in result, "エンティティ情報が含まれていません"
        assert 'relationships' in result, "関係性情報が含まれていません"
        
        # 市場影響度の検証
        assert 0 <= result['market_impact'] <= 1, "市場影響度が0-1の範囲外です"
        
        # エンティティの検証
        assert len(result['entities']) > 0, "エンティティが抽出されていません"
        for entity in result['entities']:
            assert 'name' in entity, "エンティティ名が含まれていません"
            assert 'type' in entity, "エンティティタイプが含まれていません"
        
    except Exception as e:
        pytest.fail(f"Gemini API接続テストが失敗しました: {str(e)}") 