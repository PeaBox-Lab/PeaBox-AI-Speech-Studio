import streamlit as st
from pathlib import Path
import tempfile, os, time, re, json, html
BASE=Path(__file__).parent; OUT=BASE/'outputs'; MODEL=BASE/'models'; OUT.mkdir(exist_ok=True); MODEL.mkdir(exist_ok=True)
st.set_page_config(page_title='PeaBox Voice Studio 2',page_icon='🎙️',layout='wide')
st.title('🎙️ PeaBox Voice Studio 2')
def safe(s): return re.sub(r'[^A-Za-z0-9_.-]','_',s)[:60] or 'audio'
def tmp(raw,suffix):
 fd,n=tempfile.mkstemp(suffix=suffix); os.close(fd); p=Path(n); p.write_bytes(raw); return p
def cleanup(p):
 for _ in range(10):
  try: p.unlink(missing_ok=True); return
  except PermissionError: time.sleep(.3)
def transcribe(raw,name,size,lang):
 from faster_whisper import WhisperModel
 p=tmp(raw,Path(name).suffix or '.wav')
 try:
  seg,info=WhisperModel(size,device='cpu',compute_type='int8').transcribe(str(p),language=None if lang=='Auto' else lang,vad_filter=True,beam_size=5)
  return [{'start':s.start,'end':s.end,'text':s.text.strip()} for s in seg],info.language
 finally: cleanup(p)
def kokoro(text,voice,lang,speed,name):
 import requests, soundfile as sf
 from kokoro_onnx import Kokoro
 mp=MODEL/'kokoro-v1.0.int8.onnx'; vp=MODEL/'voices-v1.0.bin'
 for p,u in [(mp,'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx'),(vp,'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin')]:
  if not p.exists():
   r=requests.get(u,timeout=180); r.raise_for_status(); p.write_bytes(r.content)
 samples,sr=Kokoro(str(mp),str(vp)).create(text,voice=voice,speed=speed,lang=lang); out=OUT/(safe(name)+'.wav'); sf.write(out,samples,sr); return out
def azure_list(key,region):
 import requests
 r=requests.get(f'https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list',headers={'Ocp-Apim-Subscription-Key':key},timeout=30);r.raise_for_status();return r.json()
