import json,subprocess,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
class VisualPixelCliTests(unittest.TestCase):
 def setup_case(self,d,include_candidate=True,color='white'):
  root=Path(d);base=root/'base';cand=root/'cand';diff=root/'diff';base.mkdir();cand.mkdir();manifest=root/'manifest.json';manifest.write_text(json.dumps({'baseline_hash':'x','viewports':[{'name':'desktop','width':4,'height':3}],'captures':[{'page':'Dashboard','viewport':'desktop','filename':'dashboard_desktop.png'}]}));Image.new('RGB',(4,3),'white').save(base/'dashboard_desktop.png')
  if include_candidate:Image.new('RGB',(4,3),color).save(cand/'dashboard_desktop.png')
  return base,cand,diff,manifest,root/'report.json'
 def run_cli(self,case):
  base,cand,diff,manifest,report=case;return subprocess.run([sys.executable,str(ROOT/'compare_visual_captures.py'),'--baseline',str(base),'--candidate',str(cand),'--manifest',str(manifest),'--diff-dir',str(diff),'--report',str(report)],cwd=ROOT,text=True,capture_output=True)
 def test_cli_success(self):
  with tempfile.TemporaryDirectory() as d:
   case=self.setup_case(d);result=self.run_cli(case);self.assertEqual(result.returncode,0);self.assertTrue(json.loads(case[-1].read_text())['success'])
 def test_cli_pixel_failure(self):
  with tempfile.TemporaryDirectory() as d:
   case=self.setup_case(d,True,'black');result=self.run_cli(case);self.assertEqual(result.returncode,1);self.assertFalse(json.loads(case[-1].read_text())['success'])
 def test_cli_not_ready(self):
  with tempfile.TemporaryDirectory() as d:
   case=self.setup_case(d,False);result=self.run_cli(case);self.assertEqual(result.returncode,2);self.assertEqual(json.loads(case[-1].read_text())['reason'],'capture_set_not_ready')
if __name__=='__main__':unittest.main()
