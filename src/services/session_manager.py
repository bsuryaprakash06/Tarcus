import queue
from typing import Optional
from src.models.input import InputRequest
from src.events.pipeline_events import PipelineEventBus
from src.utils.logger import get_logger

logger = get_logger("session.manager")

class SessionManager:
    """Sits directly between the UI and the Pipeline. Owns the thread-safe request queue."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.request_queue = queue.Queue()
            cls._instance.active_request: Optional[InputRequest] = None
            cls._instance.event_bus = PipelineEventBus()
        return cls._instance
        
    def enqueue(self, request: InputRequest) -> None:
        """UI calls this to add a new request to the processing queue."""
        logger.info(f"Enqueuing request {request.request_id} from {request.source.value}")
        self.request_queue.put(request)
        
    def dequeue(self) -> Optional[InputRequest]:
        """Pipeline Worker Thread calls this to get the next request to process."""
        try:
            request = self.request_queue.get(block=False)
            self.active_request = request
            return request
        except queue.Empty:
            return None
            
    def complete_request(self) -> None:
        """Marks the currently active request as finished, allowing the worker to grab the next one."""
        if self.active_request:
            logger.debug(f"Completed request {self.active_request.request_id}")
            self.request_queue.task_done()
            self.active_request = None
            
    def clear_queue(self) -> None:
        """Empties all pending items in the queue (e.g. during a hard cancellation)."""
        while not self.request_queue.empty():
            try:
                self.request_queue.get_nowait()
                self.request_queue.task_done()
            except queue.Empty:
                break
        logger.info("Session request queue cleared.")
