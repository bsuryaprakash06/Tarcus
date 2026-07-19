import pytest
import time
from unittest.mock import MagicMock
from src.wakeword.activation_manager import ActivationManager
from src.wakeword.activation_response_manager import ActivationResponseManager
from src.wakeword.wakeword_events import WakeWordDetected
from src.models.wakeword import WakeState, WakePhrase
from src.utils.settings import CONVERSATION_TIMEOUT

def test_activation_manager_transitions():
    mock_response_manager = MagicMock()
    manager = ActivationManager(mock_response_manager)
    
    assert manager.state == WakeState.PASSIVE
    
    # Simulate wake word
    phrase = WakePhrase(phrase="hey tarcus", confidence=0.99)
    manager._on_wake_word_detected(WakeWordDetected(phrase=phrase))
    
    # Manager should instantly transition through WAKE_DETECTED -> ACKNOWLEDGING -> LISTENING
    assert manager.state == WakeState.LISTENING
    assert manager.current_session is not None
    assert manager.current_session.wake_phrase.phrase == "hey tarcus"
    mock_response_manager.acknowledge.assert_called_once()
    
    # Test manual transitions
    manager.mark_processing()
    assert manager.state == WakeState.PROCESSING
    
    manager.mark_responding()
    assert manager.state == WakeState.RESPONDING
    
    manager.mark_follow_up()
    assert manager.state == WakeState.FOLLOW_UP
    
def test_activation_manager_timeout():
    mock_response_manager = MagicMock()
    manager = ActivationManager(mock_response_manager)
    
    phrase = WakePhrase(phrase="hey tarcus", confidence=0.99)
    manager._on_wake_word_detected(WakeWordDetected(phrase=phrase))
    
    # Force timeout
    manager.current_session.last_activity = time.time() - (CONVERSATION_TIMEOUT + 1.0)
    
    # Check timeout manually (since timer loop runs on another thread)
    expired = manager.current_session.check_timeouts()
    assert expired is True
