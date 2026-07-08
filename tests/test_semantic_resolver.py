import pytest
from src.models.interaction import InteractionNode, InteractionState
from src.interaction.interaction_graph import InteractionGraph
from src.interaction.interaction_memory import InteractionMemory
from src.interaction.semantic_resolver import SemanticResolver

def test_semantic_resolver_scoring():
    graph = InteractionGraph()
    memory = InteractionMemory()
    resolver = SemanticResolver(graph, memory)
    
    # Add some nodes
    node1 = InteractionNode(id="n1", name="Save Button", role="button", visibility=True)
    node2 = InteractionNode(id="n2", name="Save As", role="menuitem", visibility=True)
    node3 = InteractionNode(id="n3", name="Cancel", role="button", visibility=True)
    
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    
    # 1. Exact Name + Role match
    result = resolver.resolve("save", role_hint="button")
    assert result is not None
    assert result.id == "n1"
    
    # 2. Partial Name + Role match
    result = resolver.resolve("save", role_hint="menuitem")
    assert result is not None
    assert result.id == "n2"
    
    # 3. Contextual boost (Simulate a window context)
    window_node = InteractionNode(id="w1", name="Dialog", role="window")
    memory.set_active_window(window_node)
    
    # Create two nodes with same name, but one is a child of the active window
    node4 = InteractionNode(id="n4", name="Ok", role="button", parent_id="w1", visibility=True)
    node5 = InteractionNode(id="n5", name="Ok", role="button", parent_id="w2", visibility=True)
    graph.add_node(node4)
    graph.add_node(node5)
    
    result = resolver.resolve("ok")
    assert result is not None
    assert result.id == "n4" # Resolves to the one in the active window due to context scoring

def test_semantic_resolver_memory_shortcut():
    graph = InteractionGraph()
    memory = InteractionMemory()
    resolver = SemanticResolver(graph, memory)
    
    editor_node = InteractionNode(id="e1", name="Main Document", role="edit", visibility=True)
    memory.set_active_control(editor_node)
    
    # 'Continue typing' should bypass the graph completely and use the active control
    result = resolver.resolve("continue typing")
    assert result is not None
    assert result.id == "e1"
