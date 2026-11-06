import tempfile
import unittest
from pathlib import Path
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.comparisons import create_comparison_record, delete_comparison, set_comparison_preference
class ComparisonTests(unittest.TestCase):
    def test_create_prefer_delete(self):
        project = Project("Demo")
        with tempfile.TemporaryDirectory() as folder:
            a = Path(folder) / "a.wav"; b = Path(folder) / "b.wav"
            a.write_bytes(b"a"); b.write_bytes(b"b")
            variants = [{"label": "A", "voice": "one"}, {"label": "B", "voice": "two"}]
            record = create_comparison_record(project, "Hello", variants, [a, b], [{"duration_seconds": 1}, {"duration_seconds": 2}])
            self.assertEqual(record["outputs"], ["a.wav", "b.wav"])
            self.assertTrue(set_comparison_preference(project, record["id"], "B", "Clearer"))
            self.assertEqual(project.settings["comparison_history"][0]["preferred"], "B")
            self.assertTrue(delete_comparison(project, record["id"]))
    def test_requires_two_variants(self):
        with self.assertRaises(ValueError):
            create_comparison_record(Project("Demo"), "x", [], [], [])
    def test_invalid_preference_rejected(self):
        project = Project("Demo")
        with self.assertRaises(ValueError): set_comparison_preference(project, "x", "C")
    def test_history_is_bounded(self):
        project = Project("Demo")
        with tempfile.TemporaryDirectory() as folder:
            a = Path(folder) / "a.wav"; b = Path(folder) / "b.wav"; a.write_bytes(b"a"); b.write_bytes(b"b")
            for index in range(25):
                create_comparison_record(project, str(index), [{"label": "A"}, {"label": "B"}], [a, b], [{}, {}])
            self.assertEqual(len(project.settings["comparison_history"]), 20)
if __name__ == "__main__": unittest.main()
