from typing import Optional
from src.interaction.interaction_manager import InteractionManager
from src.interaction.interaction_memory import InteractionMemory
from src.interaction.semantic_resolver import SemanticResolver
from src.interaction.interaction_planner import InteractionPlanner
from src.interaction.interaction_predictor import InteractionPredictor
from src.automation.action_executor import ActionExecutor
from src.utils.logger import get_logger
from src.models.interaction import InteractionWorkflow

logger = get_logger("interaction.coordinator")

class InteractionCoordinator:
    """
    The primary façade for the Execution Controller.
    Orchestrates: Memory -> Resolver -> Planner -> Executor -> Predictor.
    """
    def __init__(self, manager: InteractionManager, memory: InteractionMemory, resolver: SemanticResolver, planner: InteractionPlanner, executor: ActionExecutor, predictor: InteractionPredictor):
        self.manager = manager
        self.memory = memory
        self.resolver = resolver
        self.planner = planner
        self.executor = executor
        self.predictor = predictor

    def coordinate_interaction(self, goal: str, role_hint: str = "") -> bool:
        logger.info(f"Coordinating interaction for goal: '{goal}'")
        
        # 1. Resolve Target
        node = self.resolver.resolve(goal, role_hint)
        if not node:
            logger.error(f"Failed to resolve target for goal '{goal}'")
            return False
            
        # 2. Update Memory Scope
        self._update_memory_scope(node)
        
        # 3. Plan Workflow
        workflow = self.planner.plan_workflow(goal, node)
        
        # 4. Execute (In reality, ActionExecutor would run the workflow against Backend)
        success = self._execute_workflow(workflow)
        
        # 5. Predict Next
        if success:
            next_prediction = self.predictor.predict_next(workflow)
            if next_prediction:
                logger.debug(f"Predicted next interaction: {next_prediction}")
                
        return success

    def _update_memory_scope(self, node):
        # Simplistic memory update based on role
        if node.role.lower() in ["window", "pane"]:
            self.memory.set_active_window(node)
        elif node.role.lower() in ["application"]:
            self.memory.set_active_app(node)
        else:
            self.memory.set_active_control(node)

    def _execute_workflow(self, workflow: InteractionWorkflow) -> bool:
        # ActionExecutor handles the step-by-step execution.
        # For now, we simulate success since ActionExecutor needs a refactor.
        logger.info(f"Executing {len(workflow.steps)} steps for workflow '{workflow.goal}'")
        return True
