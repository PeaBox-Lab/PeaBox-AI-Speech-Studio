import io
import tempfile
import unittest
import wave
from array import array
from pathlib import Path
from peabox_voice_studio.models import Project, ScriptBlock
from peabox_voice_studio.services.timeline import add_clip, arrange_sequential, block_hash, clip_status, mix_timeline, move_clip, remove_clip, timeline_manifest, validate_timeline, waveform_peaks
def make_wav(samples, rate=1000, channels=1):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(channels); writer.setsampwidth(2); writer.setframerate(rate); writer.writeframes(array("h", samples).tobytes())
    return buffer.getvalue()
class TimelineTests(unittest.TestCase):
    def test_add_clip_and_peaks(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "a.wav"; path.write_bytes(make_wav([0, 1000, -2000, 3000]))
            project = Project("Demo"); block = ScriptBlock("A", text="Hello")
            clip = add_clip(project, path, block=block)
            self.assertEqual(clip["source_hash"], block_hash(block))
            self.assertTrue(clip["peaks"])
            self.assertEqual(len(project.settings["audio_clips"]), 1)
    def test_stale_and_missing_status(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "a.wav"; path.write_bytes(make_wav([1000] * 100))
            block = ScriptBlock("A", text="Before"); project = Project("Demo", blocks=[block])
            clip = add_clip(project, path, block=block)
            self.assertTrue(clip_status(project, clip)["ready"])
            block.text = "After"
            self.assertTrue(clip_status(project, clip)["stale"])
            path.unlink()
            self.assertTrue(clip_status(project, clip)["missing"])
    def test_sequential_arrangement_and_move_remove(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Project("Demo")
            for name in ("a", "b"):
                path = Path(folder) / f"{name}.wav"; path.write_bytes(make_wav([1000] * 1000))
                add_clip(project, path, title=name)
            arrange_sequential(project, 0.5)
            self.assertEqual(project.settings["audio_clips"][1]["start_seconds"], 1.5)
            move_clip(project, 1, -1)
            self.assertEqual(project.settings["audio_clips"][0]["title"], "b")
            clip_id = project.settings["audio_clips"][0]["id"]
            self.assertTrue(remove_clip(project, clip_id))
    def test_mix_sequential_clips(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); project = Project("Demo")
            a = root / "a.wav"; b = root / "b.wav"
            a.write_bytes(make_wav([1000] * 1000)); b.write_bytes(make_wav([2000] * 1000))
            add_clip(project, a, start_seconds=0); add_clip(project, b, start_seconds=1)
            output, manifest = mix_timeline(project, "mix", root)
            self.assertTrue(output.exists())
            self.assertEqual(manifest["mix"]["duration_seconds"], 2.0)
            self.assertEqual(len(project.settings["timeline_exports"]), 1)
    def test_mix_overlapping_clips(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); project = Project("Demo")
            a = root / "a.wav"; b = root / "b.wav"
            a.write_bytes(make_wav([1000] * 1000)); b.write_bytes(make_wav([2000] * 1000))
            add_clip(project, a, start_seconds=0); add_clip(project, b, start_seconds=0)
            output, manifest = mix_timeline(project, "mix", root)
            self.assertEqual(manifest["mix"]["duration_seconds"], 1.0)
            self.assertEqual(manifest["mix"]["clipped_samples_before_limit"], 0)
    def test_format_mismatch_blocks_export(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); project = Project("Demo")
            a = root / "a.wav"; b = root / "b.wav"
            a.write_bytes(make_wav([1] * 100, rate=1000)); b.write_bytes(make_wav([1] * 100, rate=8000))
            add_clip(project, a); add_clip(project, b)
            validation = validate_timeline(project)
            self.assertFalse(validation["valid"])
            with self.assertRaises(ValueError): mix_timeline(project, "bad", root)
    def test_manifest_contains_status(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "a.wav"; path.write_bytes(make_wav([1] * 10))
            project = Project("Demo"); add_clip(project, path)
            manifest = timeline_manifest(project)
            self.assertEqual(manifest["schema_version"], 1)
            self.assertTrue(manifest["clips"][0]["status"]["ready"])
    def test_waveform_peaks_are_normalized(self):
        peaks = waveform_peaks(make_wav([0, 32767, -32768, 100]), 2)
        self.assertEqual(len(peaks), 2)
        self.assertTrue(all(0 <= peak <= 1.0001 for peak in peaks))
if __name__ == "__main__": unittest.main()