import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.services.audio_service import AudioService
from src.utils.exceptions import AudioPlaybackError

class TestAudioService(unittest.TestCase):
    @patch('ctypes.windll.winmm.mciSendStringW')
    @patch('pathlib.Path.exists')
    def test_play_file_success(self, mock_exists, mock_mci):
        mock_exists.return_value = True
        mock_mci.return_value = 0  # 0 means success
        
        service = AudioService()
        service.play_file(Path("dummy.mp3"))
        
        # Verify it called MCI open, play, close
        self.assertEqual(mock_mci.call_count, 3)

    @patch('pathlib.Path.exists')
    def test_play_file_not_found(self, mock_exists):
        mock_exists.return_value = False
        
        service = AudioService()
        with self.assertRaises(AudioPlaybackError):
            service.play_file(Path("non_existent.mp3"))
