from typing import Optional
from src.models.interaction import InteractionWorkflow, InteractionWorkflowStep
from src.utils.logger import get_logger

logger = get_logger("interaction.predictor")

class InteractionPredictor:
    """
    Analyzes workflows to predict and prefetch the likely next interaction.
    Helps reduce latency by anticipating user actions.
    """
    
    def predict_next(self, current_workflow: InteractionWorkflow) -> Optional[str]:
        """
        Returns a string representing the predicted next goal, or None.
        """
        if not current_workflow.steps:
            return None
            
        last_action = current_workflow.steps[-1].action
        goal_lower = current_workflow.goal.lower()
        
        logger.debug(f"Predicting next action after '{last_action}' for goal '{current_workflow.goal}'")
        
        if last_action == "type_text" or "type" in goal_lower:
            return "Continue Typing"
            
        if "file" in goal_lower and last_action == "click":
            # Clicking 'File' usually leads to opening a menu
            return "Open Menu"
            
        if last_action == "scroll":
            return "Continue Scrolling"
            
        return "Verify State"
