from PySide6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt, QRectF
from src.models.overlay import OverlayTarget, OverlayState
from src.utils.settings import ENABLE_OVERLAY_DEBUG

class OverlayRenderer:
    """
    Renders an OverlayTarget using a layered painting approach.
    Layers: Background -> Border -> Glow -> Badge -> Action -> Debug
    """
    def __init__(self, target, color_manager, theme_manager, profile_manager, animation_manager):
        self.target: OverlayTarget = target
        self.color_manager = color_manager
        self.theme_manager = theme_manager
        self.profile_manager = profile_manager
        self.animation_manager = animation_manager
        
    def render(self, widget, event):
        """Called by the widget's paintEvent."""
        painter = QPainter(widget)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = widget.rect()
        # Inset by 20px padding (from overlay_tracker) to get actual target bounds
        padding = 20
        target_rect = QRectF(rect).adjusted(padding, padding, -padding, -padding)
        
        profile = self.profile_manager.resolve_profile({})
        base_color = self.color_manager.resolve_color(self.target.interaction_target_id)
        
        # Override color based on state
        state_color = self._get_state_color(base_color, self.target.current_state)
        
        # 1. Background Layer (Usually transparent, unless thinking/locked)
        self._draw_background(painter, target_rect, state_color)
        
        # 2. Glow Layer
        self._draw_glow(painter, target_rect, state_color)
        
        # 3. Border Layer
        self._draw_border(painter, target_rect, state_color, profile)
        
        # 4. Badge Layer
        if profile.show_badge and self.target.badge_text:
            self._draw_badge(painter, target_rect, state_color)
            
        # 5. Action Layer
        self._draw_actions(painter, target_rect)
        
        # 6. Debug Layer
        if ENABLE_OVERLAY_DEBUG:
            self._draw_debug(painter, target_rect)
            
        painter.end()

    def _get_state_color(self, base_color: QColor, state: OverlayState) -> QColor:
        if state == OverlayState.SUCCESS:
            return QColor(0, 255, 0)
        elif state == OverlayState.ERROR:
            return QColor(255, 0, 0)
        elif state == OverlayState.RECOVERING:
            return QColor(255, 165, 0) # Orange
        elif state == OverlayState.VERIFYING:
            return QColor(255, 255, 255) # White
        elif state == OverlayState.DISCOVERING:
            return QColor(0, 255, 255) # Cyan
        elif state == OverlayState.LOCKED:
            return QColor(128, 128, 128) # Gray
        return base_color

    def _draw_background(self, painter, rect, color):
        # By default completely transparent
        pass

    def _draw_glow(self, painter, rect, color):
        # A simple multi-pass soft glow
        glow_radius = self.target.style.glow_radius
        if glow_radius <= 0:
            return
            
        for i in range(1, 4):
            alpha = max(10, 60 - (i * 15))
            c = QColor(color)
            c.setAlpha(alpha)
            pen = QPen(c)
            pen.setWidth(self.target.style.border_width + (i * 2))
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            
            path = QPainterPath()
            # Expand outwards from the target_rect to draw the outer glow
            expand = i * 2
            path.addRoundedRect(QRectF(rect).adjusted(-expand, -expand, expand, expand), self.target.style.border_radius, self.target.style.border_radius)
            painter.drawPath(path)

    def _draw_border(self, painter, rect, color, profile):
        pen = QPen(color)
        pen.setWidth(self.target.style.border_width)
        
        if profile.border_style == "dashed":
            pen.setStyle(Qt.DashLine)
            
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        path = QPainterPath()
        # Inset slightly so the border draws fully inside the widget bounds
        inset = self.target.style.border_width / 2.0
        r = QRectF(rect).adjusted(inset, inset, -inset, -inset)
        path.addRoundedRect(r, self.target.style.border_radius, self.target.style.border_radius)
        
        painter.drawPath(path)

    def _draw_badge(self, painter, rect, color):
        badge_rect = QRectF(rect.width() - 40, 0, 40, 24)
        
        # Badge background
        c = QColor(color)
        c.setAlpha(200)
        painter.setBrush(QBrush(c))
        painter.setPen(Qt.NoPen)
        
        path = QPainterPath()
        path.addRoundedRect(badge_rect, 4, 4)
        painter.drawPath(path)
        
        # Badge Text
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(badge_rect, Qt.AlignCenter, self.target.badge_text)

    def _draw_actions(self, painter, rect):
        pass

    def _draw_debug(self, painter, rect):
        painter.setPen(QPen(QColor(255, 0, 0)))
        font = QFont("Consolas", 8)
        painter.setFont(font)
        painter.drawText(10, 15, f"ID: {self.target.interaction_target_id}")
        painter.drawText(10, 30, f"State: {self.target.current_state.value}")
