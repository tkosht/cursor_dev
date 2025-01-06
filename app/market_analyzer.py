"""Gemini APIの解析結果から市場分析情報を抽出するモジュール。"""

import logging
from datetime import datetime
from typing import Any, Dict, List

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

            # エンティティの抽出
            entities = self._extract_entities(output.get('entities', []))
            
            # リレーションシップの抽出
            relationships = self._detect_relationships(output.get('relationships', []))
            
            # 影響度スコアの取得
            market_impact = self._calculate_impact_score(output.get('market_impact', 0.5))
            impact_scores = {
                'market_impact': market_impact,
                'technology_impact': self._calculate_impact_score(output.get('technology_impact', 0.5)),
                'social_impact': self._calculate_impact_score(output.get('social_impact', 0.5))
            }
            
            # トレンドの取得
            trends = output.get('trends', [])
            
            return {
                'entities': entities,
                'relationships': relationships,
                'impact_scores': impact_scores,
                'impact': market_impact,  # テストの要件に合わせて追加
                'trends': trends
            }
            
        except Exception as e:
            self.logger.error(f"Gemini出力の処理中にエラーが発生しました: {str(e)}")
            raise

    def _extract_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """エンティティを抽出して検証する"""
        if isinstance(entities, dict) and 'entities' in entities:
            entities = entities['entities']
            
        if not isinstance(entities, list):
            raise ValueError("リスト形式ではありません")

        validated_entities = []
        
        for entity in entities:
            if not isinstance(entity, dict):
                raise ValueError("エンティティは辞書形式である必要があります")

            # 必須フィールドの検証
            required_fields = ['name', 'type']
            missing_fields = [field for field in required_fields if field not in entity]
            if missing_fields:
                raise ValueError(f"必須フィールドが欠けています: {missing_fields}")
            
            # エンティティの検証と整形
            validated_entity = {
                'name': entity['name'],
                'type': entity['type'].upper(),
                'description': entity.get('description', ''),
                'properties': entity.get('properties', {})
            }
            
            validated_entities.append(validated_entity)
        
        return validated_entities

    def _detect_relationships(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """リレーションシップを抽出して検証する"""
        if isinstance(relationships, dict) and 'relationships' in relationships:
            relationships = relationships['relationships']
            
        if not isinstance(relationships, list):
            raise ValueError("リスト形式ではありません")

        validated_relationships = []
        
        for rel in relationships:
            if not isinstance(rel, dict):
                raise ValueError("リレーションシップは辞書形式である必要があります")

            # 必須フィールドの検証
            required_fields = ['type', 'source', 'target']
            missing_fields = [field for field in required_fields if field not in rel]
            if missing_fields:
                raise ValueError(f"必須フィールドが欠けています: {missing_fields}")
            
            # リレーションシップの検証と整形
            validated_rel = {
                'type': rel['type'].upper(),
                'source': rel['source'],
                'target': rel['target'],
                'description': rel.get('description', ''),
                'properties': rel.get('properties', {})
            }
            
            validated_relationships.append(validated_rel)
        
        return validated_relationships

    def _validate_score_type(self, score: Any) -> float:
        """スコアの型を検証し、数値に変換する"""
        if isinstance(score, dict) and 'market_impact' in score:
            score = score['market_impact']
        
        if isinstance(score, str):
            try:
                score = float(score)
            except ValueError:
                raise ValueError("market_impactが数値ではありません")
        elif not isinstance(score, (int, float)):
            raise ValueError("market_impactが数値ではありません")
        
        return float(score)

    def _validate_score_range(self, score: float) -> None:
        """スコアが有効な範囲内かを検証する"""
        if not 0 <= score <= 1:
            raise ValueError("market_impactは0から1の範囲である必要があります")

    def _calculate_impact_score(self, score: Any) -> float:
        """影響度スコアを計算する

        Args:
            score (Any): 影響度スコアの値

        Returns:
            float: 0.0から1.0の範囲の影響度スコア

        Raises:
            ValueError: スコアが範囲外または不正な形式の場合
        """
        try:
            score = self._validate_score_type(score)
            self._validate_score_range(score)
            return score
            
        except (TypeError, ValueError) as e:
            self.logger.error(f"影響度スコアの計算に失敗しました: {str(e)}")
            raise ValueError(str(e)) 