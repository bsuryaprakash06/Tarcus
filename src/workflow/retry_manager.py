import os
from src.models.error_codes import ErrorCode
from src.models.plan import ToolResult
from src.models.workflow import WorkflowStep

# In a production environment this would be in settings.py, loaded here dynamically
MAX_STEP_RETRIES = int(os.environ.get("MAX_STEP_RETRIES", "2"))

class RetryManager:
    """Determines if a step should be retried based on failure type."""
    
    # Terminal errors that should never be retried because they will inevitably fail again
    TERMINAL_ERRORS = {
        ErrorCode.PERMISSION_DENIED,
        ErrorCode.VALIDATION_ERROR,
        ErrorCode.FILE_NOT_FOUND,
        ErrorCode.UNKNOWN,
        ErrorCode.EXECUTION_ERROR
    }
    
    @staticmethod
    def should_retry(step: WorkflowStep, result: ToolResult) -> bool:
        """Evaluates if the step is eligible for another attempt."""
        if result.success:
            return False
            
        if step.retry_count >= MAX_STEP_RETRIES:
            return False
            
        if result.error_code in RetryManager.TERMINAL_ERRORS:
            return False
            
        # Timeout or transient connection errors are inherently retryable
        return True
