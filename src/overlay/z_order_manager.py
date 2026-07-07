class ZOrderManager:
    """
    Ensures overlapping overlays follow the true window Z-order of the OS.
    If Notepad is in front of Calculator, Notepad's overlay must be in front of Calculator's overlay.
    """
    def __init__(self, backend):
        self.backend = backend
        
    def sync_z_order(self, active_windows: dict):
        """
        Queries the OS window stack via the AutomationBackend and updates
        the Qt Window Z-Order for all active overlays.
        """
        # This requires the backend to return an ordered list of target_ids from front to back.
        # We then call window.raise_() and window.lower() in Qt.
        pass
