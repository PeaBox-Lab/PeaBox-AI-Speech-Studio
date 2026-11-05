import json
import tempfile
import unittest
from pathlib import Path

from peabox_voice_studio.services.projects import ProjectStore


class ProjectStoreTests(unittest.TestCase):
    def test_complete_project_lifecycle(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ProjectStore(Path(folder))
            project = store.create("Demo", "Initial description")
            self.assertEqual(len(store.list()), 1)
            project.script = "Hello from PeaBox."
            project.name = "Renamed Demo"
            store.save(project)
            loaded = store.load(project.id)
            self.assertEqual(loaded.name, "Renamed Demo")
            self.assertEqual(loaded.script, "Hello from PeaBox.")
            store.delete(project.id)
            self.assertEqual(store.list(), [])

    def test_invalid_identifier_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ProjectStore(Path(folder))
            with self.assertRaises(ValueError):
                store.load("../outside")

    def test_corrupt_project_is_skipped(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "broken.json").write_text("{broken", encoding="utf-8")
            store = ProjectStore(root)
            self.assertEqual(store.list(), [])


if __name__ == "__main__":
    unittest.main()
