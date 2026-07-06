from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None, reason="Are you sure you want to proceed?"):
        super().__init__(parent)
        self.setWindowTitle("Action Confirmation")
        self.setFixedSize(400, 140)
        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
                border: 1px solid #454545;
                border-radius: 8px;
            }
            QLabel {
                font-size: 14px;
                color: #cccccc;
                margin-bottom: 10px;
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
                background-color: #d13a3a;
            }
            QPushButton#cancelBtn:hover {
                background-color: #e54d4d;
            }
        """)
        
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.label = QLabel(reason)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.submit_btn = QPushButton("Confirm")
        self.submit_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.submit_btn)
        
        layout.addLayout(btn_layout)
