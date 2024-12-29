"""
クローラーモニタリング機能のテスト
"""

import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from app.monitoring.monitor import CrawlerMetrics, CrawlerMonitor


@pytest.fixture
def temp_log_file():
    """一時ログファイルを作成"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def monitor(temp_log_file):
    """モニターインスタンスを作成"""
    return CrawlerMonitor(log_file=temp_log_file)


def test_start_crawler(monitor):
    """クローラー開始のテスト"""
    company_code = "9843"
    monitor.start_crawler(company_code)

    # アクティブクローラーの確認
    assert company_code in monitor.get_active_crawlers()

    # メトリクスの確認
    metrics = monitor.get_metrics(company_code)
    assert metrics is not None
    assert metrics.company_code == company_code
    assert metrics.status == "running"
    assert metrics.error_count == 0
    assert metrics.warning_count == 0


def test_stop_crawler(monitor):
    """クローラー終了のテスト"""
    company_code = "9843"
    monitor.start_crawler(company_code)
    monitor.stop_crawler(company_code)

    # アクティブクローラーから削除されていることを確認
    assert company_code not in monitor.get_active_crawlers()


def test_log_error(monitor):
    """エラーログのテスト"""
    company_code = "9843"
    monitor.start_crawler(company_code)

    # エラーを記録
    error = ValueError("Test error")
    monitor.log_error(company_code, error)

    # エラーカウントの確認
    metrics = monitor.get_metrics(company_code)
    assert metrics.error_count == 1


def test_log_warning(monitor):
    """警告ログのテスト"""
    company_code = "9843"
    monitor.start_crawler(company_code)

    # 警告を記録
    monitor.log_warning(company_code, "Test warning")

    # 警告カウントの確認
    metrics = monitor.get_metrics(company_code)
    assert metrics.warning_count == 1


def test_update_progress(monitor):
    """進捗更新のテスト"""
    company_code = "9843"
    monitor.start_crawler(company_code)

    # 進捗を更新
    monitor.update_progress(company_code, crawled_pages=5, total_items=100)

    # 進捗の確認
    metrics = monitor.get_metrics(company_code)
    assert metrics.crawled_pages == 5
    assert metrics.total_items == 100


def test_get_active_crawlers(monitor):
    """アクティブクローラー取得のテスト"""
    # 複数のクローラーを開始
    codes = ["9843", "7203", "6758"]
    for code in codes:
        monitor.start_crawler(code)

    # アクティブクローラーの確認
    active = monitor.get_active_crawlers()
    assert len(active) == len(codes)
    assert all(code in active for code in codes)


def test_get_metrics(monitor):
    """メトリクス取得のテスト"""
    company_code = "9843"
    monitor.start_crawler(company_code)

    # 存在するメトリクス
    metrics = monitor.get_metrics(company_code)
    assert metrics is not None
    assert isinstance(metrics, CrawlerMetrics)

    # 存在しないメトリクス
    assert monitor.get_metrics("0000") is None


@patch("app.monitoring.monitor.datetime")
def test_duration_calculation(mock_datetime, monitor):
    """実行時間計算のテスト"""
    company_code = "9843"

    # 開始時刻を固定
    start_time = datetime(2024, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = start_time
    monitor.start_crawler(company_code)

    # 終了時刻を30秒後に設定
    end_time = start_time + timedelta(seconds=30)
    mock_datetime.now.return_value = end_time

    # クローラーを終了
    monitor.stop_crawler(company_code)

    # メトリクスの確認
    metrics = monitor.active_crawlers.get(company_code)
    assert metrics is None  # 終了後はアクティブリストから削除される
