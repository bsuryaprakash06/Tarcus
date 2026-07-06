from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt
from src.ui.controller import UIController
from src.ui.widgets.conversation_widget import ConversationWidget
from src.ui.widgets.input_widget import InputWidget
from src.ui.widgets.microphone_widget import MicrophoneWidget
from src.ui.widgets.workflow_widget import WorkflowWidget
from src.ui.widgets.status_widget import StatusWidget
from src.ui.widgets.stop_button_widget import StopButtonWidget
from src.ui.widgets.clarification_dialog import ClarificationDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tarcus AI Copilot")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("background-color: #1e1e1e;")
        
        self.controller = UIController()
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left Panel (Conversation & Input)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.conversation_widget = ConversationWidget()
        left_layout.addWidget(self.conversation_widget, stretch=1)
        
        # Input row
        input_row = QHBoxLayout()
        self.input_widget = InputWidget()
        self.microphone_widget = MicrophoneWidget()
        self.stop_widget = StopButtonWidget()
        
        input_row.addWidget(self.input_widget, stretch=1)
        input_row.addWidget(self.microphone_widget)
        input_row.addWidget(self.stop_widget)
        left_layout.addLayout(input_row)
        
        # Right Panel (Workflow & Status)
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #252526; border-radius: 8px;")
        right_layout = QVBoxLayout(right_panel)
        
        self.workflow_widget = WorkflowWidget()
        right_layout.addWidget(self.workflow_widget, stretch=1)
        
        self.status_widget = StatusWidget()
        right_layout.addWidget(self.status_widget)
        
        # Add to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 300])
        
    def _connect_signals(self):
        # UI Actions -> Controller
        self.input_widget.text_submitted.connect(self.controller.submit_text)
        self.microphone_widget.voice_triggered.connect(self.controller.trigger_voice)
        self.stop_widget.stop_triggered.connect(self.controller.stop_speech)
        
        # Controller Signals -> UI Widgets
        self.controller.signals.message_received.connect(self.conversation_widget.add_message)
        self.controller.signals.status_updated.connect(self.status_widget.update_status)
        self.controller.signals.workflow_started.connect(self.workflow_widget.set_workflow_started)
        self.controller.signals.step_updated.connect(self.workflow_widget.update_step)
        self.controller.signals.clarification_requested.connect(self._show_clarification_dialog)
        self.controller.signals.confirmation_requested.connect(self._show_confirmation_dialog)
        
    def _show_confirmation_dialog(self, reason: str):
        from src.ui.widgets.confirmation_dialog import ConfirmationDialog
        dialog = ConfirmationDialog(self, reason)
        if dialog.exec():
            # User clicked Confirm
            self.controller.submit_text("Yes")
        else:
            # User clicked Cancel
            self.controller.submit_text("No")
        
    def _show_clarification_dialog(self, reason: str):
        dialog = ClarificationDialog(self, reason)
        if dialog.exec():
            # User clicked Submit
            user_input = dialog.get_input()
            if user_input:
                self.controller.submit_text(user_input)
        else:
            # User clicked Cancel or closed the dialog
            self.controller.submit_text("Cancel")
        
    def closeEvent(self, event):
        """Cleanly shutdown background threads when the window is closed."""
        self.controller.pipeline_worker.stop()
        super().closeEvent(event)
