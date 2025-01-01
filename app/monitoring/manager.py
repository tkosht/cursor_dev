"""
モニタリングモジュール

アプリケーションのモニタリング機能を提供します。
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Dict, List, Optional


class MonitoringManager:
    """モニタリング管理クラス"""

    def __init__(self, log_file: str):
        """
        初期化

        Args:
            log_file: ログファイルのパス
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # ファイルハンドラの設定
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # アラート設定
        self._alert_conditions: Dict[str, Callable[[Dict[str, Any]], bool]] = {}
        self._alert_handler: Optional[Callable[[str, str], None]] = None
        self._last_alert_time: Dict[str, datetime] = {}
        self._alert_cooldown = timedelta(minutes=5)
        
        # メトリクス設定
        self._metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._metric_formatter: Optional[Callable[[str, float], str]] = None

    def info(self, message: str) -> None:
        """
        情報ログを出力

        Args:
            message: ログメッセージ
        """
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """
        警告ログを出力

        Args:
            message: ログメッセージ
        """
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """
        エラーログを出力

        Args:
            message: ログメッセージ
        """
        self.logger.error(message)

    def debug(self, message: str) -> None:
        """
        デバッグログを出力

        Args:
            message: ログメッセージ
        """
        self.logger.debug(message)

    def log_structured(self, data: Dict[str, Any]) -> None:
        """
        構造化ログを出力

        Args:
            data: ログデータ
        """
        self.logger.info(json.dumps(data))

    def add_alert_condition(
        self,
        alert_type: str,
        condition: Callable[[Dict[str, Any]], bool]
    ) -> None:
        """
        アラート条件を追加

        Args:
            alert_type: アラートタイプ
            condition: アラート条件を判定する関数
        """
        self._alert_conditions[alert_type] = condition

    def set_alert_handler(
        self,
        handler: Callable[[str, str], None]
    ) -> None:
        """
        アラートハンドラを設定

        Args:
            handler: アラートを処理する関数
        """
        self._alert_handler = handler

    def check_alerts(self, stats: Dict[str, Any]) -> None:
        """
        アラート条件をチェック

        Args:
            stats: チェック対象の統計データ
        """
        if not self._alert_handler:
            return
        
        now = datetime.now()
        for alert_type, condition in self._alert_conditions.items():
            if condition(stats):
                last_alert = self._last_alert_time.get(alert_type)
                if not last_alert or now - last_alert > self._alert_cooldown:
                    self._alert_handler(
                        alert_type,
                        f"Alert condition met: {alert_type}"
                    )
                    self._last_alert_time[alert_type] = now

    def record_metric(
        self,
        metric_name: str,
        value: float,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        メトリクスを記録

        Args:
            metric_name: メトリクス名
            value: 値
            timestamp: タイムスタンプ（省略時は現在時刻）
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        self._metrics[metric_name].append({
            "value": value,
            "timestamp": timestamp
        })
        
        if self._metric_formatter:
            formatted = self._metric_formatter(metric_name, value)
            self.info(formatted)
        else:
            self.info(f"Metric: {metric_name}={value}")

    def get_metric_stats(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        メトリクスの統計を取得

        Args:
            metric_name: メトリクス名
            start_time: 開始時刻（省略時は全期間）

        Returns:
            統計情報
        """
        metrics = self._metrics[metric_name]
        if start_time:
            metrics = [
                m for m in metrics
                if m["timestamp"] >= start_time
            ]
        
        if not metrics:
            return {
                "count": 0,
                "sum": 0,
                "avg": 0,
                "min": 0,
                "max": 0
            }
        
        values = [m["value"] for m in metrics]
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }

    def rotate_logs(self) -> None:
        """ログローテーションを実行"""
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.doRollover()

    def trigger_alert(self, alert_type: str, message: str) -> None:
        """
        アラートを発生

        Args:
            alert_type: アラートタイプ
            message: アラートメッセージ
        """
        if not self._alert_handler:
            return
        
        now = datetime.now()
        last_alert = self._last_alert_time.get(alert_type)
        if not last_alert or now - last_alert > self._alert_cooldown:
            self._alert_handler(alert_type, message)
            self._last_alert_time[alert_type] = now

    def set_metric_formatter(
        self,
        formatter: Callable[[str, float], str]
    ) -> None:
        """
        メトリクスフォーマッタを設定

        Args:
            formatter: メトリクスをフォーマットする関数
        """
        self._metric_formatter = formatter 