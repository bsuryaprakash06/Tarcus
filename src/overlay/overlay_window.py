from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPaintEvent
from typing import Optional

class OverlayWindow(QWidget):
    """
    A transparent, click-through, frameless window that sits on top of an application target.
    Delegates drawing to an OverlayRenderer.
    """
    def __init__(self, target_id: str, parent=None):
        super().__init__(parent)
        self.target_id = target_id
        self.renderer = None  # Injected later
        
        # Make the window frameless, tool (no taskbar icon), and always on top
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowTransparentForInput  # Critical: Click-through
        )
        # Transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Don't steal focus
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
    def set_renderer(self, renderer):
        self.renderer = renderer
        
    def update_bounds(self, x: int, y: int, width: int, height: int):
        self.setGeometry(x, y, width, height)
        
    def paintEvent(self, event: QPaintEvent):
        if self.renderer:
            self.renderer.render(self, event)
