import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.voice.recorder import record_audio
from src.utils.settings import RECORDINGS_DIR

class TestRecorder(unittest.TestCase):
    @patch('src.voice.recorder.VoiceActivityDetector')
    @patch('sounddevice.InputStream')
    @patch('scipy.io.wavfile.write')
    def test_record_audio_creates_file(self, mock_write, mock_input_stream, mock_vad):
        mock_vad_instance = MagicMock()
        mock_vad_instance.should_continue.side_effect = [True, False]
        mock_vad.return_value = mock_vad_instance
        
        # Simulate the audio callback being triggered to populate audio_frames
        def mock_enter(*args, **kwargs):
            callback = mock_input_stream.call_args.kwargs.get('callback')
            import numpy as np
            # Provide dummy data
            callback(np.zeros((10, 2), dtype=np.int16), 10, None, None)
            return MagicMock()
            
        mock_input_stream.return_value.__enter__ = mock_enter
        
        result_path = record_audio(duration=1)
        
        self.assertEqual(result_path.parent, RECORDINGS_DIR)
        self.assertTrue(result_path.name.endswith(".wav"))
        mock_input_stream.assert_called_once()
        mock_write.assert_called_once()
