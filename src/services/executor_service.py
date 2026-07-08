import os
import sys
import time
import uuid
from datetime import datetime
from typing import Union
from src.models.plan import ExecutionPlan, ExecutionContext, ToolResult, PlanItem
from src.models.workflow import WorkflowStep
from src.tools.registry import ToolRegistry
from src.utils.logger import get_logger, log_structured_tool_result, dump_debug_json
from src.services.metrics_service import MetricsService
from src.services.error_mapper import ErrorMapper
from src.models.error_codes import ErrorCode
import traceback

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

    def get_tool(self, tool_name: str):
        return self.registry.get_tool(tool_name)

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

    def execute_step(self, step: Union[WorkflowStep, PlanItem], context: ExecutionContext) -> ToolResult:
        """
        Executes a single workflow step using the tool registry.
        
        Args:
            step: The WorkflowStep to execute.
            context: The ExecutionContext payload.
            
        Returns:
            ToolResult: The structured result of the tool execution.
        """
        tool_name = step.tool
        arguments = step.arguments.copy()
        
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
                user_message="I don't know how to perform that action.",
                developer_message=msg,
                error_code=ErrorCode.UNKNOWN,
                duration=0.0
            )
            self.metrics.record_tool_usage(tool_name, False)
            return error_result
            
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
                developer_message=result.developer_message,
                error_code=result.error_code.value if result.error_code != ErrorCode.NONE else ""
            )
            
            return result
        except Exception as e:
            msg = f"Error during execution: {e}"
            stack = traceback.format_exc()
            logger.error(f"Error executing tool {tool_name}: {e}")
            self.metrics.record_tool_usage(tool_name, False)
            
            mapped_error = ErrorMapper.to_user_message(e)
            
            err_result = ToolResult(
                tool_name=tool_name,
                success=False,
                user_message=mapped_error.user_message,
                developer_message=msg,
                error_code=mapped_error.error_code,
                duration=0.0
            )
            log_structured_tool_result(
                logger_instance=logger,
                execution_id=context.execution_id,
                tool_name=tool_name,
                arguments=arguments,
                status="FAILED (EXCEPTION)",
                duration=0.0,
                developer_message=msg,
                error_code=mapped_error.error_code.value,
                stack_trace=stack
            )
            return err_result
