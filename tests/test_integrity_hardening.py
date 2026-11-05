import io
import json
import tempfile
import unittest
import wave
from array import array
from pathlib import Path
from unittest.mock import patch

from peabox_voice_studio.config import MAX_TIMELINE_MIX_SAMPLES
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.files import collision_safe_path, user_safe_error
from peabox_voice_studio.services.jobs import create_job, run_job
from peabox_voice_studio.services.projects import ProjectStore, export_project
from peabox_voice_studio.services.timeline import add_clip, clip_status, mix_timeline


def make_wav(frames=100, rate=1000, value=1000):
    b=io.BytesIO()
    with wave.open(b,'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(array('h',[value]*frames).tobytes())
    return b.getvalue()


class IntegrityHardeningTests(unittest.TestCase):
    def test_collision_safe_path_never_overwrites(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'audio.wav').write_bytes(b'a')
            self.assertEqual(collision_safe_path(root,'audio.wav').name,'audio_2.wav')

    def test_changed_asset_is_not_ready(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'a.wav'; path.write_bytes(make_wav(value=1000))
            project=Project('Demo'); clip=add_clip(project,path)
            path.write_bytes(make_wav(value=2000))
            status=clip_status(project,clip)
            self.assertTrue(status['asset_changed']); self.assertFalse(status['ready'])

    def test_import_rewrites_nested_job_project_and_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            store=ProjectStore(Path(folder)/'projects')
            project=Project('Demo')
            project.settings['batch_jobs']=[{'project_id':project.id,'items':[{'status':'rendered','file':'C:/old.wav'}]}]
            project.settings['audio_clips']=[{'id':'c','file':'C:/clip.wav'}]
            imported=store.import_project(export_project(project))
            job=imported.settings['batch_jobs'][0]
            self.assertEqual(job['project_id'],imported.id)
            self.assertIsNone(job['items'][0]['file']); self.assertEqual(job['items'][0]['status'],'failed')
            self.assertEqual(imported.settings['audio_clips'][0]['file'],'')

    def test_recorded_usage_is_not_actual_invoice(self):
        project=Project('Demo')
        from peabox_voice_studio.models import ScriptBlock
        project.blocks=[ScriptBlock('A',text='hello')]
        job=create_job(project,{'Kokoro local':1},{'Kokoro local'})
        with tempfile.TemporaryDirectory() as folder:
            def render(item,name):
                p=Path(folder)/'a.wav'; p.write_bytes(b'a'); return p
            _,job=run_job(job,{'Kokoro local':render})
        self.assertIsNone(job['items'][0]['actual_cost_usd'])
        self.assertIsNotNone(job['items'][0]['recorded_usage_cost_usd'])

    def test_user_safe_error_hides_unknown_exception(self):
        self.assertEqual(user_safe_error(RuntimeError('secret upstream body'),'Failed'),'Failed')
        self.assertEqual(user_safe_error(ValueError('Useful message'),'Failed'),'Useful message')


if __name__=='__main__': unittest.main()
