import json
import tempfile
import unittest
from pathlib import Path

from peabox_voice_studio.models import ScriptBlock
from peabox_voice_studio.services.projects import ProjectStore, export_project, move_block, set_all_blocks_enabled, split_script_into_blocks


class ProjectTests(unittest.TestCase):
    def test_lifecycle_preserves_blocks(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ProjectStore(Path(folder)); project = store.create("Demo")
            project.blocks = [ScriptBlock(title="Intro", text="Hello")]; store.save(project)
            loaded = store.load(project.id)
            self.assertEqual(loaded.blocks[0].title, "Intro")
            store.delete(project.id); self.assertEqual(store.list(), [])

    def test_export_import_uses_new_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ProjectStore(Path(folder)); project = store.create("Portable")
            project.blocks = [ScriptBlock(title="A", text="Text")]; store.save(project)
            exported = export_project(project)
            payload = json.loads(exported)
            self.assertEqual(payload["schema_version"], 1)
            imported = store.import_project(exported)
            self.assertNotEqual(imported.id, project.id)
            self.assertEqual(imported.blocks[0].text, "Text")
            self.assertIn("(imported)", imported.name)

    def test_import_rejects_non_object(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError): ProjectStore(Path(folder)).import_project('[]')

    def test_split_paragraphs(self):
        blocks = split_script_into_blocks("First\n\nSecond\nline\n\nThird")
        self.assertEqual([b.text for b in blocks], ["First", "Second\nline", "Third"])

    def test_move_and_bulk_enable(self):
        blocks = [ScriptBlock("A"), ScriptBlock("B")]
        move_block(blocks, 1, -1); self.assertEqual([b.title for b in blocks], ["B", "A"])
        set_all_blocks_enabled(blocks, False); self.assertFalse(any(b.enabled for b in blocks))
        set_all_blocks_enabled(blocks, True); self.assertTrue(all(b.enabled for b in blocks))

    def test_invalid_identifier(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError): ProjectStore(Path(folder)).load("../bad")


if __name__ == "__main__": unittest.main()
