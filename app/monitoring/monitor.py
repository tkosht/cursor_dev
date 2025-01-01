"""Monitoring module for tracking metrics and performance."""

import logging
from datetime import datetime
from typing import Dict, List, Union

logger = logging.getLogger(__name__)


class Monitor:
    """Monitor class for tracking metrics and performance."""

    def __init__(self):
        """Initialize the monitor."""
        self.metrics: Dict[str, Dict[str, Union[int, float, List[float]]]] = {
            "requests": {
                "total": 0,
                "success": 0,
                "failure": 0,
                "response_times": []
            },
            "extraction": {
                "total": 0,
                "success": 0,
                "failure": 0,
                "processing_times": []
            }
        }
        self.start_time = datetime.now()

    def record_request(self, success: bool, response_time: float):
        """Record a request metric.

        Args:
            success: Whether the request was successful.
            response_time: The response time in seconds.
        """
        self.metrics["requests"]["total"] += 1
        if success:
            self.metrics["requests"]["success"] += 1
        else:
            self.metrics["requests"]["failure"] += 1
        self.metrics["requests"]["response_times"].append(response_time)

    def record_extraction(self, success: bool, processing_time: float):
        """Record an extraction metric.

        Args:
            success: Whether the extraction was successful.
            processing_time: The processing time in seconds.
        """
        self.metrics["extraction"]["total"] += 1
        if success:
            self.metrics["extraction"]["success"] += 1
        else:
            self.metrics["extraction"]["failure"] += 1
        self.metrics["extraction"]["processing_times"].append(processing_time)

    def get_metrics(self) -> Dict[str, Dict[str, Union[int, float]]]:
        """Get the current metrics.

        Returns:
            Dictionary containing the current metrics.
        """
        metrics = {}
        for category, data in self.metrics.items():
            metrics[category] = {
                "total": data["total"],
                "success": data["success"],
                "failure": data["failure"],
                "success_rate": (
                    data["success"] / data["total"] if data["total"] > 0 else 0.0
                ),
                "average_time": (
                    sum(data["response_times"]) / len(data["response_times"])
                    if category == "requests" and data["response_times"]
                    else sum(data["processing_times"]) / len(data["processing_times"])
                    if category == "extraction" and data["processing_times"]
                    else 0.0
                )
            }
        return metrics

    def reset(self):
        """Reset all metrics."""
        for category in self.metrics:
            times_key = "response_times" if category == "requests" else "processing_times"
            self.metrics[category] = {
                "total": 0,
                "success": 0,
                "failure": 0,
                times_key: []
            }
        self.start_time = datetime.now()
