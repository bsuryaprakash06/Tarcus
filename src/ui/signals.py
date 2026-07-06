from PySide6.QtCore import QObject, Signal

class UISignals(QObject):
    """Bridge between background PipelineEventBus callbacks and the Qt GUI main thread."""
    # Pipeline general state
    status_updated = Signal(str)            # e.g., "LISTENING", "TRANSCRIBING"
    error_occurred = Signal(str)
    
    # Conversation updates
    message_received = Signal(dict)         # dict matching ConversationMessage
    clarification_requested = Signal(str)   # reason string
    confirmation_requested = Signal(str)    # reason string
    
    # Workflow updates
    workflow_started = Signal(str)          # workflow_id
    workflow_completed = Signal(str)
    workflow_failed = Signal(str)
    step_updated = Signal(dict)             # step status updates
