import pytest
from src.services.history_service import CommandHistoryService
from src.models.plan import ExecutionPlan

def test_history_service_singleton():
    h1 = CommandHistoryService()
    h2 = CommandHistoryService()
    assert h1 is h2

def test_create_and_get_record():
    history = CommandHistoryService()
    history._initialize()
    
    exec_id = "test-123"
    record = history.create_record(exec_id, "test command")
    
    assert record.execution_id == exec_id
    assert record.voice_command == "test command"
    
    fetched = history.get_record(exec_id)
    assert fetched is not None
    assert fetched.execution_id == exec_id
    assert fetched.overall_status == "PENDING"
