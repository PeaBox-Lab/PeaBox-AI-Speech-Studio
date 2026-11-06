import json,tempfile,unittest,zipfile
from io import BytesIO
from pathlib import Path
from PIL import Image
from peabox_voice_studio.services.visual_pixels import capture_inventory,compare_capture_set,compare_png,diff_bundle,manifest_index,validate_png,write_report
class VisualPixelTests(unittest.TestCase):
 def image(self,path,color,size=(10,8)):
  Image.new('RGB',size,color).save(path,'PNG');return path
 def manifest(self):return {'baseline_hash':'abc','viewports':[{'name':'desktop','width':10,'height':8}],'captures':[{'page':'Dashboard','viewport':'desktop','filename':'dashboard_desktop.png'}]}
 def test_validate_png_and_dimensions(self):
  with tempfile.TemporaryDirectory() as d:
   path=self.image(Path(d)/'a.png','white');valid=validate_png(path,(10,8));self.assertTrue(valid['valid']);self.assertEqual((valid['width'],valid['height']),(10,8));bad=validate_png(path,(9,8));self.assertFalse(bad['valid']);self.assertIn('dimensions:',bad['issues'][0])
 def test_validate_missing_and_non_png(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.assertEqual(validate_png(root/'missing.png')['issues'],['missing']);fake=root/'fake.png';fake.write_text('not png');self.assertEqual(validate_png(fake)['issues'],['not_png'])
 def test_manifest_index_adds_dimensions(self):self.assertEqual(manifest_index(self.manifest())['dashboard_desktop.png']['expected_size'],(10,8))
 def test_inventory_ready_missing_invalid_and_extra(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);inv=capture_inventory(root,self.manifest());self.assertFalse(inv['ready']);self.assertEqual(inv['missing'],['dashboard_desktop.png']);self.image(root/'dashboard_desktop.png','white');self.image(root/'extra.png','black');inv=capture_inventory(root,self.manifest());self.assertFalse(inv['ready']);self.assertEqual(inv['extras'],['extra.png']);(root/'extra.png').unlink();self.assertTrue(capture_inventory(root,self.manifest())['ready'])
 def test_identical_images_pass(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);a=self.image(root/'a.png','white');b=self.image(root/'b.png','white');result=compare_png(a,b);self.assertTrue(result['passed']);self.assertEqual(result['changed_pixels'],0);self.assertEqual(result['changed_percent'],0)
 def test_pixel_change_fails_and_writes_diff(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);a=self.image(root/'a.png','white');b=self.image(root/'b.png','white');img=Image.open(b);img.putpixel((0,0),(0,0,0));img.save(b);diff=root/'diff.png';result=compare_png(a,b,0,0,diff);self.assertFalse(result['passed']);self.assertEqual(result['changed_pixels'],1);self.assertTrue(diff.exists())
 def test_threshold_and_allowed_percent(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);a=self.image(root/'a.png',(100,100,100));b=self.image(root/'b.png',(105,105,105));self.assertTrue(compare_png(a,b,5,0)['passed']);self.assertFalse(compare_png(a,b,4,0)['passed']);self.assertTrue(compare_png(a,b,4,100)['passed'])
 def test_dimension_mismatch_fails(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);a=self.image(root/'a.png','white',(10,8));b=self.image(root/'b.png','white',(9,8));self.assertEqual(compare_png(a,b)['reason'],'dimension_mismatch')
 def test_capture_set_and_bundle(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);base=root/'base';cand=root/'cand';diff=root/'diff';base.mkdir();cand.mkdir();self.image(base/'dashboard_desktop.png','white');self.image(cand/'dashboard_desktop.png','black');report=compare_capture_set(base,cand,self.manifest(),0,0,diff);self.assertEqual(report['failed'],1);self.assertFalse(report['success']);bundle=zipfile.ZipFile(BytesIO(diff_bundle(report)));self.assertIn('pixel_diff_report.json',bundle.namelist());self.assertIn('diffs/dashboard_desktop.png',bundle.namelist())
 def test_invalid_capture_set_report(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);base=root/'base';cand=root/'cand';base.mkdir();cand.mkdir();self.image(base/'dashboard_desktop.png','white');report=compare_capture_set(base,cand,self.manifest());self.assertFalse(report['success']);self.assertEqual(report['results'][0]['reason'],'invalid_capture')
 def test_report_round_trip(self):
  with tempfile.TemporaryDirectory() as d:
   path=write_report({'success':True},Path(d)/'report.json');self.assertEqual(json.loads(path.read_text()),{'success':True})
if __name__=='__main__':unittest.main()
