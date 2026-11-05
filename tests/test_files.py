import tempfile
import unittest
from pathlib import Path

from peabox_voice_studio.services.files import atomic_write_bytes, safe_filename


class FileServiceTests(unittest.TestCase):
    def test_safe_filename(self):
        self.assertEqual(safe_filename("../../My Audio: 01"), "My_Audio_01")
        self.assertEqual(safe_filename("***"), "audio")

    def test_atomic_write(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "result.bin"
            atomic_write_bytes(path, b"complete")
            self.assertEqual(path.read_bytes(), b"complete")


if __name__ == "__main__":
    unittest.main()
