import pytest
from src.overlay.color_manager import ColorManager

def test_color_manager_determinism():
    manager = ColorManager()
    
    color1 = manager.resolve_color("target-A")
    color2 = manager.resolve_color("target-A")
    
    assert color1.hsvHue() == color2.hsvHue()
    assert color1.hsvSaturation() == color2.hsvSaturation()
    
def test_color_manager_uniqueness():
    manager = ColorManager()
    
    color1 = manager.resolve_color("target-A")
    color2 = manager.resolve_color("target-B")
    
    # Very likely to be different due to MD5 hashing
    assert color1.hsvHue() != color2.hsvHue() or color1.hsvSaturation() != color2.hsvSaturation()
