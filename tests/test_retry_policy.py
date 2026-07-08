import pytest
import time
from src.verification.retry_policy import RetryPolicyExecutor

def test_retry_policy_success_first_try():
    calls = 0
    def my_func():
        nonlocal calls
        calls += 1
        return "ok"
        
    result = RetryPolicyExecutor.execute_with_retry(my_func, max_retries=2, backoff_base=0.1)
    assert result == "ok"
    assert calls == 1

def test_retry_policy_success_after_retry():
    calls = 0
    def my_func():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ValueError("Fail")
        return "ok"
        
    start_time = time.time()
    result = RetryPolicyExecutor.execute_with_retry(my_func, max_retries=3, backoff_base=0.1)
    duration = time.time() - start_time
    
    assert result == "ok"
    assert calls == 3
    assert duration >= 0.2 # 0.1s + 0.2s approx

def test_retry_policy_exhausted():
    calls = 0
    def my_func():
        nonlocal calls
        calls += 1
        raise ValueError("Fail")
        
    with pytest.raises(ValueError):
        RetryPolicyExecutor.execute_with_retry(my_func, max_retries=2, backoff_base=0.01)
        
    assert calls == 3 # Initial + 2 retries
