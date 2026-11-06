import json
import tempfile
import unittest
from pathlib import Path
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.preferences import DEFAULTS, load_preferences, mark_project_opened, resolve_projects, save_preferences, sanitize_preferences, toggle_favorite
class PreferenceTests(unittest.TestCase):
    def test_missing_file_uses_defaults(self):
        with tempfile.TemporaryDirectory() as folder:
            prefs = load_preferences(Path(folder) / "missing.json")
            self.assertEqual(prefs["default_area"], "Overview")
            self.assertEqual(prefs["dashboard_detail"], "Standard")
    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "prefs.json"
            save_preferences({"default_area": "Production", "compact_navigation": True, "reduced_motion": True, "dashboard_detail": "Detailed", "favorite_project_ids": ["abc"], "recent_project_ids": ["def"]}, path)
            loaded = load_preferences(path)
            self.assertTrue(loaded["compact_navigation"])
            self.assertEqual(loaded["favorite_project_ids"], ["abc"])
    def test_corrupt_file_uses_defaults(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "prefs.json"; path.write_text("{bad", encoding="utf-8")
            self.assertEqual(load_preferences(path), DEFAULTS)
    def test_recent_projects_are_unique_and_bounded(self):
        prefs = dict(DEFAULTS)
        for index in range(20): mark_project_opened(prefs, f"p{index}")
        mark_project_opened(prefs, "p19")
        self.assertEqual(len(prefs["recent_project_ids"]), 12)
        self.assertEqual(prefs["recent_project_ids"][0], "p19")
        self.assertEqual(prefs["recent_project_ids"].count("p19"), 1)
    def test_toggle_favorite(self):
        prefs = dict(DEFAULTS)
        self.assertTrue(toggle_favorite(prefs, "abc"))
        self.assertFalse(toggle_favorite(prefs, "abc"))
        self.assertEqual(prefs["favorite_project_ids"], [])
    def test_invalid_values_are_sanitized(self):
        prefs = sanitize_preferences({"dashboard_detail": "Huge", "favorite_project_ids": ["ok", "../bad", "ok"], "recent_project_ids": "bad"})
        self.assertEqual(prefs["dashboard_detail"], "Standard")
        self.assertEqual(prefs["favorite_project_ids"], ["ok"])
        self.assertEqual(prefs["recent_project_ids"], [])
    def test_resolve_projects_preserves_requested_order(self):
        projects = [Project("A", id="a"), Project("B", id="b")]
        self.assertEqual([item.id for item in resolve_projects(projects, ["b", "missing", "a"])], ["b", "a"])
if __name__ == "__main__": unittest.main()