def azure_tts(text,key,region,voice,rate,pitch):
 import requests
 ss=f"<speak version='1.0' xml:lang='en-US'><voice name='{voice}'><prosody rate='{rate}%' pitch='{pitch}%'>{html.escape(text)}</prosody></voice></speak>"
 h={'Ocp-Apim-Subscription-Key':key,'Content-Type':'application/ssml+xml','X-Microsoft-OutputFormat':'audio-24khz-48kbitrate-mono-mp3'}
 r=requests.post(f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1',headers=h,data=ss.encode(),timeout=180);r.raise_for_status();return r.content
def aws_client(a,s,r,t=''):
 import boto3
 return boto3.client('polly',region_name=r,aws_access_key_id=a,aws_secret_access_key=s,aws_session_token=t or None)
def google_client(raw):
 from google.oauth2 import service_account
 from google.cloud import texttospeech
 c=service_account.Credentials.from_service_account_info(json.loads(raw),scopes=['https://www.googleapis.com/auth/cloud-platform']);return texttospeech.TextToSpeechClient(credentials=c)
def save(data,name,ext='mp3'): p=OUT/f'{safe(name)}.{ext}';p.write_bytes(data);return p
voices={'US English':['af_heart','af_bella','af_sarah','am_adam','am_michael'],'UK English':['bf_emma','bf_isabella','bm_george'],'Hindi':['hf_alpha','hf_beta','hm_omega','hm_psi'],'Spanish':['ef_dora','em_alex'],'French':['ff_siwis'],'Italian':['if_sara','im_nicola'],'Portuguese':['pf_dora','pm_alex'],'Japanese':['jf_alpha','jm_kumo'],'Chinese':['zf_xiaobei','zm_yunxi']}
langs={'US English':'en-us','UK English':'en-gb','Hindi':'hi','Spanish':'es','French':'fr-fr','Italian':'it','Portuguese':'pt-br','Japanese':'ja','Chinese':'cmn'}
pages=st.sidebar.radio('Workspace',['Create Speech','Transcription','Cost Guide','Help'])
if pages=='Create Speech':
 text=st.text_area('Text',height=260); name=st.text_input('Output name','narration'); chars=len(text); provider=st.selectbox('Provider',['Kokoro local','Azure Speech','Amazon Polly','Google Cloud TTS'])
 if provider=='Kokoro local':
  st.info('Free local neural TTS. First generation downloads model files. Python 3.11/3.12 recommended.')
  a,b,c=st.columns(3); language=a.selectbox('Language',voices); voice=b.selectbox('Voice',voices[language]); speed=c.slider('Speed',.6,1.6,1.0,.05)
  if st.button('Generate',type='primary',disabled=not text):
   try:
    with st.spinner('Generating...'): p=kokoro(text,voice,langs[language],speed,name)
    st.audio(str(p));st.download_button('Download WAV',p.read_bytes(),p.name)
   except Exception as e: st.exception(e)
 elif provider=='Azure Speech':
  st.markdown('[Create Speech resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices) · [Setup guide](https://learn.microsoft.com/azure/ai-services/speech-service/get-started-text-to-speech)')
  key=st.text_input('API key',type='password'); region=st.text_input('Region','centralindia');a,b=st.columns(2);rate=a.slider('Rate %',-50,100,0);pitch=b.slider('Pitch %',-50,50,0)
  if st.button('Discover voices',disabled=not key):
   try: st.session_state.av=azure_list(key,region)
   except Exception as e: st.exception(e)
  av=st.session_state.get('av',[]);loc=st.selectbox('Locale',['All']+sorted({v['Locale'] for v in av}));fv=[v for v in av if loc=='All' or v['Locale']==loc];v=st.selectbox('Voice',fv,format_func=lambda x:f"{x['DisplayName']} | {x['Locale']} | {x['ShortName']}") if fv else None
  st.caption(f'Indicative neural cost: ${chars/1e6*15:.4f} at $15 per 1M characters.')
  if st.button('Generate Azure',type='primary',disabled=not(text and key and v)):
   try:d=azure_tts(text,key,region,v['ShortName'],rate,pitch);p=save(d,name);st.audio(d);st.download_button('Download MP3',d,p.name)
   except Exception as e:st.exception(e)
 elif provider=='Amazon Polly':
  st.markdown('[AWS account](https://aws.amazon.com/free/) · [Create access key](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) · [Polly console](https://console.aws.amazon.com/polly/)')
  a=st.text_input('Access key ID');s=st.text_input('Secret access key',type='password');token=st.text_input('Session token, optional',type='password');region=st.text_input('Region','ap-south-1');engine=st.selectbox('Engine',['standard','neural','generative','long-form']);rates={'standard':4,'neural':16,'generative':30,'long-form':100}
  if st.button('Discover voices',disabled=not(a and s)):
   try:st.session_state.pv=aws_client(a,s,region,token).describe_voices(Engine=engine,IncludeAdditionalLanguageCodes=True)['Voices']
   except Exception as e:st.exception(e)
  pv=st.session_state.get('pv',[]);v=st.selectbox('Voice',pv,format_func=lambda x:f"{x['Name']} | {x['LanguageCode']} | {x['Id']}") if pv else None
  st.caption(f"Indicative cost: ${chars/1e6*rates[engine]:.4f} at ${rates[engine]} per 1M characters.")
  if st.button('Generate Polly',type='primary',disabled=not(text and a and s and v)):
   try:c=aws_client(a,s,region,token);d=c.synthesize_speech(Text=text,OutputFormat='mp3',VoiceId=v['Id'],Engine=engine)['AudioStream'].read();p=save(d,name);st.audio(d);st.download_button('Download MP3',d,p.name)
   except Exception as e:st.exception(e)
 else:
  st.markdown('[Create project](https://console.cloud.google.com/projectcreate) · [Enable TTS API](https://console.cloud.google.com/apis/library/texttospeech.googleapis.com) · [Service-account key](https://console.cloud.google.com/iam-admin/serviceaccounts)')
  cred=st.file_uploader('Service-account JSON',type='json'); lang=st.text_input('Language code','en-IN'); family=st.selectbox('Pricing family',['Standard/WaveNet','Neural2/Polyglot','Chirp 3 HD','Studio']);rates={'Standard/WaveNet':4,'Neural2/Polyglot':16,'Chirp 3 HD':30,'Studio':160}
  if cred:st.session_state.gjson=cred.getvalue().decode()
  if st.button('Discover voices',disabled=not st.session_state.get('gjson')):
   try:st.session_state.gv=list(google_client(st.session_state.gjson).list_voices(language_code=lang).voices)
   except Exception as e:st.exception(e)
  gv=st.session_state.get('gv',[]);v=st.selectbox('Voice',gv,format_func=lambda x:f"{x.name} | {','.join(x.language_codes)} | {x.natural_sample_rate_hertz}Hz") if gv else None
  st.caption(f"Indicative cost: ${chars/1e6*rates[family]:.4f} at ${rates[family]} per 1M characters.")
  if st.button('Generate Google',type='primary',disabled=not(text and v and st.session_state.get('gjson'))):
   try:
    from google.cloud import texttospeech
    c=google_client(st.session_state.gjson);d=c.synthesize_speech(input=texttospeech.SynthesisInput(text=text),voice=texttospeech.VoiceSelectionParams(language_code=v.language_codes[0],name=v.name),audio_config=texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)).audio_content;p=save(d,name);st.audio(d);st.download_button('Download MP3',d,p.name)
   except Exception as e:st.exception(e)
 st.divider();x,y,z=st.columns(3);x.metric('Characters',f'{chars:,}');y.metric('Approx. words',f'{round(chars/6):,}');z.metric('Kokoro cost','$0')
