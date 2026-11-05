import unittest
from peabox_voice_studio.services.migrations import CURRENT_PROJECT_SCHEMA, migrate_project_payload, rewrite_import_references

class MigrationTests(unittest.TestCase):
    def test_legacy_payload_migrates(self):
        data,notes=migrate_project_payload({'name':'Old'})
        self.assertEqual(data['settings'],{}); self.assertTrue(notes)

    def test_future_schema_rejected(self):
        with self.assertRaises(ValueError): migrate_project_payload({'schema_version':CURRENT_PROJECT_SCHEMA+1})

    def test_rewrite_paths_and_ids(self):
        data={'settings':{'batch_jobs':[{'project_id':'old','items':[{'file':'x','status':'rendered'}]}],'audio_clips':[{'file':'y'}]}}
        rewrite_import_references(data,'new',False)
        self.assertEqual(data['settings']['batch_jobs'][0]['project_id'],'new')
        self.assertIsNone(data['settings']['batch_jobs'][0]['items'][0]['file'])
        self.assertEqual(data['settings']['audio_clips'][0]['file'],'')

if __name__=='__main__': unittest.main()
