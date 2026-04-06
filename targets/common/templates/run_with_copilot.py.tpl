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
COPILOT_API_TOKEN_FILE = os.path.join(RUNTIME_ROOT, ".data", "credentials", "github_copilot_api_token.json")
GITHUB_COPILOT_CLIENT_ID = "Iv1.b507a08c87ecfe98"
COPILOT_TOKEN_URL = "https://api.github.com/copilot_internal/v2/token"
DEFAULT_COPILOT_API_BASE_URL = "https://api.individual.githubcopilot.com"
COPILOT_IDE_USER_AGENT = "GitHubCopilotChat/0.26.7"
COPILOT_EDITOR_VERSION = "vscode/1.96.2"
KST = timezone(timedelta(hours=9))


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def read_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def no_news_message(language: str) -> str:
    return "새 뉴스 없음" if language == "ko" else "No new newsletter items"


def log_line(message: str) -> None:
    timestamp = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")
    print(f"[{timestamp}] {message}")


def selected_entry_count(selected: dict) -> int:
    return sum(len(entries) for entries in selected.values() if isinstance(entries, list))


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


def extract_text_content(content) -> str:
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content or "")


def validate_editor_result(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise RuntimeError("GitHub Copilot response must be a JSON object")
    summary = payload.get("summary")
    messages = payload.get("messages")
    selected = payload.get("selected")
    if summary is not None and not isinstance(summary, str):
        raise RuntimeError("Editor result.summary must be a string")
    if messages is not None and not isinstance(messages, list):
        raise RuntimeError("Editor result.messages must be a list")
    if selected is not None and not isinstance(selected, dict):
        raise RuntimeError("Editor result.selected must be an object")
    return payload


def load_copilot_github_token() -> str:
    with open(COPILOT_GITHUB_TOKEN_FILE, "r", encoding="utf-8") as f:
        payload = json.load(f)
    token = str(payload.get("github_token") or "").strip()
    client_id = str(payload.get("client_id") or "").strip()
    if not token or client_id != GITHUB_COPILOT_CLIENT_ID:
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


def build_copilot_exchange_headers(github_token: str) -> dict:
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {github_token}",
        "User-Agent": COPILOT_IDE_USER_AGENT,
    }


def build_copilot_api_headers(api_token: str, extra_headers: dict | None = None) -> dict:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}",
        "User-Agent": COPILOT_IDE_USER_AGENT,
        "Editor-Version": COPILOT_EDITOR_VERSION,
    }
    if extra_headers:
        headers.update(extra_headers)
    return headers


def parse_copilot_expires_at(value) -> int:
    if isinstance(value, (int, float)) and value:
        value_int = int(value)
        return value_int * 1000 if value_int < 100_000_000_000 else value_int
    if isinstance(value, str) and value.strip():
        value_int = int(value.strip())
        return value_int * 1000 if value_int < 100_000_000_000 else value_int
    raise RuntimeError("Copilot token response missing expires_at")


