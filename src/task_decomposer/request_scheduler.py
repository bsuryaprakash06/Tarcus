from typing import List
from src.models.task_query import AtomicTask, ExecutionGraph

class RequestScheduler:
    """Determines how to group and yield tasks from the Execution Graph for processing."""
    
    @staticmethod
    def schedule(graph: ExecutionGraph) -> List[List[AtomicTask]]:
        """
        Returns a list of task batches. 
        Tasks within the same inner list can be executed in parallel.
        The outer list represents sequential steps.
        """
        scheduled = []
        
        # Currently, since ExecutionGraphBuilder chains them all sequentially,
        # we return them one at a time in strict order.
        for task in sorted(graph.tasks, key=lambda x: x.order):
            scheduled.append([task])
            
        return scheduled
