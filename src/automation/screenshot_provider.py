import os
import time
from typing import Optional, Tuple
from PIL import ImageGrab
from src.utils.settings import RECORDINGS_DIR # Reusing temp dir
from src.utils.logger import get_logger

logger = get_logger("automation.screenshots")

class ScreenshotProvider:
    """Modular screenshotting (Desktop, Window, Region, and Element)."""
    
    @staticmethod
    def _generate_path() -> str:
        timestamp = int(time.time() * 1000)
        return os.path.join(str(RECORDINGS_DIR), f"screenshot_{timestamp}.png")
        
    @staticmethod
    def capture_desktop() -> str:
        path = ScreenshotProvider._generate_path()
        img = ImageGrab.grab()
        img.save(path)
        logger.debug(f"Captured desktop to {path}")
        return path
        
    @staticmethod
    def capture_region(bbox: Tuple[int, int, int, int]) -> str:
        """bbox is (left, top, right, bottom)"""
        path = ScreenshotProvider._generate_path()
        img = ImageGrab.grab(bbox=bbox)
        img.save(path)
        logger.debug(f"Captured region to {path}")
        return path
        
    @staticmethod
    def capture_element(bounds: list) -> str:
        if not bounds or len(bounds) != 4:
            return ""
        return ScreenshotProvider.capture_region(tuple(bounds))
