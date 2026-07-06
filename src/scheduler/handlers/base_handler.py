import abc
from typing import Any
from src.models.scheduler import ExecutionNode

class BaseHandler(abc.ABC):
    """
    Abstract base class for all execution handlers (e.g., Automation, Knowledge, Vision, Browser).
    This strictly decouples the Scheduler's orchestration logic from the actual execution details.
    """
    
    @abc.abstractmethod
    def execute(self, node: ExecutionNode) -> Any:
        """
        Executes the payload contained within the node.
        Must return the result of the execution, or raise an Exception on failure.
        """
        pass
