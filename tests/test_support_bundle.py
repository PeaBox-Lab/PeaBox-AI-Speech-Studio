import io,json,unittest,zipfile
from peabox_voice_studio.services.support import create_support_bundle
class SupportBundleTests(unittest.TestCase):
 def test_bundle_contains_sanitized_operational_files(self):
  raw=create_support_bundle({'ready':True},[{'Area':'Data'}],[{'action':'x'}],[{'Check':'Python'}],'0.08.1',{'name':'Demo'})
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   self.assertEqual(set(z.namelist()),{'support_manifest.json','repository_health.json','storage_inventory.json','system_diagnostics.json','operations.json'})
   manifest=json.loads(z.read('support_manifest.json'));self.assertEqual(manifest['application_version'],'0.08.1')
  self.assertNotIn(b'api_key',raw);self.assertNotIn(b'secret_key',raw)
if __name__=='__main__':unittest.main()
