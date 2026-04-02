#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys


RUNTIME_ROOT = "__RUNTIME_ROOT__"
CONFIG_FILE = os.path.join(RUNTIME_ROOT, ".data", "config.json")


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def backend_type(config: dict) -> str:
    return ((config.get("backend") or {}).get("type") or "").strip()


def env_for_backend(config: dict) -> dict[str, str]:
    env = os.environ.copy()
    backend = backend_type(config)
    if backend == "claude":
        env["NEWSLETTER_RUNNER"] = os.path.join(RUNTIME_ROOT, "scripts", "run_with_claude.sh")
        env["NEWSLETTER_MARKER"] = "# claude-newsletter-runtime"
    elif backend == "codex":
        env["NEWSLETTER_RUNNER"] = os.path.join(RUNTIME_ROOT, "scripts", "run_with_codex.sh")
        env["NEWSLETTER_MARKER"] = "# codex-newsletter-runtime"
    elif backend == "openai":
        env["NEWSLETTER_RUNNER"] = os.path.join(RUNTIME_ROOT, "scripts", "run_with_openai.py")
        env["NEWSLETTER_MARKER"] = "# openai-newsletter-runtime"
    elif backend == "github_copilot":
        env["NEWSLETTER_RUNNER"] = os.path.join(RUNTIME_ROOT, "scripts", "run_with_copilot.py")
        env["NEWSLETTER_MARKER"] = "# github-copilot-newsletter-runtime"
    return env


def command_for_now(config: dict) -> list[str]:
    backend = backend_type(config)
    if backend == "claude":
        return [os.path.join(RUNTIME_ROOT, "scripts", "run_with_claude.sh")]
    if backend == "codex":
        return [os.path.join(RUNTIME_ROOT, "scripts", "run_with_codex.sh")]
    if backend == "openai":
        return ["python3", os.path.join(RUNTIME_ROOT, "scripts", "run_with_openai.py")]
    if backend == "github_copilot":
        return ["python3", os.path.join(RUNTIME_ROOT, "scripts", "run_with_copilot.py")]
    raise SystemExit(f"Unsupported backend: {backend}")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"now", "start", "stop", "status"}:
        raise SystemExit("Usage: newsletter_dispatch.py [now|start|stop|status]")

    config = load_config()
    if not config:
        raise SystemExit("No config saved yet. Run newsletter-onboard first.")

    command = sys.argv[1]
    env = env_for_backend(config)
    if command == "now":
        raise SystemExit(subprocess.run(command_for_now(config), env=env, check=False).returncode)

    manage = os.path.join(RUNTIME_ROOT, "scripts", "manage_cron.py")
    raise SystemExit(subprocess.run(["python3", manage, command], env=env, check=False).returncode)


if __name__ == "__main__":
    main()
