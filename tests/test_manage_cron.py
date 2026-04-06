from __future__ import annotations

import unittest
from datetime import datetime

from tests.test_helpers import load_module


manage_cron = load_module("manage_cron", "shared/newsletter/scripts/manage_cron.py")


class ManageCronTests(unittest.TestCase):
    def test_validate_interval_expression_accepts_supported_values(self):
        for expression in ("30m", "1h", "6h", "12h", "24h", "1d"):
            with self.subTest(expression=expression):
                supported, message = manage_cron.validate_interval_expression(expression)
                self.assertTrue(supported)
                self.assertIsNone(message)

    def test_validate_interval_expression_rejects_unsupported_values(self):
        for expression in ("7m", "5h", "2d", "0h"):
            with self.subTest(expression=expression):
                supported, message = manage_cron.validate_interval_expression(expression)
                self.assertFalse(supported)
                self.assertTrue(message)

    def test_resolve_collector_schedule_follows_interval(self):
        cron, description = manage_cron.resolve_collector_schedule(
            {"mode": "interval", "expression": "30m"},
            datetime(2026, 4, 6, 13, 12),
        )
        self.assertEqual(cron, "12,42 * * * *")
        self.assertIn("선행 수집", description)

    def test_status_classification_detects_existing_backend_marker(self):
        runtime_root = manage_cron.RUNTIME_ROOT
        line = (
            f"4 * * * * NEWSLETTER_DELIVERY_MODE=deliver-only "
            f"{runtime_root}/scripts/run_with_copilot.py >> {runtime_root}/.data/delivery.log 2>&1 "
            "# github-copilot-newsletter-runtime"
        )
        self.assertEqual(
            manage_cron.classify_newsletter_line(line, f"{runtime_root}/scripts/run_with_openai.py"),
            "delivery",
        )

    def test_status_classification_detects_existing_collector_entry(self):
        runtime_root = manage_cron.RUNTIME_ROOT
        line = (
            f"59 * * * * python3 {runtime_root}/scripts/run_collect_cycle.py "
            f">> {runtime_root}/.data/collect.log 2>&1 # newsletter-collector-runtime"
        )
        self.assertEqual(manage_cron.classify_newsletter_line(line, None), "collector")


if __name__ == "__main__":
    unittest.main()