elif pages=='Transcription':
 st.success('Fixed WinError 32: the mkstemp file descriptor is now closed before Faster-Whisper reads the file, with safe deletion retries.')
 f=st.file_uploader('Audio/video',type=['wav','mp3','m4a','flac','ogg','mp4','mov','mkv','webm']);a,b=st.columns(2);size=a.selectbox('Model',['tiny','base','small','medium','large-v3'],index=1);lang=b.selectbox('Language',['Auto','en','hi','de','fr','es','it','pt','ja','zh'])
 if st.button('Transcribe',type='primary',disabled=not f):
  try:
   with st.spinner('Transcribing...'): rows,det=transcribe(f.getvalue(),f.name,size,lang)
   text=' '.join(r['text'] for r in rows);srt='\n\n'.join(f"{i}\n{r['start']:.3f} --> {r['end']:.3f}\n{r['text']}" for i,r in enumerate(rows,1));st.success(f'Detected: {det}');st.text_area('Transcript',text,height=260);st.download_button('TXT',text,f'{safe(Path(f.name).stem)}.txt');st.download_button('SRT',srt,f'{safe(Path(f.name).stem)}.srt');st.dataframe(rows)
  except Exception as e:st.exception(e)
elif pages=='Cost Guide':
 st.header('Indicative public list-price guide, USD per 1M characters')
 st.dataframe([['Kokoro local',0,'No character charge; local compute'],['Azure neural',15,'Verify region/subscription'],['Polly standard',4,'Before free tier'],['Polly neural',16,'Before free tier'],['Polly generative',30,'Before free tier'],['Polly long-form',100,'Before free tier'],['Google Standard/WaveNet',4,'Free allowance may apply'],['Google Neural2/Polyglot',16,'Free allowance may apply'],['Google Chirp 3 HD',30,'Free allowance may apply'],['Google Studio',160,'Free allowance may apply']],column_config={0:'Provider/model',1:'USD/1M chars',2:'Note'},hide_index=True)
 st.warning('These are planning estimates, not invoices. Taxes, INR conversion, free tiers, region and contracts can change actual cost.')
else:
 st.header('Help');st.markdown('Use Python 3.11 or 3.12. Install FFmpeg for compressed audio/video. Cloud credentials remain in the Streamlit session and are not saved by the app. Never commit API keys or service-account JSON to GitHub.')
