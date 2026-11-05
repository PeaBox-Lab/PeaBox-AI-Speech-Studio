import unittest

from peabox_voice_studio.providers.cloud import normalize_azure_voices, normalize_google_voices, normalize_polly_voices
from peabox_voice_studio.services.catalogs import capability_rows, catalog_facets, filter_voices


class FakeGender:
    name = "FEMALE"


class FakeGoogleVoice:
    name = "en-US-Test"
    language_codes = ["en-US", "en-CA"]
    ssml_gender = FakeGender()


class CatalogTests(unittest.TestCase):
    def test_normalize_azure(self):
        voices = normalize_azure_voices([{"ShortName": "en-US-A", "DisplayName": "A", "Locale": "en-US", "Gender": "Female"}])
        self.assertEqual(voices[0]["id"], "en-US-A")
        self.assertEqual(voices[0]["provider"], "Azure Speech")

    def test_normalize_polly(self):
        voices = normalize_polly_voices([{"Id": "Joanna", "Name": "Joanna", "LanguageCode": "en-US", "Gender": "Female"}], "neural")
        self.assertEqual(voices[0]["provider"], "Amazon Polly neural")

    def test_normalize_google_expands_languages(self):
        voices = normalize_google_voices([FakeGoogleVoice()])
        self.assertEqual(len(voices), 2)
        self.assertEqual({v["language"] for v in voices}, {"en-US", "en-CA"})

    def test_filter_and_facets(self):
        voices = [
            {"provider": "Azure Speech", "id": "a", "name": "Jenny", "language": "en-US", "gender": "Female"},
            {"provider": "Google Cloud TTS", "id": "b", "name": "Ravi", "language": "hi-IN", "gender": "Male"},
        ]
        self.assertEqual(len(filter_voices(voices, "jenny")), 1)
        self.assertEqual(len(filter_voices(voices, language="hi-IN")), 1)
        facets = catalog_facets(voices)
        self.assertEqual(facets["languages"], ["en-US", "hi-IN"])

    def test_capability_rows(self):
        rows = capability_rows({"Kokoro local", "Azure Speech"}, {"Azure Speech": 100})
        azure = next(row for row in rows if row["Provider"] == "Azure Speech")
        self.assertTrue(azure["Ready"]); self.assertEqual(azure["Cached voices"], 100)


if __name__ == "__main__": unittest.main()
