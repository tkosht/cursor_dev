"""Gemini APIの解析結果から市場分析情報を抽出するモジュール。"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .gemini_analyzer import GeminiAnalyzer

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """市場分析を行うクラス"""

    def __init__(self):
        """初期化"""
        self.logger = logging.getLogger(__name__)
        self.gemini = GeminiAnalyzer()

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        市場分析を実行する

        Args:
            data (Dict[str, Any]): 分析対象のデータ
                {
                    'title': str,
                    'content': str,
                    'url': str,
                    'published_at': str
                }

        Returns:
            Dict[str, Any]: 分析結果
                {
                    'entities': List[Dict],
                    'relationships': List[Dict],
                    'impact_scores': Dict[str, float],
                    'trends': List[str],
                    'source_url': str,
                    'analyzed_at': str
                }
        """
        try:
            # Geminiによる分析
            gemini_result = self.gemini.analyze_content(data)
            
            # 結果の加工
            processed_result = self.process_gemini_output(gemini_result)
            
            # メタデータの追加
            processed_result['source_url'] = data['url']
            processed_result['analyzed_at'] = datetime.now().isoformat()
            
            return processed_result
            
        except Exception as e:
            self.logger.error(f"分析中にエラーが発生しました: {str(e)}")
            raise

    def process_gemini_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Geminiの出力を処理する

        Args:
            output (Dict[str, Any]): Geminiの分析結果

        Returns:
            Dict[str, Any]: 処理済みの結果
        """
        try:
            if not isinstance(output, dict):
                raise ValueError("辞書形式ではありません")

            # エンティティの抽出と名前からIDへのマッピング作成
            entities = self._extract_entities(output.get('entities', []))
            name_to_id = {entity['name']: entity['id'] for entity in entities}
            
            # リレーションシップの抽出（エンティティIDを使用）
            relationships = self._detect_relationships(
                output.get('relationships', []),
                name_to_id
            )
            
            # 影響度スコアの取得
            impact_scores = {
                'market_impact': self._calculate_impact_score(output.get('market_impact', 0.5)),
                'technology_impact': self._calculate_impact_score(output.get('technology_impact', 0.5)),
                'social_impact': self._calculate_impact_score(output.get('social_impact', 0.5))
            }
            
            return {
                'entities': entities,
                'relationships': relationships,
                'impact_scores': impact_scores,
                'trends': output.get('trends', []),
                'source_url': output.get('source_url', ''),
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Gemini出力の処理中にエラーが発生しました: {str(e)}")
            raise

    def _extract_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        エンティティ情報を抽出する

        Args:
            entities (List[Dict[str, Any]]): エンティティのリスト

        Returns:
            List[Dict[str, Any]]: 処理済みのエンティティリスト
        """
        try:
            processed_entities = []
            for i, entity in enumerate(entities):
                processed_entity = self._process_single_entity(i, entity)
                if processed_entity:
                    processed_entities.append(processed_entity)
            return processed_entities
        except Exception as e:
            self.logger.error(f"エンティティの抽出中にエラーが発生しました: {str(e)}")
            return []

    def _process_single_entity(self, index: int, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        単一のエンティティを処理する

        Args:
            index (int): エンティティのインデックス
            entity (Dict[str, Any]): 処理対象のエンティティ

        Returns:
            Optional[Dict[str, Any]]: 処理済みのエンティティ、無効な場合はNone
        """
        if not isinstance(entity, dict) or 'name' not in entity:
            return None

        processed_entity = {
            'id': f"entity_{index}",
            'name': entity['name'],
            'type': entity.get('type', 'ENTITY').upper(),
            'description': entity.get('description', ''),
            'properties': {
                'importance': entity.get('importance', 'medium'),
                'category': entity.get('category', ''),
                'source': entity.get('source', '')
            }
        }

        if 'properties' in entity and isinstance(entity['properties'], dict):
            for key, value in entity['properties'].items():
                if key not in processed_entity['properties']:
                    processed_entity['properties'][key] = value

        return processed_entity

    def _validate_relationship(
        self,
        rel: Dict[str, Any],
        name_to_id: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """
        リレーションシップを検証する

        Args:
            rel: 検証対象のリレーションシップ
            name_to_id: エンティティ名からIDへのマッピング辞書

        Returns:
            Optional[Dict[str, Any]]: 検証済みのリレーションシップ、無効な場合はNone
        """
        if not isinstance(rel, dict):
            return None

        # 必須フィールドの確認
        source = rel.get('source')
        target = rel.get('target')
        rel_type = rel.get('type')
        if not all([source, target, rel_type]):
            return None

        # 係タイプの検証（大文字に変換して比較）
        rel_type = rel_type.upper()
        valid_types = {'INFLUENCES', 'COMPETES', 'DEVELOPS', 'PARTICIPATES', 'PRODUCES'}
        if rel_type not in valid_types:
            self.logger.warning(f"Invalid relationship type: {rel_type}")
            return None

        # エンティティ名からIDを取得
        source_id = name_to_id.get(source)
        target_id = name_to_id.get(target)
        if not source_id or not target_id:
            return None

        # 基本プロパティの設定
        processed_rel = {
            'source': source_id,
            'target': target_id,
            'type': rel_type,
            'strength': float(rel.get('strength', 0.5)),  # 0.0-1.0の範囲に正規化
            'description': rel.get('description', ''),
            'timestamp': datetime.now().isoformat()
        }

        return processed_rel

    def _add_relationship_properties(
        self,
        rel: Dict[str, Any],
        processed_rel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        リレーションシップにプロパティを追加する

        Args:
            rel: 元のリレーションシップ
            processed_rel: 処理済みのリレーションシップ

        Returns:
            Dict[str, Any]: プロパティが追加されたリレーションシップ
        """
        if 'properties' in rel and isinstance(rel['properties'], dict):
            for key, value in rel['properties'].items():
                if key not in processed_rel:  # 既存のキーは上書きしない
                    processed_rel[key] = value
        return processed_rel

    def _detect_relationships(
        self,
        relationships: List[Dict[str, Any]],
        name_to_id: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        リレーションシップを検出して処理する

        Args:
            relationships: リレーションシップのリスト
            name_to_id: エンティティ名からIDへのマッピング辞書

        Returns:
            List[Dict[str, Any]]: 処理済みのリレーションシップリスト
        """
        try:
            processed_relationships = []
            for rel in relationships:
                # リレーションシップの検証
                processed_rel = self._validate_relationship(rel, name_to_id)
                if not processed_rel:
                    continue

                # プロパティの追加
                processed_rel = self._add_relationship_properties(rel, processed_rel)
                processed_relationships.append(processed_rel)

            return processed_relationships

        except Exception as e:
            self.logger.error(f"リレーションシップの検出中にエラーが発生しました: {str(e)}")
            return []

    def _calculate_impact_score(self, value: Any) -> float:
        """
        影響度スコアを計算する

        Args:
            value: スコア値（文字列または数値）

        Returns:
            float: 0.0から1.0の範囲の影響度スコア
        """
        try:
            if isinstance(value, str):
                value = float(value)
            elif not isinstance(value, (int, float)):
                return 0.5

            return max(0.0, min(1.0, float(value)))
        except (ValueError, TypeError):
            return 0.5 