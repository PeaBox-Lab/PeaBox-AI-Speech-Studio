import tempfile
import unittest
from pathlib import Path
from peabox_voice_studio.services.files import atomic_write_bytes, safe_filename
class FileTests(unittest.TestCase):
    def test_safe_filename(self): self.assertEqual(safe_filename("../../My Audio: 01"),"My_Audio_01")
    def test_atomic_write(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"x"; atomic_write_bytes(path,b"ok"); self.assertEqual(path.read_bytes(),b"ok")
if __name__=="__main__": unittest.main()

class FileLockTests(unittest.TestCase):
    def test_lock_prevents_concurrent_entry(self):
        from peabox_voice_studio.services.files import FileLock
        with tempfile.TemporaryDirectory() as folder:
            lock=Path(folder)/'x.lock'
            with FileLock(lock):
                with self.assertRaises(TimeoutError):
                    with FileLock(lock,timeout=0.01,delay=0.001): pass
            self.assertFalse(lock.exists())
