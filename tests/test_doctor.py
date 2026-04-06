from __future__ import annotations

import unittest
from unittest.mock import patch

from tests.test_helpers import load_module


doctor = load_module("newsletter_doctor", "shared/newsletter/scripts/newsletter_doctor.py")


class NewsletterDoctorTests(unittest.TestCase):
    @patch.object(doctor, "cron_status_text", return_value="collector: ok")
    @patch.object(doctor, "read_last_summary", return_value="hn 2")
    def test_build_report_includes_status_summary_and_diagnostics(self, *_mocks):
        config = {
            "language": "ko",
            "backend": {"type": "openai", "settings": {"base_url": "https://api.example.com/v1", "model": "gpt-test", "api_key_env": "OPENAI_API_KEY"}},
            "platforms": ["hn", "reddit"],
            "subreddits": ["OpenAI"],
            "schedule": {"mode": "interval", "expression": "1h", "label": "1h"},
            "telegram": {"enabled": False},
        }
        with patch.object(doctor, "backend_checks", return_value=[("OpenAI env OPENAI_API_KEY", "missing")]), patch.object(
            doctor, "integration_checks", return_value=[("Telegram", "disabled")]
        ):
            output = doctor.build_report(config)

        self.assertIn("뉴스레터 Doctor", output)
        self.assertIn("최근 요약: hn 2", output)
        self.assertIn("Cron 상태:", output)
        self.assertIn("OpenAI env OPENAI_API_KEY: missing", output)

    def test_build_report_handles_missing_config(self):
        output = doctor.build_report(None)
        self.assertIn("저장된 설정이 없습니다", output)


if __name__ == "__main__":
    unittest.main()
