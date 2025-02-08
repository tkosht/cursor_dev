"""市場分析モジュール。"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.exceptions import MarketAnalysisError, ValidationError
from app.gemini_analyzer import GeminiAnalyzer
from app.monitoring import PerformanceMonitor
from app.neo4j_manager import Neo4jManager

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """市場分析クラス。"""

    def __init__(
        self,
        neo4j_manager: Neo4jManager,
        gemini_analyzer: GeminiAnalyzer
    ):
        """
        MarketAnalyzerを初期化する。

        Args:
            neo4j_manager (Neo4jManager): Neo4jデータベース管理オブジェクト
            gemini_analyzer (GeminiAnalyzer): Gemini API分析オブジェクト

        Raises:
            ValidationError: 引数が不正な場合
        """
        if not isinstance(neo4j_manager, Neo4jManager):
            logger.error("neo4j_managerはNeo4jManagerのインスタンスである必要があります")
            raise ValidationError("neo4j_managerはNeo4jManagerのインスタンスである必要があります")

        if not isinstance(gemini_analyzer, GeminiAnalyzer):
            logger.error("gemini_analyzerはGeminiAnalyzerのインスタンスである必要があります")
            raise ValidationError("gemini_analyzerはGeminiAnalyzerのインスタンスである必要があります")

        self.neo4j_manager = neo4j_manager
        self.gemini_analyzer = gemini_analyzer
        self._monitor = PerformanceMonitor()
        self._created_nodes = []
        self._created_relationships = []

    def analyze_content(self, content: str) -> Dict:
        """
        コンテンツを分析する。

        Args:
            content (str): 分析対象のコンテンツ

        Returns:
            Dict: 分析結果

        Raises:
            ValidationError: コンテンツが不正な場合
            DatabaseError: データベース操作に失敗した場合
        """
        if not content or not isinstance(content, str):
            logger.error("コンテンツが不正です")
            raise ValidationError("コンテンツが不正です")

        try:
            # Gemini APIを使用してコンテンツを解析
            analysis_result = self.gemini_analyzer.analyze_content(content)

            # コンテンツノードの作成
            content_node = self._create_content_node({
                'content': content,
                'created_at': datetime.now().isoformat()
            })

            # エンティティノードの作成
            entity_nodes = []
            for entity in analysis_result.get('entities', []):
                node_data = {
                    'name': entity,
                    'type': 'ENTITY',
                    'created_at': datetime.now().isoformat()
                }
                node_id = self.neo4j_manager.create_entity_node(node_data)
                entity_nodes.append({'id': node_id, **node_data})

            # リレーションシップの作成
            relationships = []
            for rel in analysis_result.get('relationships', []):
                rel_data = {
                    'description': rel,
                    'type': 'RELATES_TO',
                    'content_id': content_node['id'],
                    'created_at': datetime.now().isoformat()
                }
                rel_id = self.neo4j_manager.create_relationship(rel_data)
                relationships.append({'id': rel_id, **rel_data})

            return {
                'content_id': content_node['id'],
                'entities': [node['name'] for node in entity_nodes],
                'relationships': [rel['description'] for rel in relationships]
            }

        except Exception as e:
            logger.error(f"コンテンツの分析に失敗しました: {str(e)}")
            raise

    def _create_content_node(self, data: Dict) -> Dict:
        """
        コンテンツノードを作成する。

        Args:
            data (Dict): ノードのプロパティ

        Returns:
            Dict: 作成されたノード情報

        Raises:
            DatabaseError: ノードの作成に失敗した場合
        """
        node_id = self.neo4j_manager.create_content_node(data)
        return {'id': node_id, **data}

    def _rollback_changes(self) -> None:
        """変更をロールバックする。"""
        try:
            self.neo4j_manager.rollback_transaction()
            self._created_nodes = []
            self._created_relationships = []
        except Exception as e:
            logger.error(f"ロールバックに失敗しました: {str(e)}")

    def _record_metrics(self, analysis_result: Dict) -> None:
        """
        メトリクスを記録する。

        Args:
            analysis_result (Dict): 分析結果
        """
        try:
            metrics = {
                'entity_count': len(analysis_result.get('entities', [])),
                'relationship_count': len(analysis_result.get('relationships', [])),
                'timestamp': datetime.now().isoformat()
            }
            self._monitor.record_metrics(metrics)
        except Exception as e:
            logger.error(f"メトリクスの記録に失敗しました: {str(e)}")

    def get_metrics(self) -> Dict:
        """
        現在のメトリクスを取得する。

        Returns:
            Dict: 収集されたメトリクス
        """
        return self._monitor.get_metrics()

    def get_market_trends(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        市場トレンドを取得する。

        Args:
            start_date (Optional[datetime]): 開始日時
            end_date (Optional[datetime]): 終了日時

        Returns:
            List[Dict]: 市場トレンドのリスト

        Raises:
            MarketAnalysisError: トレンドの取得に失敗した場合
        """
        try:
            query = """
            MATCH (c:Content)
            WHERE
                ($start_date IS NULL OR c.published_at >= $start_date) AND
                ($end_date IS NULL OR c.published_at <= $end_date)
            WITH c
            ORDER BY c.market_impact DESC
            LIMIT 10
            RETURN {
                title: c.title,
                url: c.url,
                published_at: c.published_at,
                market_impact: c.market_impact
            } as trend
            """
            params = {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
            return self.neo4j_manager.execute_query(query, params)
        except Exception as e:
            logger.error(f"市場トレンドの取得に失敗しました: {str(e)}")
            raise MarketAnalysisError(f"市場トレンドの取得に失敗しました: {str(e)}")

    def get_entity_relationships(self, entity_name: str) -> List[Dict]:
        """
        エンティティの関係を取得する。

        Args:
            entity_name (str): エンティティ名

        Returns:
            List[Dict]: 関係のリスト

        Raises:
            MarketAnalysisError: 関係の取得に失敗した場合
        """
        try:
            query = """
            MATCH (e1:Entity {name: $entity_name})-[r]-(e2:Entity)
            RETURN {
                source: e1.name,
                target: e2.name,
                type: type(r),
                strength: r.strength
            } as relationship
            """
            params = {'entity_name': entity_name}
            return self.neo4j_manager.execute_query(query, params)
        except Exception as e:
            logger.error(f"エンティティ関係の取得に失敗しました: {str(e)}")
            raise MarketAnalysisError(f"エンティティ関係の取得に失敗しました: {str(e)}") 