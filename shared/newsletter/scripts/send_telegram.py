#!/usr/bin/env python3
"""Send MarkdownV2 messages to Telegram Bot API.

Usage:
    echo "plain text with [link](url)" | python3 send_telegram.py <chat_id>
    echo "plain text" | python3 send_telegram.py              # reads chat_id from config.json

Reads plain text from stdin, escapes for MarkdownV2, splits long digests into
safe chunks, and sends them sequentially.
Bot token and chat_id are read from the runtime config.json, with an optional
`TELEGRAM_BOT_TOKEN` environment variable override for the bot token.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "..", ".data", "config.json")
MAX_TELEGRAM_MESSAGE_LENGTH = 3800


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_bot_token():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if token:
        return token
    config = load_config()
    return config.get("telegram", {}).get("bot_token")


def escape_mdv2(text):
    links = []

    def protect(match):
        links.append((match.group(1), match.group(2)))
        return f"\x00LINK{len(links) - 1}\x00"

    protected = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", protect, text)
    escaped = re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", protected)

    def restore(match):
        idx = int(match.group(1))
        title, url = links[idx]
        escaped_title = re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", title)
        escaped_url = re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", url)
        return f"[{escaped_title}]({escaped_url})"

    return re.sub(r"\x00LINK(\d+)\x00", restore, escaped)


def split_long_segment(segment: str, max_chars: int) -> list[str]:
    if len(segment) <= max_chars:
        return [segment]

    lines = segment.splitlines(keepends=True)
    if len(lines) > 1:
        chunks: list[str] = []
        current = ""
        for line in lines:
            if current and len(current) + len(line) > max_chars:
                chunks.append(current)
                current = line
            else:
                current += line
        if current:
            chunks.append(current)
        if all(len(chunk) <= max_chars for chunk in chunks):
            return chunks

    return [segment[i : i + max_chars] for i in range(0, len(segment), max_chars)]


def split_text_chunks(text: str, max_chars: int = MAX_TELEGRAM_MESSAGE_LENGTH) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []

    paragraphs = re.split(r"(\n\s*\n)", stripped)
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if not paragraph:
            continue
        if len(paragraph) > max_chars:
            for part in split_long_segment(paragraph, max_chars):
                if current:
                    chunks.append(current)
                    current = ""
                chunks.append(part)
            continue
        if current and len(current) + len(paragraph) > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current += paragraph

    if current:
        chunks.append(current)

    return [chunk.strip() for chunk in chunks if chunk.strip()]


def prepare_escaped_chunks(text: str, max_chars: int = MAX_TELEGRAM_MESSAGE_LENGTH) -> list[str]:
    pending = split_text_chunks(text, max_chars=max_chars)
    escaped_chunks: list[str] = []

    while pending:
        chunk = pending.pop(0)
        escaped = escape_mdv2(chunk)
        if len(escaped) <= max_chars:
            escaped_chunks.append(escaped)
            continue
        smaller_parts = split_long_segment(chunk, max(1, len(chunk) // 2))
        if len(smaller_parts) == 1 and smaller_parts[0] == chunk:
            raise RuntimeError("Unable to split Telegram message into safe chunks")
        pending = smaller_parts + pending

    return escaped_chunks


def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False), ""
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return False, f"Telegram API error: {e.code} {body}"
    except Exception as e:  # pragma: no cover - defensive
        return False, f"Telegram request failed: {e}"


def main():
    config = load_config()

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

    raw_text = sys.stdin.read().strip()
    if not raw_text:
        print("# No text to send", file=sys.stderr)
        sys.exit(0)

    for escaped in prepare_escaped_chunks(raw_text):
        ok, details = send_message(token, chat_id, escaped)
        if not ok:
            print(f"# {details or 'Telegram send failed'}", file=sys.stderr)
            print("FAILED", file=sys.stderr)
            sys.exit(1)

    print("OK")


if __name__ == "__main__":
    main()
