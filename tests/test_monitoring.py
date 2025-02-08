"""モニタリング機能のテストモジュール。"""

import time

import pytest

from app.monitoring import MetricsCollector, PerformanceMonitor


def test_metrics_collector_init():
    """MetricsCollectorの初期化をテストする。"""
    collector = MetricsCollector()
    metrics = collector.get_metrics()

    assert 'api_calls' in metrics
    assert 'content_processing' in metrics
    assert 'analysis' in metrics
    assert 'system' in metrics
    assert metrics['system']['uptime'] >= 0


def test_record_api_call():
    """APIコール記録をテストする。"""
    collector = MetricsCollector()

    # Gemini APIコールの記録
    collector.record_api_call('gemini', True, 0.5)
    collector.record_api_call('gemini', False, 0.3)

    # Neo4j APIコールの記録
    collector.record_api_call('neo4j', True, 0.2)

    metrics = collector.get_metrics()
    gemini_metrics = metrics['api_calls']['gemini']
    neo4j_metrics = metrics['api_calls']['neo4j']

    assert gemini_metrics['success'] == 1
    assert gemini_metrics['error'] == 1
    assert gemini_metrics['total_time'] == pytest.approx(0.8)
    assert gemini_metrics['success_rate'] == 50.0
    assert gemini_metrics['avg_response_time'] == pytest.approx(0.4)

    assert neo4j_metrics['success'] == 1
    assert neo4j_metrics['error'] == 0
    assert neo4j_metrics['total_time'] == pytest.approx(0.2)
    assert neo4j_metrics['success_rate'] == 100.0
    assert neo4j_metrics['avg_response_time'] == pytest.approx(0.2)


def test_record_content_processing():
    """コンテンツ処理記録をテストする。"""
    collector = MetricsCollector()

    collector.record_content_processing(True, 1.0)
    collector.record_content_processing(True, 2.0)
    collector.record_content_processing(False, 0.5)

    metrics = collector.get_metrics()
    processing_metrics = metrics['content_processing']

    assert processing_metrics['success'] == 2
    assert processing_metrics['error'] == 1
    assert processing_metrics['total_time'] == pytest.approx(3.5)
    assert processing_metrics['success_rate'] == pytest.approx(66.67, rel=0.01)
    assert processing_metrics['avg_processing_time'] == pytest.approx(1.17, rel=0.01)


def test_record_analysis_results():
    """分析結果の記録をテストする。"""
    collector = MetricsCollector()

    collector.record_analysis_results(
        total_entities=10,
        valid_entities=8,
        total_relationships=15,
        valid_relationships=12,
        total_trends=5,
        important_trends=3
    )

    metrics = collector.get_metrics()
    analysis_metrics = metrics['analysis']

    assert analysis_metrics['entities']['total'] == 10
    assert analysis_metrics['entities']['valid'] == 8
    assert analysis_metrics['relationships']['total'] == 15
    assert analysis_metrics['relationships']['valid'] == 12
    assert analysis_metrics['trends']['total'] == 5
    assert analysis_metrics['trends']['important'] == 3


def test_performance_monitor():
    """PerformanceMonitorの機能をテストする。"""
    monitor = PerformanceMonitor()

    # APIコールのモニタリング
    monitor.start_operation()
    time.sleep(0.1)  # 実際の処理を模擬
    duration = monitor.end_operation(
        'api_call',
        True,
        api_name='gemini'
    )

    assert duration >= 0.1
    
    metrics = monitor.get_metrics()
    assert metrics['api_calls']['gemini']['success'] == 1
    assert metrics['api_calls']['gemini']['total_time'] >= 0.1

    # コンテンツ処理のモニタリング
    monitor.start_operation()
    time.sleep(0.1)  # 実際の処理を模擬
    duration = monitor.end_operation(
        'content_processing',
        True
    )

    assert duration >= 0.1
    
    metrics = monitor.get_metrics()
    assert metrics['content_processing']['success'] == 1
    assert metrics['content_processing']['total_time'] >= 0.1

    # 分析結果のモニタリング
    monitor.start_operation()
    time.sleep(0.1)  # 実際の処理を模擬
    duration = monitor.end_operation(
        'analysis',
        True,
        total_entities=5,
        valid_entities=4,
        total_relationships=6,
        valid_relationships=5,
        total_trends=3,
        important_trends=2
    )

    assert duration >= 0.1
    
    metrics = monitor.get_metrics()
    analysis_metrics = metrics['analysis']
    assert analysis_metrics['entities']['total'] == 5
    assert analysis_metrics['entities']['valid'] == 4
    assert analysis_metrics['relationships']['total'] == 6
    assert analysis_metrics['relationships']['valid'] == 5
    assert analysis_metrics['trends']['total'] == 3
    assert analysis_metrics['trends']['important'] == 2


def test_performance_monitor_no_start():
    """開始していない操作の終了をテストする。"""
    monitor = PerformanceMonitor()
    duration = monitor.end_operation('api_call', True, api_name='gemini')
    assert duration == 0.0 