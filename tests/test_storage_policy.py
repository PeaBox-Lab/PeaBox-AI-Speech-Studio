import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from peabox_voice_studio.services.files import atomic_write_bytes
from peabox_voice_studio.services.storage_policy import active_reservations,capacity,category_for,ensure_capacity,load_policy,policy_status,release_reservation,reserve,save_policy,usage
class StoragePolicyTests(unittest.TestCase):
 def roots(self,root):
  return {'outputs':(root/'outputs',),'models':(root/'models',),'recovery':(root/'backups',root/'quarantine',root/'support'),'worker':(root/'worker',)}
 def policy(self,limit=100,enabled=True):return {'enabled':enabled,'warning_percent':80,'categories':{'outputs':limit,'models':limit,'recovery':limit,'worker':limit}}
 def test_policy_round_trip_and_normalization(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'policy.json';saved=save_policy({'enabled':True,'warning_percent':200,'categories':{'outputs':123}},path);loaded=load_policy(path);self.assertEqual(saved,loaded);self.assertEqual(loaded['warning_percent'],99);self.assertEqual(loaded['categories']['outputs'],123)
 def test_category_mapping_and_usage(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);roots=self.roots(root);p=root/'outputs'/'a.wav';p.parent.mkdir();p.write_bytes(b'123');self.assertEqual(category_for(p,roots),'outputs');self.assertEqual(usage('outputs',roots),{'bytes':3,'files':1})
 def test_warning_and_blocked_status(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);roots=self.roots(root);p=root/'outputs'/'a';p.parent.mkdir();p.write_bytes(b'x'*80);state=capacity('outputs',self.policy(),roots,root/'r.json');self.assertTrue(state['warning']);self.assertFalse(state['blocked']);p.write_bytes(b'x'*100);self.assertTrue(capacity('outputs',self.policy(),roots,root/'r.json')['blocked'])
 def test_ensure_capacity_uses_overwrite_delta(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);roots=self.roots(root);p=root/'outputs'/'a';p.parent.mkdir();p.write_bytes(b'x'*90);state=ensure_capacity(p,95,self.policy(),roots,root/'r.json');self.assertEqual(state['needed'],5)
   with self.assertRaises(OSError):ensure_capacity(p,101,self.policy(),roots,root/'r.json')
 def test_disabled_policy_allows_write(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);p=root/'outputs'/'a';self.assertTrue(ensure_capacity(p,1000,self.policy(1,False),self.roots(root),root/'r.json')['allowed'])
 def test_reservation_reduces_remaining_and_releases(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);roots=self.roots(root);[x.mkdir(parents=True,exist_ok=True) for values in roots.values() for x in values];rp=root/'reservations.json';lock=root/'lock';row=reserve('outputs',40,'test',self.policy(),roots,rp,lock);self.assertEqual(capacity('outputs',self.policy(),roots,rp)['remaining'],60);self.assertEqual(active_reservations(path=rp)[0]['id'],row['id']);self.assertTrue(release_reservation(row['id'],rp,lock));self.assertEqual(capacity('outputs',self.policy(),roots,rp)['remaining'],100)
 def test_reservation_cannot_overbook(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);roots=self.roots(root);[x.mkdir(parents=True,exist_ok=True) for values in roots.values() for x in values];rp=root/'r.json';lock=root/'lock';reserve('outputs',70,'first',self.policy(),roots,rp,lock)
   with self.assertRaises(OSError):reserve('outputs',31,'second',self.policy(),roots,rp,lock)
 def test_atomic_write_invokes_quota_preflight(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'a.bin'
   with patch('peabox_voice_studio.services.storage_policy.ensure_capacity') as check:atomic_write_bytes(path,b'abc');check.assert_called_once_with(path,3)
 def test_status_covers_all_categories(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);roots=self.roots(root);[x.mkdir(parents=True,exist_ok=True) for values in roots.values() for x in values];self.assertEqual({x['category'] for x in policy_status(self.policy(),roots,root/'r.json')},{'outputs','models','recovery','worker'})
if __name__=='__main__':unittest.main()
