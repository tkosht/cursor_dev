"""
URL分析のメトリクス収集を管理するモジュール
"""
import logging
import statistics
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ログ設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class URLAnalysisMetrics:
    """分析メトリクス"""
    total_urls: int = 0
    processed_urls: int = 0
    error_count: int = 0
    processing_times: List[float] = field(default_factory=list)
    llm_latencies: List[float] = field(default_factory=list)
    confidence_scores: List[float] = field(default_factory=list)
    relevance_scores: List[float] = field(default_factory=list)
    category_counts: Dict[str, int] = field(default_factory=dict)

    def record_url_processing(
        self,
        url: str,
        result: Optional[Dict[str, Any]],
        processing_time: float,
        llm_latency: float
    ):
        """URL処理結果の記録"""
        self.processed_urls += 1
        self.processing_times.append(processing_time)
        self.llm_latencies.append(llm_latency)

        if result:
            self.confidence_scores.append(result.get("confidence", 0.0))
            self.relevance_scores.append(result.get("relevance_score", 0.0))
            category = result.get("category", "unknown")
            self.category_counts[category] = self.category_counts.get(category, 0) + 1
        else:
            self.error_count += 1

    def record_error(self, url: str, error: Exception):
        """エラーの記録"""
        self.error_count += 1
        logger.error(f"Error processing URL {url}: {str(error)}")


class AnalysisReporter:
    """分析レポート生成"""

    def generate_report(self, metrics: URLAnalysisMetrics) -> Dict[str, Any]:
        """
        メトリクスレポートを生成

        Args:
            metrics: 収集したメトリクス

        Returns:
            レポート内容
        """
        return {
            "summary": self._generate_summary(metrics),
            "performance": self._generate_performance_metrics(metrics),
            "quality": self._generate_quality_metrics(metrics),
            "categories": self._generate_category_metrics(metrics)
        }

    def _generate_summary(self, metrics: URLAnalysisMetrics) -> Dict[str, Any]:
        """サマリー情報の生成"""
        return {
            "total_urls": metrics.total_urls,
            "processed_urls": metrics.processed_urls,
            "success_rate": self._calc_success_rate(metrics),
            "avg_processing_time": self._calc_avg(metrics.processing_times),
            "avg_confidence": self._calc_avg(metrics.confidence_scores)
        }

    def _generate_performance_metrics(
        self,
        metrics: URLAnalysisMetrics
    ) -> Dict[str, Any]:
        """パフォーマンス指標の生成"""
        return {
            "processing_time": {
                "p50": self._calc_percentile(metrics.processing_times, 50),
                "p95": self._calc_percentile(metrics.processing_times, 95),
                "p99": self._calc_percentile(metrics.processing_times, 99)
            },
            "llm_latency": {
                "p50": self._calc_percentile(metrics.llm_latencies, 50),
                "p95": self._calc_percentile(metrics.llm_latencies, 95),
                "p99": self._calc_percentile(metrics.llm_latencies, 99)
            }
        }

    def _generate_quality_metrics(
        self,
        metrics: URLAnalysisMetrics
    ) -> Dict[str, Any]:
        """品質指標の生成"""
        return {
            "confidence": {
                "avg": self._calc_avg(metrics.confidence_scores),
                "distribution": self._calc_distribution(metrics.confidence_scores)
            },
            "relevance": {
                "avg": self._calc_avg(metrics.relevance_scores),
                "distribution": self._calc_distribution(metrics.relevance_scores)
            },
            "error_rate": metrics.error_count / max(metrics.total_urls, 1)
        }

    def _generate_category_metrics(
        self,
        metrics: URLAnalysisMetrics
    ) -> Dict[str, Any]:
        """カテゴリ別指標の生成"""
        total = sum(metrics.category_counts.values())
        return {
            "counts": metrics.category_counts,
            "distribution": {
                category: count / total
                for category, count in metrics.category_counts.items()
            } if total > 0 else {}
        }

    def _calc_success_rate(self, metrics: URLAnalysisMetrics) -> float:
        """成功率の計算"""
        if metrics.total_urls == 0:
            return 0.0
        return (metrics.processed_urls - metrics.error_count) / metrics.total_urls

    def _calc_avg(self, values: List[float]) -> float:
        """平均値の計算"""
        return statistics.mean(values) if values else 0.0

    def _calc_percentile(self, values: List[float], percentile: int) -> float:
        """パーセンタイル値の計算"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * percentile / 100
        f = int(k)
        c = k - f
        if f + 1 < len(sorted_values):
            return sorted_values[f] * (1 - c) + sorted_values[f + 1] * c
        return sorted_values[f]

    def _calc_distribution(self, values: List[float]) -> Dict[str, int]:
        """分布の計算"""
        if not values:
            return {}

        bins = {
            "0.0-0.2": 0,
            "0.2-0.4": 0,
            "0.4-0.6": 0,
            "0.6-0.8": 0,
            "0.8-1.0": 0
        }

        for value in values:
            if value < 0.2:
                bins["0.0-0.2"] += 1
            elif value < 0.4:
                bins["0.2-0.4"] += 1
            elif value < 0.6:
                bins["0.4-0.6"] += 1
            elif value < 0.8:
                bins["0.6-0.8"] += 1
            else:
                bins["0.8-1.0"] += 1

        return bins 