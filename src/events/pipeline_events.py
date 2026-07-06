from typing import Callable, Dict, Any
from enum import Enum
from src.utils.logger import get_logger

logger = get_logger("events.pipeline")

class PipelineEventType(str, Enum):
    # Lifecycle
    INPUT_RECEIVED = "INPUT_RECEIVED"
    SPEECH_FINISHED = "SPEECH_FINISHED"
    NORMALIZATION_FINISHED = "NORMALIZATION_FINISHED"
    CONTEXT_RESOLVED = "CONTEXT_RESOLVED"
    INTENT_CLASSIFIED = "INTENT_CLASSIFIED"
    CLARIFICATION_REQUESTED = "CLARIFICATION_REQUESTED"
    CONFIRMATION_REQUESTED = "CONFIRMATION_REQUESTED"
    PLANNER_STARTED = "PLANNER_STARTED"
    KNOWLEDGE_GENERATED = "KNOWLEDGE_GENERATED"
    RESPONSE_GENERATED = "RESPONSE_GENERATED"
    TTS_STARTED = "TTS_STARTED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    
    # Workflow specific
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    WORKFLOW_PAUSED = "WORKFLOW_PAUSED"
    WORKFLOW_CANCELLED = "WORKFLOW_CANCELLED"
    
    STEP_STARTED = "STEP_STARTED"
    STEP_COMPLETED = "STEP_COMPLETED"
    STEP_FAILED = "STEP_FAILED"
    STEP_SKIPPED = "STEP_SKIPPED"
    STEP_RETRY = "STEP_RETRY"

class PipelineEventBus:
    """Singleton Pub/Sub event bus for decoupling execution from metrics and UI."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PipelineEventBus, cls).__new__(cls)
            cls._instance._subscribers = {}
        return cls._instance
        
    def subscribe(self, event_type: PipelineEventType, callback: Callable[[Dict[str, Any]], None]) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        
    def publish(self, event_type: PipelineEventType, payload: Dict[str, Any] = None) -> None:
        payload = payload or {}
        logger.debug(f"Event Emitted: {event_type.value} | Payload: {payload}")
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(payload)
                except Exception as e:
                    logger.error(f"Error in event subscriber for {event_type.value}: {e}")
