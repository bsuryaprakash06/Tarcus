import pytest
from src.task_decomposer.execution_graph_builder import ExecutionGraphBuilder
from src.task_decomposer.request_scheduler import RequestScheduler
from src.models.task_query import AtomicTask, DependencyType

def test_execution_graph_sequential():
    tasks = [
        AtomicTask(id="1", text="Task 1", order=1),
        AtomicTask(id="2", text="Task 2", order=2),
    ]
    
    graph = ExecutionGraphBuilder.build(tasks)
    
    assert len(graph.tasks) == 2
    # Verify sequential dependency
    assert graph.tasks[1].depends_on == ["1"]
    assert graph.tasks[1].dependency_type == DependencyType.SEQUENTIAL

def test_request_scheduler():
    tasks = [
        AtomicTask(id="1", text="Task 1", order=1),
        AtomicTask(id="2", text="Task 2", order=2),
    ]
    
    graph = ExecutionGraphBuilder.build(tasks)
    batches = RequestScheduler.schedule(graph)
    
    assert len(batches) == 2
    assert batches[0][0].id == "1"
    assert batches[1][0].id == "2"
