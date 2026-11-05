import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from peabox_voice_studio.models import Project, ScriptBlock
from peabox_voice_studio.services.batch import build_manifest, render_local_blocks
from peabox_voice_studio.services.files import build_render_zip

class BatchTests(unittest.TestCase):
    def test_manifest_totals_enabled_only(self):
        p=Project("Demo",blocks=[ScriptBlock("A",text="one two",enabled=True),ScriptBlock("B",text="ignored",enabled=False),ScriptBlock("C",text="abc",provider="Azure Speech")])
        m=build_manifest(p,{"Kokoro local":0,"Azure Speech":15})
        self.assertEqual(m["totals"]["enabled_blocks"],2)
        self.assertEqual(m["totals"]["characters"],10)
        self.assertGreater(m["totals"]["estimated_cost_usd"],0)
    def test_local_render_skips_cloud(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            def fake(text,voice,language,speed,name):
                path=root/f"{name}.wav"; path.write_bytes(text.encode()); return path
            p=Project("Demo",blocks=[ScriptBlock("Local",text="hello"),ScriptBlock("Cloud",text="world",provider="Azure Speech")])
            files,results=render_local_blocks(p,fake)
            self.assertEqual(len(files),1); self.assertEqual([r["status"] for r in results],["rendered","skipped"])
    def test_render_zip_contains_manifest_and_audio(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"a.wav"; path.write_bytes(b"audio")
            data=build_render_zip([path],{"project":"demo"})
            with zipfile.ZipFile(BytesIO(data)) as zf:
                self.assertIn("manifest.json",zf.namelist()); self.assertIn("audio/a.wav",zf.namelist())
if __name__=="__main__": unittest.main()
