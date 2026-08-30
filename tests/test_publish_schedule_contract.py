import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_content_quality.py"
SPEC = importlib.util.spec_from_file_location("validate_content_quality", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PublishScheduleContractTests(unittest.TestCase):
    def test_active_hourly_schedule_passes(self):
        workflow = 'on:\n  schedule:\n    - cron: "23 * * * *"\n  workflow_dispatch:\n'
        self.assertEqual(MODULE.publish_schedule_contract_errors(workflow), [])

    def test_paused_manual_only_passes(self):
        workflow = 'on:\n  workflow_dispatch:\nenv:\n  PUBLISH_SCHEDULE_PAUSED: "true"\n'
        self.assertEqual(MODULE.publish_schedule_contract_errors(workflow), [])

    def test_missing_schedule_and_marker_fails(self):
        workflow = 'on:\n  workflow_dispatch:\n'
        self.assertIn("publish_scheduled_workflow_missing_hourly_due_content_check", MODULE.publish_schedule_contract_errors(workflow))

    def test_paused_schedule_conflict_fails(self):
        workflow = 'on:\n  schedule:\n    - cron: "23 * * * *"\n  workflow_dispatch:\nenv:\n  PUBLISH_SCHEDULE_PAUSED: "true"\n'
        self.assertIn("publish_scheduled_workflow_paused_with_schedule", MODULE.publish_schedule_contract_errors(workflow))

    def test_false_marker_without_schedule_fails(self):
        workflow = 'on:\n  workflow_dispatch:\nenv:\n  PUBLISH_SCHEDULE_PAUSED: "false"\n'
        self.assertIn("publish_scheduled_workflow_missing_hourly_due_content_check", MODULE.publish_schedule_contract_errors(workflow))


if __name__ == "__main__":
    unittest.main()
