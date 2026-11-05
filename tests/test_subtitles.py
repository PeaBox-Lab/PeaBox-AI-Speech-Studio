import unittest
from peabox_voice_studio.services.subtitles import format_timestamp,to_srt
class SubtitleTests(unittest.TestCase):
    def test_timestamp(self): self.assertEqual(format_timestamp(3661.234),"01:01:01,234")
    def test_srt(self): self.assertEqual(to_srt([{"start":0,"end":1.25,"text":" Hi "}]),"1\n00:00:00,000 --> 00:00:01,250\nHi")
if __name__=="__main__": unittest.main()
