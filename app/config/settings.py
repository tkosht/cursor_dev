"""
設定管理

アプリケーションの設定を管理するモジュール
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ..logger import CustomLogger


class SettingsError(Exception):
    """Settings固有のエラー"""
    pass


class Settings:
    """設定管理クラス"""

    _instance = None
    _initialized = False
    _config_dir = None

    def __new__(cls, config_dir: Optional[Path] = None):
        """
        シングルトンパターンの実装
        config_dirが指定された場合は、それを保持する
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._config_dir = config_dir
        elif config_dir is not None and cls._config_dir != config_dir:
            cls._config_dir = config_dir
            cls._initialized = False  # 設定ディレクトリが変更された場合は再初期化
        return cls._instance

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Settingsの初期化
        シングルトンパターンを使用し、一度だけ初期化を行う

        Args:
            config_dir: 設定ファイルのディレクトリパス（テスト用）
        """
        if Settings._initialized:
            return

        self.logger = CustomLogger(__name__)
        self.logger.info("設定管理の初期化を開始")

        try:
            # デフォルト設定
            self._defaults = {
                "search_engine": {
                    "model_name": "intfloat/multilingual-e5-large",
                    "use_gpu": True,
                    "top_k": 5
                },
                "logging": {
                    "max_bytes": 10 * 1024 * 1024,  # 10MB
                    "backup_count": 5,
                    "debug_dir": "logs/debug",
                    "info_dir": "logs/info",
                    "error_dir": "logs/error"
                },
                "ui": {
                    "title": "ブックマーク検索",
                    "geometry": "800x600",
                    "theme": "default"
                }
            }

            # 設定ファイルのパス
            self.config_dir = Settings._config_dir if Settings._config_dir is not None else Path.home() / ".bookmarksearch"
            self.config_file = self.config_dir / "config.json"

            # 設定の読み込み
            self._settings = self._defaults.copy()
            self._load_settings()
            Settings._initialized = True
            self.logger.info("設定管理の初期化が完了")

        except Exception as e:
            Settings._initialized = False  # 初期化に失敗した場合はフラグをリセット
            error_msg = f"設定管理の初期化に失敗: {e}"
            self.logger.error(error_msg)
            raise SettingsError(error_msg)

    def _load_settings(self) -> None:
        """設定ファイルから設定を読み込む"""
        self.logger.debug("設定ファイルの読み込みを開始")
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        error_msg = "設定ファイルが空です"
                        self.logger.error(error_msg)
                        raise SettingsError(error_msg)
                    try:
                        user_settings = json.loads(content)
                        self.logger.info("既存の設定ファイルを読み込み")
                        # デフォルト設定とユーザー設定をマージ
                        self._settings = self._merge_settings(self._defaults, user_settings)
                    except json.JSONDecodeError as e:
                        error_msg = f"設定ファイルの形式が不正: {e}"
                        self.logger.error(error_msg)
                        raise SettingsError(error_msg)
            else:
                self.logger.info("デフォルト設定を使用")
                self._settings = self._defaults.copy()

        except Exception as e:
            if not isinstance(e, SettingsError):
                error_msg = f"設定ファイルの読み込みに失敗: {e}"
                self.logger.error(error_msg)
                raise SettingsError(error_msg)
            raise

    def _save_settings(self) -> None:
        """設定をファイルに保存する"""
        self.logger.debug("設定ファイルの保存を開始")
        try:
            # 設定ディレクトリが存在しない場合は作成
            os.makedirs(self.config_dir, exist_ok=True)
            
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=4, ensure_ascii=False)
            self.logger.info("設定ファイルを保存", {"file": str(self.config_file)})

        except Exception as e:
            error_msg = f"設定ファイルの保存に失敗: {e}"
            self.logger.error(error_msg)
            raise SettingsError(error_msg)

    def _merge_settings(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        設定をマージする
        base: ベースとなる設定
        update: 更新する設定
        """
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """
        設定値を取得する
        key: 設定のキー（ドット区切りで階層を表現）
        default: キーが存在しない場合のデフォルト値
        """
        self.logger.debug("設定値の取得", {"key": key})
        try:
            value = self._settings
            for k in key.split("."):
                value = value[k]
            return value
        except (KeyError, TypeError):
            self.logger.warning("設定が存在しません", {"key": key})
            return default

    def set(self, key: str, value: Any) -> None:
        """
        設定値を更新する
        key: 設定のキー（ドット区切りで階層を表現）
        value: 設定値
        """
        self.logger.info("設定値の更新", {"key": key, "value": value})
        keys = key.split(".")
        current = self._settings
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        self._save_settings()

    def reset(self, key: Optional[str] = None) -> None:
        """
        設定をリセットする
        key: リセットする設定のキー（ドット区切りで階層を表現）
             Noneの場合は全ての設定をリセット
        """
        self.logger.info("設定のリセット", {"key": key})
        if key is None:
            self._settings = self._defaults.copy()
        else:
            keys = key.split(".")
            default_value = self._defaults
            for k in keys:
                default_value = default_value[k]
            
            current = self._settings
            for k in keys[:-1]:
                current = current[k]
            current[keys[-1]] = default_value
        self._save_settings() 