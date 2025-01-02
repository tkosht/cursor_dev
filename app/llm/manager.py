"""
LLMを使用した評価を管理するモジュール
"""
import json
import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)


class LLMManager:
    """LLMを使用した評価を管理するクラス"""

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash-exp",
        temperature: float = 0.1,
        api_key: Optional[str] = None
    ):
        """LLMManagerを初期化する。

        Args:
            model_name (str): 使用するモデル名
            temperature (float): 生成時の温度パラメータ
            api_key (Optional[str]): APIキー。未指定の場合は環境変数から取得。
        """
        self._model_name = model_name
        self._temperature = temperature
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        # LLMインスタンスを初期化
        if self._model_name.startswith("gemini"):
            from .gemini import GeminiLLM
            self._llm = GeminiLLM(
                model_name=self._model_name,
                temperature=self._temperature,
                api_key=self._api_key
            )
        else:
            raise ValueError(f"未対応のモデル: {self._model_name}")
        
        logger.debug(
            f"Initialized LLMManager with model={self._model_name}, "
            f"temperature={self._temperature}"
        )

    async def generate_search_keywords(
        self,
        company_code: str,
        target_fields: List[str]
    ) -> List[str]:
        """検索キーワードを生成

        Args:
            company_code: 企業コード
            target_fields: 必要なフィールドのリスト

        Returns:
            List[str]: 生成されたキーワードのリスト
        """
        prompt = self._build_search_keywords_prompt(company_code, target_fields)
        response = await self._llm.generate(prompt)
        if not response:
            return []

        try:
            result = json.loads(response)
            return result.get("keywords", [])
        except json.JSONDecodeError:
            logger.error("Failed to parse keywords response")
            return []

    def _build_search_keywords_prompt(
        self,
        company_code: str,
        target_fields: List[str]
    ) -> str:
        """検索キーワード生成用のプロンプトを構築"""
        return f"""
以下の企業コードと必要なフィールドに基づいて、IR情報を検索するためのキーワードを生成してください。
キーワードは検索エンジンで使用することを想定しています。

企業コード: {company_code}
必要なフィールド: {json.dumps(target_fields, ensure_ascii=False)}

以下のフォーマットでJSONを返してください:
{{
    "keywords": [
        "キーワード1",
        "キーワード2",
        ...
    ]
}}
"""
