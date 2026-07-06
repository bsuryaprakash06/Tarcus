from PySide6.QtWidgets import QLabel

class StatusWidget(QLabel):
    def __init__(self):
        super().__init__("Status: IDLE")
        self.setStyleSheet("color: #aaaaaa; font-weight: bold; font-size: 12px; padding: 5px;")
        
    def update_status(self, status: str):
        self.setText(f"Status: {status}")
