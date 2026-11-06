import io
import json
import tempfile
import unittest
import wave
import zipfile
from array import array
from pathlib import Path
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.bundles import export_timeline_bundle, import_timeline_bundle
from peabox_voice_studio.services.timeline import add_clip
def make_wav(samples=None, rate=8000):
    samples = samples or [0, 1000, -1000, 0]
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(1); writer.setsampwidth(2); writer.setframerate(rate); writer.writeframes(array("h", samples).tobytes())
    return buffer.getvalue()
class BundleTests(unittest.TestCase):
    def test_export_import_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); assets = root / "assets"; assets.mkdir()
            wav = root / "voice.wav"; wav.write_bytes(make_wav())
            project = Project("Portable"); clip = add_clip(project, wav, "Voice")
            raw = export_timeline_bundle(project)
            self.assertEqual(clip["file"], str(wav), "Export must not mutate the live project")
            imported = import_timeline_bundle(raw, assets)
            self.assertNotEqual(imported.id, project.id)
            imported_clip = imported.settings["audio_clips"][0]
            self.assertTrue(Path(imported_clip["file"]).exists())
            self.assertEqual(imported_clip["file_name"], Path(imported_clip["file"]).name)
            self.assertIn("bundle import", imported.name)
    def test_collision_safe_asset_import(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); wav = root / "voice.wav"; wav.write_bytes(make_wav())
            project = Project("Portable"); add_clip(project, wav)
            raw = export_timeline_bundle(project)
            first = import_timeline_bundle(raw, root)
            second = import_timeline_bundle(raw, root)
            first_path = Path(first.settings["audio_clips"][0]["file"])
            second_path = Path(second.settings["audio_clips"][0]["file"])
            self.assertNotEqual(first_path, second_path)
            self.assertTrue(second_path.exists())
    def test_missing_source_stays_unlinked(self):
        project = Project("Missing")
        project.settings["audio_clips"] = [{"id": "x", "title": "Missing", "file": "missing.wav", "file_name": "missing.wav", "enabled": True}]
        raw = export_timeline_bundle(project)
        with tempfile.TemporaryDirectory() as folder:
            imported = import_timeline_bundle(raw, Path(folder))
            self.assertEqual(imported.settings["audio_clips"][0]["file"], "")
    def test_rejects_zip_slip(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("manifest.json", json.dumps({"schema_version": 1}))
            archive.writestr("project.json", json.dumps({"project": Project("X").to_dict()}))
            archive.writestr("../evil.wav", make_wav())
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError): import_timeline_bundle(buffer.getvalue(), Path(folder))
    def test_rejects_non_wav_referenced_asset(self):
        project = Project("X")
        project.settings["audio_clips"] = [{"id": "x", "bundle_asset": "audio/a.txt", "file": "", "title": "X"}]
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("manifest.json", json.dumps({"schema_version": 1, "clip_assets": {"x": "audio/a.txt"}}))
            archive.writestr("project.json", json.dumps({"project": project.to_dict()}))
            archive.writestr("audio/a.txt", "not audio")
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError): import_timeline_bundle(buffer.getvalue(), Path(folder))
if __name__ == "__main__": unittest.main()
class BundleTransactionTests(unittest.TestCase):
    def test_failed_commit_rolls_back_assets(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); a=root/'a.wav'; b=root/'b.wav'; a.write_bytes(make_wav()); b.write_bytes(make_wav())
            project=Project('P'); add_clip(project,a); add_clip(project,b)
            raw=export_timeline_bundle(project); target=root/'target'; target.mkdir()
            calls={'n':0}
            def flaky(clip,path):
                calls['n']+=1
                if calls['n']==2: raise RuntimeError('fail')
                from peabox_voice_studio.services.timeline import refresh_clip as real
                return real(clip,path)
            with patch('peabox_voice_studio.services.bundles.refresh_clip',side_effect=flaky):
                with self.assertRaises(RuntimeError): import_timeline_bundle(raw,target)
            self.assertEqual([p for p in target.iterdir() if p.is_file()],[])
