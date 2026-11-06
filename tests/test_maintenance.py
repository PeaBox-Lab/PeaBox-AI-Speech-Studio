import io,tempfile,unittest,wave
from array import array
from pathlib import Path
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.maintenance import analyze_output_storage,delete_quarantine_batch,list_quarantine_batches,quarantine_files,referenced_output_paths,restore_quarantine_batch,storage_inventory

def wav():
 b=io.BytesIO()
 with wave.open(b,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(array('h',[1]*20).tobytes())
 return b.getvalue()
class MaintenanceTests(unittest.TestCase):
 def test_inventory_and_orphan_analysis(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);out=root/'outputs';out.mkdir();a=out/'used.wav';b=out/'orphan.wav';a.write_bytes(wav());b.write_bytes(wav())
   project=Project('D');project.render_history=[{'output':'used.wav'}]
   analysis=analyze_output_storage([project],out)
   self.assertEqual(analysis['referenced'],1);self.assertEqual(analysis['orphaned'],1);self.assertEqual(analysis['orphaned_files'][0]['name'],'orphan.wav')
   rows=storage_inventory({'Outputs':out});self.assertEqual(rows[0]['Files'],2)
 def test_quarantine_restore_delete(self):
  import peabox_voice_studio.services.maintenance as m
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);out=root/'outputs';q=root/'q';out.mkdir();p=out/'x.wav';p.write_bytes(wav())
   old=m.OUTPUTS_DIR;m.OUTPUTS_DIR=out
   try:
    manifest=quarantine_files([p],q);self.assertFalse(p.exists());batches=list_quarantine_batches(q);self.assertEqual(len(batches),1)
    result=restore_quarantine_batch(Path(batches[0]['path']),q);self.assertEqual(result['restored'],1);self.assertTrue((out/'x.wav').exists())
    p2=out/'y.wav';p2.write_bytes(wav());quarantine_files([p2],q);batch=list_quarantine_batches(q)[0];self.assertTrue(delete_quarantine_batch(Path(batch['path']),q))
   finally:m.OUTPUTS_DIR=old
 def test_rejects_quarantine_outside_output(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'x.wav';p.write_bytes(wav())
   with self.assertRaises(ValueError):quarantine_files([p],Path(folder)/'q')
if __name__=='__main__':unittest.main()
