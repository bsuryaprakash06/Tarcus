import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.voice.text_to_speech import speak
from src.utils.exceptions import TTSError

class TestTTS(unittest.TestCase):
    @patch('src.voice.text_to_speech._generate_speech_async')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    def test_speak_cache_miss(self, mock_mkdir, mock_exists, mock_generate):
        # Mock cache miss (exists returns False)
        mock_exists.return_value = False
        
        result_path = speak("Hello test")
        
        # Verify it called _generate_speech_async to generate new file
        mock_generate.assert_called_once()
        self.assertTrue(result_path.name.startswith("tts_"))
        self.assertTrue(result_path.name.endswith(".mp3"))

    @patch('src.voice.text_to_speech._generate_speech_async')
    @patch('pathlib.Path.exists')
    def test_speak_cache_hit(self, mock_exists, mock_generate):
        # Mock cache hit (exists returns True)
        mock_exists.return_value = True
        
        result_path = speak("Hello test")
        
        # Verify it did NOT call _generate_speech_async (reused file)
        mock_generate.assert_not_called()
        self.assertTrue(result_path.name.startswith("tts_"))
        self.assertTrue(result_path.name.endswith(".mp3"))
