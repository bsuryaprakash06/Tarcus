import json
from src.models.plan import ExecutionPlan
from src.utils.logger import get_logger
from src.utils.exceptions import PlanningError

logger = get_logger("brain.parser")

def parse_execution_plan(raw_response: str) -> ExecutionPlan:
    """
    Cleans, parses, and validates the raw LLM response against the ExecutionPlan schema.
    
    Args:
        raw_response: The raw string response from the LLM.
        
    Returns:
        ExecutionPlan: Validated Pydantic model.
        
    Raises:
        PlanningError: If parsing or validation fails.
    """
    clean_response = raw_response.strip()
    
    # Strip markdown code fences if LLM ignored instructions
    if clean_response.startswith("```"):
        lines = clean_response.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        clean_response = "\n".join(lines).strip()

    try:
        data = json.loads(clean_response)
        plan = ExecutionPlan.model_validate(data)
        return plan
    except json.JSONDecodeError as jde:
        logger.error(f"JSON decoding failed: {jde}. Raw content: {raw_response}")
        raise PlanningError(f"LLM did not return valid JSON: {jde}") from jde
    except Exception as e:
        logger.error(f"Pydantic validation failed: {e}. Parsed data: {clean_response}")
        raise PlanningError(f"LLM plan does not match schema: {e}") from e
