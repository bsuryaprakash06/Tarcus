from typing import Dict, Any
from src.utils.logger import get_logger
from src.models.scheduler import ExecutionNode
from src.scheduler.handlers.base_handler import BaseHandler

logger = get_logger("scheduler.task_dispatcher")

class TaskDispatcher:
    """
    Decouples the worker threads from the specific services.
    Workers pass nodes here, and the dispatcher routes them to the correct Handler.
    """
    def __init__(self):
        self._handlers: Dict[str, BaseHandler] = {}
        
    def register_handler(self, handler_type: str, handler: BaseHandler):
        self._handlers[handler_type] = handler
        logger.info(f"Registered handler for type: {handler_type}")
        
    def dispatch(self, node: ExecutionNode) -> Any:
        handler = self._handlers.get(node.handler_type)
        if not handler:
            raise ValueError(f"No handler registered for handler_type '{node.handler_type}'")
            
        return handler.execute(node)
