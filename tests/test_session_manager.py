import pytest
import uuid
from src.services.session_manager import SessionManager
from src.models.input import InputRequest, InputSource

def test_singleton():
    manager1 = SessionManager()
    manager2 = SessionManager()
    assert manager1 is manager2

def test_enqueue_dequeue():
    manager = SessionManager()
    manager.clear_queue()
    
    req = InputRequest(request_id="test-123", source=InputSource.TEXT, text="Hello")
    manager.enqueue(req)
    
    popped = manager.dequeue()
    assert popped is not None
    assert popped.request_id == "test-123"
    assert popped.text == "Hello"
    assert manager.active_request == popped
    
    manager.complete_request()
    assert manager.active_request is None

def test_clear_queue():
    manager = SessionManager()
    manager.clear_queue()
    
    for i in range(5):
        manager.enqueue(InputRequest(request_id=str(i), source=InputSource.TEXT, text=""))
        
    assert not manager.request_queue.empty()
    manager.clear_queue()
    assert manager.request_queue.empty()
