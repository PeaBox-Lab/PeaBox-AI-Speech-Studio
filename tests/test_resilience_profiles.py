import tempfile,unittest
from pathlib import Path
from peabox_voice_studio.services.resilience_profiles import active_profile,audit_log,clone_profile,create_profile,delete_draft,instantiate,list_profiles,profile_diff,transition,update_profile,validate_settings
from peabox_voice_studio.services.storage_backends import MemoryBackend
class ResilienceProfileTests(unittest.TestCase):
 def paths(self,d):return Path(d)/'profiles.json',Path(d)/'lock'
 def settings(self,attempts=3):return {'attempts':attempts,'delay_seconds':.1,'backoff':2,'timeout_seconds':5,'failure_threshold':3,'recovery_seconds':30}
 def approve(self,pid,path,lock):transition(pid,'In Review','creator',path=path,lock_path=lock);return transition(pid,'Approved','reviewer',path=path,lock_path=lock)
 def test_create_persists_secret_free_draft(self):
  with tempfile.TemporaryDirectory() as d:
   path,lock=self.paths(d);p=create_profile('Standard','local',self.settings(),'creator','desc',path,lock);self.assertEqual(p['status'],'Draft');self.assertNotIn('credential',str(p).lower());self.assertEqual(list_profiles(path)[0]['id'],p['id'])
 def test_settings_validation_bounds(self):
  bad=[{'attempts':0},{'delay_seconds':-1},{'backoff':.5},{'timeout_seconds':0},{'failure_threshold':0},{'recovery_seconds':0}]
  for value in bad:
   with self.assertRaises(ValueError):validate_settings(value)
 def test_edit_only_draft_or_changes_requested(self):
  with tempfile.TemporaryDirectory() as d:
   path,lock=self.paths(d);p=create_profile('P','local',self.settings(),'creator',path=path,lock_path=lock);updated=update_profile(p['id'],self.settings(4),'creator',path=path,lock_path=lock);self.assertEqual(updated['settings']['attempts'],4);transition(p['id'],'In Review','creator',path=path,lock_path=lock)
   with self.assertRaises(ValueError):update_profile(p['id'],self.settings(5),'creator',path=path,lock_path=lock)
 def test_reviewer_must_differ_from_creator(self):
  with tempfile.TemporaryDirectory() as d:
   path,lock=self.paths(d);p=create_profile('P','local',self.settings(),'same',path=path,lock_path=lock);transition(p['id'],'In Review','same',path=path,lock_path=lock)
   with self.assertRaises(ValueError):transition(p['id'],'Approved','same',path=path,lock_path=lock)
 def test_approval_activation_and_single_active(self):
  with tempfile.TemporaryDirectory() as d:
   path,lock=self.paths(d);a=create_profile('A','local',self.settings(),'creator',path=path,lock_path=lock);b=create_profile('B','local',self.settings(4),'creator',path=path,lock_path=lock)
   for p in (a,b):self.approve(p['id'],path,lock)
   transition(a['id'],'Active','operator',path=path,lock_path=lock);transition(b['id'],'Active','operator',path=path,lock_path=lock);profiles={x['id']:x for x in list_profiles(path)};self.assertEqual(profiles[a['id']]['status'],'Approved');self.assertEqual(profiles[b['id']]['status'],'Active');self.assertEqual(active_profile('local',path)['id'],b['id'])
 def test_changes_requested_round_trip(self):
  with tempfile.TemporaryDirectory() as d:
   path,lock=self.paths(d);p=create_profile('P','local',self.settings(),'creator',path=path,lock_path=lock);transition(p['id'],'In Review','creator',path=path,lock_path=lock);changed=transition(p['id'],'Changes Requested','reviewer','raise timeout',path,lock);self.assertEqual(changed['status'],'Changes Requested');draft=transition(p['id'],'Draft','creator',path=path,lock_path=lock);self.assertEqual(draft['status'],'Draft')
 def test_clone_and_draft_delete(self):
  with tempfile.TemporaryDirectory() as d:
   path,lock=self.paths(d);p=create_profile('P','memory',self.settings(),'creator',path=path,lock_path=lock);clone=clone_profile(p['id'],'Clone','actor',path,lock);self.assertNotEqual(clone['id'],p['id']);self.assertTrue(delete_draft(clone['id'],'actor',path,lock));self.assertEqual(len(list_profiles(path)),1)
 def test_non_draft_delete_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   path,lock=self.paths(d);p=create_profile('P','local',self.settings(),'creator',path=path,lock_path=lock);transition(p['id'],'In Review','creator',path=path,lock_path=lock)
   with self.assertRaises(ValueError):delete_draft(p['id'],'actor',path,lock)
 def test_diff_identifies_changes(self):
  a={'settings':self.settings(3)};b={'settings':self.settings(5)};rows=profile_diff(a,b);self.assertTrue(next(x for x in rows if x['setting']=='attempts')['changed'])
 def test_audit_captures_actions(self):
  with tempfile.TemporaryDirectory() as d:
   path,lock=self.paths(d);p=create_profile('P','local',self.settings(),'creator',path=path,lock_path=lock);update_profile(p['id'],self.settings(4),'creator',path=path,lock_path=lock);actions=[x['action'] for x in audit_log(path)];self.assertEqual(actions,['profile.created','profile.updated'])
 def test_instantiate_requires_active_profile(self):
  with tempfile.TemporaryDirectory() as d:
   path,lock=self.paths(d);p=create_profile('P','memory',self.settings(),'creator',path=path,lock_path=lock)
   with self.assertRaises(ValueError):instantiate(p,MemoryBackend())
   self.approve(p['id'],path,lock);active=transition(p['id'],'Active','operator',path=path,lock_path=lock);wrapped=instantiate(active,MemoryBackend());self.assertEqual(wrapped.retry_policy.attempts,3);self.assertTrue(wrapped.health()['healthy'])
if __name__=='__main__':unittest.main()
