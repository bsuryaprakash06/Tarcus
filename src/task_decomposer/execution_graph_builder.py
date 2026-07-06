from typing import List
from src.models.task_query import AtomicTask, ExecutionGraph, DependencyType
from src.utils.logger import get_logger

logger = get_logger("task.graph")

class ExecutionGraphBuilder:
    """Analyzes atomic tasks to build an execution graph with explicit dependencies."""
    
    @staticmethod
    def build(tasks: List[AtomicTask]) -> ExecutionGraph:
        """
        For this milestone, we apply a deterministic heuristic: 
        All tasks are sequential by default unless explicitly parallelized.
        The LLM provided the 'order', so we chain them sequentially.
        """
        graph = ExecutionGraph(tasks=tasks)
        
        for i in range(1, len(tasks)):
            prev_task = tasks[i-1]
            curr_task = tasks[i]
            
            curr_task.depends_on.append(prev_task.id)
            curr_task.dependency_type = DependencyType.SEQUENTIAL
            
        logger.info(f"Built execution graph with {len(tasks)} tasks.")
        return graph
