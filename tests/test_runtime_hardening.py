import io,tempfile,unittest,wave
from array import array
from pathlib import Path
from unittest.mock import patch
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.timeline import add_clip,mix_timeline


def wav(frames=100,rate=1000):
 b=io.BytesIO()
 with wave.open(b,'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(array('h',[1]*frames).tobytes())
 return b.getvalue()

class RuntimeHardeningTests(unittest.TestCase):
 def test_timeline_memory_guard(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder); p=root/'a.wav';p.write_bytes(wav())
   project=Project('D');clip=add_clip(project,p);clip['start_seconds']=100000
   with self.assertRaisesRegex(ValueError,'too large'): mix_timeline(project,'huge',root)
 def test_whisper_model_is_cached(self):
  from peabox_voice_studio.services import transcription
  transcription._whisper_model.cache_clear()
  class Fake: pass
  with patch.dict('sys.modules',{'faster_whisper':type('M',(),{'WhisperModel':lambda *a,**k:Fake()})()}):
   self.assertIs(transcription._whisper_model('tiny'),transcription._whisper_model('tiny'))
if __name__=='__main__':unittest.main()
