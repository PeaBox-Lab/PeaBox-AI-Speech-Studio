import unittest
from peabox_voice_studio.services.migrations import CURRENT_PROJECT_SCHEMA,migrate_project_payload,rewrite_import_references
class MigrationMatrixTests(unittest.TestCase):
 def test_schema_one_minimal_fixture(self):
  data,notes=migrate_project_payload({'id':'a','name':'Legacy'});self.assertEqual(data['settings'],{});self.assertEqual(data['blocks'],[]);self.assertTrue(notes)
 def test_schema_two_fixture_is_stable(self):
  payload={'schema_version':2,'id':'a','name':'Current','settings':{},'blocks':[],'render_history':[]};data,notes=migrate_project_payload(payload);self.assertEqual(data['name'],'Current');self.assertEqual(notes,[])
 def test_future_schema_is_rejected(self):
  with self.assertRaises(ValueError):migrate_project_payload({'schema_version':CURRENT_PROJECT_SCHEMA+1})
 def test_import_rewrites_nested_job_and_paths(self):
  data={'settings':{'batch_jobs':[{'project_id':'old','items':[{'file':'C:/old.wav','status':'rendered'}]}],'audio_clips':[{'file':'C:/clip.wav'}]}};notes=rewrite_import_references(data,'new');job=data['settings']['batch_jobs'][0];self.assertEqual(job['project_id'],'new');self.assertIsNone(job['items'][0]['file']);self.assertEqual(job['items'][0]['status'],'failed');self.assertEqual(data['settings']['audio_clips'][0]['file'],'');self.assertTrue(notes)
 def test_preserve_asset_paths_mode(self):
  data={'settings':{'batch_jobs':[{'project_id':'old','items':[{'file':'x.wav','status':'rendered'}]}],'audio_clips':[{'file':'y.wav'}]}};rewrite_import_references(data,'new',True);self.assertEqual(data['settings']['batch_jobs'][0]['items'][0]['file'],'x.wav');self.assertEqual(data['settings']['audio_clips'][0]['file'],'y.wav')
if __name__=='__main__':unittest.main()
