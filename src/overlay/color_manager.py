import hashlib
from PySide6.QtGui import QColor

class ColorManager:
    """
    Deterministically generates and resolves colors based on the target ID.
    Avoids storing colors in the state model, guaranteeing consistency.
    """
    def __init__(self):
        # We can avoid certain hue ranges if they are hard to see
        pass

    def resolve_color(self, target_id: str) -> QColor:
        """
        Hashes the target_id to produce a deterministic, visually distinct QColor (using HSV).
        """
        # Create a hash of the UUID
        hash_obj = hashlib.md5(target_id.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        
        # Take the first few bytes to determine hue (0-359)
        hue = int(hash_hex[:4], 16) % 360
        
        # Keep Saturation and Value high for vibrant overlay borders
        saturation = 200 + (int(hash_hex[4:6], 16) % 55) # 200 - 255
        value = 220 + (int(hash_hex[6:8], 16) % 35)      # 220 - 255
        
        color = QColor()
        color.setHsv(hue, saturation, value)
        return color
