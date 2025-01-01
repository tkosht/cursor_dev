"""
設定管理モジュール

アプリケーションの設定を管理します。
"""

import os
from typing import Any, Dict, Optional

import yaml


class ConfigManager:
    """設定管理クラス"""

    def __init__(self, config_file: str):
        """
        初期化

        Args:
            config_file: 設定ファイルのパス
        
        Raises:
            ValueError: 設定ファイルが存在しない場合
        """
        if not config_file or not os.path.exists(config_file):
            raise ValueError(f"Config file not found: {config_file}")
        
        self._config_file = config_file
        self._config: Dict[str, Any] = {}
        self.reload()

    def get_config(self) -> Dict[str, Any]:
        """
        設定全体を取得

        Returns:
            設定データ
        """
        return self._config.copy()

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        指定セクションの設定を取得

        Args:
            section: セクション名

        Returns:
            セクションの設定データ
        """
        return self._config.get(section, {}).copy()

    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        設定を更新

        Args:
            updates: 更新データ

        Raises:
            ValueError: 不正な値が指定された場合
        """
        self._validate_updates(updates)
        
        for section, values in updates.items():
            if section not in self._config:
                self._config[section] = {}
            self._config[section].update(values)

    def reload(self) -> None:
        """設定を再読み込み"""
        with open(self._config_file, "r") as f:
            self._config = yaml.safe_load(f) or {}
        
        # 環境変数による上書き
        self._apply_environment_overrides()

    def save_config(self, file_path: Optional[str] = None) -> None:
        """
        設定を保存

        Args:
            file_path: 保存先ファイルパス（省略時は現在の設定ファイル）
        """
        target_path = file_path or self._config_file
        with open(target_path, "w") as f:
            yaml.safe_dump(self._config, f)

    def _validate_updates(self, updates: Dict[str, Any]) -> None:
        """
        更新データを検証

        Args:
            updates: 検証対象データ

        Raises:
            ValueError: 不正な値が含まれる場合
        """
        for section, values in updates.items():
            if section == "timeouts":
                for key, value in values.items():
                    if not isinstance(value, (int, float)) or value < 0:
                        raise ValueError(
                            f"Invalid timeout value for {key}: {value}"
                        )
            
            elif section == "thresholds":
                for key, value in values.items():
                    if not isinstance(value, (int, float)) or value < 0 or value > 1:
                        raise ValueError(
                            f"Invalid threshold value for {key}: {value}"
                        )

    def _apply_environment_overrides(self) -> None:
        """環境変数による設定の上書き"""
        # タイムアウト設定の上書き
        llm_timeout = os.getenv("APP_TIMEOUT_LLM")
        if llm_timeout:
            if "timeouts" not in self._config:
                self._config["timeouts"] = {}
            self._config["timeouts"]["llm"] = int(llm_timeout)
        
        # リトライ設定の上書き
        max_attempts = os.getenv("APP_RETRY_MAX_ATTEMPTS")
        if max_attempts:
            if "retry" not in self._config:
                self._config["retry"] = {}
            self._config["retry"]["max_attempts"] = int(max_attempts) 