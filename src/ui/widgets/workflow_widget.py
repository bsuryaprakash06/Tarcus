from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class WorkflowWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel("Active Workflow")
        header.setStyleSheet("font-weight: bold; color: white; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(header)
        
        self.steps_layout = QVBoxLayout()
        layout.addLayout(self.steps_layout)
        layout.addStretch()
        
    def set_workflow_started(self, workflow_id: str):
        # Clear existing steps
        for i in reversed(range(self.steps_layout.count())):
            widget = self.steps_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
    def update_step(self, step_data: dict):
        tool = step_data.get("tool", "Unknown Tool")
        status = step_data.get("status", "RUNNING")
        
        color = "white"
        if status == "SUCCESS": color = "#4CAF50" # Green
        elif status == "FAILED": color = "#F44336" # Red
        elif status == "RETRY": color = "#FF9800" # Orange
        elif status == "RUNNING": color = "#2196F3" # Blue
        
        lbl = QLabel(f"• {tool} - {status}")
        lbl.setStyleSheet(f"color: {color}; font-size: 13px; margin: 2px;")
        self.steps_layout.addWidget(lbl)
