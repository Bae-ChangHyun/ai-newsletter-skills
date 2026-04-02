#!/usr/bin/env python3
"""Send MarkdownV2 messages to Telegram Bot API.

Usage:
    echo "plain text with [link](url)" | python3 send_telegram.py <chat_id>
    echo "plain text" | python3 send_telegram.py              # reads chat_id from config.json

Reads plain text from stdin, escapes for MarkdownV2, sends via Bot API.
Bot token and chat_id are read from the plugin's config.json.
Falls back to ~/.claude/channels/telegram/.env and env var.
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "..", ".data", "config.json")


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_bot_token():
    # 1. config.json
    config = load_config()
    token = config.get("telegram", {}).get("bot_token")
    if token:
        return token
    # 2. fallback: channel env file
    env_file = os.path.expanduser("~/.claude/channels/telegram/.env")
    try:
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    return line.split("=", 1)[1]
    except FileNotFoundError:
        pass
    # 3. fallback: env var
    return os.environ.get("TELEGRAM_BOT_TOKEN")


def escape_mdv2(text):
    links = []

    def protect(m):
        links.append((m.group(1), m.group(2)))
        return f"\x00LINK{len(links)-1}\x00"

    protected = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", protect, text)
    escaped = re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", protected)

    def restore(m):
        idx = int(m.group(1))
        title, url = links[idx]
        t = re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", title)
        u = re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", url)
        return f"[{t}]({u})"

    return re.sub(r"\x00LINK(\d+)\x00", restore, escaped)


def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"# Telegram API error: {e.code} {body}", file=sys.stderr)
        return False


def main():
    config = load_config()

    # chat_id: CLI arg > config.json
    if len(sys.argv) >= 2:
        chat_id = sys.argv[1]
    else:
        chat_id = config.get("telegram", {}).get("chat_id")
        if not chat_id:
            print("Usage: echo 'text' | python3 send_telegram.py [chat_id]", file=sys.stderr)
            print("# Or set telegram.chat_id in config.json", file=sys.stderr)
            sys.exit(1)

    token = load_bot_token()
    if not token:
        print("# ERROR: TELEGRAM_BOT_TOKEN not found", file=sys.stderr)
        sys.exit(1)

    text = sys.stdin.read().strip()
    if not text:
        print("# No text to send", file=sys.stderr)
        sys.exit(0)

    escaped = escape_mdv2(text)
    ok = send_message(token, chat_id, escaped)
    if ok:
        print("OK")
    else:
        print("FAILED", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