def load_cached_copilot_api_token() -> dict | None:
    try:
        with open(COPILOT_API_TOKEN_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except FileNotFoundError:
        return None
    except Exception:
        return None

    token = str(payload.get("token") or "").strip()
    if not token:
        return None
    try:
        expires_at = parse_copilot_expires_at(payload.get("expires_at") or payload.get("expiresAt"))
    except Exception:
        return None
    return {"token": token, "expires_at": expires_at}


def is_copilot_api_token_usable(payload: dict | None, now_ms: int | None = None) -> bool:
    if not payload:
        return False
    now = now_ms if now_ms is not None else int(datetime.now(timezone.utc).timestamp() * 1000)
    return int(payload.get("expires_at") or 0) - now > 5 * 60 * 1000


def resolve_copilot_proxy_host(proxy_ep: str) -> str | None:
    value = proxy_ep.strip()
    if not value:
        return None
    url_text = value if value.startswith(("http://", "https://")) else f"https://{value}"
    try:
        from urllib.parse import urlparse

        parsed = urlparse(url_text)
    except Exception:
        return None
    if parsed.scheme not in {"http", "https"}:
        return None
    return (parsed.hostname or "").lower() or None


def derive_copilot_api_base_url_from_token(token: str) -> str | None:
    value = token.strip()
    if not value:
        return None
    for segment in value.split(";"):
        part = segment.strip()
        if not part.lower().startswith("proxy-ep="):
            continue
        proxy_ep = part.split("=", 1)[1].strip()
        proxy_host = resolve_copilot_proxy_host(proxy_ep)
        if not proxy_host:
            return None
        return f"https://{proxy_host.replace('proxy.', 'api.', 1)}"
    return None


def save_copilot_api_token(payload: dict) -> None:
    os.makedirs(os.path.dirname(COPILOT_API_TOKEN_FILE), exist_ok=True)
    with open(COPILOT_API_TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def resolve_copilot_api_token(github_token: str) -> dict:
    cached = load_cached_copilot_api_token()
    if is_copilot_api_token_usable(cached):
        return {
            "token": cached["token"],
            "expires_at": cached["expires_at"],
            "base_url": derive_copilot_api_base_url_from_token(cached["token"]) or DEFAULT_COPILOT_API_BASE_URL,
        }

    response = http_json(
        COPILOT_TOKEN_URL,
        headers=build_copilot_exchange_headers(github_token),
    )
    token = str(response.get("token") or "").strip()
    if not token:
        raise RuntimeError("Copilot token response missing token")
    expires_at = parse_copilot_expires_at(response.get("expires_at"))
    save_copilot_api_token(
        {
            "token": token,
            "expires_at": expires_at,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return {
        "token": token,
        "expires_at": expires_at,
        "base_url": derive_copilot_api_base_url_from_token(token) or DEFAULT_COPILOT_API_BASE_URL,
    }


def call_copilot(config: dict, candidates: dict) -> dict:
    model = ((config.get("backend") or {}).get("settings") or {}).get("model")
    if not model:
        raise RuntimeError("backend.settings.model is required")
    github_token = load_copilot_github_token()
    runtime_auth = resolve_copilot_api_token(github_token)
    response = http_json(
        f"{runtime_auth['base_url'].rstrip('/')}/chat/completions",
        method="POST",
        headers=build_copilot_api_headers(runtime_auth["token"]),
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
    content = extract_text_content(response.get("choices", [{}])[0].get("message", {}).get("content", ""))
    return validate_editor_result(json.loads(strip_json_response(content)))


def mark(script: str, selected: dict) -> None:
    result = subprocess.run(
        ["python3", script],
        input=json.dumps(selected, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "").strip()
        raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=details)


def send_messages(config: dict, messages: list[dict]) -> bool:
    telegram = config.get("telegram", {})
    if not telegram.get("enabled"):
        for item in messages:
            print(item.get("text", "").strip())
            print()
        return True

    for item in messages:
        result = subprocess.run(
            ["python3", SEND_TELEGRAM],
            input=item.get("text", "").strip(),
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            details = (result.stderr or result.stdout or "").strip()
            raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=details)
    return True


def write_last_message(summary: str) -> None:
    os.makedirs(os.path.dirname(LAST_MESSAGE_FILE), exist_ok=True)
    with open(LAST_MESSAGE_FILE, "w", encoding="utf-8") as f:
        f.write(summary.strip() + "\n")


def main() -> int:
    config = load_config()
    language = config.get("language", "ko")
    mode = os.environ.get("NEWSLETTER_DELIVERY_MODE", "collect-and-deliver")
    log_line(f"RUN start backend=github_copilot mode={mode}")
    collect_if_needed()
    candidates = run_collect()
    if not candidates:
        summary = no_news_message(language)
        write_last_message(summary)
        log_line(f"SUMMARY {summary}")
        return 0

    result = call_copilot(config, candidates)
    summary = result.get("summary") or no_news_message(language)
    selected = result.get("selected") or {}
    messages = result.get("messages") or []

    if not selected or not messages:
        write_last_message(summary)
        log_line(f"SUMMARY {summary}")
        return 0

    mark(MARK_CURATED, selected)
    entry_count = selected_entry_count(selected)
    log_line(f"STATE curated entries={entry_count}")
    try:
        send_messages(config, messages)
        log_line(f"DELIVERY telegram messages={len(messages)} status=ok")
    except subprocess.CalledProcessError:
        mark(MARK_FAILED, selected)
        log_line(f"STATE send_failed entries={entry_count}")
        write_last_message(summary)
        log_line(f"SUMMARY {summary}")
        return 1

    mark(MARK_DELIVERED, selected)
    log_line(f"STATE delivered entries={entry_count}")
    write_last_message(summary)
    log_line(f"SUMMARY {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
