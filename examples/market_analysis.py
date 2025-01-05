import os
from datetime import datetime
from dotenv import load_dotenv

from app.content_fetcher import ContentFetcher
from app.content_parser import ContentParser
from app.gemini_analyzer import GeminiAnalyzer
from app.market_analyzer import MarketAnalyzer
from app.neo4j_manager import Neo4jManager
from app.knowledge_repository import KnowledgeRepository


def main():
    # 環境変数の読み込み
    load_dotenv()

    # 各コンポーネントの初期化
    content_fetcher = ContentFetcher(
        timeout=float(os.getenv("REQUEST_TIMEOUT", "30")),
        max_retries=int(os.getenv("MAX_RETRIES", "3"))
    )
    content_parser = ContentParser()
    gemini_analyzer = GeminiAnalyzer(api_key=os.getenv("GOOGLE_API_KEY_GEMINI"))
    market_analyzer = MarketAnalyzer()
    neo4j_manager = Neo4jManager(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    knowledge_repository = KnowledgeRepository(neo4j_manager)

    try:
        # サンプルURLからコンテンツを取得
        url = "https://example.com/market-news"  # 実際のニュース記事URLに置き換えてください
        html_content = content_fetcher.fetch_html(url)

        # HTMLをパース
        parsed_content = content_parser.parse_html(html_content)
        parsed_content['url'] = url

        # Geminiを使用して分析
        gemini_analysis = gemini_analyzer.analyze_content(parsed_content)

        # 市場分析の実行
        market_analysis = market_analyzer.process_gemini_output(gemini_analysis)

        # 分析結果をNeo4jに保存
        knowledge_repository.store_analysis({
            'entities': market_analysis['entities'],
            'relationships': market_analysis['relationships'],
            'impact_scores': market_analysis['impact_scores'],
            'source_url': url,
            'analyzed_at': datetime.now()
        })

        print("市場分析が完了しました。")
        print(f"エンティティ数: {len(market_analysis['entities'])}")
        print(f"関係性数: {len(market_analysis['relationships'])}")
        print("要約:", market_analysis.get('summary', '要約なし'))

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

    finally:
        # Neo4j接続のクローズ
        neo4j_manager.close()


if __name__ == "__main__":
    main() 