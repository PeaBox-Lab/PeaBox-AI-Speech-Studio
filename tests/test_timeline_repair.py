import io
import tempfile
import unittest
import wave
from array import array
from pathlib import Path
from peabox_voice_studio.models import Project, ScriptBlock
from peabox_voice_studio.services.timeline import acknowledge_clip_source, add_clip, cleanup_invalid_clips, duplicate_timeline, refresh_clip, relink_clip
def make_wav(value=1000, frames=100, rate=1000):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(1); writer.setsampwidth(2); writer.setframerate(rate); writer.writeframes(array("h", [value] * frames).tobytes())
    return buffer.getvalue()
class TimelineRepairTests(unittest.TestCase):
    def test_relink_refreshes_metadata_and_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); old = root / "old.wav"; new = root / "new.wav"
            old.write_bytes(make_wav(frames=100)); new.write_bytes(make_wav(frames=200))
            project = Project("Demo"); clip = add_clip(project, old)
            old_hash = clip["asset_hash"]
            relink_clip(clip, new)
            self.assertEqual(clip["duration_seconds"], 0.2)
            self.assertNotEqual(clip["asset_hash"], old_hash)
            self.assertEqual(clip["file_name"], "new.wav")
    def test_refresh_existing_clip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "a.wav"; path.write_bytes(make_wav(frames=100))
            project = Project("Demo"); clip = add_clip(project, path)
            path.write_bytes(make_wav(frames=300))
            refresh_clip(clip)
            self.assertEqual(clip["duration_seconds"], 0.3)
    def test_acknowledge_stale_source(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "a.wav"; path.write_bytes(make_wav())
            block = ScriptBlock("B", text="old"); project = Project("Demo", blocks=[block]); clip = add_clip(project, path, block=block)
            block.text = "new"
            self.assertTrue(acknowledge_clip_source(project, clip))
    def test_cleanup_repairs_duplicate_ids_and_optional_missing(self):
        project = Project("Demo")
        project.settings["audio_clips"] = [
            {"id": "same", "title": "A", "file": "missing-a.wav", "start_seconds": -2, "gain_db": 100},
            {"id": "same", "title": "B", "file": "missing-b.wav"},
        ]
        result = cleanup_invalid_clips(project, remove_missing=False)
        self.assertEqual(result["repaired_ids"], 1)
        self.assertEqual(project.settings["audio_clips"][0]["start_seconds"], 0)
        self.assertEqual(project.settings["audio_clips"][0]["gain_db"], 12)
        result = cleanup_invalid_clips(project, remove_missing=True)
        self.assertEqual(result["removed"], 2)
    def test_duplicate_timeline_appends_copies(self):
        project = Project("Demo")
        project.settings["audio_clips"] = [{"id": "a", "title": "One", "file": "x.wav"}]
        duplicate = duplicate_timeline(project)
        self.assertEqual(len(project.settings["audio_clips"]), 2)
        self.assertNotEqual(duplicate[0]["id"], "a")
        self.assertIn("copy", duplicate[0]["title"])
if __name__ == "__main__": unittest.main()