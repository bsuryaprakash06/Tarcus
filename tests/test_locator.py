import pytest
from src.automation.locator import CompositeLocator, NameLocator, FuzzyLocator

class MockNode:
    def __init__(self, name="", auto_id="", class_name=""):
        self.Name = name
        self.AutomationId = auto_id
        self.ClassName = class_name

def test_name_locator():
    locator = NameLocator()
    node = MockNode(name="Save")
    assert locator.match(node, "Save") == 100.0
    assert locator.match(node, "Cancel") == 0.0

def test_fuzzy_locator():
    locator = FuzzyLocator()
    node = MockNode(name="Save File")
    score = locator.match(node, "Save")
    assert score > 50.0

def test_composite_locator():
    locator = CompositeLocator()
    nodes = [MockNode(name="Cancel"), MockNode(name="Save File"), MockNode(auto_id="btnSave")]
    
    # Exact auto_id match
    best, score = locator.find_best_match(nodes, "btnSave")
    assert best.AutomationId == "btnSave"
    assert score == 100.0
    
    # Fuzzy match
    best, score = locator.find_best_match(nodes, "Save")
    assert best.Name == "Save File"
    assert score > 75.0
