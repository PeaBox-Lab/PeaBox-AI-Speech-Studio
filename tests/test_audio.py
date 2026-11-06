import io
import math
import tempfile
import unittest
import wave
from array import array
from pathlib import Path
from peabox_voice_studio.services.audio import inspect_wav, normalize_wav, save_processed_wav, trim_silence_wav
def make_wav(samples, rate=8000, channels=1):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(2)
        writer.setframerate(rate)
        writer.writeframes(array("h", samples).tobytes())
    return buffer.getvalue()
class AudioTests(unittest.TestCase):
    def test_inspect_wav(self):
        raw = make_wav([0, 1000, -1000, 2000, -2000], rate=5)
        metrics = inspect_wav(raw)
        self.assertEqual(metrics["sample_rate_hz"], 5)
        self.assertEqual(metrics["duration_seconds"], 1.0)
        self.assertEqual(metrics["sample_width_bits"], 16)
        self.assertLess(metrics["peak_dbfs"], 0)
    def test_normalize_reaches_target(self):
        raw = make_wav([1000, -1000, 500, -500])
        processed, details = normalize_wav(raw, -1.0)
        metrics = inspect_wav(processed)
        self.assertTrue(details["changed"])
        self.assertAlmostEqual(metrics["peak_dbfs"], -1.0, places=1)
    def test_silent_normalization_is_noop(self):
        raw = make_wav([0] * 10)
        processed, details = normalize_wav(raw)
        self.assertEqual(processed, raw)
        self.assertFalse(details["changed"])
    def test_trim_silence(self):
        raw = make_wav([0] * 800 + [5000] * 800 + [0] * 800, rate=8000)
        processed, details = trim_silence_wav(raw, -40, 0)
        self.assertTrue(details["changed"])
        self.assertAlmostEqual(inspect_wav(processed)["duration_seconds"], 0.1, places=2)
    def test_trim_silent_file_is_noop(self):
        raw = make_wav([0] * 100)
        processed, details = trim_silence_wav(raw)
        self.assertEqual(processed, raw)
        self.assertFalse(details["changed"])
    def test_rejects_non_16_bit_pcm(self):
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as writer:
            writer.setnchannels(1); writer.setsampwidth(1); writer.setframerate(8000); writer.writeframes(bytes([128] * 10))
        with self.assertRaises(ValueError): inspect_wav(buffer.getvalue())
    def test_save_processed_wav(self):
        raw = make_wav([1, 2, 3])
        with tempfile.TemporaryDirectory() as folder:
            path = save_processed_wav(raw, "My Audio", "Normalized", Path(folder))
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "My_Audio_Normalized.wav")
if __name__ == "__main__": unittest.main()
