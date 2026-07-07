from PySide6.QtCore import QObject, QTimer, Signal
from src.utils.settings import OVERLAY_REFRESH_RATE
from src.events.pipeline_events import PipelineEventBus
from src.overlay.overlay_events import OverlayBoundsUpdated
from src.utils.logger import get_logger

logger = get_logger("overlay.tracker")

class OverlayTracker(QObject):
    """
    Synchronizes overlay positions with physical window positions.
    Prefers OS event hooks if available via AutomationBackend, falls back to polling.
    """
    bounds_updated = Signal(str, int, int, int, int)
    
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.event_bus = PipelineEventBus()
        self.active_targets = set()
        
        # Try to use OS hooks
        self.hooks_active = self.backend.subscribe_to_window_events(self._on_window_event)
        
        # Fallback to polling if hooks aren't supported or failed
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_bounds)
        
        if not self.hooks_active:
            logger.info(f"OS Event hooks not available for backend {self.backend.backend_name}, falling back to polling.")
            self.poll_timer.start(OVERLAY_REFRESH_RATE)
            
    def start_tracking(self, target_id: str):
        self.active_targets.add(target_id)
        # Force initial sync
        self._sync_target(target_id)
        
    def stop_tracking(self, target_id: str):
        self.active_targets.discard(target_id)
        
    def _on_window_event(self, event_data: dict):
        """Callback for OS native hooks (e.g. from SetWinEventHook)."""
        target_id = event_data.get("target_id")
        if target_id in self.active_targets:
            self._sync_target(target_id)
            
    def _poll_bounds(self):
        """Fallback polling loop."""
        for target_id in list(self.active_targets):
            self._sync_target(target_id)
            
    def _sync_target(self, target_id: str):
        bounds = self.backend.get_bounds(target_id)
        if bounds:
            x, y, w, h = bounds
            # Emit Signal to update the Qt GUI thread window immediately
            self.bounds_updated.emit(target_id, x, y, w, h)
            # Also publish an event for history/debugging if needed
            self.event_bus.publish_event(OverlayBoundsUpdated(
                interaction_target_id=target_id,
                x=x, y=y, width=w, height=h
            ))
