"""パフォーマンスモニタリングモジュール。"""

import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """パフォーマンスモニタリングクラス。"""

    def __init__(self) -> None:
        """初期化メソッド。"""
        self.metrics: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}

    def start_measurement(self, operation: str) -> None:
        """
        計測を開始する。

        Args:
            operation (str): 計測対象の操作名
        """
        self.start_times[operation] = time.time()

    def end_measurement(self, operation: str) -> Optional[float]:
        """
        計測を終了し、経過時間を記録する。

        Args:
            operation (str): 計測対象の操作名

        Returns:
            Optional[float]: 経過時間（秒）。開始時刻が記録されていない場合はNone。
        """
        if operation not in self.start_times:
            logger.warning(f"操作 '{operation}' の開始時刻が記録されていません。")
            return None

        elapsed_time = time.time() - self.start_times[operation]
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(elapsed_time)
        del self.start_times[operation]
        return elapsed_time

    def measure_time(self, operation: str) -> Any:
        """
        処理時間を計測するデコレータ。

        Args:
            operation (str): 計測対象の操作名

        Returns:
            Any: デコレータ関数
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                self.start_measurement(operation)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    self.end_measurement(operation)
            return wrapper
        return decorator

    def get_metrics(self, operation: Optional[str] = None) -> Dict[str, List[float]]:
        """
        メトリクスを取得する。

        Args:
            operation (Optional[str]): 取得対象の操作名。Noneの場合は全操作のメトリクスを返す。

        Returns:
            Dict[str, List[float]]: 操作名をキー、計測時間のリストを値とする辞書
        """
        if operation:
            return {operation: self.metrics.get(operation, [])}
        return self.metrics

    def get_average_time(self, operation: str) -> Optional[float]:
        """
        平均処理時間を取得する。

        Args:
            operation (str): 計測対象の操作名

        Returns:
            Optional[float]: 平均処理時間（秒）。メトリクスが存在しない場合はNone。
        """
        times = self.metrics.get(operation, [])
        return sum(times) / len(times) if times else None

    def clear_metrics(self, operation: Optional[str] = None) -> None:
        """
        メトリクスをクリアする。

        Args:
            operation (Optional[str]): クリア対象の操作名。Noneの場合は全操作のメトリクスをクリア。
        """
        if operation:
            self.metrics.pop(operation, None)
        else:
            self.metrics.clear()
            self.start_times.clear() 