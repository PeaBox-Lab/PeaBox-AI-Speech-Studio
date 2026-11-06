import json,os,tempfile,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from peabox_voice_studio.services.maintenance import apply_retention,complete,create,load,pause,retention_preview,save,status
class MaintenanceTests(unittest.TestCase):
 def test_create_due_complete_and_history(self):
  base=datetime(2026,1,1,tzinfo=timezone.utc);plan=create('Weekly','Weekly',['Review']);plan['next_due_at']=base.isoformat();self.assertEqual(status(plan,base),'Due');self.assertEqual(status(plan,base+timedelta(seconds=1)),'Overdue');complete(plan,{'Review':'Complete'},'ok',base);self.assertEqual(len(plan['history']),1);self.assertEqual(plan['next_due_at'],(base+timedelta(days=7)).isoformat())
 def test_pause_and_resume(self):
  plan=create('Plan');due=plan['next_due_at'];pause(plan,True);self.assertEqual(status(plan,due),'Paused');pause(plan,False);self.assertEqual(status(plan,due),'Due')
 def test_save_and_load_round_trip(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'plans.json';plans=[create('Monthly','Monthly')];save(plans,path);self.assertEqual(load(path)[0]['name'],'Monthly')
 def test_retention_preview_keeps_latest_backups(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);b=root/'backups';q=root/'q';s=root/'support';b.mkdir();q.mkdir();s.mkdir();point=datetime(2026,2,1,tzinfo=timezone.utc)
   for i in range(4):
    p=b/f'{i}.db';p.write_bytes(bytes([i]));stamp=(point-timedelta(days=i)).timestamp();os.utime(p,(stamp,stamp))
   preview=retention_preview({'keep_backups':2},point,b,q,s);self.assertEqual({x['name'] for x in preview['candidates']},{'2.db','3.db'});self.assertTrue(all(p.exists() for p in b.glob('*.db')))
 def test_retention_includes_old_restored_records_and_support(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);b=root/'b';q=root/'q';s=root/'s';b.mkdir();q.mkdir();s.mkdir();point=datetime(2026,3,1,tzinfo=timezone.utc);meta=q/'done.json';meta.write_text(json.dumps({'restored_at':'yes'}));artifact=s/'support.zip';artifact.write_bytes(b'x');old=(point-timedelta(days=40)).timestamp();os.utime(meta,(old,old));os.utime(artifact,(old,old));preview=retention_preview({'restored_quarantine_days':30,'support_days':14},point,b,q,s);self.assertEqual({x['kind'] for x in preview['candidates']},{'quarantine-record','support-artifact'})
 def test_apply_removes_exact_candidates_only(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);b=root/'b';q=root/'q';s=root/'s';b.mkdir();q.mkdir();s.mkdir();remove=b/'remove.db';keep=b/'keep.db';remove.write_bytes(b'x');keep.write_bytes(b'y');preview={'candidates':[{'kind':'backup','path':str(remove.resolve()),'name':remove.name,'bytes':1}]};result=apply_retention(preview,b,q,s);self.assertFalse(remove.exists());self.assertTrue(keep.exists());self.assertEqual(result['files'],1)
 def test_apply_skips_outside_roots(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);b=root/'b';q=root/'q';s=root/'s';b.mkdir();q.mkdir();s.mkdir();outside=root/'project.json';outside.write_text('important');preview={'candidates':[{'kind':'backup','path':str(outside.resolve()),'name':outside.name,'bytes':9}]};result=apply_retention(preview,b,q,s);self.assertTrue(outside.exists());self.assertEqual(result['files'],0);self.assertEqual(len(result['skipped']),1)
if __name__=='__main__':unittest.main()
