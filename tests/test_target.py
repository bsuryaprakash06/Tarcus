from src.models.target import Target, TargetType, TargetLifecycle, TargetCapability
from src.automation.target_registry import TargetRegistry
from src.automation.target_resolver import TargetResolver

def test_target_registry_lifecycle():
    registry = TargetRegistry()
    
    # Simulate a new window being discovered
    t1 = Target(
        id="", type=TargetType.WINDOW, backend="windows_uia", 
        name="Notepad", native_handle="0x111", 
        lifecycle_state=TargetLifecycle.DISCOVERED,
        capabilities=[TargetCapability.TYPING]
    )
    
    registered = registry.register_target(t1)
    
    # Should assign ID and promote to AVAILABLE
    assert registered.id.startswith("target_")
    assert registered.lifecycle_state == TargetLifecycle.AVAILABLE
    
    # Simulate window closing
    registry.update_lifecycle(registered.id, TargetLifecycle.CLOSED)
    
    # Active targets should not include closed ones
    active = registry.list_targets(active_only=True)
    assert len(active) == 0
    
def test_target_resolver():
    registry = TargetRegistry()
    # Add a target manually for testing
    t2 = Target(
        id="test_id", type=TargetType.BROWSER_TAB, backend="playwright", 
        name="YouTube - Google Chrome", native_handle="tab_1", 
        lifecycle_state=TargetLifecycle.ACTIVE,
        capabilities=[]
    )
    registry.register_target(t2)
    
    resolver = TargetResolver()
    
    # Should resolve fuzzy name
    resolved = resolver.resolve("youtube")
    assert resolved is not None
    assert resolved.native_handle == "tab_1"
    
    # Should not resolve bad name
    bad_resolve = resolver.resolve("calculator")
    assert bad_resolve is None
