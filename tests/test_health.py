import tempfile,unittest
from pathlib import Path
from peabox_voice_studio.models import Project,ScriptBlock
from peabox_voice_studio.services.health import apply_repairs,check_project,repair_preview
class HealthTests(unittest.TestCase):
 def test_detect_and_repair(self):
  block=ScriptBlock('',text='x',id='same');project=Project('D',blocks=[block,ScriptBlock('B',id='same')]);project.settings['batch_jobs']=[{'project_id':'old','items':[{'status':'weird','file':'missing'}]}];project.settings['audio_clips']=[{'id':'','file':'missing.wav','enabled':True}]
  report=check_project(project);self.assertFalse(report['healthy']);actions=repair_preview(project,report);applied=apply_repairs(project,actions);self.assertTrue(applied);self.assertNotEqual(project.blocks[0].id,project.blocks[1].id);self.assertFalse(project.settings['audio_clips'][0]['enabled']);self.assertEqual(project.settings['batch_jobs'][0]['project_id'],project.id)
 def test_healthy_project(self):self.assertTrue(check_project(Project('D'))['healthy'])
if __name__=='__main__':unittest.main()
