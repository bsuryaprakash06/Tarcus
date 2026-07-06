from typing import Dict, Any
import uuid
from PySide6.QtCore import QObject
from src.ui.signals import UISignals
from src.events.pipeline_events import PipelineEventBus, PipelineEventType
from src.services.pipeline_worker import PipelineWorker
from src.models.input import InputSource, InputRequest, MessageRole
from src.services.session_manager import SessionManager

class UIController(QObject):
    """
    Acts as the View-Model bridge. Subscribes to the backend PipelineEventBus and 
    emits Qt Signals to safely update the UI thread.
    """
    def __init__(self):
        super().__init__()
        self.signals = UISignals()
        self.event_bus = PipelineEventBus()
        self.session_manager = SessionManager()
        
        # Start the backend pipeline worker thread. 
        # It's a standard python daemon thread, decoupled from Qt.
        self.pipeline_worker = PipelineWorker()
        self.pipeline_worker.start()
        
        self._subscribe_events()
        
    def _subscribe_events(self):
        # Bind pipeline events to Qt signals safely
        self.event_bus.subscribe(PipelineEventType.INPUT_RECEIVED, self._on_input_received)
        self.event_bus.subscribe(PipelineEventType.SPEECH_FINISHED, self._on_speech_finished)
        self.event_bus.subscribe(PipelineEventType.NORMALIZATION_FINISHED, lambda p: self.signals.status_updated.emit("NORMALIZING"))
        self.event_bus.subscribe(PipelineEventType.CONTEXT_RESOLVED, lambda p: self.signals.status_updated.emit("RESOLVING_CONTEXT"))
        self.event_bus.subscribe(PipelineEventType.INTENT_CLASSIFIED, lambda p: self.signals.status_updated.emit("ROUTING"))
        self.event_bus.subscribe(PipelineEventType.CLARIFICATION_REQUESTED, lambda p: self.signals.clarification_requested.emit(p.get("reason", "Please clarify.")))
        self.event_bus.subscribe(PipelineEventType.CONFIRMATION_REQUESTED, lambda p: self.signals.confirmation_requested.emit(p.get("reason", "Are you sure?")))
        self.event_bus.subscribe(PipelineEventType.PLANNER_STARTED, lambda p: self.signals.status_updated.emit("PLANNING"))
        self.event_bus.subscribe(PipelineEventType.RESPONSE_GENERATED, self._on_response_generated)
        self.event_bus.subscribe(PipelineEventType.TTS_STARTED, lambda p: self.signals.status_updated.emit("SPEAKING"))
        self.event_bus.subscribe(PipelineEventType.COMPLETED, lambda p: self.signals.status_updated.emit("IDLE"))
        self.event_bus.subscribe(PipelineEventType.ERROR, self._on_error)
        
        self.event_bus.subscribe(PipelineEventType.WORKFLOW_STARTED, lambda p: self.signals.workflow_started.emit(p.get("workflow_id", "")))
        self.event_bus.subscribe(PipelineEventType.WORKFLOW_COMPLETED, lambda p: self.signals.workflow_completed.emit(p.get("workflow_id", "")))
        self.event_bus.subscribe(PipelineEventType.WORKFLOW_FAILED, lambda p: self.signals.workflow_failed.emit(p.get("workflow_id", "")))
        
        self.event_bus.subscribe(PipelineEventType.STEP_STARTED, self._on_step_updated("RUNNING"))
        self.event_bus.subscribe(PipelineEventType.STEP_COMPLETED, self._on_step_updated("SUCCESS"))
        self.event_bus.subscribe(PipelineEventType.STEP_FAILED, self._on_step_updated("FAILED"))
        self.event_bus.subscribe(PipelineEventType.STEP_RETRY, self._on_step_updated("RETRY"))

    def submit_text(self, text: str):
        self.signals.status_updated.emit("PROCESSING")
        req = InputRequest(request_id=str(uuid.uuid4()), source=InputSource.TEXT, text=text)
        
        # Instantly echo user text to UI
        msg = {"id": req.request_id, "role": MessageRole.USER.value, "content": text}
        self.signals.message_received.emit(msg)
        
        self.session_manager.enqueue(req)
        
    def trigger_voice(self):
        self.signals.status_updated.emit("LISTENING")
        req = InputRequest(request_id=str(uuid.uuid4()), source=InputSource.VOICE, text="")
        self.session_manager.enqueue(req)

    def stop_speech(self):
        """Immediately halts TTS playback and clears the audio queue."""
        self.pipeline_worker.tts_service.stop()

    def _on_input_received(self, payload: Dict[str, Any]):
        if payload.get("source") != InputSource.VOICE.value:
            self.signals.status_updated.emit("PROCESSING")
        else:
            self.signals.status_updated.emit("TRANSCRIBING")

    def _on_speech_finished(self, payload: Dict[str, Any]):
        self.signals.status_updated.emit("PROCESSING")
        text = payload.get("text", "")
        if text.strip():
            msg = {"id": str(uuid.uuid4()), "role": MessageRole.USER.value, "content": text}
            self.signals.message_received.emit(msg)

    def _on_response_generated(self, payload: Dict[str, Any]):
        text = payload.get("text", "")
        msg = {"id": str(uuid.uuid4()), "role": MessageRole.ASSISTANT.value, "content": text}
        self.signals.message_received.emit(msg)
        
    def _on_error(self, payload: Dict[str, Any]):
        self.signals.status_updated.emit("ERROR")
        self.signals.error_occurred.emit(payload.get("error", "Unknown Error"))
        
    def _on_step_updated(self, status: str):
        def handler(payload: Dict[str, Any]):
            payload["status"] = status
            self.signals.step_updated.emit(payload)
        return handler
