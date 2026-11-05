import runpy
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ["Projects", "System Check", "Provider Setup", "Voice Library", "Quality Studio", "Audio Quality Lab", "Script Blocks", "Batch Production", "Create Speech", "Transcription", "Render History", "Roadmap & Help"]


class SessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class DummyContainer:
    def __init__(self, owner):
        self.owner = owner

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def radio(self, label, options, **kwargs):
        if label == "Studio":
            return self.owner.page
        return options[0]

    def columns(self, spec, **kwargs):
        count = spec if isinstance(spec, int) else len(spec)
        return [DummyContainer(self.owner) for _ in range(count)]

    def tabs(self, labels):
        return [DummyContainer(self.owner) for _ in labels]

    def selectbox(self, label, options, **kwargs):
        options = list(options)
        index = kwargs.get("index", 0)
        return options[index] if options else None

    def text_input(self, label, value="", **kwargs):
        return value

    def text_area(self, label, value="", **kwargs):
        return value

    def checkbox(self, label, value=False, **kwargs):
        return value

    def slider(self, label, min_value=None, max_value=None, value=None, *args, **kwargs):
        return value

    def button(self, *args, **kwargs):
        return False

    def file_uploader(self, *args, **kwargs):
        return None

    def download_button(self, *args, **kwargs):
        return False

    def expander(self, *args, **kwargs):
        return DummyContainer(self.owner)

    def spinner(self, *args, **kwargs):
        return DummyContainer(self.owner)

    def __getattr__(self, name):
        def no_op(*args, **kwargs):
            return None
        return no_op


class FakeStreamlit(types.ModuleType):
    def __init__(self, page):
        super().__init__("streamlit")
        self.page = page
        self.session_state = SessionState()
        self.sidebar = DummyContainer(self)
        self._container = DummyContainer(self)

    def __getattr__(self, name):
        return getattr(self._container, name)


class PageSmokeTests(unittest.TestCase):
    def test_every_navigation_page_executes_without_project(self):
        original = sys.modules.get("streamlit")
        try:
            for page in PAGES:
                with self.subTest(page=page):
                    sys.modules["streamlit"] = FakeStreamlit(page)
                    runpy.run_path(str(ROOT / "app.py"), run_name=f"__peabox_smoke_{page.replace(' ', '_')}__")
        finally:
            if original is None:
                sys.modules.pop("streamlit", None)
            else:
                sys.modules["streamlit"] = original


if __name__ == "__main__":
    unittest.main()
