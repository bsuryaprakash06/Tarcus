import time
from typing import Dict, Any, List
from pydantic import BaseModel
from src.utils.logger import get_logger
from src.models.scheduler import TaskGraph, TaskStatus
from src.scheduler.execution_queue import ExecutionQueue
from src.scheduler.task_dispatcher import TaskDispatcher
from src.scheduler.worker_pool import WorkerPool
from src.scheduler.handlers.automation_handler import AutomationHandler
from src.scheduler.handlers.knowledge_handler import KnowledgeHandler
from src.scheduler.handlers.workflow_handler import WorkflowHandler

logger = get_logger("scheduler.orchestrator")

class ExecutionSummary(BaseModel):
    success: bool
    completed_nodes: int
    failed_nodes: int
    duration_seconds: float
    results: Dict[str, Any]

class Scheduler:
    """
    Master orchestrator for executing a TaskGraph.
    Domain-agnostic and extensible for future agents.
    """
    def __init__(self):
        self.dispatcher = TaskDispatcher()
        self._register_handlers()
        
    def _register_handlers(self):
        # Dynamically register handlers (extensible for Browser/Vision later)
        self.dispatcher.register_handler("AutomationHandler", AutomationHandler())
        self.dispatcher.register_handler("KnowledgeHandler", KnowledgeHandler())
        self.dispatcher.register_handler("WorkflowHandler", WorkflowHandler())
        
    def execute(self, graph: TaskGraph) -> ExecutionSummary:
        """
        Executes the full graph asynchronously using the WorkerPool, blocking until finished.
        """
        start_time = time.time()
        
        if not graph.nodes:
            logger.warning("Empty TaskGraph provided to Scheduler.")
            return ExecutionSummary(success=True, completed_nodes=0, failed_nodes=0, duration_seconds=0.0, results={})
            
        logger.info(f"Scheduler starting execution of {len(graph.nodes)} nodes.")
        
        queue = ExecutionQueue(graph)
        pool = WorkerPool(queue, self.dispatcher)
        
        try:
            pool.start()
            # Wait for all tasks to reach terminal states (COMPLETED, FAILED, CANCELLED)
            while True:
                with queue.lock:
                    pending_or_running = any(n.status in (TaskStatus.PENDING, TaskStatus.READY, TaskStatus.WAITING, TaskStatus.RUNNING) for n in graph.nodes.values())
                    if not pending_or_running:
                        break
                time.sleep(0.1) # Small poll to prevent hot loop
                
        finally:
            pool.shutdown(wait=True)
            
        completed = sum(1 for n in graph.nodes.values() if n.status == TaskStatus.COMPLETED)
        failed = sum(1 for n in graph.nodes.values() if n.status == TaskStatus.FAILED)
        
        results = {node_id: node.result for node_id, node in graph.nodes.items() if node.status == TaskStatus.COMPLETED}
        
        duration = time.time() - start_time
        success = failed == 0
        
        logger.info(f"Scheduler finished in {duration:.2f}s. Success: {success}, Completed: {completed}, Failed: {failed}")
        
        return ExecutionSummary(
            success=success,
            completed_nodes=completed,
            failed_nodes=failed,
            duration_seconds=duration,
            results=results
        )
