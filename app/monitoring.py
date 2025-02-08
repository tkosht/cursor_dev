"""モニタリングとメトリクス収集を行うモジュール。"""

import logging
import time
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


class MetricsCollector:
    """システム全体のメトリクスを収集・管理するクラス。"""

    def __init__(self):
        """MetricsCollectorを初期化する。"""
        self._metrics = {
            'api_calls': {
                'gemini': {'success': 0, 'error': 0, 'total_time': 0.0},
                'neo4j': {'success': 0, 'error': 0, 'total_time': 0.0}
            },
            'content_processing': {
                'success': 0,
                'error': 0,
                'total_time': 0.0
            },
            'analysis': {
                'entities': {'total': 0, 'valid': 0},
                'relationships': {'total': 0, 'valid': 0},
                'trends': {'total': 0, 'important': 0}
            }
        }
        self._start_time = datetime.now()

    def record_api_call(self, api_name: str, success: bool, duration: float) -> None:
        """APIコールの結果を記録する。

        Args:
            api_name (str): API名（'gemini'または'neo4j'）
            success (bool): 成功したかどうか
            duration (float): 実行時間（秒）
        """
        if api_name not in self._metrics['api_calls']:
            return

        status = 'success' if success else 'error'
        self._metrics['api_calls'][api_name][status] += 1
        self._metrics['api_calls'][api_name]['total_time'] += duration

    def record_content_processing(self, success: bool, duration: float) -> None:
        """コンテンツ処理の結果を記録する。

        Args:
            success (bool): 成功したかどうか
            duration (float): 処理時間（秒）
        """
        status = 'success' if success else 'error'
        self._metrics['content_processing'][status] += 1
        self._metrics['content_processing']['total_time'] += duration

    def record_analysis_results(
        self,
        total_entities: int,
        valid_entities: int,
        total_relationships: int,
        valid_relationships: int,
        total_trends: int,
        important_trends: int
    ) -> None:
        """分析結果のメトリクスを記録する。

        Args:
            total_entities (int): 全エンティティ数
            valid_entities (int): 有効なエンティティ数
            total_relationships (int): 全リレーションシップ数
            valid_relationships (int): 有効なリレーションシップ数
            total_trends (int): 全トレンド数
            important_trends (int): 重要なトレンド数
        """
        self._metrics['analysis']['entities']['total'] += total_entities
        self._metrics['analysis']['entities']['valid'] += valid_entities
        self._metrics['analysis']['relationships']['total'] += total_relationships
        self._metrics['analysis']['relationships']['valid'] += valid_relationships
        self._metrics['analysis']['trends']['total'] += total_trends
        self._metrics['analysis']['trends']['important'] += important_trends

    def get_metrics(self) -> Dict[str, Any]:
        """現在のメトリクスを取得する。

        Returns:
            Dict[str, Any]: 収集されたメトリクス
        """
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        metrics = self._metrics.copy()
        metrics['system'] = {
            'uptime': uptime,
            'start_time': self._start_time.isoformat()
        }

        # API成功率の計算
        for api_name in self._metrics['api_calls']:
            api_metrics = self._metrics['api_calls'][api_name]
            total_calls = api_metrics['success'] + api_metrics['error']
            if total_calls > 0:
                metrics['api_calls'][api_name]['success_rate'] = (
                    api_metrics['success'] / total_calls * 100
                )
                metrics['api_calls'][api_name]['avg_response_time'] = (
                    api_metrics['total_time'] / total_calls
                )

        # コンテンツ処理の成功率計算
        total_processing = (
            self._metrics['content_processing']['success'] +
            self._metrics['content_processing']['error']
        )
        if total_processing > 0:
            metrics['content_processing']['success_rate'] = (
                self._metrics['content_processing']['success'] /
                total_processing * 100
            )
            metrics['content_processing']['avg_processing_time'] = (
                self._metrics['content_processing']['total_time'] /
                total_processing
            )

        return metrics


class PerformanceMonitor:
    """パフォーマンスモニタリングを行うクラス。"""

    def __init__(self):
        """PerformanceMonitorを初期化する。"""
        self._metrics = {}
        self._start_times = {}

    def start_measurement(self, operation_name: str) -> None:
        """
        処理時間の計測を開始する。

        Args:
            operation_name (str): 計測対象の処理名
        """
        self._start_times[operation_name] = time.time()

    def end_measurement(self, operation_name: str) -> float:
        """
        処理時間の計測を終了し、経過時間を返す。

        Args:
            operation_name (str): 計測対象の処理名

        Returns:
            float: 経過時間（秒）

        Raises:
            KeyError: 指定された処理名の計測が開始されていない場合
        """
        if operation_name not in self._start_times:
            raise KeyError(f"処理 '{operation_name}' の計測が開始されていません")

        end_time = time.time()
        start_time = self._start_times.pop(operation_name)
        duration = end_time - start_time

        if operation_name not in self._metrics:
            self._metrics[operation_name] = {
                "total_time": 0,
                "call_count": 0,
                "min_time": float("inf"),
                "max_time": 0
            }

        metrics = self._metrics[operation_name]
        metrics["total_time"] += duration
        metrics["call_count"] += 1
        metrics["min_time"] = min(metrics["min_time"], duration)
        metrics["max_time"] = max(metrics["max_time"], duration)

        logger.info(
            f"処理時間計測: {operation_name}, "
            f"所要時間: {duration:.3f}秒"
        )

        return duration

    def get_metrics(self) -> Dict[str, Dict[str, float]]:
        """
        計測結果を取得する。

        Returns:
            Dict[str, Dict[str, float]]: 処理名をキーとする計測結果
        """
        return self._metrics

    def reset_metrics(self) -> None:
        """計測結果をリセットする。"""
        self._metrics = {} 