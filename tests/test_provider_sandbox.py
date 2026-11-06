import sys,unittest
from peabox_voice_studio.providers.sandbox import GoogleVoice,ProviderSandbox,SandboxError,default_sandboxes,run_contract,run_suite
class ProviderSandboxTests(unittest.TestCase):
 def test_default_suite_passes_all_providers(self):
  results=run_suite();self.assertEqual(len(results),4);self.assertTrue(all(x['passed'] for x in results));self.assertEqual({x['provider'] for x in results},{'Azure Speech','Amazon Polly standard','Amazon Polly neural','Google Cloud TTS'})
 def test_azure_discovery_and_ssml_contract(self):
  sandbox=default_sandboxes()['Azure Speech'];voices=sandbox.discover({'key':'not-used','region':'sandbox'});self.assertEqual(voices[0]['provider'],'Azure Speech');result=sandbox.synthesize('Hi [[pause:1]] & bye',voices[0]['id'],voices[0]['language'],1.2);self.assertIn('<break time="1s"/>',result.request['ssml']);self.assertIn('&amp;',result.request['ssml']);self.assertIn("rate='20%'",result.request['ssml'])
 def test_polly_engine_and_normalization(self):
  sandbox=default_sandboxes()['Amazon Polly neural'];voices=sandbox.discover({},'neural');self.assertEqual(voices[0]['provider'],'Amazon Polly neural');result=sandbox.synthesize('Hello',voices[0]['id'],engine='neural');self.assertEqual(result.request['engine'],'neural')
 def test_google_multilanguage_normalization(self):
  sandbox=ProviderSandbox('Google Cloud TTS',[GoogleVoice('multi',['en-US','fr-FR'],'FEMALE')]);voices=sandbox.discover();self.assertEqual([x['language'] for x in voices],['en-US','fr-FR'])
 def test_audio_fixture_is_deterministic(self):
  a=ProviderSandbox('Azure Speech');x=a.synthesize('Hello','Voice').audio;y=ProviderSandbox('Azure Speech').synthesize('Hello','Voice').audio;self.assertEqual(x,y);self.assertTrue(x.startswith(b'ID3SANDBOX'))
 def test_input_validation(self):
  sandbox=ProviderSandbox('Azure Speech')
  with self.assertRaises(ValueError):sandbox.synthesize('','Voice')
  with self.assertRaises(ValueError):sandbox.synthesize('Hello','')
 def test_failure_injection(self):
  discovery=ProviderSandbox('Azure Speech',fail_discovery=True);result=run_contract(discovery);self.assertFalse(result['passed']);self.assertIn('discovery:SandboxError',result['issues'])
  synth=ProviderSandbox('Azure Speech',[{'ShortName':'Voice','Locale':'en-US'}],fail_synthesis=True);result=run_contract(synth);self.assertFalse(result['passed']);self.assertIn('synthesis:SandboxError',result['issues'])
 def test_call_report_contains_no_secret_values(self):
  sandbox=default_sandboxes()['Azure Speech'];sandbox.discover({'key':'actual-secret','region':'sandbox'});report=sandbox.report();payload=report['last_call']['payload'];self.assertEqual(payload['profile_fields'],['key','region']);self.assertNotIn('actual-secret',str(payload))
 def test_sandbox_does_not_import_network_clients(self):
  before=set(sys.modules);run_suite();new=set(sys.modules)-before;self.assertNotIn('boto3',new);self.assertNotIn('requests',new);self.assertFalse(any(x.startswith('google.cloud') for x in new))
 def test_report_counts_calls(self):
  sandbox=default_sandboxes()['Azure Speech'];sandbox.discover();sandbox.synthesize('Hello','Voice');report=sandbox.report();self.assertEqual(report['calls'],2);self.assertEqual(report['discovery_calls'],1);self.assertEqual(report['synthesis_calls'],1)
if __name__=='__main__':unittest.main()
