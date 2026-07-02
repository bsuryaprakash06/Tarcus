import logging
import json
from .settings import LOGS_DIR, DEBUG_MODE

# Set up logging configuration
log_file = LOGS_DIR / "voice_assistant.log"

logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger with the given name."""
    return logging.getLogger(name)

def log_structured_tool_result(logger_instance: logging.Logger, execution_id: str, tool_name: str, arguments: dict, status: str, duration: float, message: str) -> None:
    """Logs a clean, vertical, structured tool execution block."""
    arg_str = ", ".join([f"{k} = {v}" for k, v in arguments.items()])
    if not arg_str:
        arg_str = "None"
        
    block = [
        "",
        "=" * 32,
        f"Execution #{execution_id}",
        "",
        "Tool",
        f"  {tool_name}",
        "",
        "Arguments",
        f"  {arg_str}",
        "",
        "Status",
        f"  {status}",
        "",
        "Duration",
        f"  {int(duration * 1000)} ms",
        "",
        "Message",
        f"  {message}",
        "=" * 32,
        ""
    ]
    
    logger_instance.info("\n".join(block))

def dump_debug_json(logger_instance: logging.Logger, label: str, data: dict) -> None:
    """Only dumps large JSON blocks if DEBUG_MODE is True."""
    if DEBUG_MODE:
        logger_instance.debug(f"{label}:\n{json.dumps(data, indent=2)}")
