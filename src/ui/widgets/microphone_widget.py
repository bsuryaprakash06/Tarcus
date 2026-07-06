from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal

class MicrophoneWidget(QPushButton):
    voice_triggered = Signal()
    
    def __init__(self):
        super().__init__("Mic")
        self.setFixedSize(60, 60)
        self.setStyleSheet("""
            QPushButton { 
                background-color: #2b2b2b; 
                color: white; 
                border-radius: 30px; 
                font-size: 16px;
                border: 2px solid #444;
            }
            QPushButton:hover { border: 2px solid #007acc; }
        """)
        self.clicked.connect(self.voice_triggered.emit)
