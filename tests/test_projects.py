import tempfile
import unittest
from pathlib import Path
from peabox_voice_studio.models import ScriptBlock
from peabox_voice_studio.services.projects import ProjectStore, move_block, split_script_into_blocks

class ProjectTests(unittest.TestCase):
    def test_lifecycle_preserves_blocks(self):
        with tempfile.TemporaryDirectory() as folder:
            store=ProjectStore(Path(folder)); project=store.create("Demo")
            project.blocks=[ScriptBlock(title="Intro",text="Hello")]; store.save(project)
            loaded=store.load(project.id)
            self.assertEqual(loaded.blocks[0].title,"Intro"); self.assertEqual(loaded.blocks[0].text,"Hello")
            store.delete(project.id); self.assertEqual(store.list(),[])
    def test_split_paragraphs(self):
        blocks=split_script_into_blocks("First\n\nSecond\nline\n\nThird")
        self.assertEqual([b.text for b in blocks],["First","Second\nline","Third"])
    def test_move_block(self):
        blocks=[ScriptBlock("A"),ScriptBlock("B")]
        move_block(blocks,1,-1); self.assertEqual([b.title for b in blocks],["B","A"])
    def test_invalid_identifier(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError): ProjectStore(Path(folder)).load("../bad")
if __name__=="__main__": unittest.main()
