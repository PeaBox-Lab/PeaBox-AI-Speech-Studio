import unittest
from peabox_voice_studio.facades import batch,timeline,transcription
from peabox_voice_studio.services import batch as batch_service,jobs,timeline as timeline_service,transcripts,diagnostics,bundles
class FacadeParityTests(unittest.TestCase):
 def test_batch_facade_exports_real_services(self):
  self.assertIs(batch.build_manifest,batch_service.build_manifest);self.assertIs(batch.run_job,jobs.run_job);self.assertIs(batch.create_job,jobs.create_job)
 def test_timeline_facade_exports_real_services(self):
  self.assertIs(timeline.add_clip,timeline_service.add_clip);self.assertIs(timeline.mix_timeline,timeline_service.mix_timeline);self.assertIs(timeline.export_timeline_bundle,bundles.export_timeline_bundle)
 def test_transcription_facade_exports_real_services(self):
  self.assertIs(transcription.validate_segments,transcripts.validate_segments);self.assertIs(transcription.export_transcript_bundle,transcripts.export_transcript_bundle);self.assertIs(transcription.transcription_readiness,diagnostics.transcription_readiness)
 def test_facade_exports_are_unique(self):
  for module in (batch,timeline,transcription):self.assertEqual(len(module.__all__),len(set(module.__all__)))
 def test_facade_exports_exist(self):
  for module in (batch,timeline,transcription):
   for name in module.__all__:self.assertTrue(callable(getattr(module,name)),f'{module.__name__}.{name}')
if __name__=='__main__':unittest.main()
