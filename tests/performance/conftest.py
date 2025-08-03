"""Performance testing configuration and fixtures."""

import time
from contextlib import contextmanager
from typing import Generator, Dict, Any
import psutil
import pytest
from pytest_benchmark.fixture import BenchmarkFixture


class PerformanceMetrics:
    """Container for performance metrics."""
    
    def __init__(self):
        self.start_time: float = 0
        self.end_time: float = 0
        self.duration: float = 0
        self.start_memory: float = 0
        self.end_memory: float = 0
        self.peak_memory: float = 0
        self.memory_delta: float = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "duration_seconds": self.duration,
            "memory_start_mb": self.start_memory / 1024 / 1024,
            "memory_end_mb": self.end_memory / 1024 / 1024,
            "memory_peak_mb": self.peak_memory / 1024 / 1024,
            "memory_delta_mb": self.memory_delta / 1024 / 1024,
        }


@contextmanager
def performance_monitor() -> Generator[PerformanceMetrics, None, None]:
    """Context manager for monitoring performance metrics."""
    process = psutil.Process()
    metrics = PerformanceMetrics()
    
    # Capture start state
    metrics.start_time = time.time()
    metrics.start_memory = process.memory_info().rss
    
    try:
        yield metrics
    finally:
        # Capture end state
        metrics.end_time = time.time()
        metrics.duration = metrics.end_time - metrics.start_time
        
        memory_info = process.memory_info()
        metrics.end_memory = memory_info.rss
        metrics.peak_memory = memory_info.rss  # Note: This is current, not true peak
        metrics.memory_delta = metrics.end_memory - metrics.start_memory


@pytest.fixture
def performance_metrics():
    """Fixture for performance monitoring."""
    return performance_monitor


@pytest.fixture
def generate_evaluations():
    """Factory fixture for generating test evaluations."""
    def _generate(count: int) -> list:
        """Generate a list of evaluation dictionaries."""
        evaluations = []
        for i in range(count):
            evaluation = {
                "persona_id": f"persona_{i}",
                "ratings": {
                    "usability": (i % 10) * 10,
                    "accuracy": ((i + 3) % 10) * 10,
                    "performance": ((i + 7) % 10) * 10,
                },
                "suggestions": [
                    {
                        "category": "improvement",
                        "description": f"Suggestion {i}: Improve feature X",
                        "priority": i % 3,
                    }
                ],
                "comments": {
                    "positive": f"Positive comment {i}",
                    "negative": f"Negative comment {i}" if i % 3 == 0 else None,
                },
                "metadata": {
                    "timestamp": f"2025-08-03T{10 + (i % 12):02d}:00:00Z",
                    "session_id": f"session_{i // 100}",
                },
            }
            evaluations.append(evaluation)
        return evaluations
    
    return _generate


@pytest.fixture
def benchmark_config(benchmark: BenchmarkFixture):
    """Configure benchmark settings."""
    benchmark.pedantic = True
    benchmark.disable_gc = True
    benchmark.warmup = True
    return benchmark


def format_performance_report(metrics: PerformanceMetrics, operation: str) -> str:
    """Format performance metrics into a readable report."""
    data = metrics.to_dict()
    report = f"\n{'='*60}\n"
    report += f"Performance Report: {operation}\n"
    report += f"{'='*60}\n"
    report += f"Duration: {data['duration_seconds']:.3f} seconds\n"
    report += f"Memory Start: {data['memory_start_mb']:.2f} MB\n"
    report += f"Memory End: {data['memory_end_mb']:.2f} MB\n"
    report += f"Memory Delta: {data['memory_delta_mb']:.2f} MB\n"
    report += f"{'='*60}\n"
    return report