"""知識リポジトリを管理するモジュール。"""

import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from app.exceptions import ValidationError
from app.neo4j_manager import Neo4jManager
from app.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class KnowledgeRepository:
    """Neo4jデータベースを使用して市場分析結果を保存・管理するクラス。"""

    def __init__(self, neo4j_manager: Neo4jManager):
        """初期化メソッド。

        Args:
            neo4j_manager (Neo4jManager): Neo4jデータベース管理オブジェクト
        """
        self.neo4j_manager = neo4j_manager
        self._monitor = PerformanceMonitor()

    def store_analysis(self, analysis_result: Dict[str, Any]) -> bool:
        """分析結果を保存する。

        Args:
            analysis_result (Dict[str, Any]): 分析結果

        Returns:
            bool: 保存が成功した場合はTrue

        Raises:
            ValueError: 分析結果の形式が不正な場合
            Exception: データベース操作に失敗した場合
        """
        try:
            # バリデーションチェック
            if not self._validate_analysis_result(analysis_result):
                raise ValueError("Invalid analysis result format")

            # 空のデータセットの処理
            if not analysis_result['entities']:
                logger.info("No entities to store")
                return True

            # エンティティの保存とリレーションシップの作成
            return self._store_analysis_data(analysis_result)

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Database operation error: {str(e)}")
            raise

    def _store_analysis_data(self, analysis_result: Dict[str, Any]) -> bool:
        """分析結果のデータを保存する。

        Args:
            analysis_result: 分析結果

        Returns:
            bool: 保存が成功した場合はTrue

        Raises:
            Exception: データベース操作に失敗した場合
        """
        try:
            self._monitor.start_operation()
            self.neo4j_manager.begin_transaction()

            # エンティティの保存
            entity_id_map = self._store_entities(analysis_result)
            if not entity_id_map:
                logger.error("Failed to store entities")
                raise Exception("Failed to store entities")

            # リレーションシップの保存
            self._store_relationships(analysis_result, entity_id_map)

            self.neo4j_manager.commit_transaction()
            self._monitor.end_operation(
                'store_analysis',
                True,
                entities_count=len(analysis_result['entities']),
                relationships_count=len(analysis_result['relationships']),
                scores_count=len(analysis_result['impact_scores'])
            )
            return True

        except Exception as e:
            self.neo4j_manager.rollback_transaction()
            self._monitor.end_operation(
                'store_analysis',
                False,
                error=str(e)
            )
            logger.error(f"分析結果の保存中にエラーが発生しました: {str(e)}")
            raise

    def _validate_url(self, url: str) -> bool:
        """URLの形式を検証する。

        Args:
            url (str): 検証するURL

        Returns:
            bool: 検証結果
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _validate_analysis_result(self, analysis_result: Dict[str, Any]) -> bool:
        """分析結果のバリデーション。

        Args:
            analysis_result (Dict[str, Any]): 分析結果

        Returns:
            bool: バリデーション結果
        """
        try:
            # 基本的な検証
            if not self._validate_basic_checks(analysis_result):
                return False

            # 空のデータセットは有効とする
            if not analysis_result['entities']:
                return True

            # 詳細な検証
            return self._validate_data_contents(analysis_result)

        except Exception as e:
            logger.error(f"Error validating analysis result: {str(e)}")
            return False

    def _validate_basic_checks(self, analysis_result: Dict[str, Any]) -> bool:
        """分析結果の基本的な検証を行う。

        Args:
            analysis_result (Dict[str, Any]): 分析結果

        Returns:
            bool: 検証結果
        """
        # 基本的な型と必須キーの確認
        if not self._validate_basic_structure(analysis_result):
            return False

        # 各フィールドの型と内容の確認
        if not self._validate_field_types(analysis_result):
            return False

        # URLの形式を検証
        if not self._validate_url(analysis_result['source_url']):
            logger.error("Invalid URL format")
            return False

        return True

    def _validate_data_contents(self, analysis_result: Dict[str, Any]) -> bool:
        """分析結果の詳細な内容を検証する。

        Args:
            analysis_result (Dict[str, Any]): 分析結果

        Returns:
            bool: 検証結果
        """
        # エンティティの検証
        if not self._validate_entities(analysis_result['entities']):
            return False

        # リレーションシップの検証（存在する場合のみ）
        has_relationships = bool(analysis_result['relationships'])
        if has_relationships:
            if not self._validate_relationships(analysis_result['relationships']):
                return False

        # 影響度スコアの検証（存在する場合のみ）
        has_impact_scores = bool(analysis_result['impact_scores'])
        if has_impact_scores:
            if not self._validate_impact_scores(
                analysis_result['impact_scores'],
                analysis_result['entities']
            ):
                return False

        return True

    def _validate_basic_structure(self, analysis_result: Dict[str, Any]) -> None:
        """基本構造を検証する。

        Args:
            analysis_result: 分析結果

        Raises:
            ValidationError: 検証に失敗した場合
        """
        if not isinstance(analysis_result, dict):
            logger.error("Analysis result must be a dictionary")
            raise ValidationError("Analysis result must be a dictionary")

        required_keys = {'entities', 'relationships', 'impact_scores'}
        missing_keys = required_keys - set(analysis_result.keys())
        if missing_keys:
            logger.error("Missing required keys in analysis result")
            raise ValidationError(f"Missing required keys: {missing_keys}")

    def _validate_field_types(self, analysis_result: Dict[str, Any]) -> None:
        """フィールドの型を検証する。

        Args:
            analysis_result: 分析結果

        Raises:
            ValidationError: 検証に失敗した場合
        """
        self._validate_entities_type(analysis_result)
        self._validate_relationships_type(analysis_result)
        self._validate_impact_scores_type(analysis_result)
        self._validate_source_url_type(analysis_result)
        self._validate_analyzed_at_type(analysis_result)

    def _validate_entities_type(self, analysis_result: Dict[str, Any]) -> None:
        """エンティティの型を検証する。

        Args:
            analysis_result: 分析結果

        Raises:
            ValidationError: 検証に失敗した場合
        """
        if not isinstance(analysis_result['entities'], list):
            logger.error("Entities must be a list")
            raise ValidationError("Entities must be a list")

    def _validate_relationships_type(self, analysis_result: Dict[str, Any]) -> None:
        """リレーションシップの型を検証する。

        Args:
            analysis_result: 分析結果

        Raises:
            ValidationError: 検証に失敗した場合
        """
        if not isinstance(analysis_result['relationships'], list):
            logger.error("Relationships must be a list")
            raise ValidationError("Relationships must be a list")

    def _validate_impact_scores_type(self, analysis_result: Dict[str, Any]) -> None:
        """インパクトスコアの型を検証する。

        Args:
            analysis_result: 分析結果

        Raises:
            ValidationError: 検証に失敗した場合
        """
        if not isinstance(analysis_result['impact_scores'], dict):
            logger.error("Impact scores must be a dictionary")
            raise ValidationError("Impact scores must be a dictionary")

    def _validate_source_url_type(self, analysis_result: Dict[str, Any]) -> None:
        """ソースURLの型を検証する。

        Args:
            analysis_result: 分析結果

        Raises:
            ValidationError: 検証に失敗した場合
        """
        if 'source_url' in analysis_result and not isinstance(analysis_result['source_url'], str):
            logger.error("Source URL must be a string")
            raise ValidationError("Source URL must be a string")

    def _validate_analyzed_at_type(self, analysis_result: Dict[str, Any]) -> None:
        """分析日時の型を検証する。

        Args:
            analysis_result: 分析結果

        Raises:
            ValidationError: 検証に失敗した場合
        """
        if 'analyzed_at' in analysis_result:
            if isinstance(analysis_result['analyzed_at'], str):
                try:
                    datetime.fromisoformat(
                        analysis_result['analyzed_at'].replace('Z', '+00:00')
                    )
                except ValueError:
                    logger.error("Analyzed at must be a valid ISO format datetime string")
                    raise ValidationError(
                        "Analyzed at must be a valid ISO format datetime string"
                    )
            elif not isinstance(analysis_result['analyzed_at'], datetime):
                logger.error("Analyzed at must be a datetime or ISO format string")
                raise ValidationError(
                    "Analyzed at must be a datetime or ISO format string"
                )

    def _validate_entities(self, entities: Any) -> bool:
        """エンティティ情報を検証する。

        Args:
            entities (Any): 検証するエンティティ情報

        Returns:
            bool: 検証結果
        """
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

            # IDは文字列型であることを確認
            if not isinstance(entity['id'], str):
                logger.error(f"Entity ID must be a string: {entity['id']}")
                return False

            if not isinstance(entity['name'], str) or not isinstance(entity['type'], str):
                logger.error(f"Entity name and type must be strings: {entity}")
                return False

        return True

    def _validate_impact_scores(self, impact_scores: Dict[str, float], entities: List[Dict[str, Any]]) -> bool:
        """影響度スコアのバリデーション。

        Args:
            impact_scores (Dict[str, float]): 影響度スコア
            entities (List[Dict[str, Any]]): エンティティリスト

        Returns:
            bool: バリデーション結果

        Note:
            - スコアは0.0から1.0の範囲内の数値
            - すべてのエンティティにスコアが設定されている必要がある
            - スコアは数値型（int or float）である必要がある
        """
        try:
            # 基本的な型チェック
            if not self._validate_impact_scores_basic_types(impact_scores, entities):
                return False

            # エンティティIDの整合性チェック
            entity_ids = self._extract_entity_ids(entities)
            if not entity_ids:
                return False

            if not self._validate_impact_scores_consistency(impact_scores, entity_ids):
                return False

            # スコア値の検証
            if not self._validate_score_values(impact_scores):
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating impact scores: {str(e)}")
            return False

    def _validate_impact_scores_basic_types(
        self,
        impact_scores: Dict[str, float],
        entities: List[Dict[str, Any]]
    ) -> None:
        """インパクトスコアの基本型を検証する。

        Args:
            impact_scores: インパクトスコア
            entities: エンティティリスト

        Raises:
            ValidationError: 検証に失敗した場合
        """
        # エンティティIDの抽出
        entity_ids = self._extract_entity_ids(entities)
        if not entity_ids:
            logger.error("No valid entity IDs found")
            raise ValidationError("No valid entity IDs found")

        # スコアの型チェック
        for entity_id, score in impact_scores.items():
            if not isinstance(entity_id, str):
                logger.error(
                    f"Entity ID must be a string: {entity_id}"
                )
                raise ValidationError(
                    f"Entity ID must be a string: {entity_id}"
                )

            if not isinstance(score, (int, float)):
                logger.error(
                    f"Impact score must be a number: {entity_id} -> {score}"
                )
                raise ValidationError(
                    f"Impact score must be a number: {entity_id} -> {score}"
                )

            if not 0 <= score <= 1:
                logger.error(
                    f"Impact score must be between 0 and 1: {entity_id} -> {score}"
                )
                raise ValidationError(
                    f"Impact score must be between 0 and 1: {entity_id} -> {score}"
                )

    def _validate_impact_scores_consistency(
        self,
        entities: List[Dict[str, Any]],
        impact_scores: Dict[str, float]
    ) -> None:
        """インパクトスコアとエンティティIDの整合性を検証する。

        Args:
            entities: エンティティリスト
            impact_scores: インパクトスコア

        Raises:
            ValidationError: 検証に失敗した場合
        """
        # エンティティIDの抽出
        entity_ids = self._extract_entity_ids(entities)
        if not entity_ids:
            logger.error("No valid entity IDs found")
            raise ValidationError("No valid entity IDs found")

        # すべてのエンティティにスコアが設定されているか確認
        missing_entities = entity_ids - set(impact_scores.keys())
        if missing_entities:
            logger.error(
                f"Missing impact scores for entities: {missing_entities}"
            )
            raise ValidationError(
                f"Missing impact scores for entities: {missing_entities}"
            )

        # 余分なスコアがないか確認
        extra_scores = set(impact_scores.keys()) - entity_ids
        if extra_scores:
            logger.error(
                f"Found impact scores for non-existent entities: {extra_scores}"
            )
            raise ValidationError(
                f"Found impact scores for non-existent entities: {extra_scores}"
            )

    def _validate_score_values(self, impact_scores: Dict[str, float]) -> None:
        """スコア値を検証する。

        Args:
            impact_scores: インパクトスコア

        Raises:
            ValidationError: 検証に失敗した場合
        """
        for entity_id, score in impact_scores.items():
            if not isinstance(score, (int, float)):
                logger.error(f"Impact score must be a number: {entity_id} -> {score}")
                raise ValidationError(f"Impact score must be a number: {entity_id} -> {score}")

            if not 0 <= score <= 1:
                logger.error(f"Impact score must be between 0 and 1: {entity_id} -> {score}")
                raise ValidationError(f"Impact score must be between 0 and 1: {entity_id} -> {score}")

            if isinstance(score, float) and (math.isnan(score) or math.isinf(score)):
                logger.error(f"Impact score must be a finite number: {entity_id} -> {score}")
                raise ValidationError(f"Impact score must be a finite number: {entity_id} -> {score}")

    def _extract_entity_ids(self, entities: List[Dict[str, Any]]) -> Set[str]:
        """エンティティIDを抽出する。

        Args:
            entities: エンティティリスト

        Returns:
            Set[str]: エンティティIDのセット

        Raises:
            ValidationError: 検証に失敗した場合
        """
        entity_ids = set()
        for entity in entities:
            if not isinstance(entity, dict):
                logger.error("Entity must be a dictionary")
                raise ValidationError("Entity must be a dictionary")

            if 'id' not in entity:
                logger.error("Entity missing required 'id' field")
                raise ValidationError("Entity missing required 'id' field")

            if not isinstance(entity['id'], str):
                logger.error("Entity ID must be a string")
                raise ValidationError("Entity ID must be a string")

            entity_ids.add(entity['id'])

        if not entity_ids:
            logger.error("No valid entity IDs found")
            raise ValidationError("No valid entity IDs found")

        return entity_ids

    def _store_entities(
        self,
        analysis_result: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """エンティティを保存する。

        Args:
            analysis_result (Dict[str, Any]): 分析結果

        Returns:
            Optional[Dict[str, str]]: エンティティ名とIDのマッピング、失敗時はNone

        Raises:
            Exception: データベース操作に失敗した場合
        """
        entity_id_map = {}
        try:
            for entity in analysis_result['entities']:
                # エンティティIDの検証
                if not entity.get('id') or not isinstance(entity['id'], str):
                    logger.error(f"Invalid entity ID: {entity.get('id')}")
                    raise ValueError(f"Invalid entity ID: {entity.get('id')}")

                # プロパティを基本型に変換
                properties = {
                    'id': entity['id'],
                    'name': entity.get('name', ''),
                    'type': entity.get('type', 'ENTITY'),
                    'description': entity.get('description', ''),
                    'importance': float(entity.get('properties', {}).get('importance', 0.5)),
                    'category': str(entity.get('properties', {}).get('category', '')),
                    'source': str(entity.get('properties', {}).get('source', ''))
                }

                # 既存のエンティティを検索
                existing = self.neo4j_manager.find_node(
                    labels=[entity.get('type', 'ENTITY')],
                    properties={'id': entity['id']}
                )

                node_id = None
                if existing:
                    # 既存のエンティティを更新
                    success = self.neo4j_manager.update_node(
                        node_id=entity['id'],
                        properties=properties
                    )
                    if success:
                        node_id = entity['id']
                        self._update_timestamp(node_id, entity.get('type', 'ENTITY'))
                else:
                    # 新規エンティティを作成
                    node_id = self.neo4j_manager.create_node(
                        labels=[entity.get('type', 'ENTITY')],
                        properties=properties
                    )

                if not node_id:
                    logger.error(f"Failed to store entity: {entity['id']}")
                    raise Exception(f"Failed to store entity: {entity['id']}")

                entity_id_map[entity['name']] = node_id

            return entity_id_map

        except Exception as e:
            logger.error(f"Error storing entities: {str(e)}")
            raise

    def _store_relationships(
        self,
        analysis_result: Dict[str, Any],
        entity_id_map: Dict[str, str]
    ) -> None:
        """関係性を保存する。

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
                success = self.neo4j_manager.create_relationship(
                    start_node_id=source_id,
                    end_node_id=target_id,
                    rel_type=rel['type'],
                    properties={
                        'description': rel.get('description', ''),
                        'strength': rel.get('strength', 1.0),
                        'created_at': datetime.now().isoformat()
                    }
                )
                if not success:
                    logger.error(f"Failed to create relationship: {rel['type']}")
                    continue  # 失敗したリレーションシップはスキップ

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

    def _validate_relationships(self, relationships: List[Dict[str, Any]]) -> bool:
        """関係性のバリデーション。

        Args:
            relationships (List[Dict[str, Any]]): 関係性のリスト

        Returns:
            bool: バリデーション結果
        """
        try:
            for rel in relationships:
                # 必須キーの存在確認
                if not all(key in rel for key in ['source', 'target', 'type']):
                    return False

                # 型の確認
                if not isinstance(rel['source'], str) or \
                   not isinstance(rel['target'], str) or \
                   not isinstance(rel['type'], str):
                    return False

                # strengthが存在する場合は数値であることを確認
                if 'strength' in rel and not isinstance(rel['strength'], (int, float)):
                    return False

                # strengthが範囲内であることを確認
                if 'strength' in rel and (rel['strength'] < 0 or rel['strength'] > 1):
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating relationships: {str(e)}")
            return False

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
        """指定されたノードドドの更新日時を現在時刻に更新する

        Args:
            node_id (str): ノードID
            label (str): ノードのラベル
        """
        self.neo4j_manager.update_node(
            node_id=node_id,
            properties={'updated_at': datetime.now().isoformat()}
        ) 

    def save_analysis_result(self, result: Dict[str, Any]) -> bool:
        """
        市場分析結果をNeo4jに保存する。

        Args:
            result (Dict[str, Any]): 保存する分析結果

        Returns:
            bool: 保存に成功した場合はTrue、失敗した場合はFalse

        Raises:
            ValueError: 分析結果が不正な形式の場合
        """
        if not self._validate_result_format(result):
            raise ValueError("Invalid analysis result format")

        try:
            self._monitor.start_operation()
            self.neo4j_manager.begin_transaction()

            # エンティティの保存
            for entity in result.get('entities', []):
                self.neo4j_manager.create_or_update_entity(entity)

            # リレーションシップの保存
            for rel in result.get('relationships', []):
                self.neo4j_manager.create_or_update_relationship(rel)

            # インパクトスコアの保存
            for score in result.get('impact_scores', []):
                self.neo4j_manager.create_or_update_impact_score(score)

            self.neo4j_manager.commit_transaction()
            self._monitor.end_operation(
                'save_analysis',
                True,
                entities_count=len(result.get('entities', [])),
                relationships_count=len(result.get('relationships', [])),
                scores_count=len(result.get('impact_scores', []))
            )
            return True
        except Exception as e:
            self.neo4j_manager.rollback_transaction()
            self._monitor.end_operation(
                'save_analysis',
                False,
                error=str(e)
            )
            logger.error(f"分析結果の保存中にエラーが発生しました: {str(e)}")
            return False

    def get_metrics(self) -> dict:
        """
        現在のメトリクスを取得する。

        Returns:
            dict: 収集されたメトリクス
        """
        return self._monitor.get_metrics() 