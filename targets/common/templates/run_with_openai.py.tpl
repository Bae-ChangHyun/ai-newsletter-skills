#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

from newsletter_backend_common import (
    extract_text_content,
    run_backend,
    strip_json_response,
    validate_editor_result,
)


PROMPT_FILE = "__RUNTIME_ROOT__/prompts/run_newsletter_openai.md"


def chat_endpoint(base_url: str) -> str:
    base_url = base_url.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


def call_openai_compatible(config: dict, candidates: dict, prompt_text: str) -> dict:
    editor = ((config.get("backend") or {}).get("settings") or {})
    base_url = editor.get("base_url")
    model = editor.get("model")
    api_key_env = editor.get("api_key_env", "OPENAI_API_KEY")
    api_key = __import__("os").environ.get(api_key_env)
    if not base_url or not model:
        raise RuntimeError("backend.settings.base_url and model are required")
    if not api_key:
        raise RuntimeError(f"{api_key_env} is not set")

    payload = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": prompt_text},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "language": config.get("language", "ko"),
                        "now_kst": __import__("datetime").datetime.now(__import__("datetime").timezone(__import__("datetime").timedelta(hours=9))).strftime("%Y-%m-%d %H:%M KST"),
                        "candidates": candidates,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
            },
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

    content = extract_text_content(data["choices"][0]["message"]["content"])
    return validate_editor_result(json.loads(strip_json_response(content)), "OpenAI-compatible")


if __name__ == "__main__":
    sys.exit(run_backend("openai", PROMPT_FILE, call_openai_compatible))
