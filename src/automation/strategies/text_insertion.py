from abc import abstractmethod
from src.automation.strategies.interaction_strategy import InteractionStrategy
from src.models.target import TargetSession
from src.utils.logger import get_logger

logger = get_logger("automation.strategies.text_insertion")

class TextInsertionStrategy(InteractionStrategy):
    @abstractmethod
    def execute(self, session: TargetSession, text: str, clear_first: bool = False) -> bool:
        pass

class UIAutomationValuePatternStrategy(TextInsertionStrategy):
    """Inserts text directly via UIAutomation ValuePattern. Fast and background-safe."""
    def execute(self, session: TargetSession, text: str, clear_first: bool = False) -> bool:
        try:
            import uiautomation as auto
            if not session.target.native_handle:
                return False
            
            # Using the ControlFromHandle to get the object, then using ValuePattern
            control = auto.ControlFromHandle(int(session.target.native_handle))
            if not control:
                return False
                
            if auto.PatternId.ValuePatternId in control.GetSupportedPatterns():
                value_pattern = control.GetValuePattern()
                if clear_first:
                    value_pattern.SetValue(text)
                else:
                    current = value_pattern.Value
                    value_pattern.SetValue(current + text)
                return True
            return False
        except Exception as e:
            logger.debug(f"UIAutomationValuePatternStrategy failed: {e}")
            return False

class KeyboardSimulationStrategy(TextInsertionStrategy):
    """Fallback strategy that simulates keystrokes."""
    def execute(self, session: TargetSession, text: str, clear_first: bool = False) -> bool:
        try:
            import uiautomation as auto
            import time
            time.sleep(0.1) # UI settle time
            if clear_first:
                auto.SendKeys('{Ctrl}a{Delete}')
            auto.SendKeys(text)
            return True
        except Exception as e:
            logger.debug(f"KeyboardSimulationStrategy failed: {e}")
            return False
