import os
import sys
import time
from datetime import datetime
import pyperclip
from src.models.plan import ExecutionPlan, ExecutionContext, ToolResult
from src.tools.registry import ToolRegistry
from src.utils.logger import get_logger

logger = get_logger("executor_service")

class ExecutorService:
    """Service layer class responsible for executing sequential plan items using the tool registry."""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.registry = tool_registry or ToolRegistry()

    def get_current_context(self) -> ExecutionContext:
        """Gathers system and environment information into an ExecutionContext."""
        try:
            user = os.getlogin()
        except Exception:
            user = os.environ.get("USERNAME", "unknown")
            
        try:
            clipboard = pyperclip.paste()
        except Exception:
            clipboard = ""
            
        return ExecutionContext(
            cwd=os.getcwd(),
            os=sys.platform,
            user=user,
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            clipboard=clipboard
        )

    def execute_plan(self, plan: ExecutionPlan) -> list[ToolResult]:
        """
        Executes a sequence of planned tool calls and returns the structured results.
        
        Args:
            plan: The ExecutionPlan to execute.
            
        Returns:
            list[ToolResult]: List of results for each executed step.
        """
        results = []
        context = self.get_current_context()
        
        # Structured log of the incoming plan and context
        logger.info("Planner JSON plan received:")
        logger.info(plan.model_dump_json(indent=2))
        logger.info("Execution context:")
        logger.info(context.model_dump_json(indent=2))
        
        for index, item in enumerate(plan.plan, 1):
            tool_name = item.tool
            arguments = item.arguments
            
            logger.info(f"Step {index}: Fetching tool '{tool_name}'...")
            tool = self.registry.get_tool(tool_name)
            
            if not tool:
                logger.error(f"Tool '{tool_name}' not found in registry.")
                error_result = ToolResult(
                    tool_name=tool_name,
                    success=False,
                    message=f"Tool '{tool_name}' is not supported.",
                    duration=0.0
                )
                results.append(error_result)
                continue
                
            try:
                start_time = time.time()
                result = tool.execute(arguments, context)
                duration = time.time() - start_time
                
                # Update duration if tool doesn't populate it perfectly
                if result.duration == 0.0:
                    result.duration = duration
                    
                # Structured logs for execution results
                logger.info(f"Executor result for tool '{tool_name}':")
                logger.info(f"  Status: {'SUCCESS' if result.success else 'FAILED'}")
                logger.info(f"  Duration: {result.duration:.2f} s")
                logger.info(f"  Message: {result.message}")
                
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing step {index} ({tool_name}): {e}")
                results.append(ToolResult(
                    tool_name=tool_name,
                    success=False,
                    message=f"Error during execution: {e}",
                    duration=0.0
                ))
                
        return results
