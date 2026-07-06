from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple
from rapidfuzz import fuzz

class BaseLocatorStrategy(ABC):
    """Evaluates a node and returns a confidence score (0.0 to 100.0)."""
    @abstractmethod
    def match(self, node: Any, query: str) -> float:
        pass

class NameLocator(BaseLocatorStrategy):
    def match(self, node: Any, query: str) -> float:
        name = getattr(node, "Name", "")
        if name and name.lower() == query.lower():
            return 100.0
        return 0.0

class AutomationIdLocator(BaseLocatorStrategy):
    def match(self, node: Any, query: str) -> float:
        auto_id = getattr(node, "AutomationId", "")
        if auto_id and auto_id.lower() == query.lower():
            return 100.0
        return 0.0
        
class ClassLocator(BaseLocatorStrategy):
    def match(self, node: Any, query: str) -> float:
        cls_name = getattr(node, "ClassName", "")
        if cls_name and cls_name.lower() == query.lower():
            return 100.0
        return 0.0
        
class FuzzyLocator(BaseLocatorStrategy):
    def match(self, node: Any, query: str) -> float:
        name = getattr(node, "Name", "")
        if not name:
            return 0.0
        return fuzz.WRatio(query.lower(), name.lower())

class CompositeLocator:
    """
    Evaluates multiple locator strategies to find the best matching UI node.
    """
    def __init__(self):
        # Ordered by strictness and performance
        self.strategies = [
            AutomationIdLocator(),
            NameLocator(),
            ClassLocator(),
            FuzzyLocator()
        ]
        
    def find_best_match(self, nodes: List[Any], query: str, min_confidence: float = 75.0) -> Tuple[Optional[Any], float]:
        """
        Iterates over all nodes and strategies to find the highest scoring match.
        """
        best_node = None
        best_score = 0.0
        
        for node in nodes:
            for strategy in self.strategies:
                score = strategy.match(node, query)
                if score == 100.0:
                    return node, 100.0 # Instant exact match
                    
                if score > best_score:
                    best_score = score
                    best_node = node
                    
        if best_score >= min_confidence:
            return best_node, best_score
            
        return None, 0.0
