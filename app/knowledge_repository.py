"""Neo4jデータベースを使用して市場分析結果を保存・管理するモジュール。"""

import logging
from datetime import datetime
from typing import Any, Dict

from .neo4j_manager import Neo4jManager

logger = logging.getLogger(__name__)


class KnowledgeRepository:
    """Neo4jデータベースを使用して市場分析結果を保存・管理するクラス。"""

    def __init__(self, neo4j_manager: Neo4jManager):
        """初期化メソッド。

        Args:
            neo4j_manager (Neo4jManager): Neo4jデータベース管理オブジェクト
        """
        self.neo4j_manager = neo4j_manager

    def store_analysis(self, analysis_result: Dict[str, Any]) -> bool:
        """市場分析結果をNeo4jデータベースに保存する。

        Args:
            analysis_result (Dict[str, Any]): 市場分析結果
                {
                    "entities": List[Dict],  # エンティティ情報のリスト
                    "relationships": List[Dict],  # 関係性情報のリスト
                    "impact_scores": Dict[str, float],  # エンティティごとの影響度スコア
                    "source_url": str,  # 分析元のURL
                    "analyzed_at": datetime  # 分析実施日時
                }

        Returns:
            bool: 保存が成功した場合はTrue、失敗した場合はFalse

        Raises:
            ValueError: 分析結果の形式が不正な場合
            RuntimeError: データベース操作に失敗した場合
        """
        try:
            # 分析結果の検証
            if not self._validate_analysis_result(analysis_result):
                raise ValueError("Invalid analysis result format")

            # エンティティの保存
            entity_id_map = self._store_entities(analysis_result)

            # 関係性の保存
            self._store_relationships(analysis_result, entity_id_map)

            return True

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except RuntimeError as e:
            logger.error(f"Database operation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to store analysis result: {str(e)}")
            return False

    def _store_entities(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """エンティティを保存する

        Args:
            analysis_result (Dict[str, Any]): 分析結果

        Returns:
            Dict[str, str]: エンティティ名とIDのマッピング

        Raises:
            RuntimeError: データベース操作に失敗した場合
        """
        entity_id_map = {}
        for entity in analysis_result['entities']:
            # エンティティの存在確認
            if self._check_duplicate(entity['id'], entity['type']):
                # 既存のエンティティを更新
                self._update_timestamp(entity['id'], entity['type'])
                success = self.neo4j_manager.update_node(
                    node_id=entity['id'],
                    properties={
                        'impact_score': analysis_result['impact_scores'].get(entity['id'], 0.5)
                    }
                )
                if not success:
                    raise RuntimeError(f"Failed to update entity: {entity['name']}")
                entity_id_map[entity['name']] = entity['id']
            else:
                # 新規エンティティを作成
                node_id = self.neo4j_manager.create_node(
                    labels=[entity['type']],
                    properties={
                        'id': entity['id'],
                        'name': entity['name'],
                        'description': entity.get('description', ''),
                        'created_at': datetime.now().isoformat(),
                        'impact_score': analysis_result['impact_scores'].get(entity['id'], 0.5)
                    }
                )
                if not node_id:
                    raise RuntimeError(f"Failed to create entity: {entity['name']}")
                entity_id_map[entity['name']] = node_id

        return entity_id_map

    def _store_relationships(
        self,
        analysis_result: Dict[str, Any],
        entity_id_map: Dict[str, str]
    ) -> None:
        """関係性を保存する

        Args:
            analysis_result (Dict[str, Any]): 分析結果
            entity_id_map (Dict[str, str]): エンティティ名とIDのマッピング

        Raises:
            RuntimeError: データベース操作に失敗した場合
        """
        for rel in analysis_result['relationships']:
            source_id = entity_id_map.get(rel['source'])
            target_id = entity_id_map.get(rel['target'])
            
            if source_id and target_id:
                rel_id = self.neo4j_manager.create_relationship(
                    start_node_id=source_id,
                    end_node_id=target_id,
                    rel_type=rel['type'],
                    properties={
                        'description': rel.get('description', ''),
                        'strength': rel.get('strength', 1.0),
                        'created_at': datetime.now().isoformat()
                    }
                )
                if not rel_id:
                    raise RuntimeError(
                        f"Failed to create relationship: {rel['type']}"
                    )

    def _validate_analysis_result(self, analysis_result: Dict[str, Any]) -> bool:
        """分析結果の形式を検証する

        Args:
            analysis_result (Dict[str, Any]): 検証する分析結果

        Returns:
            bool: 検証が成功した場合はTrue、失敗した場合はFalse
        """
        try:
            # 必須キーの検証
            if not self._validate_required_keys(analysis_result):
                return False

            # エンティティの検証
            if not self._validate_entities(analysis_result['entities']):
                return False

            # リレーションシップの検証
            if not self._validate_relationships(analysis_result['relationships']):
                return False

            # 影響度スコアの検証
            if not self._validate_impact_scores(analysis_result['impact_scores']):
                return False

            return True

        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return False

    def _validate_required_keys(self, analysis_result: Dict[str, Any]) -> bool:
        """必須キーの存在を確認する"""
        if not isinstance(analysis_result, dict):
            logger.error("Analysis result must be a dictionary")
            return False

        required_keys = ['entities', 'relationships', 'impact_scores', 'source_url', 'analyzed_at']
        missing_keys = [key for key in required_keys if key not in analysis_result]
        if missing_keys:
            logger.error(f"Missing required keys in analysis result: {missing_keys}")
            return False
        return True

    def _validate_entities(self, entities: Any) -> bool:
        """エンティティ情報を検証する"""
        if not isinstance(entities, list):
            logger.error("Entities must be a list")
            return False

        for entity in entities:
            if not isinstance(entity, dict):
                logger.error(f"Entity must be a dictionary: {entity}")
                return False

            required_keys = ['id', 'name', 'type']
            missing_keys = [key for key in required_keys if key not in entity]
            if missing_keys:
                logger.error(f"Missing required keys in entity: {missing_keys}")
                return False

            if not isinstance(entity['name'], str) or not isinstance(entity['type'], str):
                logger.error(f"Entity name and type must be strings: {entity}")
                return False

        return True

    def _validate_relationships(self, relationships: Any) -> bool:
        """関係性情報を検証する"""
        if not isinstance(relationships, list):
            logger.error("Relationships must be a list")
            return False

        for rel in relationships:
            if not isinstance(rel, dict):
                logger.error(f"Relationship must be a dictionary: {rel}")
                return False

            required_keys = ['source', 'target', 'type']
            missing_keys = [key for key in required_keys if key not in rel]
            if missing_keys:
                logger.error(f"Missing required keys in relationship: {missing_keys}")
                return False

            if not all(isinstance(rel[k], str) for k in ['source', 'target', 'type']):
                logger.error(f"Relationship source, target, and type must be strings: {rel}")
                return False

        return True

    def _validate_impact_scores(self, impact_scores: Any) -> bool:
        """影響度スコアを検証する"""
        if not isinstance(impact_scores, dict):
            logger.error("Impact scores must be a dictionary")
            return False

        for key, score in impact_scores.items():
            if not isinstance(key, str):
                logger.error(f"Impact score key must be a string: {key}")
                return False
            if not isinstance(score, (int, float)) or not 0 <= score <= 1:
                logger.error(f"Impact score must be a number between 0 and 1: {score}")
                return False

        return True

    def _check_duplicate(self, node_id: str, label: str) -> bool:
        """指定されたIDとラベルを持つノードが存在するかチェックする

        Args:
            node_id (str): ノードID
            label (str): ノードのラベル

        Returns:
            bool: ノードが存在する場合はTrue、存在しない場合はFalse
        """
        query = (
            f"MATCH (n:{label} {{id: $node_id}}) "
            "RETURN count(n) as count"
        )
        result = self.neo4j_manager.run_query(query, {'node_id': node_id})
        return result[0]['count'] > 0

    def _update_timestamp(self, node_id: str, label: str) -> None:
        """指定されたノードの更新日時を現在時刻に更新する

        Args:
            node_id (str): ノードID
            label (str): ノードのラベル
        """
        self.neo4j_manager.update_node(
            node_id=node_id,
            properties={'updated_at': datetime.now().isoformat()}
        ) 