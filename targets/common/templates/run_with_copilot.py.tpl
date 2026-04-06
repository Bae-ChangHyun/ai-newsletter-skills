#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from urllib import error, request

from newsletter_backend_common import (
    extract_text_content,
    run_backend,
    strip_json_response,
    validate_editor_result,
)


PROMPT_FILE = "__RUNTIME_ROOT__/prompts/run_newsletter_copilot.md"
RUNTIME_ROOT = "__RUNTIME_ROOT__"
COPILOT_GITHUB_TOKEN_FILE = os.path.join(RUNTIME_ROOT, ".data", "credentials", "github_copilot_github_token.json")
COPILOT_API_TOKEN_FILE = os.path.join(RUNTIME_ROOT, ".data", "credentials", "github_copilot_api_token.json")
GITHUB_COPILOT_CLIENT_ID = "Iv1.b507a08c87ecfe98"
COPILOT_TOKEN_URL = "https://api.github.com/copilot_internal/v2/token"
DEFAULT_COPILOT_API_BASE_URL = "https://api.individual.githubcopilot.com"
COPILOT_IDE_USER_AGENT = "GitHubCopilotChat/0.26.7"
COPILOT_EDITOR_VERSION = "vscode/1.96.2"
KST = timezone(timedelta(hours=9))


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


def call_copilot(config: dict, candidates: dict, prompt_text: str) -> dict:
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
                {"role": "system", "content": prompt_text},
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
    return validate_editor_result(json.loads(strip_json_response(content)), "GitHub Copilot")


if __name__ == "__main__":
    sys.exit(run_backend("github_copilot", PROMPT_FILE, call_copilot))
