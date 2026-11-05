import unittest

from peabox_voice_studio.services.quality import pronunciation_conflicts, pronunciation_preview


class QualityConflictTests(unittest.TestCase):
    def test_duplicate_rules_are_reported(self):
        entries = [
            {"source": "AI", "replacement": "A I", "case_sensitive": False, "whole_word": True},
            {"source": "ai", "replacement": "artificial intelligence", "case_sensitive": False, "whole_word": True},
        ]
        issues = pronunciation_conflicts(entries)
        self.assertTrue(any(issue["severity"] == "warning" for issue in issues))

    def test_overlapping_sources_are_reported(self):
        entries = [
            {"source": "Voice", "replacement": "voice", "case_sensitive": False, "whole_word": True},
            {"source": "Voice Studio", "replacement": "voice studio", "case_sensitive": False, "whole_word": True},
        ]
        self.assertTrue(any(issue["severity"] == "info" for issue in pronunciation_conflicts(entries)))

    def test_preview_reports_change(self):
        entries = [{"source": "PeaBox", "replacement": "pea box", "case_sensitive": False, "whole_word": True}]
        preview = pronunciation_preview("Use PEABOX", entries)
        self.assertTrue(preview["changed"])
        self.assertEqual(preview["prepared"], "Use pea box")


if __name__ == "__main__": unittest.main()
