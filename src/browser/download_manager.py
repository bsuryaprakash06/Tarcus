from src.utils.logger import get_logger

logger = get_logger("browser.download_manager")

class DownloadManager:
    """
    Stub for future Milestone 7.4.
    Will handle downloading files from the browser and interacting with the local filesystem.
    """
    def __init__(self):
        self.downloads = []
        
    def start(self):
        logger.debug("DownloadManager started.")
        
    def stop(self):
        logger.debug("DownloadManager stopped.")
        
    def list(self) -> list:
        return self.downloads
