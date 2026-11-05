import unittest

from peabox_voice_studio.models import Project
from peabox_voice_studio.services.transcripts import export_transcript_bundle, repair_segment_timing, save_transcript_session, update_transcript_session, validate_segments


class TranscriptValidationTests(unittest.TestCase):
    def test_detects_overlap_and_zero_duration(self):
        rows = [
            {"start": 0, "end": 1, "text": "A"},
            {"start": 0.5, "end": 0.5, "text": "B"},
        ]
        validation = validate_segments(rows)
        self.assertFalse(validation["valid"])
        self.assertGreaterEqual(validation["errors"], 2)

    def test_repair_removes_overlap_and_zero_duration(self):
        rows = [
            {"start": 0, "end": 1, "text": "A"},
            {"start": 0.5, "end": 0.5, "text": "B"},
        ]
        repaired = repair_segment_timing(rows)
        self.assertTrue(validate_segments(repaired)["valid"])
        self.assertGreater(repaired[1]["end"], repaired[1]["start"])
        self.assertGreaterEqual(repaired[1]["start"], repaired[0]["end"])

    def test_invalid_timing_blocks_export_and_save(self):
        rows = [{"start": 1, "end": 1, "text": "Bad"}]
        with self.assertRaises(ValueError): export_transcript_bundle(rows)
        with self.assertRaises(ValueError): save_transcript_session(Project("Demo"), "Bad", rows)

    def test_update_saved_session(self):
        project = Project("Demo")
        session = save_transcript_session(project, "Good", [{"start": 0, "end": 1, "text": "Old"}])
        self.assertTrue(update_transcript_session(project, session["id"], [{"start": 0, "end": 2, "text": "New"}]))
        self.assertEqual(project.settings["transcript_sessions"][0]["segments"][0]["text"], "New")
        self.assertEqual(project.settings["transcript_sessions"][0]["schema_version"], 2)

    def test_empty_text_is_warning_not_error(self):
        validation = validate_segments([{"start": 0, "end": 1, "text": ""}])
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["warnings"], 1)


if __name__ == "__main__": unittest.main()
