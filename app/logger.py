"""
カスタムロガーモジュール

アプリケーション全体で使用するロギング機能を提供します。
"""

import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional


class LogLevel:
    """ログレベルの定義"""

    ERROR = 40  # エラーイベント（アプリケーション停止の可能性）
    WARNING = 30  # 警告イベント（問題の可能性）
    INFO = 20  # 一般的な情報イベント
    DEBUG = 10  # デバッグ用の詳細情報


class JsonFormatter(logging.Formatter):
    """JSONフォーマッタ"""

    def format(self, record: logging.LogRecord) -> str:
        """ログレコードをJSON形式にフォーマット"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "message": record.getMessage(),
            "details": getattr(record, "details", {}),
        }
        return json.dumps(log_data, ensure_ascii=False)


class CustomLogger:
    """カスタムロガークラス"""

    def __init__(
        self,
        name: str,
        log_dir: str = "logs",
        max_bytes: int = 10_485_760,  # 10MB
        backup_count: int = 5,
    ):
        """
        カスタムロガーの初期化

        Args:
            name: ロガー名
            log_dir: ログディレクトリのパス
            max_bytes: ログファイルの最大サイズ（バイト）
            backup_count: 保持する過去ログファイルの数
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # ログディレクトリの作成
        self.log_dir = Path(log_dir)
        for level in ["debug", "info", "error"]:
            (self.log_dir / level).mkdir(parents=True, exist_ok=True)

        # 各レベルのハンドラを設定
        self._setup_handlers(max_bytes, backup_count)

    def _setup_handlers(self, max_bytes: int, backup_count: int) -> None:
        """ログハンドラの設定"""
        formatter = JsonFormatter()

        # デバッグログ
        debug_handler = RotatingFileHandler(
            self.log_dir / "debug" / f"{self.logger.name}.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        self.logger.addHandler(debug_handler)

        # 情報ログ
        info_handler = RotatingFileHandler(
            self.log_dir / "info" / f"{self.logger.name}.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        self.logger.addHandler(info_handler)

        # エラーログ
        error_handler = RotatingFileHandler(
            self.log_dir / "error" / f"{self.logger.name}.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)

        # コンソール出力
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _log(
        self,
        level: int,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """ログ出力の共通処理"""
        if details is None:
            details = {}
        extra = {"details": details}
        self.logger.log(level, message, extra=extra)

    def debug(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """デバッグログの出力"""
        self._log(LogLevel.DEBUG, message, details)

    def info(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """情報ログの出力"""
        self._log(LogLevel.INFO, message, details)

    def warning(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """警告ログの出力"""
        self._log(LogLevel.WARNING, message, details)

    def error(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """エラーログの出力"""
        self._log(LogLevel.ERROR, message, details)
