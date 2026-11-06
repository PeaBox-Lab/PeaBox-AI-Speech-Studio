import unittest
from unittest.mock import MagicMock, patch
from peabox_voice_studio.providers.cloud import generate_azure
class CloudSsmlTests(unittest.TestCase):
    @patch("requests.post")
    def test_azure_payload_contains_compiled_break(self, post):
        response = MagicMock()
        response.content = b"audio"
        response.raise_for_status.return_value = None
        post.return_value = response
        with patch("peabox_voice_studio.providers.cloud.atomic_write_bytes") as write:
            write.return_value = MagicMock()
            generate_azure("Hello [[pause:1]] world", {"key": "secret", "region": "region"}, "Voice", 1.0, "test")
        payload = post.call_args.kwargs["data"].decode("utf-8")
        self.assertIn('<break time="1s"/>', payload)
        self.assertNotIn("[[pause:", payload)
if __name__ == "__main__": unittest.main()