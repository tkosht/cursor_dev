"""
メトリクス収集のテストモジュール
"""

import time
from datetime import datetime, timedelta

import pytest

from app.metrics.collector import MetricsCollector


@pytest.fixture
def collector():
    """MetricsCollectorのフィクスチャ"""
    return MetricsCollector()


def test_record_success(collector):
    """成功記録のテスト"""
    collector.record_success("test_operation")
    stats = collector.get_stats("test_operation")
    assert stats["success_rate"] == 1.0
    assert stats["total_operations"] == 1


def test_record_failure(collector):
    """失敗記録のテスト"""
    collector.record_failure("test_operation")
    stats = collector.get_stats("test_operation")
    assert stats["error_rate"] == 1.0
    assert stats["total_operations"] == 1


def test_record_error(collector):
    """エラー記録のテスト"""
    collector.record_error("test_operation", "test_error")
    error_types = collector.get_error_types("test_operation")
    assert "test_error" in error_types
    stats = collector.get_stats("test_operation")
    assert stats["error_rate"] == 1.0


def test_measure_time(collector):
    """処理時間計測のテスト"""
    with collector.measure_time("test_operation"):
        time.sleep(0.1)  # 100ms待機して確実に時間を計測
    stats = collector.get_stats("test_operation")
    assert stats["avg_response_time"] > 0
    assert stats["min_response_time"] > 0
    assert stats["max_response_time"] > 0
    assert 0.1 <= stats["avg_response_time"] <= 0.15  # 実際の処理時間を検証


def test_record_resource_usage(collector):
    """リソース使用率記録のテスト"""
    test_usage = 0.75
    collector.record_resource_usage("cpu", test_usage)
    stats = collector.get_resource_stats("cpu")
    assert stats["avg_usage"] == test_usage
    assert stats["min_usage"] == test_usage
    assert stats["max_usage"] == test_usage


def test_record_time_series(collector):
    """時系列データ記録のテスト"""
    now = datetime.now()
    test_value = 42.0
    collector.record_time_series("test_metric", test_value, now)
    
    start_time = now - timedelta(minutes=1)
    end_time = now + timedelta(minutes=1)
    time_series = collector.get_time_series("test_metric", start_time, end_time)
    
    assert len(time_series) == 1
    assert time_series[0]["value"] == test_value
    assert time_series[0]["timestamp"] == now


def test_get_overall_stats(collector):
    """全体統計のテスト"""
    collector.record_success("op1")
    collector.record_success("op2")
    collector.record_failure("op1")
    
    stats = collector.get_overall_stats()
    assert stats["total_operations"] == 3
    assert stats["total_success"] == 2
    assert stats["total_failure"] == 1
    assert stats["overall_success_rate"] == pytest.approx(2/3)


def test_reset(collector):
    """リセット機能のテスト"""
    collector.record_success("test_operation")
    collector.reset()
    stats = collector.get_stats("test_operation")
    assert stats["total_operations"] == 0


def test_empty_stats(collector):
    """空の統計情報のテスト"""
    stats = collector.get_stats("non_existent")
    assert stats["total_operations"] == 0
    assert stats["success_rate"] == 0.0
    assert stats["error_rate"] == 0.0 