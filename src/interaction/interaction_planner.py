from typing import List
from src.models.interaction import InteractionNode, InteractionWorkflow, InteractionWorkflowStep, InteractionCapability, InteractionConstraint
from src.interaction.capability_analyzer import CapabilityAnalyzer
from src.utils.logger import get_logger

logger = get_logger("interaction.planner")

class InteractionPlanner:
    """
    Transforms a high-level goal and an InteractionNode into a deterministic InteractionWorkflow.
    Example: "Click Save" -> [Verify Visible, Focus, Click, Verify Window Closed]
    """
    def __init__(self):
        self.analyzer = CapabilityAnalyzer()

    def plan_workflow(self, goal: str, node: InteractionNode) -> InteractionWorkflow:
        logger.info(f"Planning workflow for goal '{goal}' on node {node.id}")
        
        capabilities, constraints = self.analyzer.analyze(node)
        
        workflow = InteractionWorkflow(
            goal=goal,
            target_node_id=node.id,
            required_capabilities=capabilities,
            required_constraints=constraints
        )
        
        goal_lower = goal.lower()
        
        # 1. Pre-execution Verification Steps
        if InteractionConstraint.VISIBLE in constraints:
            workflow.steps.append(InteractionWorkflowStep(action="verify", arguments={"rule": "is_visible"}))
        if InteractionConstraint.ENABLED in constraints:
            workflow.steps.append(InteractionWorkflowStep(action="verify", arguments={"rule": "is_enabled"}))
            
        # 2. Execution Preparation
        if InteractionCapability.FOCUS in capabilities:
            workflow.steps.append(InteractionWorkflowStep(action="focus"))
            
        # 3. Execution Action
        if "type" in goal_lower and InteractionCapability.TEXT_INPUT in capabilities:
            # Extract text (mock extraction for now)
            text_to_type = goal.replace("type", "").replace("Type", "").strip()
            workflow.steps.append(InteractionWorkflowStep(action="type_text", arguments={"text": text_to_type}))
            
        elif "click" in goal_lower and InteractionCapability.CLICK in capabilities:
            workflow.steps.append(InteractionWorkflowStep(action="click"))
            
        elif "scroll" in goal_lower and InteractionCapability.SCROLL in capabilities:
            workflow.steps.append(InteractionWorkflowStep(action="scroll", arguments={"direction": "down"}))
            
        else:
            # Fallback action
            logger.warning(f"No specific capability matched for goal '{goal}', defaulting to custom execute.")
            workflow.steps.append(InteractionWorkflowStep(action="execute_custom"))
            
        # 4. Post-execution Verification (Deferred to Verification Engine during execution)
        
        logger.debug(f"Planned workflow has {len(workflow.steps)} steps.")
        return workflow
