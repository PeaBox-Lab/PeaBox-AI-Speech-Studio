import tempfile,unittest
from pathlib import Path
from peabox_voice_studio.services.operations import operation_log_health,read_operations,record_operation

class OperationTests(unittest.TestCase):
 def test_record_read_health(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'ops.jsonl';record_operation('test',project_id='p',path=path);rows=read_operations(path=path)
   self.assertEqual(rows[0]['action'],'test');self.assertEqual(operation_log_health(path)['entries'],1)
 def test_rotation(self):
  import peabox_voice_studio.services.operations as ops
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'ops.jsonl';path.write_text('x'*100)
   old=ops.MAX_OPERATION_LOG_BYTES;ops.MAX_OPERATION_LOG_BYTES=10
   try:record_operation('rotate',path=path)
   finally:ops.MAX_OPERATION_LOG_BYTES=old
   self.assertTrue(path.with_suffix('.1.jsonl').exists());self.assertEqual(read_operations(path=path)[0]['action'],'rotate')
if __name__=='__main__':unittest.main()
