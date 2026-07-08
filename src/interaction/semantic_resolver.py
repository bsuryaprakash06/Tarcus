from typing import Optional, List, Tuple
from src.models.interaction import InteractionNode
from src.interaction.interaction_graph import InteractionGraph
from src.interaction.interaction_memory import InteractionMemory
from src.utils.logger import get_logger

logger = get_logger("interaction.resolver")

class SemanticResolver:
    """
    Resolves natural language intents ("Click Save", "Continue typing") to specific InteractionNodes.
    Uses a scoring engine rather than simple fuzzy matching.
    """
    def __init__(self, graph: InteractionGraph, memory: InteractionMemory):
        self.graph = graph
        self.memory = memory

    def resolve(self, intent: str, role_hint: str = "") -> Optional[InteractionNode]:
        """
        Resolves an intent in the following order:
        1. Dialogue Context (Explicit references like 'Click it')
        2. Interaction Memory (Contextual fallback like 'Continue typing')
        3. Interaction Graph (Scoring Engine)
        """
        intent = intent.lower()
        
        # 1. & 2. Check Interaction Memory / Dialogue Context
        context = self.memory.get_context()
        if intent in ["it", "that", "this", "continue", "continue typing", "type here"]:
            if context["control"]:
                logger.info(f"Resolved '{intent}' to InteractionMemory Control Scope: {context['control'].id}")
                return context["control"]
            elif context["window"]:
                # Could be a window-level operation
                return context["window"]
                
        # 3. Score against Interaction Graph
        candidates = list(self.graph.nodes.values())
        if not candidates:
            logger.warning("InteractionGraph is empty. Cannot resolve.")
            return None
            
        best_node, best_score = self._score_candidates(intent, role_hint, candidates, context)
        
        if best_node and best_score > 0.3: # Minimum confidence threshold
            logger.info(f"Resolved '{intent}' to '{best_node.name}' (Role: {best_node.role}) with score {best_score:.2f}")
            return best_node
            
        logger.warning(f"Could not reliably resolve intent: '{intent}'")
        return None

    def _score_candidates(self, intent: str, role_hint: str, candidates: List[InteractionNode], context: dict) -> Tuple[Optional[InteractionNode], float]:
        best_node = None
        best_score = 0.0
        
        for node in candidates:
            score = 0.0
            
            # 1. Name Match (40%)
            if node.name and node.name.lower() in intent:
                score += 0.40
            elif node.name and intent in node.name.lower():
                score += 0.20
                
            # 2. Role Match (25%)
            if role_hint and node.role.lower() == role_hint.lower():
                score += 0.25
                
            # 3. Dialogue Context / Memory Proximity (10%)
            if context["window"] and node.parent_id == context["window"].id:
                score += 0.10
                
            # 4. Visibility (15%) - We strongly prefer visible nodes
            if node.visibility:
                score += 0.15
                
            if score > best_score:
                best_score = score
                best_node = node
                
        return best_node, best_score
