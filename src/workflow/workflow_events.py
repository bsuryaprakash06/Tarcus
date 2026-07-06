from typing import Callable, Dict, List, Any
from enum import Enum
from src.utils.logger import get_logger

logger = get_logger("workflow.events")

class WorkflowEventType(str, Enum):
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

class WorkflowEventBus:
    """Singleton Pub/Sub event bus for decoupling execution from metrics and UI."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WorkflowEventBus, cls).__new__(cls)
            cls._instance._subscribers = {}
        return cls._instance
        
    def subscribe(self, event_type: WorkflowEventType, callback: Callable[[Dict[str, Any]], None]) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        
    def publish(self, event_type: WorkflowEventType, payload: Dict[str, Any]) -> None:
        logger.debug(f"Event Emitted: {event_type.value} | Payload: {payload}")
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(payload)
                except Exception as e:
                    logger.error(f"Error in event subscriber for {event_type.value}: {e}")
