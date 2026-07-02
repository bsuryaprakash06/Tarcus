import os
import sys
import time
import uuid
from datetime import datetime
from src.models.plan import ExecutionPlan, ExecutionContext, ToolResult
from src.tools.registry import ToolRegistry
from src.utils.logger import get_logger, log_structured_tool_result, dump_debug_json
from src.services.metrics_service import MetricsService

logger = get_logger("executor_service")

def normalize_query(query: str) -> str:
    """Lightweight rule-based normalization for common query terms."""
    if not isinstance(query, str):
        return query
    
    mapping = {
        "chat gpt": "ChatGPT",
        "chatgpt": "ChatGPT",
        "github": "GitHub",
        "youtube": "YouTube"
    }
    
    import re
    lower_q = query.lower()
    for key, val in mapping.items():
        if key in lower_q:
            query = re.sub(re.escape(key), val, query, flags=re.IGNORECASE)
    return query

class ExecutorService:
    """Service layer class responsible for executing sequential plan items using the tool registry."""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.registry = tool_registry or ToolRegistry()
        self.metrics = MetricsService()

    def get_current_context(self, session_id: str = "") -> ExecutionContext:
        """Gathers system and environment information into a lightweight ExecutionContext."""
        try:
            user = os.getlogin()
        except Exception:
            user = os.environ.get("USERNAME", "unknown")
            
        if not session_id:
            session_id = uuid.uuid4().hex[:8]
            
        execution_id = uuid.uuid4().hex[:8]
            
        return ExecutionContext(
            cwd=os.getcwd(),
            os=sys.platform,
            user=user,
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            session_id=session_id,
            execution_id=execution_id
        )

    def execute_plan(self, plan: ExecutionPlan, session_id: str = "") -> list[ToolResult]:
        """
        Executes a sequence of planned tool calls and returns the structured results.
        
        Args:
            plan: The ExecutionPlan to execute.
            session_id: The session ID for the execution context.
            
        Returns:
            list[ToolResult]: List of results for each executed step.
        """
        results = []
        context = self.get_current_context(session_id)
        
        # Structured log of the incoming plan and context
        logger.info(f"Starting Execution Phase for execution_id: {context.execution_id}")
        dump_debug_json(logger, "Planner JSON Plan", plan.model_dump())
        dump_debug_json(logger, "Execution Context", context.model_dump())
        
        for index, item in enumerate(plan.plan, 1):
            tool_name = item.tool
            arguments = item.arguments
            
            # Normalize arguments
            for key, val in arguments.items():
                if isinstance(val, str):
                    arguments[key] = normalize_query(val)
            
            tool = self.registry.get_tool(tool_name)
            
            if not tool:
                msg = f"Tool '{tool_name}' is not supported."
                logger.error(msg)
                error_result = ToolResult(
                    tool_name=tool_name,
                    success=False,
                    message=msg,
                    duration=0.0
                )
                self.metrics.record_tool_usage(tool_name, False)
                results.append(error_result)
                continue
                
            try:
                start_time = time.time()
                result = tool.execute(arguments, context)
                duration = time.time() - start_time
                
                # Update duration if tool doesn't populate it perfectly
                if result.duration == 0.0:
                    result.duration = duration
                    
                self.metrics.record_execution_latency(result.duration)
                self.metrics.record_tool_usage(tool_name, result.success)
                
                log_structured_tool_result(
                    logger_instance=logger,
                    execution_id=context.execution_id,
                    tool_name=tool_name,
                    arguments=arguments,
                    status="SUCCESS" if result.success else "FAILED",
                    duration=result.duration,
                    message=result.message
                )
                
                results.append(result)
            except Exception as e:
                msg = f"Error during execution: {e}"
                logger.error(f"Error executing step {index} ({tool_name}): {e}")
                self.metrics.record_tool_usage(tool_name, False)
                
                err_result = ToolResult(
                    tool_name=tool_name,
                    success=False,
                    message=msg,
                    duration=0.0
                )
                log_structured_tool_result(
                    logger_instance=logger,
                    execution_id=context.execution_id,
                    tool_name=tool_name,
                    arguments=arguments,
                    status="FAILED (EXCEPTION)",
                    duration=0.0,
                    message=msg
                )
                results.append(err_result)
                
        return results
