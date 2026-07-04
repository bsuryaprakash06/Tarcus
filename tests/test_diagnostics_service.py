import time
import pytest
from src.services.diagnostics_service import DiagnosticsService

def test_diagnostics_timing():
    diag = DiagnosticsService()
    diag.start_timer("TestStage")
    time.sleep(0.01)
    diag.stop_timer("TestStage")
    
    assert "TestStage" in diag.timings
    assert diag.timings["TestStage"] > 0.0

def test_diagnostics_set_duration():
    diag = DiagnosticsService()
    diag.set_duration("ManualStage", 1.23)
    assert diag.timings["ManualStage"] == 1.23
