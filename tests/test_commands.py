import unittest

from peabox_voice_studio.models import Project
from peabox_voice_studio.services.commands import COMMANDS, onboarding_status, record_command, resolve_commands, search_commands


class CommandTests(unittest.TestCase):
    def test_search_matches_labels_and_keywords(self):
        self.assertEqual(search_commands("subtitle")[0]["page"], "Transcription")
        self.assertTrue(any(item["page"] == "Timeline Studio" for item in search_commands("mix wav")))

    def test_project_required_commands_are_disabled_without_project(self):
        result = next(item for item in search_commands("governance", False) if item["page"] == "Governance")
        self.assertTrue(result["requires_project"])
        self.assertFalse(result["available"])
        self.assertTrue(next(item for item in search_commands("governance", True) if item["page"] == "Governance")["available"])

    def test_empty_query_returns_all_commands(self):
        self.assertEqual(len(search_commands("")), len(COMMANDS))

    def test_recent_command_history_is_unique_and_bounded(self):
        preferences = {}
        for index in range(15): record_command(preferences, COMMANDS[index % len(COMMANDS)]["id"], limit=10)
        self.assertLessEqual(len(preferences["recent_command_ids"]), 10)
        command_id = preferences["recent_command_ids"][-1]
        record_command(preferences, command_id, limit=10)
        self.assertEqual(preferences["recent_command_ids"][0], command_id)
        self.assertEqual(preferences["recent_command_ids"].count(command_id), 1)

    def test_resolve_commands_ignores_unknown(self):
        ids = [COMMANDS[1]["id"], "missing", COMMANDS[0]["id"]]
        self.assertEqual([item["id"] for item in resolve_commands(ids)], [COMMANDS[1]["id"], COMMANDS[0]["id"]])

    def test_onboarding_progress(self):
        empty = onboarding_status(None, 1)
        self.assertEqual(empty["completed"], 1)
        project = Project("Demo", script="Hello")
        project.render_history.append({"output": "a.wav"})
        project.settings["audio_clips"] = [{"id": "a"}]
        complete = onboarding_status(project, 1)
        self.assertEqual(complete["percent"], 100)
        self.assertTrue(all(step["complete"] for step in complete["steps"]))


if __name__ == "__main__": unittest.main()
