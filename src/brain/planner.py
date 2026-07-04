from src.brain.prompt_builder import PromptBuilder
from src.brain.parser import parse_execution_plan
from src.models.plan import ExecutionPlan
from src.tools.registry import ToolRegistry
from src.providers import BaseProvider, get_provider_from_settings
from src.utils.logger import get_logger
from src.utils.exceptions import PlanningError

logger = get_logger("brain.planner")

class Planner:
    """The planning engine coordinating system prompting, LLM query routing, parsing, and validation checks."""
    
    def __init__(self, provider: BaseProvider = None, tool_registry: ToolRegistry = None):
        self.registry = tool_registry or ToolRegistry()
        self.prompt_builder = PromptBuilder(self.registry)
        self.provider = provider or get_provider_from_settings()

    def plan(self, user_command: str) -> ExecutionPlan:
        """
        Queries the configured LLM provider, validates the plan against Pydantic
        and semantic registry constraints, and executes smart retries with error feedback.
        """
        system_prompt = self.prompt_builder.build_prompt()
        max_retries = 3
        last_error = None
        current_user_prompt = user_command
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"Generating plan via '{self.provider.provider_name}', attempt {attempt}/{max_retries}...")
            
            # Incorporate error feedback if retrying
            if attempt > 1 and last_error:
                current_user_prompt = (
                    f"{user_command}\n\n"
                    f"⚠️ CRITICAL: Your previous plan failed validation check:\n"
                    f"\"{str(last_error)}\"\n"
                    f"Please correct the issue and return ONLY a valid raw JSON plan matching the requested schema."
                )

            try:
                # Call provider (decoupled from prompting / network details)
                response = self.provider.generate(system_prompt, current_user_prompt, require_json=True)
                
                # Perform 3-stage validation (syntax, schema, semantics)
                execution_plan = parse_execution_plan(response.text, self.registry)
                
                # Detailed architectural performance logging
                logger.info("Plan generation and validation succeeded.")
                logger.info(f"  Provider: {response.provider_name.capitalize()}")
                logger.info(f"  Model: {response.model_name}")
                logger.info(f"  Latency: {response.latency * 1000:.0f} ms")
                logger.info(f"  Validation: Passed")
                logger.info(f"  Retry Count: {attempt - 1}")
                if response.usage:
                    logger.info(f"  Usage: {response.usage}")
                
                return execution_plan
                
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt} failed generation or validation: {e}. "
                    f"Provider: {self.provider.provider_name.capitalize()}, "
                    f"Model: {getattr(self.provider, 'model_name', 'unknown')}"
                )
                
        raise PlanningError(
            f"Failed to generate a valid execution plan after {max_retries} attempts. "
            f"Last error: {last_error}"
        )
