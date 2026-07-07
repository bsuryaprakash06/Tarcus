from PySide6.QtCore import QObject, Signal, Slot
from typing import Dict, Any
from src.utils.logger import get_logger
from src.events.pipeline_events import PipelineEventBus
from src.automation.interaction_manager import TargetRegisteredEvent, TargetStateChangedEvent
from src.execution.recovery_engine import RecoveredEvent
from src.models.overlay import OverlayTarget, OverlayState, ActionIndicatorType
from src.overlay.overlay_events import (
    OverlayCreated, OverlayDestroyed, OverlayShown, OverlayHidden, 
    OverlayStateChanged, OverlayActionTriggered
)
from src.overlay.overlay_window import OverlayWindow
from src.overlay.overlay_renderer import OverlayRenderer
from src.overlay.color_manager import ColorManager
from src.overlay.badge_manager import BadgeManager
from src.overlay.animation_manager import AnimationManager
from src.overlay.theme_manager import ThemeManager
from src.overlay.overlay_profile_manager import OverlayProfileManager

logger = get_logger("overlay.manager")

class OverlayEventBridge(QObject):
    """
    Bridges Python thread callbacks to the Qt Main Thread via Signals.
    """
    target_registered = Signal(object)
    target_state_changed = Signal(object)
    step_started = Signal(object)
    step_completed = Signal(object)
    step_failed = Signal(object)
    recovering = Signal(object)

class OverlayManager(QObject):
    """
    Central controller for the Visual Interaction Layer.
    Listens to Pipeline events on background threads, bridges them to Qt's main thread,
    and manages the lifecycle of OverlayWindows.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bridge = OverlayEventBridge()
        self.event_bus = PipelineEventBus()
        
        # Overlay Sub-Managers
        self.theme_manager = ThemeManager()
        self.color_manager = ColorManager()
        self.badge_manager = BadgeManager()
        self.profile_manager = OverlayProfileManager()
        self.animation_manager = AnimationManager()
        
        # State
        self.targets: Dict[str, OverlayTarget] = {}
        self.windows: Dict[str, OverlayWindow] = {}
        self.renderers: Dict[str, OverlayRenderer] = {}
        
        self._connect_signals()
        self._subscribe_to_bus()
        logger.info("OverlayManager initialized.")

    def _connect_signals(self):
        # Connect bridged signals to Qt slots (executed on main GUI thread)
        self.bridge.target_registered.connect(self.on_target_registered)
        self.bridge.target_state_changed.connect(self.on_target_state_changed)
        self.bridge.recovering.connect(self.on_recovering)
        # We can add more specific step event connections here later

    def _subscribe_to_bus(self):
        # Background threads publish these, we just emit the Qt signal
        self.event_bus.subscribe_event(TargetRegisteredEvent, lambda event: self.bridge.target_registered.emit(event))
        self.event_bus.subscribe_event(TargetStateChangedEvent, lambda event: self.bridge.target_state_changed.emit(event))
        self.event_bus.subscribe_event(RecoveredEvent, lambda event: self.bridge.recovering.emit(event))
        
    @Slot(object)
    def on_target_registered(self, event: TargetRegisteredEvent):
        target_id = event.target.id
        if target_id in self.targets:
            return
            
        logger.debug(f"Creating overlay for target: {target_id}")
        
        # 1. Generate visual data
        badge_text = self.badge_manager.assign_badge(target_id)
        
        # 2. Create tracking model
        target = OverlayTarget(
            interaction_target_id=target_id,
            friendly_name=event.target.properties.get("name", "Unknown"),
            badge_text=badge_text,
            current_state=OverlayState.VISIBLE
        )
        self.targets[target_id] = target
        
        # 3. Create GUI Window
        window = OverlayWindow(target_id)
        self.windows[target_id] = window
        
        # 4. Initialize Renderer
        renderer = OverlayRenderer(
            target=target,
            color_manager=self.color_manager,
            theme_manager=self.theme_manager,
            profile_manager=self.profile_manager,
            animation_manager=self.animation_manager
        )
        self.renderers[target_id] = renderer
        window.set_renderer(renderer)
        
        # Show window immediately (it will be positioned by OverlayTracker)
        window.show()
        
        # Emit OverlayCreated
        self.event_bus.publish_event(OverlayCreated(
            interaction_target_id=target_id,
            friendly_name=target.friendly_name,
            initial_state=OverlayState.VISIBLE
        ))
        
    @Slot(object)
    def on_target_state_changed(self, event: TargetStateChangedEvent):
        # In the future, parse target state bounds and visibility
        pass
        
    @Slot(object)
    def on_recovering(self, event: RecoveredEvent):
        target_id = event.target_id
        if target_id in self.targets:
            self.targets[target_id].current_state = OverlayState.RECOVERING
            if target_id in self.windows:
                self.windows[target_id].update() # Trigger repaint
            self.event_bus.publish_event(OverlayStateChanged(
                interaction_target_id=target_id,
                new_state=OverlayState.RECOVERING
            ))
