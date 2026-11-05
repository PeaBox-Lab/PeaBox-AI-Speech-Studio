import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WindowsLauncherTests(unittest.TestCase):
    def test_batch_delegates_to_powershell_launcher(self):
        text = (ROOT / "start_windows.bat").read_text(encoding="utf-8")
        self.assertIn("start_windows.ps1", text)
        self.assertNotIn("py -3.11 -m venv", text)

    def test_launcher_checks_multiple_python_versions(self):
        text = (ROOT / "start_windows.ps1").read_text(encoding="utf-8")
        for version in ("-3.12", "-3.11", "-3.10"):
            self.assertIn(version, text)
        self.assertIn('Executable = "python"', text)
        self.assertIn('Executable = "python3"', text)

    def test_supported_version_range_is_bounded(self):
        text = (ROOT / "start_windows.ps1").read_text(encoding="utf-8")
        self.assertRegex(text, r'MinimumVersion\s*=\s*\[Version\]"3\.10\.0"')
        self.assertRegex(text, r'MaximumVersion\s*=\s*\[Version\]"3\.13\.0"')

    def test_existing_environment_is_reused_or_rebuilt(self):
        text = (ROOT / "start_windows.ps1").read_text(encoding="utf-8")
        self.assertIn("Using existing virtual environment", text)
        self.assertIn("Rebuilding it", text)
        self.assertIn("Remove-Item -Recurse -Force", text)

    def test_streamlit_uses_virtual_environment_python(self):
        text = (ROOT / "start_windows.ps1").read_text(encoding="utf-8")
        self.assertIn('& $venvPython -m streamlit run "app.py"', text)


if __name__ == "__main__":
    unittest.main()
