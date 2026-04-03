#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from urllib import error, request


RUNTIME_ROOT = "__RUNTIME_ROOT__"
CONFIG_FILE = os.path.join(RUNTIME_ROOT, ".data", "config.json")
PROMPT_FILE = os.path.join(RUNTIME_ROOT, "prompts", "run_newsletter_copilot.md")
RUN_ALL = os.path.join(RUNTIME_ROOT, "scripts", "run_all.py")
SEND_TELEGRAM = os.path.join(RUNTIME_ROOT, "scripts", "send_telegram.py")
MARK_CURATED = os.path.join(RUNTIME_ROOT, "scripts", "mark_curated.py")
MARK_FAILED = os.path.join(RUNTIME_ROOT, "scripts", "mark_send_failed.py")
MARK_DELIVERED = os.path.join(RUNTIME_ROOT, "scripts", "mark_delivered.py")
LAST_MESSAGE_FILE = os.path.join(RUNTIME_ROOT, ".data", "last_run.txt")
COPILOT_GITHUB_TOKEN_FILE = os.path.join(RUNTIME_ROOT, ".data", "credentials", "github_copilot_github_token.json")
DEFAULT_COPILOT_API_BASE_URL = "https://api.githubcopilot.com"
COPILOT_USER_AGENT = "ai-newsletter-skills/1.0"
KST = timezone(timedelta(hours=9))


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def read_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def no_news_message(language: str) -> str:
    return "새 뉴스 없음" if language == "ko" else "No new newsletter items"


def build_prompt(config: dict, candidates: dict) -> str:
    payload = json.dumps(
        {
            "language": config.get("language", "ko"),
            "now_kst": datetime.now(KST).strftime("%Y-%m-%d %H:%M KST"),
            "candidates": candidates,
        },
        ensure_ascii=False,
        indent=2,
    )
    return f"{read_prompt()}\n\nInput JSON:\n{payload}\n"


def run_collect() -> dict:
    result = subprocess.run(["python3", RUN_ALL, "--from-state"], text=True, capture_output=True, check=False)
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    return json.loads(stdout)


def collect_if_needed() -> None:
    if os.environ.get("NEWSLETTER_DELIVERY_MODE") == "deliver-only":
        return
    subprocess.run(["python3", RUN_ALL, "--collect-only"], text=True, check=True)


def strip_json_response(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def load_copilot_github_token() -> str:
    with open(COPILOT_GITHUB_TOKEN_FILE, "r", encoding="utf-8") as f:
        payload = json.load(f)
    token = str(payload.get("github_token") or "").strip()
    if not token:
        raise RuntimeError("GitHub Copilot login is required")
    return token


def http_json(url: str, method: str = "GET", headers: dict | None = None, payload: dict | None = None) -> dict:
    data = None
    final_headers = dict(headers or {})
    if payload is not None:
      data = json.dumps(payload).encode("utf-8")
      final_headers.setdefault("Content-Type", "application/json")
    req = request.Request(url, data=data, method=method, headers=final_headers)
    try:
        with request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return json.loads(body)
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub Copilot API error: HTTP {exc.code} {body}") from exc
    except Exception as exc:
        raise RuntimeError(f"GitHub Copilot request failed: {exc}") from exc


def call_copilot(config: dict, candidates: dict) -> dict:
    model = ((config.get("backend") or {}).get("settings") or {}).get("model")
    if not model:
        raise RuntimeError("backend.settings.model is required")
    github_token = load_copilot_github_token()
    response = http_json(
        f"{DEFAULT_COPILOT_API_BASE_URL.rstrip('/')}/chat/completions",
        method="POST",
        headers={
            "Authorization": f"Bearer {github_token}",
            "User-Agent": COPILOT_USER_AGENT,
            "Openai-Intent": "conversation-edits",
            "x-initiator": "user",
        },
        payload={
            "model": model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": read_prompt()},
                {"role": "user", "content": json.dumps(
                    {
                        "language": config.get("language", "ko"),
                        "now_kst": datetime.now(KST).strftime("%Y-%m-%d %H:%M KST"),
                        "candidates": candidates,
                    },
                    ensure_ascii=False,
                    indent=2,
                )},
            ],
            "response_format": {"type": "json_object"},
        },
    )
    content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return json.loads(strip_json_response(content))


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
    collect_if_needed()
    candidates = run_collect()
    if not candidates:
        summary = no_news_message(language)
        write_last_message(summary)
        print(summary)
        return 0

    result = call_copilot(config, candidates)
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
