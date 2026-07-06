from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal

class StopButtonWidget(QPushButton):
    stop_triggered = Signal()
    
    def __init__(self):
        super().__init__("Stop")
        self.setFixedSize(60, 60)
        self.setStyleSheet("""
            QPushButton { 
                background-color: #2b2b2b; 
                color: #ff5555; 
                border-radius: 30px; 
                font-size: 14px;
                border: 2px solid #444;
                font-weight: bold;
            }
            QPushButton:hover { border: 2px solid #ff5555; background-color: #3b2b2b; }
        """)
        self.clicked.connect(self.stop_triggered.emit)
