#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess


RUNTIME_ROOT = "__RUNTIME_ROOT__"
CONFIG_FILE = os.path.join(RUNTIME_ROOT, ".data", "config.json")
DISPATCH = os.path.join(RUNTIME_ROOT, "scripts", "newsletter_dispatch.py")


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def main() -> None:
    config = load_config()
    if not config:
        print("No config saved yet.")
        return

    backend = (config.get("backend") or {}).get("type", "-")
    backend_settings = (config.get("backend") or {}).get("settings") or {}
    print("Backend:", backend)
    if backend_settings:
        print("Backend settings:", json.dumps(backend_settings, ensure_ascii=False))
    print("Language:", config.get("language", "ko"))
    print("Platforms:", ", ".join(config.get("platforms", [])) or "-")
    if config.get("subreddits"):
        print("Subreddits:", ", ".join(config["subreddits"]))
    if config.get("ai_keywords"):
        print("AI keywords:", ", ".join(config["ai_keywords"]))
    schedule = config.get("schedule", {})
    print("Schedule:", schedule.get("label") or schedule.get("expression") or schedule.get("cron", "-"))
    telegram = config.get("telegram", {})
    print("Telegram:", "enabled" if telegram.get("enabled") else "disabled")
    if config.get("threads_accounts"):
        print("Threads:", ", ".join(config["threads_accounts"]))
        print("RSSHub:", config.get("rsshub_url", "-"))

    result = subprocess.run(["python3", DISPATCH, "status"], text=True, capture_output=True, check=False)
    text = (result.stdout or result.stderr or "").strip()
    print("Runner status:", text or "unknown")


if __name__ == "__main__":
    main()
