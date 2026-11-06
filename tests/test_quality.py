import unittest
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.quality import add_pronunciation, apply_pronunciations, compile_ssml_text, delete_pronunciation, insert_pause, prepare_text, validate_pause_markers
class QualityTests(unittest.TestCase):
    def test_pronunciation_dictionary(self):
        project = Project("Demo")
        item = add_pronunciation(project, "PeaBox", "pea box")
        self.assertEqual(prepare_text("Use PEABOX now", project, "Azure Speech"), "Use pea box now")
        self.assertTrue(delete_pronunciation(project, item["id"]))
    def test_whole_word_does_not_replace_inside_word(self):
        entries = [{"source": "AI", "replacement": "A I", "whole_word": True, "case_sensitive": False}]
        self.assertEqual(apply_pronunciations("AI daily", entries), "A I daily")
    def test_pause_marker_compiles_to_ssml(self):
        compiled = compile_ssml_text("Hello [[pause:1.5]] world & more")
        self.assertEqual(compiled, 'Hello <break time="1.5s"/> world &amp; more')
    def test_local_pause_is_approximated(self):
        project = Project("Demo")
        text = prepare_text("Hello [[pause:1]] world", project, "Kokoro local")
        self.assertNotIn("[[pause:", text)
        self.assertIn("...", text)
    def test_pause_validation_and_insert(self):
        self.assertIn("[[pause:2]]", insert_pause("Hello", 2))
        self.assertEqual(validate_pause_markers("OK [[pause:1]]"), [])
        self.assertTrue(validate_pause_markers("Bad [[pause:20]]"))
        self.assertTrue(validate_pause_markers("Bad [[pause:x]]"))
    def test_invalid_rule_rejected(self):
        with self.assertRaises(ValueError): add_pronunciation(Project("Demo"), "", "spoken")
if __name__ == "__main__": unittest.main()
