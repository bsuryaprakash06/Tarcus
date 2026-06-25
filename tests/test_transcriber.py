import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.voice.speech_to_text import transcribe
from src.utils.exceptions import TranscriptionError
from src.models.transcription import TranscriptionResult

class TestTranscriber(unittest.TestCase):
    @patch('src.voice.speech_to_text.get_model')
    @patch('pathlib.Path.exists')
    def test_transcribe_success(self, mock_exists, mock_get_model):
        mock_exists.return_value = True
        
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "Hello World",
            "language": "en",
            "segments": [{"end": 3.5}]
        }
        mock_get_model.return_value = mock_model
        
        result = transcribe(Path("dummy_path.wav"))
        
        self.assertIsInstance(result, TranscriptionResult)
        self.assertEqual(result.text, "Hello World")
        self.assertEqual(result.language, "en")
        self.assertEqual(result.duration, 3.5)
        mock_model.transcribe.assert_called_once_with("dummy_path.wav", fp16=False)

    @patch('pathlib.Path.exists')
    def test_transcribe_file_not_found(self, mock_exists):
        mock_exists.return_value = False
        
        with self.assertRaises(TranscriptionError):
            transcribe(Path("non_existent.wav"))
