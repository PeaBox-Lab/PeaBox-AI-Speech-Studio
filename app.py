import streamlit as st
from pathlib import Path
import sqlite3,tempfile,datetime,re
BASE=Path(__file__).parent; DATA=BASE/'data'; OUT=BASE/'outputs'; DATA.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True); DB=DATA/'studio.db'
st.set_page_config(page_title='PeaBox Voice Studio',page_icon='🎙️',layout='wide')
st.markdown("<div style='padding:22px;border-radius:18px;background:linear-gradient(135deg,#172554,#4338ca);color:white'><h1>🎙️ PeaBox Voice Studio</h1><p>Private local narration and AI transcription</p></div>",unsafe_allow_html=True)
def db():
 c=sqlite3.connect(DB); c.execute("CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY,created TEXT,type TEXT,name TEXT,status TEXT,path TEXT,details TEXT)"); c.commit(); return c
def log(t,n,s,p='',d=''):
 with db() as c: c.execute('INSERT INTO jobs(created,type,name,status,path,details) VALUES(?,?,?,?,?,?)',(datetime.datetime.now().isoformat(timespec='seconds'),t,n,s,p,d)); c.commit()
def safe(x): return re.sub(r'[^A-Za-z0-9_.-]+','_',x)[:60] or 'output'
def getvoices():
 import pyttsx3; e=pyttsx3.init()
 try:return [(getattr(v,'name',v.id),v.id) for v in e.getProperty('voices')]
 finally:e.stop()
def speak(text,vid,rate,volume,name):
 import pyttsx3
 p=OUT/(safe(name)+'.wav'); e=pyttsx3.init(); e.setProperty('voice',vid); e.setProperty('rate',rate); e.setProperty('volume',volume); e.save_to_file(text,str(p)); e.runAndWait(); e.stop()
 if not p.exists() or p.stat().st_size<100: raise RuntimeError('System speech engine did not produce audio.')
 return p
def extract(f):
 ext=Path(f.name).suffix.lower(); raw=f.getvalue()
 if ext in ['.txt','.md']: return raw.decode('utf-8',errors='replace')
 p=Path(tempfile.mkstemp(suffix=ext)[1]); p.write_bytes(raw)
 try:
  if ext=='.docx':
   from docx import Document
   return '\n'.join(x.text for x in Document(p).paragraphs)
  if ext=='.pdf':
   from pypdf import PdfReader
   return '\n'.join((x.extract_text() or '') for x in PdfReader(p).pages)
  raise ValueError('Unsupported file')
 finally:p.unlink(missing_ok=True)
def transcribe(raw,name,size,lang):
 from faster_whisper import WhisperModel
 p=Path(tempfile.mkstemp(suffix=Path(name).suffix or '.wav')[1]); p.write_bytes(raw)
 try:
  seg,info=WhisperModel(size,device='cpu',compute_type='int8').transcribe(str(p),language=None if lang=='Auto' else lang,vad_filter=True,beam_size=5)
  rows=[{'start':round(s.start,2),'end':round(s.end,2),'text':s.text.strip()} for s in seg]; return rows,info.language
 finally:p.unlink(missing_ok=True)
def stamp(x):
 ms=int(x*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000); return f'{h:02}:{m:02}:{s:02},{ms:03}'
page=st.sidebar.radio('Workspace',['Text to Speech','Transcription','History','System Check']); st.sidebar.caption('All project data stays in this folder.')
if page=='Text to Speech':
 st.header('Text to Speech'); st.info('Uses voices already installed on your computer. No API key is required.')
 f=st.file_uploader('Import TXT, Markdown, Word or PDF',type=['txt','md','docx','pdf']); initial=''
 if f:
  try: initial=extract(f)
  except Exception as e: st.error(e)
 text=st.text_area('Narration script',initial,height=300); vv=[]
 try:vv=getvoices()
 except Exception as e:st.error(f'Voice engine unavailable: {e}')
 a,b,c=st.columns(3)
 with a:v=a.selectbox('Voice',vv,format_func=lambda z:z[0]) if vv else None
 with b:rate=b.slider('Rate',100,260,175)
 with c:vol=c.slider('Volume',0.1,1.0,1.0,0.1)
 name=st.text_input('Output name','narration')
 if st.button('Generate WAV',type='primary',disabled=not(text.strip() and v)):
  try:
   with st.spinner('Generating locally...'):p=speak(text,v[1],rate,vol,name)
   log('TTS',name,'Completed',str(p),f'{len(text)} characters'); st.success('Audio created'); st.audio(str(p)); st.download_button('Download WAV',p.read_bytes(),p.name,'audio/wav')
  except Exception as e:log('TTS',name,'Failed',d=str(e));st.exception(e)
elif page=='Transcription':
 st.header('Local AI Transcription'); st.info('First use downloads the selected Whisper model; subsequent runs use the local cache.')
 mode=st.radio('Source',['Upload','Microphone'],horizontal=True); raw=None; name='recording.wav'
 if mode=='Upload':
  f=st.file_uploader('Audio or video',type=['wav','mp3','m4a','flac','ogg','mp4','mov','mkv'])
  if f:raw=f.getvalue();name=f.name;st.audio(raw)
 else:
  f=st.audio_input('Record',sample_rate=16000)
  if f:raw=f.getvalue();st.audio(raw)
 a,b=st.columns(2); size=a.selectbox('Model',['tiny','base','small'],index=1); lang=b.selectbox('Language',['Auto','en','hi','de','fr','es','it','pt'])
 if st.button('Transcribe',type='primary',disabled=raw is None):
  try:
   with st.spinner('Transcribing on this computer...'):rows,det=transcribe(raw,name,size,lang)
   text=' '.join(x['text'] for x in rows); stem=safe(Path(name).stem); tp=OUT/(stem+'_transcript.txt'); sp=OUT/(stem+'_subtitles.srt'); tp.write_text(text,encoding='utf-8'); sp.write_text('\n\n'.join(f"{i}\n{stamp(x['start'])} --> {stamp(x['end'])}\n{x['text']}" for i,x in enumerate(rows,1)),encoding='utf-8'); log('STT',name,'Completed',str(tp),det)
   st.success(f'Completed. Detected: {det}');st.text_area('Transcript',text,height=250);x,y=st.columns(2);x.download_button('Download TXT',tp.read_bytes(),tp.name);y.download_button('Download SRT',sp.read_bytes(),sp.name);st.dataframe(rows,use_container_width=True)
  except Exception as e:log('STT',name,'Failed',d=str(e));st.exception(e);st.caption('Install FFmpeg for compressed audio and video.')
elif page=='History':
 st.header('Project History')
 with db() as c:r=c.execute('SELECT * FROM jobs ORDER BY id DESC').fetchall()
 st.dataframe(r,use_container_width=True)
 if st.button('Clear history'):
  with db() as c:c.execute('DELETE FROM jobs');c.commit()
  st.rerun()
else:
 import sys,platform,shutil
 st.header('System Check');st.json({'Python':sys.version.split()[0],'Platform':platform.platform(),'FFmpeg':shutil.which('ffmpeg') or 'Not detected','Data':str(DATA),'Outputs':str(OUT)})
 try:st.success(f'{len(getvoices())} system voices detected')
 except Exception as e:st.error(e)
 try:import faster_whisper;st.success('Faster-Whisper installed')
 except Exception as e:st.warning(e)
