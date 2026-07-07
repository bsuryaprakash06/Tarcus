from PySide6.QtGui import QColor

class ThemeManager:
    """
    Manages the overall color palette and themes for the overlay engine.
    Allows for future Dark/Light mode, High Contrast, and Accessibility color palettes.
    """
    def __init__(self):
        self.current_theme = "default"
        
        self.themes = {
            "default": {
                "background_opacity": 0.0,
                "text_color": QColor(255, 255, 255),
                "badge_bg_opacity": 0.8,
                "font_family": "Inter, Roboto, sans-serif"
            },
            "high_contrast": {
                "background_opacity": 0.0,
                "text_color": QColor(0, 0, 0),
                "badge_bg_opacity": 1.0,
                "font_family": "Arial"
            }
        }
        
    def get_setting(self, key: str):
        theme = self.themes.get(self.current_theme, self.themes["default"])
        return theme.get(key, self.themes["default"].get(key))
