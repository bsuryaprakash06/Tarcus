import pytest
from src.services.context_service import ContextService
from src.events.pipeline_events import PipelineEventBus, PipelineEventType

def test_automation_entity_extraction():
    cs = ContextService()
    bus = PipelineEventBus()
    
    # Simulate a step completed event for Automation
    payload = {
        "result": {
            "tool_name": "open_application",
            "data": {"application": "Notepad", "pid": 1234}
        }
    }
    
    bus.publish(PipelineEventType.STEP_COMPLETED, payload)
    
    apps = cs.automation_context.applications
    assert len(apps) == 1
    assert apps[0].name == "Notepad"
    assert apps[0].metadata["pid"] == 1234

def test_knowledge_entity_extraction():
    cs = ContextService()
    bus = PipelineEventBus()
    
    payload = {
        "primary_topic": "Embedding",
        "secondary_topics": ["Vector"]
    }
    
    bus.publish(PipelineEventType.KNOWLEDGE_GENERATED, payload)
    
    assert cs.knowledge_context.current_topic == "Embedding"
