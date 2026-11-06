import unittest
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.transcripts import delete_transcript_session, export_transcript_bundle, filter_segments, normalize_segments, save_transcript_session, transcript_text
class TranscriptTests(unittest.TestCase):
    def rows(self):
        return [{"start": 0, "end": 1.25, "speaker": "Speaker 1", "text": " Hello "}, {"start": 1.25, "end": 2, "speaker": "", "text": "World"}]
    def test_normalize_and_text(self):
        rows = normalize_segments(self.rows())
        self.assertEqual(rows[0]["text"], "Hello")
        self.assertIn("Speaker 1: Hello", transcript_text(rows))
    def test_export_bundle(self):
        bundle = export_transcript_bundle(self.rows())
        self.assertTrue(bundle["vtt"].startswith("WEBVTT"))
        self.assertIn("00:00:00,000 --> 00:00:01,250", bundle["srt"])
        self.assertIn("Speaker 1: Hello", bundle["txt"])
    def test_filter(self):
        self.assertEqual(len(filter_segments(self.rows(), "speaker 1")), 1)
        self.assertEqual(len(filter_segments(self.rows(), "world")), 1)
    def test_save_and_delete_session(self):
        project = Project("Demo")
        session = save_transcript_session(project, "Interview", self.rows(), "audio.mp3", "en")
        self.assertEqual(project.settings["transcript_sessions"][0]["name"], "Interview")
        self.assertTrue(delete_transcript_session(project, session["id"]))
    def test_session_history_is_bounded(self):
        project = Project("Demo")
        for index in range(25): save_transcript_session(project, f"T{index}", self.rows())
        self.assertEqual(len(project.settings["transcript_sessions"]), 20)
if __name__ == "__main__": unittest.main()