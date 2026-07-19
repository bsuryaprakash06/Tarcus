import uuid
import threading
import time
from src.models.wakeword import WakeState, ActivationSession
from src.wakeword.wakeword_events import WakeWordDetected, SessionExpired, StateChanged
from src.wakeword.activation_response_manager import ActivationResponseManager
from src.events.pipeline_events import PipelineEventBus
from src.utils.logger import get_logger

logger = get_logger("wakeword.activation_manager")

class ActivationManager:
    """
    Controls the assistant's lifecycle (PASSIVE -> WAKE_DETECTED -> ... -> PASSIVE).
    Enforces conversation timeouts and manages the active ActivationSession.
    """
    def __init__(self, response_manager: ActivationResponseManager):
        self.response_manager = response_manager
        self.event_bus = PipelineEventBus()
        self.state = WakeState.PASSIVE
        self.current_session: ActivationSession = None
        
        self._lock = threading.RLock()
        self._timer_thread = threading.Thread(target=self._timeout_loop, daemon=True)
        self._timer_thread.start()
        
        # Subscribe to WakeWordDetected events
        self.event_bus.subscribe_event(WakeWordDetected, self._on_wake_word_detected)

    def _set_state(self, new_state: WakeState):
        with self._lock:
            if self.state == new_state:
                return
            old_state = self.state
            self.state = new_state
            logger.info(f"ActivationManager State Transition: {old_state.value} -> {new_state.value}")
            self.event_bus.publish_event(StateChanged(old_state=old_state, new_state=new_state))

    def _on_wake_word_detected(self, event: WakeWordDetected):
        with self._lock:
            # If we are currently processing or responding, treat this as an interruption
            if self.state in [WakeState.PROCESSING, WakeState.RESPONDING]:
                logger.info(f"Wake word detected during {self.state.value}. Interrupting!")
                self._set_state(WakeState.INTERRUPTED)
                # We can choose to clear the current session or keep it. Let's start fresh.
                self.current_session = None
            
            # If we are already listening, just extend the session, no need to interrupt
            elif self.state == WakeState.LISTENING:
                logger.debug("Wake word detected while already listening. Extending session.")
                if self.current_session:
                    self.current_session.touch()
                return
                
            elif self.state not in [WakeState.PASSIVE, WakeState.FOLLOW_UP, WakeState.INTERRUPTED]:
                logger.debug(f"Ignored wake word while in state: {self.state.value}")
                return
                
            self._set_state(WakeState.WAKE_DETECTED)
            
            # Create a new session if we don't have one
            if not self.current_session:
                self.current_session = ActivationSession(
                    id=uuid.uuid4().hex[:8],
                    wake_phrase=event.phrase
                )
                logger.info(f"Started ActivationSession {self.current_session.id}")
            else:
                self.current_session.touch()
            
            self._set_state(WakeState.ACKNOWLEDGING)
            self.response_manager.acknowledge()
            
            # Immediately transition to listening so VAD/Recorder can take over
            self._set_state(WakeState.LISTENING)

    def mark_processing(self):
        with self._lock:
            if self.state == WakeState.LISTENING:
                self._set_state(WakeState.PROCESSING)
                
    def mark_responding(self):
        with self._lock:
            if self.state == WakeState.PROCESSING:
                self._set_state(WakeState.RESPONDING)

    def mark_follow_up(self):
        with self._lock:
            if self.state == WakeState.RESPONDING or self.state == WakeState.PROCESSING:
                self._set_state(WakeState.FOLLOW_UP)
                if self.current_session:
                    self.current_session.touch()

    def touch_session(self):
        with self._lock:
            if self.current_session:
                self.current_session.touch()

    def _timeout_loop(self):
        while True:
            time.sleep(1.0)
            with self._lock:
                if self.current_session and self.current_session.is_active:
                    if self.current_session.check_timeouts():
                        logger.info(f"ActivationSession {self.current_session.id} expired due to inactivity.")
                        self.event_bus.publish_event(SessionExpired(session_id=self.current_session.id))
                        self.current_session = None
                        self._set_state(WakeState.PASSIVE)
