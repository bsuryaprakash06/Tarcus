import threading
from typing import List, Optional
from src.utils.logger import get_logger
from src.models.scheduler import ExecutionNode, TaskStatus, TaskGraph
from src.scheduler.resource_manager import ResourceManager

logger = get_logger("scheduler.execution_queue")

class ExecutionQueue:
    """
    Thread-safe priority queue managing the lifecycle of ExecutionNodes.
    Workers block on get_next_ready() until a node is available or the graph completes.
    """
    def __init__(self, graph: TaskGraph):
        self.graph = graph
        self.resource_manager = ResourceManager()
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        
        self.pending_count = len(graph.nodes)
        self.active_count = 0
        self.is_cancelled = False
        
    def cancel_all(self):
        with self.lock:
            self.is_cancelled = True
            for node in self.graph.nodes.values():
                if node.status in (TaskStatus.PENDING, TaskStatus.WAITING, TaskStatus.READY):
                    node.status = TaskStatus.CANCELLED
                    self.pending_count -= 1
            self.condition.notify_all()
            
    def get_next_ready(self) -> Optional[ExecutionNode]:
        """
        Blocks until a node is READY and its resources are available.
        Returns None if all tasks are complete or the graph is cancelled.
        """
        with self.lock:
            while not self.is_cancelled and (self.pending_count > 0 or self.active_count > 0):
                # 1. Update states (PENDING -> READY)
                for node in self.graph.nodes.values():
                    if node.status == TaskStatus.PENDING:
                        deps_met = all(self.graph.nodes[dep].status == TaskStatus.COMPLETED for dep in node.dependencies if dep in self.graph.nodes)
                        deps_failed = any(self.graph.nodes[dep].status in (TaskStatus.FAILED, TaskStatus.CANCELLED) for dep in node.dependencies if dep in self.graph.nodes)
                        
                        if deps_failed:
                            node.status = TaskStatus.CANCELLED
                            self.pending_count -= 1
                            logger.info(f"Node {node.id} cancelled due to dependency failure.")
                        elif deps_met:
                            node.status = TaskStatus.READY
                            
                # 2. Find READY nodes sorted by priority (higher int = higher priority)
                ready_nodes = [n for n in self.graph.nodes.values() if n.status == TaskStatus.READY]
                ready_nodes.sort(key=lambda x: x.priority, reverse=True)
                
                # 3. Try to lock resources and return the first acquirable node
                for node in ready_nodes:
                    if self.resource_manager.acquire_locks(node.id, node.resource_requirements):
                        node.status = TaskStatus.RUNNING
                        self.pending_count -= 1
                        self.active_count += 1
                        return node
                        
                # 4. Nothing is ready (or resources are locked), wait for another task to complete
                self.condition.wait()
                
            return None # Graph finished or cancelled
            
    def mark_completed(self, node_id: str, result: Any = None):
        with self.lock:
            node = self.graph.nodes[node_id]
            node.status = TaskStatus.COMPLETED
            node.result = result
            self.active_count -= 1
            self.resource_manager.release_locks(node_id)
            self.condition.notify_all()
            
    def mark_failed(self, node_id: str, error: str):
        with self.lock:
            node = self.graph.nodes[node_id]
            node.status = TaskStatus.FAILED
            node.error = error
            self.active_count -= 1
            self.resource_manager.release_locks(node_id)
            self.condition.notify_all()
