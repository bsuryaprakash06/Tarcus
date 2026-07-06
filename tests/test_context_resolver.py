import pytest
import time
from src.services.context_service import ContextService
from src.models.context_scope import AutomationEntity

def test_context_resolution_priorities():
    cs = ContextService()
    
    # 1. Test Automation Resolution
    entity1 = AutomationEntity(id="1", type="Application", name="Notepad", tool="open_application")
    entity1.last_accessed = time.time() - 10 # 10 seconds ago
    
    cs.automation_context.add_entity(entity1, "applications")
    
    res, conf = cs.resolve_reference("Close it.", "AUTOMATION")
    assert res == "Close Notepad."
    assert conf == 1.0
    
    # 2. Test Knowledge Resolution (Knowledge should NOT resolve to Notepad)
    cs.knowledge_context.current_topic = "Embeddings"
    res, conf = cs.resolve_reference("Explain it.", "KNOWLEDGE")
    assert res == "Explain Embeddings."
    assert conf == 1.0
    
    # 3. Test Ambiguity (Two apps opened at the same time)
    entity2 = AutomationEntity(id="2", type="Application", name="Calculator", tool="open_application")
    entity2.last_accessed = time.time() - 9.5 # 0.5s difference
    cs.automation_context.add_entity(entity2, "applications")
    
    res, conf = cs.resolve_reference("Close it.", "AUTOMATION")
    assert conf == 0.50 # Ambiguous
    assert res == "Close it." # Resolver leaves unmodified on low confidence
