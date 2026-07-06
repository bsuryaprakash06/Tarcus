import pytest
from src.services.dialogue_manager import DialogueManager
from src.models.dialogue_state import DialogueState

def test_dialogue_state_lifecycle():
    dm = DialogueManager()
    
    assert dm.conversation_state.dialogue_state == DialogueState.IDLE
    
    dm.set_pending_clarification("Close it.", "AUTOMATION", "Ambiguous")
    
    assert dm.conversation_state.dialogue_state == DialogueState.WAITING_FOR_CLARIFICATION
    assert dm.get_pending_clarification().original_text == "Close it."
    
    dm.clear_pending_clarification()
    assert dm.conversation_state.dialogue_state == DialogueState.IDLE
    
def test_cancellation():
    dm = DialogueManager()
    
    assert dm.check_cancellation("Nevermind.") == True
    assert dm.check_cancellation("Cancel") == True
    assert dm.check_cancellation("Actually, open it.") == False
