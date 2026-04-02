#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta


RUNTIME_ROOT = "__RUNTIME_ROOT__"
CONFIG_FILE = os.path.join(RUNTIME_ROOT, ".data", "config.json")
PROMPT_FILE = os.path.join(RUNTIME_ROOT, "prompts", "run_newsletter_openai.md")
RUN_ALL = os.path.join(RUNTIME_ROOT, "scripts", "run_all.py")
SEND_TELEGRAM = os.path.join(RUNTIME_ROOT, "scripts", "send_telegram.py")
MARK_CURATED = os.path.join(RUNTIME_ROOT, "scripts", "mark_curated.py")
MARK_FAILED = os.path.join(RUNTIME_ROOT, "scripts", "mark_send_failed.py")
MARK_DELIVERED = os.path.join(RUNTIME_ROOT, "scripts", "mark_delivered.py")
LAST_MESSAGE_FILE = os.path.join(RUNTIME_ROOT, ".data", "last_run.txt")
KST = timezone(timedelta(hours=9))


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def read_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def no_news_message(language: str) -> str:
    return "새 뉴스 없음" if language == "ko" else "No new newsletter items"


def build_user_prompt(config: dict, candidates: dict) -> str:
    now_kst = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    return json.dumps(
        {
            "language": config.get("language", "ko"),
            "now_kst": now_kst,
            "candidates": candidates,
        },
        ensure_ascii=False,
        indent=2,
    )


def chat_endpoint(base_url: str) -> str:
    base_url = base_url.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


def call_openai_compatible(config: dict, candidates: dict) -> dict:
    editor = ((config.get("backend") or {}).get("settings") or {})
    base_url = editor.get("base_url")
    model = editor.get("model")
    api_key_env = editor.get("api_key_env", "OPENAI_API_KEY")
    api_key = os.environ.get(api_key_env)
    if not base_url or not model:
        raise RuntimeError("backend.settings.base_url and model are required")
    if not api_key:
        raise RuntimeError(f"{api_key_env} is not set")

    payload = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": read_prompt()},
            {"role": "user", "content": build_user_prompt(config, candidates)},
        ],
    }
    request = urllib.request.Request(
        chat_endpoint(base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI-compatible API error: {exc.code} {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenAI-compatible API request failed: {exc}") from exc

    content = data["choices"][0]["message"]["content"]
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return json.loads(content)


def run_collect() -> dict:
    result = subprocess.run(["python3", RUN_ALL], text=True, capture_output=True, check=False)
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    return json.loads(stdout)


def mark(script: str, selected: dict) -> None:
    subprocess.run(
        ["python3", script],
        input=json.dumps(selected, ensure_ascii=False),
        text=True,
        check=True,
    )


def send_messages(config: dict, messages: list[dict]) -> bool:
    telegram = config.get("telegram", {})
    if not telegram.get("enabled"):
        for item in messages:
            print(item.get("text", "").strip())
            print()
        return True

    for item in messages:
        subprocess.run(
            ["python3", SEND_TELEGRAM],
            input=item.get("text", "").strip(),
            text=True,
            check=True,
        )
    return True


def write_last_message(summary: str) -> None:
    os.makedirs(os.path.dirname(LAST_MESSAGE_FILE), exist_ok=True)
    with open(LAST_MESSAGE_FILE, "w", encoding="utf-8") as f:
        f.write(summary.strip() + "\n")


def main() -> int:
    config = load_config()
    language = config.get("language", "ko")
    candidates = run_collect()
    if not candidates:
        summary = no_news_message(language)
        write_last_message(summary)
        print(summary)
        return 0

    result = call_openai_compatible(config, candidates)
    summary = result.get("summary") or no_news_message(language)
    selected = result.get("selected") or {}
    messages = result.get("messages") or []

    if not selected or not messages:
        write_last_message(summary)
        print(summary)
        return 0

    mark(MARK_CURATED, selected)
    try:
        send_messages(config, messages)
    except subprocess.CalledProcessError:
        mark(MARK_FAILED, selected)
        write_last_message(summary)
        print(summary)
        return 1

    mark(MARK_DELIVERED, selected)
    write_last_message(summary)
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
