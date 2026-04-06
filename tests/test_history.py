from __future__ import annotations

import os
import tempfile
import unittest

from tests.test_helpers import load_module


history = load_module("newsletter_history", "shared/newsletter/scripts/newsletter_history.py")


class NewsletterHistoryTests(unittest.TestCase):
    def test_load_delivered_entries_reads_and_sorts_seen_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            seen_path = os.path.join(temp_dir, "hn_seen.jsonl")
            with open(seen_path, "w", encoding="utf-8") as f:
                f.write('{"title":"Older","url":"https://example.com/1","delivered_at":1000,"source":"HN"}\n')
                f.write('{"title":"Newer","url":"https://example.com/2","delivered_at":2000,"source":"HN"}\n')
                f.write('{"title":"Ignored","url":"https://example.com/3","source":"HN"}\n')

            entries = history.load_delivered_entries(temp_dir)

            self.assertEqual([entry["title"] for entry in entries], ["Newer", "Older"])
            self.assertTrue(all(entry["platform"] == "hn" for entry in entries))

    def test_read_recent_summaries_parses_summary_lines(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "delivery.log")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("[2026-04-06 10:00:00 KST] RUN start backend=codex mode=deliver-only\n")
                f.write("[2026-04-06 10:00:05 KST] SUMMARY hn 2, reddit 1\n")
                f.write("[2026-04-06 11:00:05 KST] SUMMARY hn 1\n")

            summaries = history.read_recent_summaries(log_path, limit=5)

            self.assertEqual(len(summaries), 2)
            self.assertEqual(summaries[-1]["summary"], "hn 1")

    def test_build_output_includes_latest_summary_and_platform_counts(self):
        config = {"language": "ko", "backend": {"type": "codex"}}
        delivered_entries = [
            {
                "platform": "hn",
                "title": "Example",
                "url": "https://example.com",
                "source": "HN",
                "delivered_at": 1_712_400_000,
            },
            {
                "platform": "reddit",
                "title": "Other",
                "url": "https://example.com/reddit",
                "source": "r/OpenAI",
                "delivered_at": 1_712_300_000,
            },
        ]

        output = history.build_output(config, delivered_entries, "hn 1, reddit 1", [], limit=10)

        self.assertIn("뉴스레터 발송 이력", output)
        self.assertIn("최근 요약: hn 1, reddit 1", output)
        self.assertIn("hn: 1", output)
        self.assertIn("reddit: 1", output)


if __name__ == "__main__":
    unittest.main()
