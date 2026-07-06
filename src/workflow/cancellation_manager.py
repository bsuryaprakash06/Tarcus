import threading
from typing import Dict, Optional
from src.models.workflow import WorkflowStatus
from src.utils.logger import get_logger

logger = get_logger("workflow.cancellation")

class CancellationManager:
    """Thread-safe interface for managing async workflow interruption requests."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CancellationManager, cls).__new__(cls)
            cls._instance._lock = threading.Lock()
            # Maps workflow_id -> target WorkflowStatus (PAUSED or CANCELLED)
            cls._instance._interrupt_requests: Dict[str, WorkflowStatus] = {}
        return cls._instance
        
    def request_pause(self, workflow_id: str) -> None:
        """Safely requests the engine to pause before the next step."""
        with self._lock:
            self._interrupt_requests[workflow_id] = WorkflowStatus.PAUSED
            logger.info(f"Requested PAUSE for workflow {workflow_id}")
            
    def request_cancel(self, workflow_id: str) -> None:
        """Safely requests the engine to cancel execution."""
        with self._lock:
            self._interrupt_requests[workflow_id] = WorkflowStatus.CANCELLED
            logger.info(f"Requested CANCEL for workflow {workflow_id}")
            
    def clear_request(self, workflow_id: str) -> None:
        """Clears any pending interrupt flags for the workflow."""
        with self._lock:
            self._interrupt_requests.pop(workflow_id, None)
            
    def get_interrupt_request(self, workflow_id: str) -> Optional[WorkflowStatus]:
        """Returns the pending interrupt status if one exists, otherwise None."""
        with self._lock:
            return self._interrupt_requests.get(workflow_id)
