import numpy as np

class NoiseSuppressionNode:
    """
    Placeholder for a Noise Suppression stage (e.g. WebRTC NS, RNNoise).
    Currently acts as a passthrough.
    """
    def __init__(self):
        self.enabled = False
        
    def process(self, frame: np.ndarray) -> np.ndarray:
        if not self.enabled:
            return frame
        # Placeholder for noise suppression logic
        return frame
