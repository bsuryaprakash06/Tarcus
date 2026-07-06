from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class ClarificationDialog(QDialog):
    def __init__(self, parent=None, reason="Please provide clarification:"):
        super().__init__(parent)
        self.setWindowTitle("Clarification Required")
        self.setFixedSize(400, 170)
        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
                border: 1px solid #454545;
                border-radius: 8px;
            }
            QLabel {
                font-size: 14px;
                color: #cccccc;
                margin-bottom: 5px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #094771;
            }
            QPushButton#cancelBtn {
                background-color: #3c3c3c;
            }
            QPushButton#cancelBtn:hover {
                background-color: #4c4c4c;
            }
        """)
        
        # Remove standard windows borders for a neat modern look
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        self.label = QLabel(reason)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your response...")
        layout.addWidget(self.input_field)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.submit_btn)
        
        layout.addLayout(btn_layout)
        
    def get_input(self) -> str:
        return self.input_field.text().strip()
