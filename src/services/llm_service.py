from src.brain.planner import Planner
from src.models.plan import ExecutionPlan
from src.tools.registry import ToolRegistry

class LLMService:
    """Service layer class interfacing with the LLM planner brain."""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.planner = Planner(tool_registry)

    def generate_plan(self, user_command: str) -> ExecutionPlan:
        """Generates a structured execution plan for the user command."""
        return self.planner.plan(user_command)
