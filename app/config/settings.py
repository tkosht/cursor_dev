"""
グローバル設定の管理
"""
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLMの設定"""

    default_model: str = Field(
        default="gemini-2.0-flash-exp", description="デフォルトのLLMモデル"
    )
    temperature: float = Field(default=0.1, description="生成時の温度パラメータ")
    max_retries: int = Field(default=3, description="リトライ回数")


class CrawlerConfig(BaseModel):
    """クローラーの設定"""

    max_concurrent: int = Field(default=5, description="最大同時実行数")
    update_interval: int = Field(default=3600, description="更新間隔（秒）")
    timeout: int = Field(default=30, description="タイムアウト時間（秒）")
    retry_interval: int = Field(default=60, description="リトライ間隔（秒）")


class GlobalSettings(BaseModel):
    """グローバル設定"""

    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLMの設定")
    crawler: CrawlerConfig = Field(
        default_factory=CrawlerConfig, description="クローラーの設定"
    )

    @classmethod
    def load_from_file(cls, file_path: str) -> "GlobalSettings":
        """
        設定ファイルから読み込み

        Args:
            file_path (str): 設定ファイルのパス

        Returns:
            GlobalSettings: 設定オブジェクト
        """
        with open(file_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
            return cls.model_validate(config_dict)

    def save_to_file(self, file_path: str) -> None:
        """
        設定ファイルに保存

        Args:
            file_path (str): 設定ファイルのパス
        """
        config_dict = self.model_dump()
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_dict, f, allow_unicode=True)


_settings: Optional[GlobalSettings] = None


def get_settings() -> GlobalSettings:
    """
    グローバル設定を取得

    Returns:
        GlobalSettings: 設定オブジェクト
    """
    global _settings
    if _settings is None:
        _settings = GlobalSettings()
    return _settings


def load_settings(file_path: str) -> GlobalSettings:
    """
    設定ファイルから設定を読み込み

    Args:
        file_path (str): 設定ファイルのパス

    Returns:
        GlobalSettings: 設定オブジェクト
    """
    global _settings
    _settings = GlobalSettings.load_from_file(file_path)
    return _settings
