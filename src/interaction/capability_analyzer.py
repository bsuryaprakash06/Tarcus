from typing import List, Tuple
from src.models.interaction import InteractionNode, InteractionCapability, InteractionConstraint
from src.utils.logger import get_logger

logger = get_logger("interaction.capability_analyzer")

class CapabilityAnalyzer:
    """
    Assesses InteractionNodes to discover what actions they support (Capabilities)
    and what conditions must be met to perform them (Constraints).
    """
    def analyze(self, node: InteractionNode) -> Tuple[List[InteractionCapability], List[InteractionConstraint]]:
        """
        In a real scenario, this interrogates the platform backend or uses heuristics based on role.
        """
        capabilities = list(node.capabilities)
        constraints = list(node.constraints)
        
        # Heuristics if backend didn't provide them
        role = node.role.lower()
        
        if not capabilities:
            if role in ["button", "menuitem", "listitem", "checkbox"]:
                capabilities.append(InteractionCapability.CLICK)
                capabilities.append(InteractionCapability.FOCUS)
            elif role in ["edit", "document", "textbox"]:
                capabilities.append(InteractionCapability.TEXT_INPUT)
                capabilities.append(InteractionCapability.CLICK)
                capabilities.append(InteractionCapability.FOCUS)
                capabilities.append(InteractionCapability.READ)
            elif role in ["scrollbar", "pane", "window"]:
                capabilities.append(InteractionCapability.SCROLL)
                
        if not constraints:
            if role in ["button", "menuitem", "checkbox"]:
                constraints.append(InteractionConstraint.ENABLED)
                constraints.append(InteractionConstraint.VISIBLE)
            elif role in ["edit", "document"]:
                constraints.append(InteractionConstraint.ENABLED)
                constraints.append(InteractionConstraint.VISIBLE)
                constraints.append(InteractionConstraint.EDITABLE)
                
        logger.debug(f"Analyzed node {node.id} ({node.name}). Capabilities: {capabilities}, Constraints: {constraints}")
        return capabilities, constraints
