import logging
from .settings import LOGS_DIR

# Set up logging configuration
log_file = LOGS_DIR / "voice_assistant.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger with the given name."""
    return logging.getLogger(name)
