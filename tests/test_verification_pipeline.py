import pytest
from src.verification.verification_pipeline import VerificationPipeline
from src.verification.verification_cache import VerificationCache
from src.verification.verification_provider import VerificationProvider
from src.models.verification import VerificationStatus
from src.models.target import TargetSession, InteractionTarget

class MockProvider(VerificationProvider):
    @property
    def provider_name(self) -> str: return "Mock"
    
    def evaluate(self, rule_name: str, session: TargetSession, context: dict) -> bool:
        if rule_name == "pass_rule": return True
        if rule_name == "fail_rule": return False
        if rule_name == "error_rule": raise ValueError("Test Error")
        return False

def test_pipeline_all_pass():
    provider = MockProvider()
    cache = VerificationCache(ttl_seconds=1.0)
    pipeline = VerificationPipeline(provider, cache)
    
    session = TargetSession(
        session_id="s1",
        target=InteractionTarget(id="t1", properties={})
    )
    
    result = pipeline.execute(["pass_rule", "pass_rule"], session)
    assert result.status == VerificationStatus.SUCCESS
    assert len(result.failed_rules) == 0

def test_pipeline_partial_fail():
    provider = MockProvider()
    cache = VerificationCache(ttl_seconds=1.0)
    pipeline = VerificationPipeline(provider, cache)
    
    session = TargetSession(
        session_id="s1",
        target=InteractionTarget(id="t1", properties={})
    )
    
    # "pass_rule" from cache would pass, but let's just evaluate them
    result = pipeline.execute(["pass_rule", "fail_rule"], session)
    assert result.status == VerificationStatus.PARTIAL
    assert "fail_rule" in result.failed_rules
    assert "pass_rule" not in result.failed_rules

def test_pipeline_all_fail():
    provider = MockProvider()
    cache = VerificationCache(ttl_seconds=1.0)
    pipeline = VerificationPipeline(provider, cache)
    
    session = TargetSession(
        session_id="s1",
        target=InteractionTarget(id="t1", properties={})
    )
    
    result = pipeline.execute(["fail_rule", "error_rule"], session)
    assert result.status == VerificationStatus.FAILED
    assert "fail_rule" in result.failed_rules
    assert "error_rule" in result.failed_rules
