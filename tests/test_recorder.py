import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.voice.recorder import record_audio
from src.utils.settings import RECORDINGS_DIR

class TestRecorder(unittest.TestCase):
    @patch('sounddevice.rec')
    @patch('sounddevice.wait')
    @patch('scipy.io.wavfile.write')
    def test_record_audio_creates_file(self, mock_write, mock_wait, mock_rec):
        mock_rec.return_value = MagicMock()
        
        result_path = record_audio(duration=1)
        
        self.assertEqual(result_path.parent, RECORDINGS_DIR)
        self.assertTrue(result_path.name.endswith(".wav"))
        mock_rec.assert_called_once()
        mock_wait.assert_called_once()
        mock_write.assert_called_once()
