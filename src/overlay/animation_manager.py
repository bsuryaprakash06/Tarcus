from PySide6.QtCore import QObject, QPropertyAnimation, QVariantAnimation, QEasingCurve, Slot
from src.models.overlay import OverlayState, ActionIndicatorType

class AnimationManager(QObject):
    """
    Manages state-based and action-based animations for overlays.
    (e.g., pulsing borders for EXECUTING, expanding ripples for CLICK).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Store active animations so they don't get garbage collected
        self.active_animations = {}

    def animate_state_transition(self, target, old_state: OverlayState, new_state: OverlayState, update_callback):
        """
        Triggers a visual animation (e.g. pulse) when a target changes state.
        update_callback is a function to force a repaint of the window.
        """
        # For simplicity, we just change the target's current_state, and rely on 
        # the renderer's paintEvent to pick up the new state for colors.
        # But we could also animate `style.glow_radius` using a QVariantAnimation here.
        target.current_state = new_state
        update_callback()
        
    def trigger_action_animation(self, target, action: ActionIndicatorType, update_callback):
        """
        Triggers a temporary action indicator (e.g. Click Ripple).
        """
        pass
