from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame
from PySide6.QtCore import Qt
from src.models.input import MessageRole

class ConversationWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #1e1e1e; }")
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #1e1e1e;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
    def add_message(self, msg_dict: dict):
        role = msg_dict.get("role", MessageRole.USER.value)
        content = msg_dict.get("content", "")
        
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background-color: #2b2b2b; border-radius: 8px; margin: 5px; padding: 10px; }" 
            if role == MessageRole.USER.value 
            else "QFrame { background-color: #1e1e1e; border-radius: 8px; margin: 5px; padding: 10px; border: 1px solid #3a3a3a; }"
        )
        frame_layout = QVBoxLayout(frame)
        
        header = QLabel("You" if role == MessageRole.USER.value else "Tarcus")
        header.setStyleSheet("font-weight: bold; color: #888888; font-size: 12px;")
        
        text_label = QLabel(content)
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        text_label.setStyleSheet("color: white; font-size: 14px;")
        
        frame_layout.addWidget(header)
        frame_layout.addWidget(text_label)
        
        self.content_layout.addWidget(frame)
        
        # Auto-scroll to bottom
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
