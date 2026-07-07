import pytest
from src.overlay.badge_manager import BadgeManager

def test_badge_manager_sequential_assignment():
    manager = BadgeManager()
    
    badge1 = manager.assign_badge("target-A")
    assert badge1 == "T1"
    
    badge2 = manager.assign_badge("target-B")
    assert badge2 == "T2"
    
def test_badge_manager_idempotency():
    manager = BadgeManager()
    
    badge1 = manager.assign_badge("target-A")
    badge2 = manager.assign_badge("target-A")
    
    assert badge1 == badge2 == "T1"
