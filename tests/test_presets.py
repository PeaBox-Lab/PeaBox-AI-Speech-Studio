import unittest

from peabox_voice_studio.models import Project, ScriptBlock
from peabox_voice_studio.services.presets import apply_preset, create_preset, delete_preset, list_presets


class PresetTests(unittest.TestCase):
    def test_create_apply_delete(self):
        project = Project("Demo")
        source = ScriptBlock("Source", provider="Azure Speech", language="en-US", voice="Jenny", speed=1.2, notes="Warm")
        preset = create_preset(project, "Narrator", source)
        target = ScriptBlock("Target")
        apply_preset(target, preset)
        self.assertEqual(target.provider, "Azure Speech")
        self.assertEqual(target.voice, "Jenny")
        self.assertEqual(target.notes, "Warm")
        self.assertTrue(delete_preset(project, preset["id"]))
        self.assertEqual(list_presets(project), [])

    def test_empty_name_rejected(self):
        with self.assertRaises(ValueError): create_preset(Project("Demo"), "  ", ScriptBlock("A"))

    def test_preset_history_is_bounded(self):
        project = Project("Demo"); block = ScriptBlock("A")
        for index in range(55): create_preset(project, f"P{index}", block)
        self.assertEqual(len(list_presets(project)), 50)


if __name__ == "__main__": unittest.main()
