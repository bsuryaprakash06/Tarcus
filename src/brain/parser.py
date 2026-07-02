import json
from src.models.plan import ExecutionPlan
from src.utils.logger import get_logger
from src.utils.exceptions import PlanningError

logger = get_logger("brain.parser")

from src.tools.registry import ToolRegistry

def validate_plan_semantics(plan: ExecutionPlan, registry: ToolRegistry) -> None:
    """
    Validates the plan semantically against the ToolRegistry (Stage 3):
    1. Tool exists in the registry.
    2. No unknown arguments are provided.
    3. Required arguments (default behavior unless marked optional) are present.
    4. Strings are not empty or whitespace-only.
    5. Value types match the schema (string, integer, number, boolean).
    6. Value matches enum choices if specified in the schema.
    """
    for item in plan.plan:
        tool = registry.get_tool(item.tool)
        if not tool:
            raise PlanningError(f"Stage 3 Validation Error: Tool '{item.tool}' is not registered.")

        schema = tool.arguments_schema
        provided_args = item.arguments

        # Check for unknown arguments
        for arg_name in provided_args:
            if arg_name not in schema:
                raise PlanningError(
                    f"Stage 3 Validation Error: Tool '{item.tool}' does not accept argument '{arg_name}'. "
                    f"Expected arguments: {list(schema.keys())}"
                )

        # Validate arguments according to tool schema
        for arg_name, arg_info in schema.items():
            expected_type = arg_info.get("type")
            is_optional = arg_info.get("optional", False) or "default" in arg_info

            # Check if required argument is missing
            if arg_name not in provided_args:
                if not is_optional:
                    raise PlanningError(
                        f"Stage 3 Validation Error: Tool '{item.tool}' requires argument '{arg_name}' "
                        f"which is missing in the plan."
                    )
                continue

            val = provided_args[arg_name]

            # Enforce non-empty string for required strings
            if expected_type == "string" and isinstance(val, str) and not val.strip():
                raise PlanningError(
                    f"Stage 3 Validation Error: Tool '{item.tool}' argument '{arg_name}' "
                    f"cannot be empty or whitespace-only."
                )

            # Type validation
            if expected_type == "string" and not isinstance(val, str):
                raise PlanningError(
                    f"Stage 3 Validation Error: Tool '{item.tool}' argument '{arg_name}' "
                    f"must be a string. Got type {type(val).__name__}."
                )
            elif expected_type == "integer" and not isinstance(val, int):
                raise PlanningError(
                    f"Stage 3 Validation Error: Tool '{item.tool}' argument '{arg_name}' "
                    f"must be an integer. Got type {type(val).__name__}."
                )
            elif expected_type == "number" and not isinstance(val, (int, float)):
                raise PlanningError(
                    f"Stage 3 Validation Error: Tool '{item.tool}' argument '{arg_name}' "
                    f"must be a number. Got type {type(val).__name__}."
                )
            elif expected_type == "boolean" and not isinstance(val, bool):
                raise PlanningError(
                    f"Stage 3 Validation Error: Tool '{item.tool}' argument '{arg_name}' "
                    f"must be a boolean. Got type {type(val).__name__}."
                )

            # Enum validation
            if "enum" in arg_info:
                allowed = arg_info["enum"]
                if val not in allowed:
                    raise PlanningError(
                        f"Stage 3 Validation Error: Tool '{item.tool}' argument '{arg_name}' "
                        f"value '{val}' is not valid. Allowed values: {allowed}"
                    )

def parse_execution_plan(raw_response: str, registry: ToolRegistry = None) -> ExecutionPlan:
    """
    Cleans, parses, and validates the raw LLM response against the ExecutionPlan schema.
    If registry is supplied, executes Stage 3 semantic validation.
    
    Args:
        raw_response: The raw string response from the LLM.
        registry: Optional ToolRegistry instance to run semantic validations.
        
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
        
        # Execute Stage 3 Semantic Validation if registry is provided
        if registry is not None:
            validate_plan_semantics(plan, registry)
            
        return plan
    except json.JSONDecodeError as jde:
        logger.error(f"JSON decoding failed: {jde}. Raw content: {raw_response}")
        raise PlanningError(f"LLM did not return valid JSON: {jde}") from jde
    except PlanningError:
        # Re-raise PlanningError from validate_plan_semantics directly
        raise
    except Exception as e:
        logger.error(f"Pydantic validation failed: {e}. Parsed data: {clean_response}")
        raise PlanningError(f"LLM plan does not match schema: {e}") from e
