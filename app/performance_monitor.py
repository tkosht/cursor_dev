"""パフォーマンスモニタリングを行うモジュール。"""

import logging
import statistics
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """パフォーマンスモニタリングを行うクラス。"""

    def __init__(self):
        """初期化。"""
        self._start_times = {}
        self._measurements = {}
        self._operation_start_times = {}
        self._operation_metrics = {}

    def start_measurement(self, operation_name: str) -> None:
        """計測を開始する。

        Args:
            operation_name: 操作名
        """
        self._start_times[operation_name] = time.time()

    def end_measurement(self, operation_name: str) -> float:
        """計測を終了し、経過時間を返す。

        Args:
            operation_name: 操作名

        Returns:
            float: 経過時間（秒）
        """
        if operation_name not in self._start_times:
            logger.warning(f"No start time recorded for {operation_name}")
            return 0.0

        duration = time.time() - self._start_times[operation_name]
        if operation_name not in self._measurements:
            self._measurements[operation_name] = []
        self._measurements[operation_name].append(duration)
        return duration

    def get_average(self, operation_name: str) -> Optional[float]:
        """平均実行時間を取得する。

        Args:
            operation_name: 操作名

        Returns:
            Optional[float]: 平均実行時間（秒）
        """
        if operation_name not in self._measurements:
            return None
        return statistics.mean(self._measurements[operation_name])

    def get_percentile(self, operation_name: str, percentile: float) -> Optional[float]:
        """パーセンタイル値を取得する。

        Args:
            operation_name: 操作名
            percentile: パーセンタイル（0-100）

        Returns:
            Optional[float]: パーセンタイル値（秒）
        """
        if operation_name not in self._measurements:
            return None
        return statistics.quantiles(self._measurements[operation_name], n=100)[int(percentile)-1]

    def get_metrics(self) -> Dict[str, Any]:
        """メトリクスを取得する。

        Returns:
            Dict[str, Any]: メトリクス
        """
        metrics = {}
        for operation_name in self._measurements:
            metrics[operation_name] = {
                'count': len(self._measurements[operation_name]),
                'average': self.get_average(operation_name),
                'p95': self.get_percentile(operation_name, 95),
                'p99': self.get_percentile(operation_name, 99)
            }
        return metrics

    def clear_metrics(self) -> None:
        """メトリクスをクリアする。"""
        self._measurements.clear()
        self._start_times.clear()

    def start_operation(self, operation_name: str = 'default') -> None:
        """操作の計測を開始する。

        Args:
            operation_name: 操作名
        """
        self._operation_start_times[operation_name] = time.time()

    def end_operation(self, operation_name: str = 'default', success: bool = True, **kwargs) -> float:
        """操作の計測を終了し、経過時間を返す。

        Args:
            operation_name: 操作名
            success: 操作が成功したかどうか
            **kwargs: 追加のメトリクス

        Returns:
            float: 経過時間（秒）
        """
        if operation_name not in self._operation_start_times:
            logger.warning(f"No start time recorded for operation {operation_name}")
            return 0.0

        duration = time.time() - self._operation_start_times[operation_name]
        if operation_name not in self._operation_metrics:
            self._operation_metrics[operation_name] = {
                'success_count': 0,
                'error_count': 0,
                'total_duration': 0.0,
                'details': []
            }

        metrics = self._operation_metrics[operation_name]
        if success:
            metrics['success_count'] += 1
        else:
            metrics['error_count'] += 1
        metrics['total_duration'] += duration

        operation_details = {
            'duration': duration,
            'success': success,
            'timestamp': time.time(),
            **kwargs
        }
        metrics['details'].append(operation_details)

        del self._operation_start_times[operation_name]
        return duration 