import unittest
from unittest.mock import patch

from peabox_voice_studio.services.diagnostics import system_diagnostics, transcription_readiness


class DiagnosticsTests(unittest.TestCase):
    @patch("peabox_voice_studio.services.diagnostics.shutil.which", return_value=None)
    def test_compressed_media_requires_ffmpeg(self, _):
        result = transcription_readiness("video.mp4")
        self.assertFalse(result["ready"])
        self.assertTrue(result["requires_ffmpeg"])

    @patch("peabox_voice_studio.services.diagnostics.shutil.which", return_value=None)
    def test_wav_does_not_require_ffmpeg(self, _):
        result = transcription_readiness("audio.wav")
        self.assertTrue(result["ready"])
        self.assertFalse(result["requires_ffmpeg"])

    @patch("peabox_voice_studio.services.diagnostics.shutil.which", return_value="C:/ffmpeg/bin/ffmpeg.exe")
    def test_compressed_media_ready_with_ffmpeg(self, _):
        self.assertTrue(transcription_readiness("audio.mp3")["ready"])

    def test_system_diagnostics_has_core_checks(self):
        checks = {row["Check"] for row in system_diagnostics()}
        self.assertTrue({"Python", "FFmpeg", "Project storage", "Output storage", "Kokoro model", "Kokoro voices"}.issubset(checks))


if __name__ == "__main__": unittest.main()
