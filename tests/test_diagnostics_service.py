import time
import pytest
from src.services.diagnostics_service import DiagnosticsService

def test_diagnostics_timing():
    diag = DiagnosticsService()
    diag.start_timer("Planner")
    time.sleep(0.01)
    diag.stop_timer("Planner")
    
    assert "Planner" in diag.timings
    assert diag.timings["Planner"] > 0.0

def test_diagnostics_set_duration():
    diag = DiagnosticsService()
    diag.set_duration("ManualStage", 1.23)
    assert diag.timings["ManualStage"] == 1.23

def test_diagnostics_calculate_metrics():
    diag = DiagnosticsService()
    diag.set_duration("Silence Detection", 0.5)
    diag.set_duration("Whisper", 1.0)
    diag.set_duration("Planner", 0.5)
    diag.set_duration("Execution", 0.1)
    
    diag.calculate_metrics()
    # Response Latency = Silence + Whisper + Planner + Execution
    assert diag.timings["Response Latency"] == 2.1
