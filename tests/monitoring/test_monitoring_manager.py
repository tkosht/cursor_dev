"""
MonitoringManagerのテストモジュール
"""

import json
import logging
import os
import tempfile
from datetime import datetime, timedelta
from typing import Any, Dict

import pytest

from app.monitoring.manager import MonitoringManager


@pytest.fixture
def log_file():
    """一時ログファイルを作成"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def monitoring_manager(log_file):
    """MonitoringManagerインスタンスを作成"""
    return MonitoringManager(log_file)


def test_log_levels(monitoring_manager, log_file):
    """各ログレベルでの出力をテスト"""
    messages = {
        "debug": "Debug message",
        "info": "Info message", 
        "warning": "Warning message",
        "error": "Error message"
    }
    
    # 各レベルでログを出力
    monitoring_manager.debug(messages["debug"])
    monitoring_manager.info(messages["info"])
    monitoring_manager.warning(messages["warning"])
    monitoring_manager.error(messages["error"])
    
    # ログファイルの内容を確認
    with open(log_file) as f:
        log_content = f.read()
        
    # 各メッセージが出力されていることを確認
    for level, message in messages.items():
        assert message in log_content
        assert level.upper() in log_content


def test_structured_logging(monitoring_manager, log_file):
    """構造化ログの出力をテスト"""
    data = {
        "event": "test_event",
        "value": 123,
        "metadata": {"key": "value"}
    }
    
    monitoring_manager.log_structured(data)
    
    with open(log_file) as f:
        log_content = f.read()
    
    # JSONとしてパースできることを確認
    assert json.dumps(data) in log_content


def test_alert_condition(monitoring_manager):
    """アラート条件の設定と判定をテスト"""
    alert_triggered = False
    
    def alert_handler(alert_type: str, message: str):
        nonlocal alert_triggered
        alert_triggered = True
    
    # CPU使用率が80%を超えたらアラート
    def cpu_alert_condition(stats: Dict[str, Any]) -> bool:
        return stats.get("cpu_usage", 0) > 80
    
    monitoring_manager.add_alert_condition("high_cpu", cpu_alert_condition)
    monitoring_manager.set_alert_handler(alert_handler)
    
    # アラート条件を満たさない場合
    monitoring_manager.check_alerts({"cpu_usage": 70})
    assert not alert_triggered
    
    # アラート条件を満たす場合
    monitoring_manager.check_alerts({"cpu_usage": 90})
    assert alert_triggered


def test_metric_recording(monitoring_manager):
    """メトリクス記録をテスト"""
    metric_name = "test_metric"
    values = [1.0, 2.0, 3.0]
    
    # メトリクスを記録
    for value in values:
        monitoring_manager.record_metric(metric_name, value)
    
    # 統計を取得
    stats = monitoring_manager.get_metric_stats(metric_name)
    
    assert stats["count"] == len(values)
    assert stats["sum"] == sum(values)
    assert stats["avg"] == sum(values) / len(values)
    assert stats["min"] == min(values)
    assert stats["max"] == max(values)


def test_metric_stats_with_timerange(monitoring_manager):
    """時間範囲を指定したメトリクス統計をテスト"""
    metric_name = "test_metric"
    now = datetime.now()
    
    # 1時間前のデータを記録
    old_time = now - timedelta(hours=1)
    monitoring_manager.record_metric(metric_name, 1.0, old_time)
    
    # 現在のデータを記録
    monitoring_manager.record_metric(metric_name, 2.0, now)
    
    # 30分前以降のデータを取得
    start_time = now - timedelta(minutes=30)
    stats = monitoring_manager.get_metric_stats(metric_name, start_time)
    
    assert stats["count"] == 1  # 現在のデータのみ
    assert stats["sum"] == 2.0
    assert stats["avg"] == 2.0
    assert stats["min"] == 2.0
    assert stats["max"] == 2.0


def test_alert_cooldown(monitoring_manager):
    """アラートのクールダウンをテスト"""
    alert_count = 0
    
    def alert_handler(alert_type: str, message: str):
        nonlocal alert_count
        alert_count += 1
    
    def alert_condition(stats: Dict[str, Any]) -> bool:
        return True  # 常にアラート条件を満たす
    
    monitoring_manager.add_alert_condition("test_alert", alert_condition)
    monitoring_manager.set_alert_handler(alert_handler)
    
    # 最初のアラート
    monitoring_manager.check_alerts({})
    assert alert_count == 1
    
    # クールダウン中の場合、アラートは発生しない
    monitoring_manager.check_alerts({})
    assert alert_count == 1


def test_metric_formatter(monitoring_manager):
    """メトリクスフォーマッタをテスト"""
    formatted_message = None
    
    def custom_formatter(metric_name: str, value: float) -> str:
        return f"Custom format: {metric_name}={value:.2f}"
    
    # 標準出力をキャプチャ
    class LogCapture(logging.Handler):
        def emit(self, record):
            nonlocal formatted_message
            formatted_message = record.getMessage()
    
    monitoring_manager.logger.addHandler(LogCapture())
    monitoring_manager.set_metric_formatter(custom_formatter)
    
    # メトリクスを記録
    monitoring_manager.record_metric("test_metric", 123.456)
    
    assert formatted_message == "Custom format: test_metric=123.46"


def test_log_rotation(monitoring_manager, log_file):
    """ログローテーションをテスト"""
    # 大量のログを出力
    for i in range(1000):
        monitoring_manager.info(f"Test log message {i}")
    
    # ログローテーションを実行
    monitoring_manager.rotate_logs()
    
    # バックアップファイルが作成されていることを確認
    backup_file = f"{log_file}.1"
    assert os.path.exists(backup_file)
    
    # クリーンアップ
    if os.path.exists(backup_file):
        os.unlink(backup_file) 