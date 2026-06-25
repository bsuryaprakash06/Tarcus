import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.services.voice_service import VoiceService
from src.models.transcription import TranscriptionResult

class TestVoiceService(unittest.TestCase):
    @patch('src.services.voice_service.record_audio')
    @patch('src.services.voice_service.transcribe')
    def test_listen_pipeline(self, mock_transcribe, mock_record):
        mock_record.return_value = Path("dummy.wav")
        mock_result = TranscriptionResult(
            text="Test speech",
            language="en",
            duration=2.5
        )
        mock_transcribe.return_value = mock_result
        
        service = VoiceService()
        result = service.listen(duration=2)
        
        mock_record.assert_called_once_with(2)
        mock_transcribe.assert_called_once_with(Path("dummy.wav"))
        self.assertEqual(result, mock_result)
