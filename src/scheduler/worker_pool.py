import concurrent.futures
import time
from typing import Optional
from src.utils.logger import get_logger
from src.models.scheduler import ExecutionNode, TaskStatus
from src.scheduler.execution_queue import ExecutionQueue
from src.scheduler.task_dispatcher import TaskDispatcher
from src.events.pipeline_events import PipelineEventBus, PipelineEventType
from src.utils.settings import MAX_WORKER_THREADS

logger = get_logger("scheduler.worker_pool")

class WorkerPool:
    """
    Manages a pool of threads that constantly pull READY tasks from the ExecutionQueue.
    Abstracts away concurrency primitives.
    """
    def __init__(self, queue: ExecutionQueue, dispatcher: TaskDispatcher):
        self.queue = queue
        self.dispatcher = dispatcher
        self.event_bus = PipelineEventBus()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS)
        self.futures = []
        
    def start(self):
        """Starts worker threads pulling from the queue."""
        logger.info(f"Starting WorkerPool with {MAX_WORKER_THREADS} threads.")
        for i in range(MAX_WORKER_THREADS):
            future = self.executor.submit(self._worker_loop, i)
            self.futures.append(future)
            
    def _worker_loop(self, worker_id: int):
        import pythoncom
        pythoncom.CoInitialize()
        logger.debug(f"Worker {worker_id} started.")
        try:
            while True:
                node = self.queue.get_next_ready()
                if not node:
                    break # Queue is empty and graph is complete/cancelled
                    
                self._execute_node(worker_id, node)
        finally:
            logger.debug(f"Worker {worker_id} exiting.")
            pythoncom.CoUninitialize()
        
    def _execute_node(self, worker_id: int, node: ExecutionNode):
        node.started_at = time.time()
        logger.info(f"[Worker {worker_id}] Started node {node.id} ({node.handler_type})")
        self.event_bus.publish(PipelineEventType.STEP_STARTED, {"node_id": node.id, "handler": node.handler_type})
        
        try:
            result = self.dispatcher.dispatch(node)
            node.completed_at = time.time()
            logger.info(f"[Worker {worker_id}] Completed node {node.id}")
            
            self.event_bus.publish(PipelineEventType.STEP_COMPLETED, {"node_id": node.id, "result": str(result)})
            self.queue.mark_completed(node.id, result)
            
        except Exception as e:
            node.completed_at = time.time()
            logger.error(f"[Worker {worker_id}] Failed node {node.id}: {e}")
            
            self.event_bus.publish(PipelineEventType.STEP_FAILED, {"node_id": node.id, "error": str(e)})
            self.queue.mark_failed(node.id, str(e))
            
    def shutdown(self, wait: bool = True):
        logger.info("Shutting down WorkerPool...")
        self.queue.cancel_all()
        self.executor.shutdown(wait=wait)
