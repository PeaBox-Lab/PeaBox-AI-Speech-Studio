import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path

from peabox_voice_studio.models import Project, ScriptBlock
from peabox_voice_studio.services.batch import build_manifest, render_local_blocks, summarize_results, validate_batch
from peabox_voice_studio.services.files import build_render_zip


class BatchTests(unittest.TestCase):
    def test_manifest_has_validation_and_enabled_totals(self):
        project = Project("Demo", blocks=[ScriptBlock("A", text="one two"), ScriptBlock("B", text="ignored", enabled=False), ScriptBlock("C", text="abc", provider="Azure Speech")])
        manifest = build_manifest(project, {"Kokoro local": 0, "Azure Speech": 15}, {"Kokoro local", "Azure Speech"})
        self.assertEqual(manifest["schema_version"], 2)
        self.assertTrue(manifest["validation"]["ready"])
        self.assertEqual(manifest["validation"]["warnings"], 0)
        self.assertEqual(manifest["totals"]["enabled_blocks"], 2)
        self.assertEqual(manifest["totals"]["characters"], 10)

    def test_empty_enabled_block_fails_validation_and_render(self):
        project = Project("Demo", blocks=[ScriptBlock("Empty", text="   ")])
        validation = validate_batch(project)
        self.assertFalse(validation["ready"]); self.assertEqual(validation["errors"], 1)
        files, results = render_local_blocks(project, lambda *args: None)
        self.assertEqual(files, []); self.assertEqual(results[0]["status"], "failed")

    def test_no_enabled_blocks_is_not_ready(self):
        project = Project("Demo", blocks=[ScriptBlock("Off", text="text", enabled=False)])
        self.assertFalse(validate_batch(project)["ready"])

    def test_local_render_skips_cloud_and_summarizes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def fake(text, voice, language, speed, name):
                path = root / f"{name}.wav"; path.write_bytes(text.encode()); return path
            project = Project("Demo", blocks=[ScriptBlock("Local", text="hello"), ScriptBlock("Cloud", text="world", provider="Azure Speech")])
            files, results = render_local_blocks(project, fake)
            self.assertEqual(len(files), 1)
            self.assertEqual(summarize_results(results), {"rendered": 1, "skipped": 1, "failed": 0})

    def test_render_zip_contains_manifest_and_audio(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "a.wav"; path.write_bytes(b"audio")
            data = build_render_zip([path], {"project": "demo"})
            with zipfile.ZipFile(BytesIO(data)) as archive:
                self.assertIn("manifest.json", archive.namelist()); self.assertIn("audio/a.wav", archive.namelist())


if __name__ == "__main__": unittest.main()
