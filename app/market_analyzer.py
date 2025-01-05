"""Gemini APIの解析結果から市場分析情報を抽出するモジュール。"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Gemini APIの解析結果から市場分析情報を抽出するクラス。"""

    def process_gemini_output(self, gemini_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        GeminiAnalyzerの解析結果から市場影響度、関連企業、関係性などを抽出する。

        Args:
            gemini_result (Dict[str, Any]): GeminiAnalyzerからの解析結果

        Returns:
            Dict[str, Any]: {
                "entities": List[Dict],  # 抽出されたエンティティ
                "relationships": List[Dict],  # エンティティ間の関係
                "impact": float,  # 市場影響度
                "trends": List[str]  # 市場トレンド
            }

        Raises:
            ValueError: 入力が不正な場合
        """
        if not isinstance(gemini_result, dict):
            raise ValueError("解析結果が辞書形式ではありません。")

        try:
            entities = self._extract_entities(gemini_result)
            relationships = self._detect_relationships(gemini_result)
            impact = self._calculate_impact_score(gemini_result)
            trends = gemini_result.get("trends", [])

            return {
                "entities": entities,
                "relationships": relationships,
                "impact": impact,
                "trends": trends
            }

        except Exception as e:
            logger.error(f"解析結果の処理中にエラーが発生しました: {str(e)}")
            raise ValueError(f"解析結果の処理に失敗しました: {str(e)}")

    def _extract_entities(self, gemini_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        エンティティ（企業名、製品名など）を抽出する。

        Args:
            gemini_result (Dict[str, Any]): GeminiAnalyzerからの解析結果

        Returns:
            List[Dict[str, str]]: 抽出されたエンティティのリスト

        Raises:
            ValueError: エンティティの形式が不正な場合
        """
        entities = gemini_result.get("entities", [])
        if not isinstance(entities, list):
            raise ValueError("entitiesがリスト形式ではありません。")

        validated_entities = []
        for entity in entities:
            if not isinstance(entity, dict):
                continue

            # 必須フィールドの存在確認
            if not all(key in entity for key in ["name", "type", "description"]):
                continue

            # エンティティタイプの検証
            if entity["type"] not in ["COMPANY", "PRODUCT", "KEYWORD"]:
                continue

            validated_entities.append({
                "name": entity["name"],
                "type": entity["type"],
                "description": entity["description"]
            })

        return validated_entities

    def _detect_relationships(self, gemini_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        エンティティ間の関係性を特定する。

        Args:
            gemini_result (Dict[str, Any]): GeminiAnalyzerからの解析結果

        Returns:
            List[Dict[str, Any]]: 関係性のリスト

        Raises:
            ValueError: 関係性の形式が不正な場合
        """
        relationships = gemini_result.get("relationships", [])
        if not isinstance(relationships, list):
            raise ValueError("relationshipsがリスト形式ではありません。")

        validated_relationships = []
        for rel in relationships:
            if not isinstance(rel, dict):
                continue

            # 必須フィールドの存在確認
            if not all(key in rel for key in ["source", "target", "type", "description"]):
                continue

            # 関係性タイプの検証
            if rel["type"] not in ["INFLUENCES", "COMPETES", "PARTICIPATES"]:
                continue

            validated_relationships.append({
                "source": rel["source"],
                "target": rel["target"],
                "type": rel["type"],
                "description": rel["description"]
            })

        return validated_relationships

    def _calculate_impact_score(self, gemini_result: Dict[str, Any]) -> float:
        """
        市場影響度を算出する。

        Args:
            gemini_result (Dict[str, Any]): GeminiAnalyzerからの解析結果

        Returns:
            float: 0.0-1.0の範囲の市場影響度

        Raises:
            ValueError: impact_scoreが不正な場合
        """
        impact_score = gemini_result.get("impact_score")
        if not isinstance(impact_score, (int, float)):
            raise ValueError("impact_scoreが数値ではありません。")

        if not 0.0 <= impact_score <= 1.0:
            raise ValueError("impact_scoreが0.0-1.0の範囲外です。")

        return float(impact_score) 