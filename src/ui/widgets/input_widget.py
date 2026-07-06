from PySide6.QtWidgets import QWidget, QHBoxLayout, QTextEdit, QPushButton
from PySide6.QtCore import Qt, Signal

class InputTextEdit(QTextEdit):
    enter_pressed = Signal()
    
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Type a command... (Shift+Enter for newline)")
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QTextEdit { 
                background-color: #2b2b2b; 
                color: white; 
                border: 1px solid #444; 
                border-radius: 5px; 
                padding: 5px; 
                font-size: 14px;
            }
        """)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
            self.enter_pressed.emit()
            event.accept()
        else:
            super().keyPressEvent(event)

class InputWidget(QWidget):
    text_submitted = Signal(str)
    
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_box = InputTextEdit()
        self.text_box.enter_pressed.connect(self._submit)
        
        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(80, 60)
        self.send_button.setStyleSheet("""
            QPushButton { 
                background-color: #007acc; 
                color: white; 
                border-radius: 5px; 
                font-weight: bold; 
                font-size: 14px;
            }
            QPushButton:hover { background-color: #0098ff; }
        """)
        self.send_button.clicked.connect(self._submit)
        
        layout.addWidget(self.text_box)
        layout.addWidget(self.send_button)
        
    def _submit(self):
        text = self.text_box.toPlainText().strip()
        if text:
            self.text_submitted.emit(text)
            self.text_box.clear()
