from typing import List
from src.models.target import TargetSession

class InteractionPlan:
    """A granular sequence of micro-operations necessary to complete an interaction."""
    def __init__(self, steps: List[str]):
        self.steps = steps

class InteractionPlanner:
    """
    Translates high-level interaction intent into a concrete sequence of micro-operations.
    """
    
    @staticmethod
    def plan_typing(session: TargetSession, text: str, clear_first: bool) -> InteractionPlan:
        steps = ["focus"]
        if clear_first:
            steps.append("clear")
        steps.append("insert")
        steps.append("verify")
        steps.append("update_session")
        return InteractionPlan(steps=steps)
        
    @staticmethod
    def plan_click(session: TargetSession, double: bool = False, right: bool = False) -> InteractionPlan:
        return InteractionPlan(steps=["focus", "click", "verify", "update_session"])
