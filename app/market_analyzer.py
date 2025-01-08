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
            market_impact = self._calculate_impact_score(output.get('market_impact', 0.5))
            
            # 各エンティティに対する影響度スコアを生成
            impact_scores = {}
            for entity in entities:
                # エンティティの重要度に基づいてスコアを調整
                properties = entity.get('properties', {})
                importance = properties.get('importance', 'medium')
                importance_factor = {
                    'high': 1.0,
                    'medium': 0.7,
                    'low': 0.4
                }.get(importance, 0.7)
                
                impact_scores[entity['id']] = importance_factor * market_impact
            
            return {
                'entities': entities,
                'relationships': relationships,
                'impact_scores': impact_scores,
                'impact': market_impact,  # テストの要件に合わせて追加
                'trends': output.get('trends', [])
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
                if not isinstance(entity, dict):
                    continue

                # 必須フィールドの確認
                name = entity.get('name')
                if not name:
                    continue

                # エンティティの作成
                processed_entity = self._create_entity(i, entity)
                if processed_entity:
                    processed_entities.append(processed_entity)

            return processed_entities

        except Exception as e:
            self.logger.error(f"エンティティの抽出中にエラーが発生しました: {str(e)}")
            return []

    def _create_entity(self, index: int, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        エンティティを作成する

        Args:
            index: エンティティのインデックス
            entity: 元のエンティティデータ

        Returns:
            Dict[str, Any]: 処理済みのエンティティ
        """
        # 基本プロパティの設定
        processed_entity = {
            'id': f"entity_{index}",  # 一意のIDを生成
            'name': entity['name'],
            'type': entity.get('type', 'Entity'),  # デフォルトタイプを設定
            'content': entity.get('description', ''),  # 要件に合わせてdescriptionをcontentとして使用
            'source': entity.get('source', ''),
            'timestamp': datetime.now().isoformat(),  # 現在時刻を設定
            'impact': entity.get('importance_score', 0.5),  # デフォルトの影響度
            'category': entity.get('category', ''),
            'importance': entity.get('importance', 'medium')
        }

        # その他のプロパティを追加（既存のキーは上書きしない）
        if 'properties' in entity and isinstance(entity['properties'], dict):
            for key, value in entity['properties'].items():
                if key not in processed_entity and isinstance(value, (str, int, float, bool)):
                    processed_entity[key] = value

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

        # 係タイプの検証
        valid_types = {'INFLUENCES', 'COMPETES', 'DEVELOPS', 'PARTICIPATES'}
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
            # 基本スコアの検証と変換
            base_score = self._validate_score_type(score)
            self._validate_score_range(base_score)

            # 市場トレンドと企業動向の影響を考慮
            trend_factor = self._calculate_trend_factor()
            company_factor = self._calculate_company_factor()
            
            # 最終スコアの計算（各要素を重み付けして合算）
            final_score = (
                base_score * 0.5 +  # 基本スコア（50%）
                trend_factor * 0.3 +  # トレンドの影響（30%）
                company_factor * 0.2  # 企業動向の影響（20%）
            )

            # 0.0-1.0の範囲に正規化
            return max(0.0, min(1.0, final_score))
            
        except (TypeError, ValueError) as e:
            self.logger.error(f"影響度スコアの計算に失敗しました: {str(e)}")
            raise ValueError(str(e))

    def _calculate_trend_factor(self) -> float:
        """市場トレンドの影響度を計算する

        Returns:
            float: 0.0から1.0の範囲のトレンド影響度

        Note:
            以下の要素を考慮してトレンド影響度を計算:
            1. トレンドの新規性（最近のトレンドか）
            2. トレンドの重要度（市場への影響度）
            3. トレンドの関連企業数（どれだけの企業が関与しているか）
        """
        try:
            # トレンドの重要度を評価（0.0-1.0）
            trend_importance = self._evaluate_trend_importance()
            
            # トレンドの新規性を評価（0.0-1.0）
            trend_novelty = self._evaluate_trend_novelty()
            
            # トレンドの関連企業数を評価（0.0-1.0）
            trend_coverage = self._evaluate_trend_coverage()
            
            # 各要素を重み付けして合算
            trend_factor = (
                trend_importance * 0.4 +  # 重要度（40%）
                trend_novelty * 0.3 +     # 新規性（30%）
                trend_coverage * 0.3      # 関連企業数（30%）
            )
            
            # 0.0-1.0の範囲に正規化
            return max(0.0, min(1.0, trend_factor))
            
        except Exception as e:
            self.logger.error(f"トレンド影響度の計算に失敗しました: {str(e)}")
            return 0.5  # エラー時は中間値を返す

    def _evaluate_trend_importance(self) -> float:
        """トレンドの重要度を評価する

        Returns:
            float: 0.0から1.0の範囲のトレンド重要度

        Note:
            以下の要素を考慮してトレンド重要度を評価:
            1. トレンドの市場影響度（Geminiの分析結果）
            2. トレンドに関連する企業の重要度
            3. トレンドの言及頻度
        """
        try:
            # Geminiの分析結果からトレンドの市場影響度を取得
            market_impact = self._get_trend_market_impact()
            
            # トレンドに関連する企業の重要度を評価
            company_importance = self._get_trend_company_importance()
            
            # トレンドの言及頻度を評価
            mention_frequency = self._get_trend_mention_frequency()
            
            # 各要素を重み付けして合算
            importance = (
                market_impact * 0.4 +       # 市場影響度（40%）
                company_importance * 0.4 +   # 企業重要度（40%）
                mention_frequency * 0.2      # 言及頻度（20%）
            )
            
            # 0.0-1.0の範囲に正規化
            return max(0.0, min(1.0, importance))
            
        except Exception as e:
            self.logger.error(f"トレンド重要度の評価に失敗しました: {str(e)}")
            return 0.5  # エラー時は中間値を返す

    def _get_trend_market_impact(self) -> float:
        """トレンドの市場影響度を取得する"""
        try:
            # Geminiの分析結果から市場影響度を取得
            # TODO: 実際の市場影響度の取得ロジックを実装
            # 現時点では中間値を返す
            return 0.5
            
        except Exception as e:
            self.logger.error(f"トレンドの市場影響度の取得に失敗しました: {str(e)}")
            return 0.5

    def _get_trend_company_importance(self) -> float:
        """トレンドに関連する企業の重要度を評価する"""
        try:
            # トレンドに関連する企業の重要度を評価
            # TODO: 実際の企業重要度の評価ロジックを実装
            # 現時点では中間値を返す
            return 0.5
            
        except Exception as e:
            self.logger.error(f"トレンドの企業重要度の評価に失敗しました: {str(e)}")
            return 0.5

    def _get_trend_mention_frequency(self) -> float:
        """トレンドの言及頻度を評価する"""
        try:
            # トレンドの言及頻度を評価
            # TODO: 実際の言及頻度の評価ロジックを実装
            # 現時点では中間値を返す
            return 0.5
            
        except Exception as e:
            self.logger.error(f"トレンドの言及頻度の評価に失敗しました: {str(e)}")
            return 0.5

    def _evaluate_trend_novelty(self) -> float:
        """トレンドの新規性を評価する

        Returns:
            float: 0.0から1.0の範囲のトレンド新規性

        Note:
            以下の要素を考慮してトレンド新規性を評価:
            1. トレンドの初出時期（最初の言及時期）
            2. トレンドの言及頻度の変化（急激な増加は新規性が高い）
            3. 類似トレンドとの比較
        """
        try:
            # トレンドの初出時期を評価
            first_mention = self._evaluate_first_mention()
            
            # トレンドの言及頻度の変化を評価
            mention_change = self._evaluate_mention_change()
            
            # 類似トレンドとの比較を評価
            similarity = self._evaluate_trend_similarity()
            
            # 各要素を重み付けして合算
            novelty = (
                first_mention * 0.4 +    # 初出時期（40%）
                mention_change * 0.4 +   # 言及頻度の変化（40%）
                similarity * 0.2         # 類似性（20%）
            )
            
            # 0.0-1.0の範囲に正規化
            return max(0.0, min(1.0, novelty))
            
        except Exception as e:
            self.logger.error(f"トレンド新規性の評価に失敗しました: {str(e)}")
            return 0.5  # エラー時は中間値を返す

    def _evaluate_first_mention(self) -> float:
        """トレンドの初出時期を評価する"""
        try:
            # トレンドの初出時期を評価
            # TODO: 実際の初出時期の評価ロジックを実装
            # 現時点では中間値を返す
            return 0.5
            
        except Exception as e:
            self.logger.error(f"トレンドの初出時期の評価に失敗しました: {str(e)}")
            return 0.5

    def _evaluate_mention_change(self) -> float:
        """トレンドの言及頻度の変化を評価する"""
        try:
            # トレンドの言及頻度の変化を評価
            # TODO: 実際の言及頻度変化の評価ロジックを実装
            # 現時点では中間値を返す
            return 0.5
            
        except Exception as e:
            self.logger.error(f"トレンドの言及頻度変化の評価に失敗しました: {str(e)}")
            return 0.5

    def _evaluate_trend_similarity(self) -> float:
        """類似トレンドとの比較を評価する"""
        try:
            # 類似トレンドとの比較を評価
            # TODO: 実際の類似性評価ロジックを実装
            # 現時点では中間値を返す
            return 0.5
            
        except Exception as e:
            self.logger.error(f"トレンドの類似性評価に失敗しました: {str(e)}")
            return 0.5

    def _evaluate_trend_coverage(self) -> float:
        """トレンドの関連企業数を評価する

        Returns:
            float: 0.0から1.0の範囲のトレンドカバレッジ

        Note:
            以下の要素を考慮してトレンドカバレッジを評価:
            1. 関連企業の総数
            2. 関連企業の市場シェア
            3. 関連企業の業界分布
        """
        try:
            # 関連企業の総数を評価
            company_count = self._evaluate_company_count()
            
            # 関連企業の市場シェアを評価
            market_share = self._evaluate_market_share()
            
            # 関連企業の業界分布を評価
            industry_distribution = self._evaluate_industry_distribution()
            
            # 各要素を重み付けして合算
            coverage = (
                company_count * 0.4 +          # 企業数（40%）
                market_share * 0.4 +           # 市場シェア（40%）
                industry_distribution * 0.2     # 業界分布（20%）
            )
            
            # 0.0-1.0の範囲に正規化
            return max(0.0, min(1.0, coverage))
            
        except Exception as e:
            self.logger.error(f"トレンドカバレッジの評価に失敗しました: {str(e)}")
            return 0.5  # エラー時は中間値を返す

    def _evaluate_company_count(self) -> float:
        """関連企業の総数を評価する"""
        try:
            # 関連企業の総数を評価
            # TODO: 実際の企業数の評価ロジックを実装
            # 現時点では中間値を返す
            return 0.5
            
        except Exception as e:
            self.logger.error(f"関連企業数の評価に失敗しました: {str(e)}")
            return 0.5

    def _evaluate_market_share(self) -> float:
        """関連企業の市場シェアを評価する"""
        try:
            # 関連企業の市場シェアを評価
            # TODO: 実際の市場シェアの評価ロジックを実装
            # 現時点では中間値を返す
            return 0.5
            
        except Exception as e:
            self.logger.error(f"市場シェアの評価に失敗しました: {str(e)}")
            return 0.5

    def _evaluate_industry_distribution(self) -> float:
        """関連企業の業界分布を評価する"""
        try:
            # 関連企業の業界分布を評価
            # TODO: 実際の業界分布の評価ロジックを実装
            # 現時点では中間値を返す
            return 0.5
            
        except Exception as e:
            self.logger.error(f"業界分布の評価に失敗しました: {str(e)}")
            return 0.5

    def _calculate_company_factor(self) -> float:
        """企業動向の影響度を計算する"""
        # TODO: 実際の企業分析に基づいて計算
        # 現時点では中間値を返す
        return 0.5 