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

        Raises:
            ValueError: 入力が辞書形式でない場合
            Exception: 必須フィールドが欠落している場合
        """
        try:
            if not isinstance(output, dict):
                raise ValueError("辞書形式ではありません")

            # 必須フィールドの確認
            required_fields = ['entities', 'relationships', 'trends']
            missing_fields = [field for field in required_fields if field not in output]
            if missing_fields:
                raise Exception(f"必須フィールドが欠落しています: {', '.join(missing_fields)}")

            # エンティティの抽出と名前からIDへのマッピング作成
            entities = self._extract_entities(output.get('entities', []))
            name_to_id = {entity['name']: entity['id'] for entity in entities}
            
            # リレーションシップの抽出（エンティティIDを使用）
            relationships = self._detect_relationships(
                output.get('relationships', []),
                name_to_id
            )
            
            # トレンド分析の実行
            trends = self._analyze_trends(
                output.get('trends', []),
                entities,
                relationships
            )
            
            # 影響度スコアの取得と計算
            impact_scores = self._calculate_impact_scores(
                output,
                entities,
                relationships,
                trends
            )
            
            return {
                'entities': entities,
                'relationships': relationships,
                'impact_scores': impact_scores,
                'trends': trends,
                'source_url': output.get('source_url', ''),
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Gemini出力の処理中にエラーが発生しました: {str(e)}")
            raise

    def _analyze_trends(
        self,
        raw_trends: List[str],
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        トレンドを分析し、重要度や関連情報を付加する

        Args:
            raw_trends (List[str]): 生のトレンドリスト
            entities (List[Dict[str, Any]]): エンティティリスト
            relationships (List[Dict[str, Any]]): リレーションシップリスト

        Returns:
            List[Dict[str, Any]]: 分析済みのトレンドリスト
        """
        analyzed_trends = []
        for trend in raw_trends:
            trend_info = {
                'name': trend,
                'importance': self._calculate_trend_factor(trend, entities, relationships),
                'related_entities': self._find_related_entities(trend, entities),
                'market_impact': self._calculate_market_impact(trend, entities, relationships)
            }
            analyzed_trends.append(trend_info)
        
        # 重要度でソート
        return sorted(analyzed_trends, key=lambda x: x['importance'], reverse=True)

    def _calculate_trend_factor(
        self,
        trend: str,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> float:
        """
        トレンドの重要度を計算する

        Args:
            trend (str): トレンド名
            entities (List[Dict[str, Any]]): エンティティリスト
            relationships (List[Dict[str, Any]]): リレーションシップリスト

        Returns:
            float: 0.0-1.0の重要度スコア
        """
        # 企業関連度の評価（企業エンティティとの関連）
        company_factor = self._calculate_company_factor(trend, entities)
        
        # 市場影響度の評価（リレーションシップの強度）
        market_factor = self._calculate_market_factor(trend, relationships)
        
        # トレンドの新規性評価
        novelty_factor = self._calculate_novelty_factor(trend)
        
        # 各要素の重み付け
        weights = {
            'company': 0.4,  # 企業関連度の重み
            'market': 0.4,   # 市場影響度の重み
            'novelty': 0.2   # 新規性の重み
        }
        
        # 総合スコアの計算
        total_score = (
            company_factor * weights['company'] +
            market_factor * weights['market'] +
            novelty_factor * weights['novelty']
        )
        
        return min(1.0, max(0.0, total_score))

    def _calculate_company_factor(
        self,
        trend: str,
        entities: List[Dict[str, Any]]
    ) -> float:
        """
        トレンドと企業エンティティの関連度を計算する

        Args:
            trend (str): トレンド名
            entities (List[Dict[str, Any]]): エンティティリスト

        Returns:
            float: 0.0-1.0の関連度スコア
        """
        company_entities = [
            entity for entity in entities
            if entity['type'] == 'COMPANY'
        ]
        
        if not company_entities:
            return 0.0
        
        # 企業の重要度を考慮した関連度を計算
        total_importance = 0.0
        for entity in company_entities:
            importance = float(entity['properties'].get('importance', 0.5))
            if trend.lower() in entity['name'].lower() or trend.lower() in entity['description'].lower():
                total_importance += importance
        
        # 正規化（最大値1.0）
        return min(1.0, total_importance / len(company_entities))

    def _calculate_market_factor(
        self,
        trend: str,
        relationships: List[Dict[str, Any]]
    ) -> float:
        """
        トレンドの市場影響度を計算する

        Args:
            trend (str): トレンド名
            relationships (List[Dict[str, Any]]): リレーションシップリスト

        Returns:
            float: 0.0-1.0の市場影響度スコア
        """
        if not relationships:
            return 0.0
        
        # 影響度の強いリレーションシップを評価
        influence_relationships = [
            rel for rel in relationships
            if rel['type'] in ['INFLUENCES', 'DEVELOPS']
        ]
        
        if not influence_relationships:
            return 0.0
        
        # リレーションシップの強度を考慮した影響度を計算
        total_strength = sum(
            float(rel.get('strength', 0.5))
            for rel in influence_relationships
        )
        
        # 正規化（最大値1.0）
        return min(1.0, total_strength / len(influence_relationships))

    def _calculate_novelty_factor(self, trend: str) -> float:
        """
        トレンドの新規性を評価する

        Args:
            trend (str): トレンド名

        Returns:
            float: 0.0-1.0の新規性スコア
        """
        # 現時点では簡易的な実装
        # TODO: 過去のトレンドデータとの比較や時系列分析を追加
        return 0.5

    def _find_related_entities(
        self,
        trend: str,
        entities: List[Dict[str, Any]]
    ) -> List[str]:
        """
        トレンドに関連するエンティティを見つける

        Args:
            trend (str): トレンド名
            entities (List[Dict[str, Any]]): エンティティリスト

        Returns:
            List[str]: 関連エンティティのIDリスト
        """
        related = []
        trend_lower = trend.lower()
        
        for entity in entities:
            if (trend_lower in entity['name'].lower() or
                    trend_lower in entity['description'].lower()):
                related.append(entity['id'])
        
        return related

    def _calculate_market_impact(
        self,
        trend: str,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> float:
        """
        トレンドの市場影響度を総合的に評価する

        Args:
            trend (str): トレンド名
            entities (List[Dict[str, Any]]): エンティティリスト
            relationships (List[Dict[str, Any]]): リレーションシップリスト

        Returns:
            float: 0.0-1.0の市場影響度スコア
        """
        # 企業関連度
        company_factor = self._calculate_company_factor(trend, entities)
        
        # 市場影響度
        market_factor = self._calculate_market_factor(trend, relationships)
        
        # 重み付けして合算
        return (company_factor * 0.6) + (market_factor * 0.4)

    def _calculate_impact_scores(
        self,
        output: Dict[str, Any],
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        trends: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        各エンティティの影響度スコアを計算する

        Args:
            output (Dict[str, Any]): Gemini出力
            entities (List[Dict[str, Any]]): エンティティリスト
            relationships (List[Dict[str, Any]]): 関係性リスト
            trends (List[Dict[str, Any]]): トレンドリスト

        Returns:
            Dict[str, float]: エンティティIDをキー、影響度スコアを値とする辞書
        """
        impact_scores = {}
        
        # すべてのエンティティに対してスコアを計算
        for entity in entities:
            entity_id = entity.get('id')
            if not entity_id:
                continue

            # エンティティの基本スコアを計算
            base_score = 0.5  # デフォルトの基本スコア

            # エンティティタイプに基づくスコア調整
            type_weights = {
                'COMPANY': 0.8,
                'PRODUCT': 0.6,
                'TECHNOLOGY': 0.7,
                'MARKET': 0.8,
                'SERVICE': 0.6
            }
            type_weight = type_weights.get(entity.get('type', ''), 0.5)

            # 関係性の数に基づくスコア調整
            rel_count = sum(1 for rel in relationships if
                          rel.get('source_id') == entity_id or
                          rel.get('target_id') == entity_id)
            rel_factor = min(1.0, rel_count * 0.2)  # 関係性が多いほどスコアが高くなる

            # トレンドとの関連性に基づくスコア調整
            trend_factor = 0.0
            for trend in trends:
                if entity.get('name', '').lower() in trend.get('description', '').lower():
                    trend_factor = max(trend_factor, trend.get('impact', 0.0))

            # 最終スコアの計算
            final_score = (base_score * 0.3 +
                         type_weight * 0.3 +
                         rel_factor * 0.2 +
                         trend_factor * 0.2)

            # スコアを0.0-1.0の範囲に正規化
            impact_scores[entity_id] = min(1.0, max(0.0, final_score))

        return impact_scores

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

        # importanceを数値に変換
        importance = entity.get('importance', 0.5)
        if isinstance(importance, str):
            importance = {
                'high': 0.8,
                'medium': 0.5,
                'low': 0.2
            }.get(importance.lower(), 0.5)

        processed_entity = {
            'id': f"entity_{index}",
            'name': entity['name'],
            'type': entity.get('type', 'ENTITY').upper(),
            'description': entity.get('description', ''),
            'properties': {
                'importance': importance,
                'category': entity.get('category', ''),
                'source': entity.get('source', '')
            }
        }

        if 'properties' in entity and isinstance(entity['properties'], dict):
            for key, value in entity['properties'].items():
                if key not in processed_entity['properties']:
                    processed_entity['properties'][key] = value

        return processed_entity

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