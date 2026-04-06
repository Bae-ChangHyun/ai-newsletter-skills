from __future__ import annotations

import os
import tempfile
import unittest

from tests.test_helpers import load_module


send_telegram = load_module("send_telegram", "shared/newsletter/scripts/send_telegram.py")


class SendTelegramTests(unittest.TestCase):
    def test_split_text_chunks_limits_size(self):
        paragraph = "line\n" * 1200
        chunks = send_telegram.split_text_chunks(paragraph, max_chars=200)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 200 for chunk in chunks))

    def test_load_bot_token_prefers_env_and_ignores_external_claude_env(self):
        original_env = os.environ.get("TELEGRAM_BOT_TOKEN")
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                f.write('{"telegram": {"bot_token": "config-token"}}\n')

            previous_config = send_telegram.CONFIG_FILE
            send_telegram.CONFIG_FILE = config_path
            os.environ["TELEGRAM_BOT_TOKEN"] = "env-token"
            try:
                self.assertEqual(send_telegram.load_bot_token(), "env-token")
            finally:
                send_telegram.CONFIG_FILE = previous_config
                if original_env is None:
                    os.environ.pop("TELEGRAM_BOT_TOKEN", None)
                else:
                    os.environ["TELEGRAM_BOT_TOKEN"] = original_env


if __name__ == "__main__":
    unittest.main()
