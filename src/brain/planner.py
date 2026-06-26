import requests
from src.brain.prompt_builder import PromptBuilder
from src.brain.parser import parse_execution_plan
from src.models.plan import ExecutionPlan
from src.tools.registry import ToolRegistry
from src.utils.settings import OLLAMA_API_URL, OLLAMA_MODEL
from src.utils.logger import get_logger
from src.utils.exceptions import PlanningError

logger = get_logger("brain.planner")

class Planner:
    """The planning engine representing the LLM brain of the assistant."""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.registry = tool_registry or ToolRegistry()
        self.prompt_builder = PromptBuilder(self.registry)

    def plan(self, user_command: str) -> ExecutionPlan:
        """
        Queries the Qwen3 model on local Ollama, parses, and validates the execution plan.
        Retries up to 3 times if plan validation fails.
        """
        system_prompt = self.prompt_builder.build_prompt()
        
        max_retries = 3
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"Generating plan, attempt {attempt}/{max_retries}...")
            try:
                payload = {
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_command}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.0,  # Deterministic execution plan
                        "thinking": False
                    },
                    "think": False  # Disable reasoning thinking block output
                }
                
                response = requests.post(OLLAMA_API_URL, json=payload, timeout=90)
                if response.status_code != 200:
                    raise PlanningError(f"Ollama server returned HTTP {response.status_code}: {response.text}")
                    
                result_json = response.json()
                raw_response = result_json.get("message", {}).get("content", "")
                
                # Clean and validate the plan against Pydantic schema
                execution_plan = parse_execution_plan(raw_response)
                logger.info(f"Plan validation succeeded on attempt {attempt}.")
                return execution_plan
                
            except PlanningError as pe:
                logger.warning(f"Attempt {attempt} failed plan validation: {pe}")
                last_error = pe
            except Exception as e:
                logger.warning(f"Attempt {attempt} unexpected error: {e}")
                last_error = PlanningError(str(e))
                
        raise PlanningError(f"Failed to generate a valid execution plan after {max_retries} attempts. Last error: {last_error}")
