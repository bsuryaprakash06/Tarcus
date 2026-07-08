from typing import Optional, Dict
from src.models.interaction import InteractionNode, ApplicationSession, WindowSession, InteractionSession
from src.interaction.interaction_graph import InteractionGraph
from src.automation.driver import AutomationBackend
from src.utils.logger import get_logger
import uuid

logger = get_logger("interaction.manager")

class InteractionManager:
    """
    Manages hierarchical sessions (Application -> Window -> Interaction)
    and orchestrates incremental graph updates with the platform backends.
    """
    def __init__(self, graph: InteractionGraph, backend: AutomationBackend):
        self.graph = graph
        self.backend = backend
        self.active_apps: Dict[str, ApplicationSession] = {}

    def start_application_session(self, app_node_id: str) -> ApplicationSession:
        session_id = str(uuid.uuid4())
        session = ApplicationSession(session_id=session_id, app_node_id=app_node_id)
        self.active_apps[app_node_id] = session
        logger.info(f"Started ApplicationSession {session_id} for app {app_node_id}")
        return session

    def start_window_session(self, app_session: ApplicationSession, window_node_id: str) -> WindowSession:
        session_id = str(uuid.uuid4())
        session = WindowSession(session_id=session_id, window_node_id=window_node_id)
        app_session.active_window_sessions[window_node_id] = session
        logger.info(f"Started WindowSession {session_id} for window {window_node_id}")
        return session
        
    def start_interaction_session(self, window_session: WindowSession, node_id: str) -> InteractionSession:
        session_id = str(uuid.uuid4())
        session = InteractionSession(session_id=session_id, node_id=node_id)
        window_session.active_interaction_sessions[node_id] = session
        logger.info(f"Started InteractionSession {session_id} for node {node_id}")
        return session

    def refresh_branch(self, root_node_id: str):
        """
        Incrementally refreshes a branch of the InteractionGraph via the backend.
        """
        logger.debug(f"Requesting backend refresh for branch {root_node_id}")
        # The backend should return the updated root node and all its flattened descendants
        updated_root, descendants = self.backend.refresh(root_node_id)
        if updated_root:
            self.graph.update_branch(updated_root, descendants)
        else:
            logger.warning(f"Failed to refresh branch {root_node_id}")
