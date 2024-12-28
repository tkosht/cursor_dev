"""
LLMマネージャー
"""
from typing import Any, Dict, Optional, Type

from app.llm.base import BaseLLM
from app.llm.gemini import GeminiLLM
from app.llm.gpt import GPT4LLM


class LLMManager:
    """LLMマネージャー"""
    
    def __init__(self):
        """初期化"""
        self.models: Dict[str, Type[BaseLLM]] = {
            "gemini-2.0-flash-exp": GeminiLLM,
            "gpt-4o": GPT4LLM
        }
        self.instances: Dict[str, BaseLLM] = {}
    
    def load_model(
        self,
        model_name: str,
        api_key: str,
        temperature: float = 0.1
    ) -> BaseLLM:
        """
        モデルをロード

        Args:
            model_name (str): モデル名
            api_key (str): APIキー
            temperature (float, optional): 生成時の温度パラメータ. Defaults to 0.1.

        Returns:
            BaseLLM: LLMインスタンス

        Raises:
            ValueError: モデルが見つからない場合
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        if model_name not in self.instances:
            model_class = self.models[model_name]
            self.instances[model_name] = model_class(
                api_key=api_key,
                model=model_name,
                temperature=temperature
            )
        
        return self.instances[model_name]
    
    def get_model(self, model_name: str) -> Optional[BaseLLM]:
        """
        モデルを取得

        Args:
            model_name (str): モデル名

        Returns:
            Optional[BaseLLM]: LLMインスタンス
        """
        return self.instances.get(model_name)
    
    async def generate_selector(
        self,
        model_name: str,
        html_content: str
    ) -> Dict[str, str]:
        """
        セレクタを生成

        Args:
            model_name (str): モデル名
            html_content (str): HTMLコンテンツ

        Returns:
            Dict[str, str]: 生成されたセレクタ
        """
        model = self.get_model(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not loaded")
        
        result = await model.analyze_content(html_content, "selector")
        return result
    
    async def generate_content(
        self,
        model_name: str,
        html_content: str
    ) -> Dict[str, Any]:
        """
        コンテンツを生成

        Args:
            model_name (str): モデル名
            html_content (str): HTMLコンテンツ

        Returns:
            Dict[str, Any]: 生成されたコンテンツ
        """
        model = self.get_model(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not loaded")
        
        result = await model.analyze_content(html_content, "extract")
        return result
    
    async def analyze_error(
        self,
        model_name: str,
        error_content: str
    ) -> Dict[str, Any]:
        """
        エラーを分析

        Args:
            model_name (str): モデル名
            error_content (str): エラー情報

        Returns:
            Dict[str, Any]: 分析結果
        """
        model = self.get_model(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not loaded")
        
        result = await model.analyze_content(error_content, "error")
        return result
    
    def get_metrics(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        メトリクスを取得

        Args:
            model_name (str): モデル名

        Returns:
            Optional[Dict[str, Any]]: メトリクス
        """
        model = self.get_model(model_name)
        if not model:
            return None
        
        metrics = model.get_metrics()
        return metrics.model_dump()
    
    def reset_metrics(self, model_name: str) -> None:
        """
        メトリクスをリセット

        Args:
            model_name (str): モデル名
        """
        model = self.get_model(model_name)
        if model:
            model.reset_metrics() 
    
    async def analyze_html_structure(self, html: str) -> Dict[str, Any]:
        """
        HTMLの構造を分析

        Args:
            html (str): HTML文字列

        Returns:
            Dict[str, Any]: 分析結果
        """
        model = self._get_default_model()
        result = await model.analyze_content(html, "structure")
        return result
    
    async def generate_selectors(
        self,
        html: str,
        target_data: Dict[str, str]
    ) -> Dict[str, str]:
        """
        セレクタを生成

        Args:
            html (str): HTML文字列
            target_data (Dict[str, str]): 取得対象データの辞書

        Returns:
            Dict[str, str]: セレクタの辞書
        """
        model = self._get_default_model()
        result = await model.analyze_content(
            {
                "html": html,
                "target_data": target_data
            },
            "selector"
        )
        return result
    
    async def validate_data(
        self,
        data: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> bool:
        """
        データを検証

        Args:
            data (Dict[str, Any]): 検証対象データの辞書
            rules (Dict[str, Any]): 検証ルールの辞書

        Returns:
            bool: 検証結果
        """
        model = self._get_default_model()
        result = await model.analyze_content(
            {
                "data": data,
                "rules": rules
            },
            "validate"
        )
        return result.get("is_valid", False)
    
    def _get_default_model(self) -> BaseLLM:
        """
        デフォルトのモデルを取得

        Returns:
            BaseLLM: デフォルトのLLMインスタンス

        Raises:
            ValueError: モデルがロードされていない場合
        """
        # 最初に見つかったモデルを使用
        for model in self.instances.values():
            return model
        
        raise ValueError("No model loaded") 