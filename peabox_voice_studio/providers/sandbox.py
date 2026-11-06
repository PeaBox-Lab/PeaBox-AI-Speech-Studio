import hashlib,html,json
from dataclasses import dataclass,field
from peabox_voice_studio.providers.cloud import normalize_azure_voices,normalize_google_voices,normalize_polly_voices
from peabox_voice_studio.services.quality import compile_ssml_text
class SandboxError(RuntimeError):pass
@dataclass
class SandboxResponse:
 audio:bytes
 request:dict
@dataclass
class ProviderSandbox:
 provider:str
 voices:list=field(default_factory=list)
 fail_discovery:bool=False
 fail_synthesis:bool=False
 latency_ms:int=0
 calls:list=field(default_factory=list)
 def _record(self,operation,payload):
  row={'provider':self.provider,'operation':operation,'payload':payload,'sequence':len(self.calls)+1};self.calls.append(row);return row
 def discover(self,profile=None,engine='standard',language=''):
  profile=profile or {};self._record('discover',{'profile_fields':sorted(profile),'engine':engine,'language':language})
  if self.fail_discovery:raise SandboxError(f'{self.provider} sandbox discovery failure')
  if self.provider=='Azure Speech':return normalize_azure_voices(self.voices)
  if self.provider.startswith('Amazon Polly'):return normalize_polly_voices(self.voices,engine)
  if self.provider=='Google Cloud TTS':return normalize_google_voices(self.voices)
  raise ValueError('Unsupported sandbox provider')
 def synthesize(self,text,voice,language='',speed=1.0,engine='standard',output_format='mp3'):
  if not text.strip():raise ValueError('Text is required')
  if not voice.strip():raise ValueError('Voice is required')
  ssml=self._ssml(text,voice,language,speed);request={'voice':voice,'language':language,'speed':speed,'engine':engine,'output_format':output_format,'ssml':ssml};self._record('synthesize',request)
  if self.fail_synthesis:raise SandboxError(f'{self.provider} sandbox synthesis failure')
  token=json.dumps({'provider':self.provider,**request},sort_keys=True).encode();audio=b'ID3SANDBOX'+hashlib.sha256(token).digest()+token[:96];return SandboxResponse(audio,request)
 def _ssml(self,text,voice,language,speed):
  prepared=compile_ssml_text(text)
  if self.provider=='Azure Speech':rate=round((speed-1)*100);return "<speak version='1.0' xml:lang='en-US'>"+f"<voice name='{html.escape(voice,quote=True)}'><prosody rate='{rate}%'>{prepared}</prosody></voice></speak>"
  return f'<speak>{prepared}</speak>'
 def report(self):return {'provider':self.provider,'calls':len(self.calls),'discovery_calls':sum(x['operation']=='discover' for x in self.calls),'synthesis_calls':sum(x['operation']=='synthesize' for x in self.calls),'last_call':self.calls[-1] if self.calls else None}
class _Gender:
 def __init__(self,name):self.name=name
class GoogleVoice:
 def __init__(self,name,languages,gender='NEUTRAL'):self.name=name;self.language_codes=languages;self.ssml_gender=_Gender(gender)
def default_sandboxes():
 return {
  'Azure Speech':ProviderSandbox('Azure Speech',[{'ShortName':'en-US-AvaNeural','DisplayName':'Ava','Locale':'en-US','Gender':'Female','StyleList':['chat']},{'ShortName':'hi-IN-SwaraNeural','DisplayName':'Swara','Locale':'hi-IN','Gender':'Female'}]),
  'Amazon Polly standard':ProviderSandbox('Amazon Polly standard',[{'Id':'Joanna','Name':'Joanna','LanguageCode':'en-US','Gender':'Female'},{'Id':'Aditi','Name':'Aditi','LanguageCode':'en-IN','Gender':'Female'}]),
  'Amazon Polly neural':ProviderSandbox('Amazon Polly neural',[{'Id':'Matthew','Name':'Matthew','LanguageCode':'en-US','Gender':'Male'}]),
  'Google Cloud TTS':ProviderSandbox('Google Cloud TTS',[GoogleVoice('en-US-Neural2-F',['en-US'],'FEMALE'),GoogleVoice('hi-IN-Wavenet-A',['hi-IN'],'FEMALE')]),
 }
def run_contract(sandbox):
 issues=[]
 try:voices=sandbox.discover({'sandbox':True},'neural' if 'neural' in sandbox.provider else 'standard')
 except Exception as exc:return {'provider':sandbox.provider,'passed':False,'issues':[f'discovery:{type(exc).__name__}'],'voices':0,'audio_bytes':0,'report':sandbox.report()}
 if not voices:issues.append('empty_catalog')
 for voice in voices:
  missing=[key for key in ('provider','id','name','language','gender','styles') if key not in voice]
  if missing:issues.append('voice_fields:'+','.join(missing));break
 try:result=sandbox.synthesize('Hello [[pause:1]] & welcome',voices[0]['id'],voices[0]['language'],1.1,'neural' if 'neural' in sandbox.provider else 'standard')
 except Exception as exc:issues.append(f'synthesis:{type(exc).__name__}');result=None
 if result and '<break time="1s"/>' not in result.request['ssml']:issues.append('pause_not_compiled')
 if result and '&amp;' not in result.request['ssml']:issues.append('text_not_escaped')
 if result and not result.audio.startswith(b'ID3SANDBOX'):issues.append('invalid_audio_fixture')
 return {'provider':sandbox.provider,'passed':not issues,'issues':issues,'voices':len(voices),'audio_bytes':len(result.audio) if result else 0,'report':sandbox.report()}
def run_suite(sandboxes=None):return [run_contract(x) for x in (sandboxes or default_sandboxes()).values()]
