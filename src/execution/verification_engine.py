import warnings
from typing import Dict, Any, Tuple
from src.utils.logger import get_logger

logger = get_logger("execution.verification_engine")

class VerificationEngine:
    """
    DEPRECATED: Use src.verification.verification_manager.VerificationManager instead.
    This class is maintained only as a thin wrapper to prevent breaking legacy imports.
    """
    def __init__(self):
        warnings.warn(
            "src.execution.verification_engine.VerificationEngine is deprecated. "
            "Use src.verification.verification_manager.VerificationManager instead.",
            DeprecationWarning, stacklevel=2
        )
        logger.warning("Instantiated deprecated VerificationEngine.")
        
    def verify(self, rule: Any, context: Any) -> Tuple[Any, str]:
        # Return a simulated pass for legacy code, as new code uses ExecutionController directly
        return None, "Deprecated"
