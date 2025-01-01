"""
メトリクス収集モジュール

アプリケーションのメトリクスを収集・管理します。
"""

import time
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional


class MetricsCollector:
    """メトリクス収集クラス"""

    def __init__(self):
        """初期化"""
        self._metrics: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "success": 0,
                "failure": 0,
                "errors": defaultdict(int),
                "response_times": [],
                "resource_usage": defaultdict(list),
                "time_series": []
            }
        )

    def record_success(self, operation_type: str) -> None:
        """
        成功を記録

        Args:
            operation_type: 操作タイプ
        """
        self._metrics[operation_type]["success"] += 1

    def record_failure(self, operation_type: str) -> None:
        """
        失敗を記録

        Args:
            operation_type: 操作タイプ
        """
        self._metrics[operation_type]["failure"] += 1

    def record_error(self, operation_type: str, error_type: str) -> None:
        """
        エラーを記録

        Args:
            operation_type: 操作タイプ
            error_type: エラータイプ
        """
        self._metrics[operation_type]["errors"][error_type] += 1
        self.record_failure(operation_type)

    @contextmanager
    def measure_time(self, operation_type: str):
        """
        処理時間を計測

        Args:
            operation_type: 操作タイプ
        """
        start_time = time.time()
        try:
            yield
        finally:
            elapsed_time = time.time() - start_time
            if operation_type not in self._metrics:
                self._metrics[operation_type] = {
                    "success": 0,
                    "failure": 0,
                    "errors": defaultdict(int),
                    "response_times": [],
                    "resource_usage": defaultdict(list),
                    "time_series": []
                }
            self._metrics[operation_type]["response_times"].append(elapsed_time)
            self.record_success(operation_type)

    def record_resource_usage(
        self,
        resource_type: str,
        usage: float,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        リソース使用率を記録

        Args:
            resource_type: リソースタイプ
            usage: 使用率
            timestamp: タイムスタンプ（省略時は現在時刻）
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        self._metrics[resource_type]["resource_usage"]["usage"].append({
            "value": usage,
            "timestamp": timestamp
        })

    def record_time_series(
        self,
        metric_name: str,
        value: float,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        時系列データを記録

        Args:
            metric_name: メトリクス名
            value: 値
            timestamp: タイムスタンプ（省略時は現在時刻）
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        self._metrics[metric_name]["time_series"].append({
            "value": value,
            "timestamp": timestamp
        })

    def get_stats(self, operation_type: str) -> Dict[str, Any]:
        """
        統計情報を取得

        Args:
            operation_type: 操作タイプ

        Returns:
            統計情報
        """
        metrics = self._metrics[operation_type]
        total = metrics["success"] + metrics["failure"]
        response_times = metrics["response_times"]
        
        if total == 0:
            return {
                "success_rate": 0.0,
                "error_rate": 0.0,
                "total_operations": 0,
                "avg_response_time": 0.0,
                "min_response_time": 0.0,
                "max_response_time": 0.0
            }
        
        return {
            "success_rate": metrics["success"] / total if total > 0 else 0.0,
            "error_rate": metrics["failure"] / total if total > 0 else 0.0,
            "total_operations": total,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0.0,
            "min_response_time": min(response_times) if response_times else 0.0,
            "max_response_time": max(response_times) if response_times else 0.0
        }

    def get_error_types(self, operation_type: str) -> List[str]:
        """
        エラータイプの一覧を取得

        Args:
            operation_type: 操作タイプ

        Returns:
            エラータイプのリスト
        """
        return list(self._metrics[operation_type]["errors"].keys())

    def get_resource_stats(self, resource_type: str) -> Dict[str, float]:
        """
        リソース使用率の統計を取得

        Args:
            resource_type: リソースタイプ

        Returns:
            統計情報
        """
        usage_data = [
            item["value"]
            for item in self._metrics[resource_type]["resource_usage"]["usage"]
        ]
        
        if not usage_data:
            return {
                "avg_usage": 0.0,
                "min_usage": 0.0,
                "max_usage": 0.0
            }
        
        return {
            "avg_usage": sum(usage_data) / len(usage_data),
            "min_usage": min(usage_data),
            "max_usage": max(usage_data)
        }

    def get_time_series(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        時系列データを取得

        Args:
            metric_name: メトリクス名
            start_time: 開始時刻
            end_time: 終了時刻

        Returns:
            時系列データのリスト
        """
        return [
            item for item in self._metrics[metric_name]["time_series"]
            if start_time <= item["timestamp"] <= end_time
        ]

    def get_overall_stats(self) -> Dict[str, Any]:
        """
        全体の統計情報を取得

        Returns:
            統計情報
        """
        total_success = sum(
            metrics["success"]
            for metrics in self._metrics.values()
        )
        total_failure = sum(
            metrics["failure"]
            for metrics in self._metrics.values()
        )
        total = total_success + total_failure
        
        return {
            "total_operations": total,
            "total_success": total_success,
            "total_failure": total_failure,
            "overall_success_rate": total_success / total if total > 0 else 0.0
        }

    def reset(self) -> None:
        """メトリクスをリセット"""
        self._metrics.clear() 