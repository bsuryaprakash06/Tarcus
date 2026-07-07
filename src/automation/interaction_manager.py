import threading
from typing import Dict, List, Optional
from src.models.target import InteractionTarget, TargetSession, TargetState
from src.models.interaction_graph import InteractionGraph
from src.automation.driver import AutomationBackend
from src.events.pipeline_events import PipelineEventBus
from src.utils.logger import get_logger

logger = get_logger("automation.interaction_manager")

from pydantic import BaseModel

class TargetRegisteredEvent(BaseModel):
    target_id: str
        
class TargetStateChangedEvent(BaseModel):
    target_id: str
    old_state: TargetState
    new_state: TargetState

class InteractionManager:
    """
    Actively manages targets, sessions, discovery, synchronization, and event publishing.
    Replaces the passive TargetRegistry.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InteractionManager, cls).__new__(cls)
            cls._instance._lock = threading.Lock()
            cls._instance._sessions: Dict[str, TargetSession] = {}
            cls._instance._graph = InteractionGraph(root_id="system_root")
            cls._instance.event_bus = PipelineEventBus()
        return cls._instance

    def register_target(self, target: InteractionTarget) -> TargetSession:
        """Registers a target and creates a stateful session for it."""
        with self._lock:
            if target.id in self._sessions:
                # Update existing session's underlying target details if needed
                # (Since InteractionTarget is immutable, we replace it in the session)
                session = self._sessions[target.id]
                session.target = target
                return session

            session = TargetSession(target=target, state=TargetState.ACTIVE)
            self._sessions[target.id] = session
            self._graph.add_node(target)
            
            logger.info(f"Registered new InteractionTarget: {target.id} ({target.friendly_name})")
            self.event_bus.publish_event(TargetRegisteredEvent(target_id=target.id))
            return session

    def get_session(self, target_id: str) -> Optional[TargetSession]:
        with self._lock:
            return self._sessions.get(target_id)
            
    def update_state(self, target_id: str, new_state: TargetState):
        with self._lock:
            session = self._sessions.get(target_id)
            if session and session.state != new_state:
                old_state = session.state
                session.state = new_state
                self.event_bus.publish_event(TargetStateChangedEvent(target_id, old_state, new_state))

    def list_sessions(self, active_only: bool = True) -> List[TargetSession]:
        with self._lock:
            if active_only:
                return [s for s in self._sessions.values() if s.state == TargetState.ACTIVE]
            return list(self._sessions.values())
            
    def discover_and_sync(self, backend: AutomationBackend):
        """Actively triggers the backend to discover targets and syncs them to the registry."""
        graph = backend.discover()
        
        # Merge graph nodes into the manager
        with self._lock:
            for node_id, target in graph.nodes.items():
                # Register all found targets
                if target.id not in self._sessions:
                    session = TargetSession(target=target, state=TargetState.ACTIVE)
                    self._sessions[target.id] = session
                    self.event_bus.publish_event(TargetRegisteredEvent(target_id=target.id))
                
                # Merge edges
                self._graph.add_node(target, parent_id=None) # We can refine parent_id merging later
                
            # Copy edges from the backend's graph
            for parent, children in graph.edges.items():
                if parent not in self._graph.edges:
                    self._graph.edges[parent] = []
                for child in children:
                    if child not in self._graph.edges[parent]:
                        self._graph.edges[parent].append(child)
                        
        logger.info(f"InteractionManager sync complete via {backend.backend_name}")
