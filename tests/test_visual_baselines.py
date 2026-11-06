import json,tempfile,unittest
from pathlib import Path
from peabox_voice_studio.services.visual_baselines import baseline_document,collect_screen_snapshots,compare_baselines,contrast_ratio,navigation_snapshot,read_baseline,screen_source_snapshot,screenshot_manifest,stable_hash,theme_snapshot,validate_baseline,validate_theme,write_baseline
ROOT=Path(__file__).resolve().parents[1]
class VisualBaselineTests(unittest.TestCase):
 def setUp(self):self.ui=(ROOT/'peabox_voice_studio/ui.py').read_text();self.screens=collect_screen_snapshots(ROOT/'peabox_voice_studio/screens');self.doc=baseline_document(self.ui,self.screens)
 def test_navigation_snapshot_has_all_pages_once(self):
  snap=navigation_snapshot(self.ui);pages=[x['page'] for g in snap['groups'] for x in g['pages']];self.assertEqual(len(pages),19);self.assertEqual(len(set(pages)),19);self.assertEqual(set(pages),set(snap['page_meta']))
 def test_theme_contract_has_required_tokens_components_and_breakpoint(self):self.assertEqual(validate_theme(theme_snapshot(self.ui)),[])
 def test_contrast_meets_wcag_normal_text(self):self.assertGreaterEqual(contrast_ratio('#ffffff','#203b64'),4.5);self.assertGreaterEqual(contrast_ratio('#172033','#ffffff'),4.5)
 def test_screen_snapshots_cover_all_modules(self):self.assertEqual(len(self.screens),19);self.assertTrue(all(x['source_hash'] and x['lines']>0 for x in self.screens.values()))
 def test_baseline_is_deterministic(self):self.assertEqual(self.doc['hash'],baseline_document(self.ui,self.screens)['hash']);self.assertEqual(self.doc['hash'],stable_hash({k:v for k,v in self.doc.items() if k!='hash'}))
 def test_baseline_validates(self):self.assertEqual(validate_baseline(self.doc),[])
 def test_baseline_round_trip(self):
  with tempfile.TemporaryDirectory() as d:
   path=write_baseline(self.doc,Path(d)/'baseline.json');self.assertEqual(read_baseline(path),self.doc)
 def test_comparison_detects_navigation_theme_and_screen_changes(self):
  changed=json.loads(json.dumps(self.doc));changed['navigation']['groups'][0]['group']='Changed';changed['theme']['tokens']['--pb-blue']='#000';page=next(iter(changed['screens']));changed['screens'][page]['lines']+=1;changed['hash']='changed';result=compare_baselines(self.doc,changed);self.assertFalse(result['matches']);self.assertIn('navigation',result['changes']);self.assertIn('theme',result['changes']);self.assertIn(f'screen:{page}',result['changes'])
 def test_screenshot_manifest_has_three_viewports_per_page(self):
  manifest=screenshot_manifest(self.doc);self.assertEqual([x['name'] for x in manifest['viewports']],['desktop','tablet','mobile']);self.assertEqual(len(manifest['captures']),57);self.assertEqual(len({x['filename'] for x in manifest['captures']}),57)
 def test_checked_in_baseline_matches_generated(self):
  checked=json.loads((ROOT/'visual_baselines/ui_baseline_0.11.2.json').read_text());self.assertEqual(compare_baselines(checked,self.doc)['matches'],True)
 def test_checked_in_manifest_matches_hash(self):
  manifest=json.loads((ROOT/'visual_baselines/screenshot_manifest.json').read_text());self.assertEqual(manifest['baseline_hash'],self.doc['hash']);self.assertEqual(len(manifest['captures']),57)
if __name__=='__main__':unittest.main()
