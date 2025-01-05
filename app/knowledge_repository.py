from datetime import datetime
from typing import Dict, Any, Optional, List

from .neo4j_manager import Neo4jManager


class KnowledgeRepository:
    """市場分析結果をNeo4jデータベースに保存・管理するクラス"""

    def __init__(self, neo4j_manager: Neo4jManager):
        """
        Args:
            neo4j_manager (Neo4jManager): Neo4jデータベース接続を管理するインスタンス
        """
        self._neo4j_manager = neo4j_manager

    def store_analysis(self, analysis_result: Dict[str, Any]) -> None:
        """市場分析結果をNeo4jデータベースに保存

        Args:
            analysis_result (Dict[str, Any]): 市場分析結果
                {
                    'entities': List[Dict],  # エンティティ情報のリスト
                    'relationships': List[Dict],  # 関係性情報のリスト
                    'impact_scores': Dict[str, float],  # 影響度スコア
                    'source_url': str,  # 分析元URL
                    'analyzed_at': datetime  # 分析実施日時
                }

        Raises:
            ValueError: 分析結果の形式が不正な場合
            RuntimeError: データベース操作に失敗した場合
        """
        if not self._validate_analysis_result(analysis_result):
            raise ValueError("Invalid analysis result format")

        try:
            # エンティティの保存
            for entity in analysis_result['entities']:
                if not self._check_duplicate(entity['id'], entity['type']):
                    self._neo4j_manager.create_node(
                        labels=[entity['type']],
                        properties={
                            'id': entity['id'],
                            'name': entity['name'],
                            'description': entity.get('description', ''),
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }
                    )
                else:
                    self._update_timestamp(entity['id'], entity['type'])

            # 関係性の保存
            for rel in analysis_result['relationships']:
                self._neo4j_manager.create_relationship(
                    start_node_id=rel['source_id'],
                    end_node_id=rel['target_id'],
                    relationship_type=rel['type'],
                    properties={
                        'strength': rel.get('strength', 1.0),
                        'description': rel.get('description', ''),
                        'created_at': datetime.now().isoformat()
                    }
                )

            # 影響度スコアの更新
            for entity_id, score in analysis_result['impact_scores'].items():
                self._neo4j_manager.update_node(
                    node_id=entity_id,
                    properties={'impact_score': score}
                )

        except Exception as e:
            raise RuntimeError(f"Failed to store analysis result: {str(e)}")

    def _validate_analysis_result(self, result: Dict[str, Any]) -> bool:
        """分析結果の形式を検証

        Args:
            result (Dict[str, Any]): 検証する分析結果

        Returns:
            bool: 検証結果（True: 正常、False: 不正）
        """
        required_keys = {'entities', 'relationships', 'impact_scores', 'source_url', 'analyzed_at'}
        if not all(key in result for key in required_keys):
            return False

        # エンティティの検証
        for entity in result['entities']:
            if not all(key in entity for key in {'id', 'type', 'name'}):
                return False

        # 関係性の検証
        for rel in result['relationships']:
            if not all(key in rel for key in {'source_id', 'target_id', 'type'}):
                return False

        return True

    def _check_duplicate(self, node_id: str, label: str) -> bool:
        """指定されたIDとラベルを持つノードが既に存在するか確認

        Args:
            node_id (str): ノードID
            label (str): ノードのラベル

        Returns:
            bool: 存在する場合はTrue、存在しない場合はFalse
        """
        query = f"MATCH (n:{label} {{id: $node_id}}) RETURN count(n) as count"
        result = self._neo4j_manager.run_query(query, {'node_id': node_id})
        return result[0]['count'] > 0

    def _update_timestamp(self, node_id: str, label: str) -> None:
        """ノードの更新日時を現在時刻に更新

        Args:
            node_id (str): 更新対象のノードID
            label (str): ノードのラベル
        """
        self._neo4j_manager.update_node(
            node_id=node_id,
            properties={'updated_at': datetime.now().isoformat()}
        ) 