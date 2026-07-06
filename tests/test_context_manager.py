import pytest
from src.models.context import SessionContext, EntityType
from src.context.entity_tracker import EntityTracker
from src.context.session import SessionStore
from src.context.context_resolver import ContextResolver
from src.models.plan import ExecutionPlan, PlanItem

def test_entity_tracker_extraction():
    context = SessionContext(session_id="test-1")
    plan = ExecutionPlan(
        plan=[
            PlanItem(tool="open_application", arguments={"application": "Notepad"}),
            PlanItem(tool="create_folder", arguments={"name": "Physics"})
        ]
    )
    
    EntityTracker.extract_from_plan(plan, context)
    
    assert context.automation.last_application is not None
    assert context.automation.last_application.value == "Notepad"
    
    assert context.automation.last_folder is not None
    assert context.automation.last_folder.value == "Physics"
    
def test_knowledge_topic_extraction():
    context = SessionContext(session_id="test-2")
    query = "What is an embedding?"
    
    EntityTracker.extract_knowledge_topic(query, context)
    
    assert context.knowledge.current_topic is not None
    assert context.knowledge.current_topic.value == "What is an embedding?"
    
def test_deterministic_resolution():
    context = SessionContext(session_id="test-3")
    plan = ExecutionPlan(
        plan=[
            PlanItem(tool="open_application", arguments={"application": "Calculator"})
        ]
    )
    EntityTracker.extract_from_plan(plan, context)
    
    resolver = ContextResolver()
    
    # The fast path should instantly resolve this without hitting the LLM (confidence >= 0.90)
    resolved, conf = resolver.resolve("Close it", context)
    assert resolved.lower() == "close calculator"
    assert conf >= 0.90
    
def test_session_store_clearing():
    store = SessionStore()
    store.clear_session() # ensure empty state
    
    session = store.get_or_create_session()
    assert store.current_session is not None
    assert store.current_session.session_id == session.session_id
    
    store.clear_session()
    assert store.current_session is None
