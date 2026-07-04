import pytest
from src.services.metrics_service import MetricsService

def test_metrics_service_singleton():
    m1 = MetricsService()
    m2 = MetricsService()
    assert m1 is m2

def test_record_latencies():
    metrics = MetricsService()
    # Reset state due to singleton
    metrics._initialize()
    
    metrics.record_planner_latency(1.5)
    metrics.record_planner_latency(2.5)
    metrics.record_execution_latency(0.5)
    
    assert len(metrics.planner_latencies) == 2
    assert len(metrics.execution_latencies) == 1
    
    stats = metrics._compute_stats(metrics.planner_latencies)
    assert stats["average"] == 2.0
    assert stats["min"] == 1.5
    assert stats["max"] == 2.5

def test_record_tool_usage():
    metrics = MetricsService()
    metrics._initialize()
    
    metrics.record_tool_usage("take_screenshot", True)
    metrics.record_tool_usage("take_screenshot", True)
    metrics.record_tool_usage("close_application", False)
    
    assert metrics.tool_usage["take_screenshot"] == 2
    assert metrics.tool_usage["close_application"] == 1
    assert metrics.successful_executions == 2
    assert metrics.failed_executions == 1
