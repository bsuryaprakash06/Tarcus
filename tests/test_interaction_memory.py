import pytest
from src.models.interaction import InteractionNode
from src.interaction.interaction_memory import InteractionMemory

def test_interaction_memory_scoping():
    memory = InteractionMemory()
    
    app_node = InteractionNode(id="app1", name="Notepad", role="application")
    window_node = InteractionNode(id="win1", name="Untitled", role="window")
    control_node = InteractionNode(id="btn1", name="Save", role="button")
    
    memory.set_active_app(app_node)
    memory.set_active_window(window_node)
    memory.set_active_control(control_node)
    
    context = memory.get_context()
    
    assert context["app"] == app_node
    assert context["window"] == window_node
    assert context["control"] == control_node
    
    # Simulate closing window
    memory.clear()
    context = memory.get_context()
    assert context["app"] is None
    assert context["window"] is None
    assert context["control"] is None
