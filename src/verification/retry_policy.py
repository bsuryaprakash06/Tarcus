import time
from typing import Callable, Any
from src.utils.logger import get_logger

logger = get_logger("verification.retry")

class RetryPolicyExecutor:
    """
    Executes a function with retry logic based on a max_retries count.
    Supports exponential backoff or immediate retries.
    """
    @staticmethod
    def execute_with_retry(func: Callable, max_retries: int = 2, backoff_base: float = 0.5) -> Any:
        attempts = 0
        last_exception = None
        
        while attempts <= max_retries:
            try:
                if attempts > 0:
                    logger.info(f"Retry attempt {attempts}/{max_retries}")
                return func()
            except Exception as e:
                last_exception = e
                attempts += 1
                if attempts <= max_retries:
                    sleep_time = backoff_base * (2 ** (attempts - 1))
                    logger.warning(f"Execution failed: {e}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    
        logger.error(f"Execution failed after {max_retries} retries.")
        raise last_exception
