from __future__ import annotations

import unittest

from tests.test_helpers import load_module


run_all = load_module("run_all", "shared/newsletter/scripts/run_all.py")


class RunAllTests(unittest.TestCase):
    def test_format_platform_items_preserves_cross_platform_duplicates(self):
        items = [
            {
                "title": "Same story",
                "url": "https://example.com/story",
                "source": "HN",
                "platform": "hn",
                "score": 10,
                "comments": 3,
            },
            {
                "title": "Same story",
                "url": "https://example.com/story",
                "source": "r/OpenAI",
                "platform": "reddit",
                "score": 20,
                "comments": 5,
            },
        ]

        grouped = run_all.format_platform_items(items)

        self.assertIn("hn", grouped)
        self.assertIn("reddit", grouped)
        self.assertEqual(grouped["hn"][0]["url"], "https://example.com/story")
        self.assertEqual(grouped["reddit"][0]["url"], "https://example.com/story")


if __name__ == "__main__":
    unittest.main()
