import sys
import os
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.startup import run_startup_checks
from src.utils.logger import get_logger
from src.utils.settings import ENABLE_DESKTOP_UI

logger = get_logger("main")

def main():
    logger.info("Initializing Tarcus Copilot...")
    
    if not run_startup_checks():
        print("\n[!] Startup checks failed! Please check the logs.")
        sys.exit(1)
        
    if not ENABLE_DESKTOP_UI:
        print("\n[!] Console mode is currently deprecated in favor of the PySide6 Desktop UI.")
        sys.exit(0)
        
    # Boot the Qt Application
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Native-looking cross-platform style
    
    # Instantiate the main desktop view
    window = MainWindow()
    window.show()
    
    # Start the event loop (this blocks the main thread, while PipelineWorker runs in the background)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
