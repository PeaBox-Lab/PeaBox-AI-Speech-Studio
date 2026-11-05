import hashlib,tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock,patch
from peabox_voice_studio.providers.kokoro import _download

class ModelIntegrityTests(unittest.TestCase):
 def test_download_creates_checksum_sidecar(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'model.bin'; response=MagicMock();response.content=b'x'*2048;response.raise_for_status.return_value=None
   with patch('requests.get',return_value=response): _download(path,'https://example/model')
   self.assertEqual(path.with_suffix('.bin.sha256').read_text(),hashlib.sha256(response.content).hexdigest())
 def test_modified_model_is_rejected(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'model.bin';path.write_bytes(b'good');path.with_suffix('.bin.sha256').write_text(hashlib.sha256(b'good').hexdigest())
   path.write_bytes(b'bad')
   with self.assertRaisesRegex(ValueError,'Integrity check failed'): _download(path,'https://example/model')
if __name__=='__main__':unittest.main()
