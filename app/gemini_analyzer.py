"""Gemini APIを使用してコンテンツ分析モジュール。"""

import json
import logging
from typing import Any, Dict

import google.generativeai as genai

from app.exceptions import GeminiError, ValidationError
from app.monitoring import PerformanceMonitor

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """Gemini APIを使用してコンテンツを分析するクラス。"""

    def __init__(self, api_key: str):
        """初期化。

        Args:
            api_key: Gemini APIキー

        Raises:
            ValidationError: APIキーが不正な場合
        """
        if not isinstance(api_key, str) or not api_key:
            raise ValidationError("APIキーは空でない文字列である必要があります")

        genai.configure(api_key=api_key)
        self._performance_monitor = PerformanceMonitor()
        self._request_count = 0
        self._error_count = 0

    def analyze_content(self, content: Dict[str, str]) -> dict:
        """コンテンツを分析する。

        Args:
            content: 分析対象のコンテンツ

        Returns:
            dict: 分析結果

        Raises:
            ValidationError: 入力値が不正な場合
            GeminiError: API呼び出しに失敗した場合
        """
        self._validate_input(content)

        try:
            prompt = self._create_prompt(content)
            model = self._get_model()
            response = self._generate_response(model, prompt)
            result = self._process_response(response)
            parsed_result = self._parse_response(result)
            self._validate_analysis_result(parsed_result)
            return parsed_result
        except (ValidationError, GeminiError):
            self._error_count += 1
            raise

    def _validate_input(self, content: Dict[str, str]) -> bool:
        """入力コンテンツを検証する。

        Args:
            content: 検証対象のコンテンツ

        Returns:
            bool: 検証結果

        Raises:
            ValidationError: 検証に失敗した場合
        """
        if not isinstance(content, dict):
            raise ValidationError("コンテンツは辞書型である必要があります")

        required_keys = {'title', 'content', 'date', 'url'}
        missing_keys = required_keys - set(content.keys())
        if missing_keys:
            raise ValidationError(f"必須キーが欠落しています: {missing_keys}")

        for key in required_keys:
            if not isinstance(content[key], str):
                raise ValidationError(f"{key}は文字列型である必要があります")

        return True

    def get_metrics(self) -> dict:
        """メトリクスを取得する。

        Returns:
            dict: メトリクス情報
        """
        return {
            'request_count': self._request_count,
            'error_count': self._error_count,
            'average_response_time': self._performance_monitor.get_average('api_call'),
            'p95_response_time': self._performance_monitor.get_percentile('api_call', 95),
            'p99_response_time': self._performance_monitor.get_percentile('api_call', 99)
        }

    def _create_prompt(self, content: Dict[str, str]) -> str:
        """プロンプトを生成する。

        Args:
            content: 分析対象のコンテンツ

        Returns:
            str: 生成されたプロンプト
        """
        return f"""
        以下のコンテンツを分析し、エンティティと関係性を抽出してください。
        
        タイトル: {content['title']}
        本文: {content['content']}
        日付: {content['date']}
        URL: {content['url']}
        
        以下のJSON形式で出力してください:
        {{
            "entities": [
                {{"id": "string", "name": "string", "type": "string"}}
            ],
            "relationships": [
                {{"source": "string", "target": "string", "type": "string"}}
            ],
            "impact_scores": {{
                "entity_id": float  // 0.0から1.0の範囲
            }}
        }}
        """

    def _get_model(self) -> Any:
        """Geminiモデルを取得する。

        Returns:
            Any: Geminiモデル

        Raises:
            GeminiError: モデルの取得に失敗した場合
        """
        try:
            return genai.GenerativeModel('gemini-pro')
        except Exception as e:
            raise GeminiError(f"モデルの取得に失敗しました: {str(e)}")

    def _generate_response(self, model: Any, prompt: str) -> Any:
        """レスポンスを生成する。

        Args:
            model: Geminiモデル
            prompt: プロンプト

        Returns:
            Any: 生成されたレスポンス

        Raises:
            GeminiError: レスポンスの生成に失敗した場合
        """
        try:
            return model.generate_content(prompt)
        except Exception as e:
            raise GeminiError(f"レスポンスの生成に失敗しました: {str(e)}")

    def _process_response(self, response: Any) -> str:
        """レスポンスを処理する。

        Args:
            response: APIレスポンス

        Returns:
            str: 処理されたレスポンス

        Raises:
            GeminiError: レスポンスの処理に失敗した場合
        """
        try:
            if not response.text:
                raise GeminiError("空のレスポンスが返されました")
            return response.text
        except Exception as e:
            raise GeminiError(f"レスポンスの処理に失敗しました: {str(e)}")

    def _parse_response(self, response: str) -> dict:
        """APIレスポンスをパースする。

        Args:
            response: APIレスポンス（JSON文字列）

        Returns:
            dict: パースされたレスポンス

        Raises:
            ValidationError: レスポンスの形式が不正な場合
        """
        try:
            # レスポンスからJSON部分を抽出
            text = response.strip()
            if text.startswith('```json'):
                text = text[7:]  # '```json'を削除
            if text.endswith('```'):
                text = text[:-3]  # '```'を削除
            text = text.strip()

            # シングルクォートをダブルクォートに置換
            text = text.replace("'", '"')

            # JSONパース
            result = json.loads(text)
            if not isinstance(result, dict):
                raise ValidationError("APIレスポンスが辞書型ではありません")
            return result
        except json.JSONDecodeError as e:
            raise ValidationError(f"APIレスポンスのJSONパースに失敗しました: {str(e)}")

    def _validate_result_type(self, result: Any) -> None:
        """分析結果の型を検証する。

        Args:
            result: 検証対象の分析結果

        Raises:
            ValidationError: 型が不正な場合
        """
        if not isinstance(result, dict):
            raise ValidationError("分析結果が辞書型ではありません")

    def _validate_required_keys(self, result: Dict[str, Any]) -> None:
        """必須キーの存在を検証する。

        Args:
            result: 検証対象の分析結果

        Raises:
            ValidationError: 必須キーが存在しない場合
        """
        required_keys = {"entities", "relationships", "impact_scores"}
        missing_keys = required_keys - set(result.keys())
        if missing_keys:
            raise ValidationError(f"必須キーが不足しています: {missing_keys}")

    def _validate_field_types(self, result: Dict[str, Any]) -> None:
        """各フィールドの型を検証する。

        Args:
            result: 検証対象の分析結果

        Raises:
            ValidationError: フィールドの型が不正な場合
        """
        if not isinstance(result["entities"], list):
            raise ValidationError("entitiesがリスト型ではありません")
        if not isinstance(result["relationships"], list):
            raise ValidationError("relationshipsがリスト型ではありません")
        if not isinstance(result["impact_scores"], dict):
            raise ValidationError("impact_scoresが辞書型ではありません")

    def _validate_impact_scores(self, result: Dict[str, Any]) -> None:
        """影響度スコアを検証する。

        Args:
            result: 検証対象の分析結果

        Raises:
            ValidationError: 影響度スコアが不正な場合
        """
        for entity_id, score in result["impact_scores"].items():
            if not isinstance(score, (int, float)):
                raise ValidationError(f"影響度スコアが数値型ではありません: {entity_id}")
            if not 0 <= score <= 1:
                raise ValidationError(f"影響度スコアが0-1の範囲外です: {entity_id}")

    def _validate_analysis_result(self, result: Dict[str, Any]) -> None:
        """分析結果を検証する。

        Args:
            result: 検証対象の分析結果

        Raises:
            ValidationError: 検証に失敗した場合
        """
        self._validate_result_type(result)
        self._validate_required_keys(result)
        self._validate_field_types(result)
        self._validate_impact_scores(result) 