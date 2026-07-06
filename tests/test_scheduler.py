from src.models.scheduler import TaskGraph, ExecutionNode, ExecutionStrategy, ResourceLock, ResourceType, TaskStatus
from src.scheduler.execution_queue import ExecutionQueue
from src.scheduler.resource_manager import ResourceManager
import time

def test_dag_dependency_ordering():
    graph = TaskGraph()
    
    node1 = ExecutionNode(id="task_1", handler_type="Dummy", payload={}, dependencies=[])
    node2 = ExecutionNode(id="task_2", handler_type="Dummy", payload={}, dependencies=["task_1"])
    
    graph.add_node(node1)
    graph.add_node(node2)
    
    queue = ExecutionQueue(graph)
    
    # Task 1 should be ready
    ready_node = queue.get_next_ready()
    assert ready_node is not None
    assert ready_node.id == "task_1"
    
    # If we call again without completing task 1, it should block (simulate by asserting no other node is ready without waiting)
    # Actually get_next_ready blocks. So we must mark completed first in a real scenario.
    queue.mark_completed("task_1", result="done")
    
    # Now task 2 should be ready
    ready_node2 = queue.get_next_ready()
    assert ready_node2 is not None
    assert ready_node2.id == "task_2"
    
    queue.mark_completed("task_2", result="done")
    
    # Graph is empty
    assert queue.get_next_ready() is None

def test_resource_locks_exclusive():
    graph = TaskGraph()
    
    lock1 = ResourceLock(resource_type=ResourceType.APPLICATION, identifier="notepad", exclusive=True)
    
    node1 = ExecutionNode(id="task_1", handler_type="Dummy", payload={}, resource_requirements=[lock1])
    node2 = ExecutionNode(id="task_2", handler_type="Dummy", payload={}, resource_requirements=[lock1])
    
    graph.add_node(node1)
    graph.add_node(node2)
    
    queue = ExecutionQueue(graph)
    
    ready_1 = queue.get_next_ready()
    assert ready_1 is not None
    
    # Resource manager should now have the lock
    rm = ResourceManager()
    # Attempting to acquire again for node 2 should fail
    assert not rm.acquire_locks("task_2", [lock1])
    
    queue.mark_completed(ready_1.id)
    
    # Now node 2 can acquire
    ready_2 = queue.get_next_ready()
    assert ready_2 is not None
    assert ready_2.id != ready_1.id
    queue.mark_completed(ready_2.id)
