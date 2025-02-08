"""パフォーマンステストモジュール。"""

from unittest.mock import MagicMock

import pytest

from app.content_parser import ContentParser
from app.gemini_analyzer import GeminiAnalyzer
from app.market_analyzer import MarketAnalyzer
from app.neo4j_manager import Neo4jManager
from app.performance_monitor import PerformanceMonitor


@pytest.fixture
def performance_monitor():
    """PerformanceMonitorのインスタンスを生成するフィクスチャ。"""
    return PerformanceMonitor()


@pytest.fixture
def neo4j_manager():
    """Neo4jManagerのモックを生成するフィクスチャ。"""
    manager = MagicMock(spec=Neo4jManager)
    manager.uri = "bolt://localhost:7687"
    manager.username = "neo4j"
    manager.password = "password"
    return manager


@pytest.fixture
def gemini_analyzer():
    """GeminiAnalyzerのモックを生成するフィクスチャ。"""
    analyzer = MagicMock(spec=GeminiAnalyzer)
    analyzer.api_key = "test_api_key"
    return analyzer


@pytest.fixture
def market_analyzer(neo4j_manager, gemini_analyzer):
    """MarketAnalyzerのインスタンスを生成するフィクスチャ。"""
    return MarketAnalyzer(neo4j_manager, gemini_analyzer)


class TestPerformance:
    """パフォーマンステストクラス。"""

    def test_content_parser_performance(self, performance_monitor):
        """ContentParserのパフォーマンスをテストする。"""
        parser = ContentParser()
        html = """
        <html>
            <head>
                <title>テストタイトル</title>
            </head>
            <body>
                <article>
                    <h1>記事タイトル</h1>
                    <p>これは本文です。</p>
                    <time datetime="2025-01-11">2025年1月11日</time>
                </article>
            </body>
        </html>
        """ * 100  # 大量のHTMLを生成

        # パフォーマンス計測開始
        performance_monitor.start_measurement("content_parser")

        # 100回パースを実行
        for _ in range(100):
            parser.parse_content(html)

        # パフォーマンス計測終了
        elapsed_time = performance_monitor.end_measurement("content_parser")

        # 平均処理時間を取得
        average_time = performance_monitor.get_average("content_parser")

        # 95パーセンタイル値を取得
        percentile_95 = performance_monitor.get_percentile("content_parser", 95)

        # 検証
        assert elapsed_time is not None
        assert average_time is not None
        assert percentile_95 is not None
        assert average_time < 0.1  # 平均処理時間が0.1秒未満
        assert percentile_95 < 0.2  # 95パーセンタイル値が0.2秒未満

    def test_market_analyzer_performance(self, market_analyzer, performance_monitor):
        """MarketAnalyzerのパフォーマンスをテストする。"""
        content = {
            "title": "テストタイトル",
            "content": "テストコンテンツ",
            "date": "2025-01-11",
            "url": "https://example.com"
        }

        # モックの設定
        market_analyzer.gemini_analyzer.analyze_content.return_value = {
            "entities": [
                {"id": "1", "name": "エンティティ1", "type": "TYPE1"}
            ],
            "relationships": [
                {"source": "1", "target": "2", "type": "RELATED_TO"}
            ],
            "impact_scores": {
                "1": 0.8,
                "2": 0.6
            }
        }

        # パフォーマンス計測開始
        performance_monitor.start_measurement("market_analyzer")

        # 100回分析を実行
        for _ in range(100):
            market_analyzer.analyze_content(content)

        # パフォーマンス計測終了
        elapsed_time = performance_monitor.end_measurement("market_analyzer")

        # 平均処理時間を取得
        average_time = performance_monitor.get_average("market_analyzer")

        # 95パーセンタイル値を取得
        percentile_95 = performance_monitor.get_percentile("market_analyzer", 95)

        # 検証
        assert elapsed_time is not None
        assert average_time is not None
        assert percentile_95 is not None
        assert average_time < 0.1  # 平均処理時間が0.1秒未満
        assert percentile_95 < 0.2  # 95パーセンタイル値が0.2秒未満

    def test_neo4j_performance(self, neo4j_manager, performance_monitor):
        """Neo4jManagerのパフォーマンスをテストする。"""
        # パフォーマンス計測開始
        performance_monitor.start_measurement("neo4j")

        # 100回クエリを実行
        for i in range(100):
            neo4j_manager.execute_query(
                f"CREATE (n:Test {{id: {i}}}) RETURN n"
            )

        # パフォーマンス計測終了
        elapsed_time = performance_monitor.end_measurement("neo4j")

        # 平均処理時間を取得
        average_time = performance_monitor.get_average("neo4j")

        # 95パーセンタイル値を取得
        percentile_95 = performance_monitor.get_percentile("neo4j", 95)

        # 検証
        assert elapsed_time is not None
        assert average_time is not None
        assert percentile_95 is not None
        assert average_time < 0.05  # 平均処理時間が0.05秒未満
        assert percentile_95 < 0.1  # 95パーセンタイル値が0.1秒未満

    def test_concurrent_operations_performance(self, neo4j_manager, performance_monitor):
        """並行処理のパフォーマンスをテストする。"""
        # パフォーマンス計測開始
        performance_monitor.start_measurement("concurrent")

        # 10個の並行処理を実行
        for i in range(10):
            # 各処理で10回のクエリを実行
            for j in range(10):
                neo4j_manager.execute_query(
                    f"CREATE (n:Test {{id: {i}_{j}}}) RETURN n"
                )

        # パフォーマンス計測終了
        elapsed_time = performance_monitor.end_measurement("concurrent")

        # 平均処理時間を取得
        average_time = performance_monitor.get_average("concurrent")

        # 95パーセンタイル値を取得
        percentile_95 = performance_monitor.get_percentile("concurrent", 95)

        # 検証
        assert elapsed_time is not None
        assert average_time is not None
        assert percentile_95 is not None
        assert average_time < 0.5  # 平均処理時間が0.5秒未満
        assert percentile_95 < 1.0  # 95パーセンタイル値が1.0秒未満 