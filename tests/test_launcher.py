import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class LauncherTests(unittest.TestCase):
    def test_supported_versions(self):
        text=(ROOT/"start_windows.ps1").read_text(encoding="utf-8")
        for value in ("-3.12","-3.11","-3.10","python","python3"): self.assertIn(value,text)
    def test_venv_python_runs_app(self):
        text=(ROOT/"start_windows.ps1").read_text(encoding="utf-8")
        self.assertIn('$venvPython -m streamlit run "app.py"',text)
    def test_batch_delegates(self): self.assertIn("start_windows.ps1",(ROOT/"start_windows.bat").read_text(encoding="utf-8"))
if __name__=="__main__": unittest.main()