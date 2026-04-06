#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from smoke_backends import (  # type: ignore
    actual_home,
    backend_prereq,
    build_backend_env,
    copy_claude_profile,
    copy_copilot_credentials,
    copy_codex_profile,
    copy_fixture_seen_files,
    install_backend_runtime,
    load_base_config,
    print_report,
    render_common_runtime,
    selected_backends,
)

import shutil
import subprocess
import tempfile


BACKENDS = ("claude", "codex", "github_copilot", "openai")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register a near-future cron smoke run and verify automatic cleanup.")
    parser.add_argument("--backend", default="all", choices=("all",) + BACKENDS)
    parser.add_argument("--skip-missing", action="store_true")
    parser.add_argument("--timeout", type=int, default=150, help="max seconds to wait for cron execution")
    parser.add_argument("--keep-temp", action="store_true")
    return parser.parse_args()


def next_minute_schedule() -> tuple[str, str]:
    now = datetime.now()
    delta_minutes = 2 if now.second >= 50 else 1
    target = now + timedelta(minutes=delta_minutes)
    cron = f"{target.minute} {target.hour} * * *"
    label = target.strftime("%Y-%m-%d %H:%M")
    return cron, label


def backend_config_overlay(backend: str) -> dict:
    saved_config = {}
    config_path = actual_home() / ".ai-newsletter" / "runtime" / ".data" / "config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            saved_config = json.load(f)
    except FileNotFoundError:
        saved_config = {}

    saved_backend = (saved_config.get("backend") or {}).get("settings") or {}
    if backend == "claude":
        return {"backend": {"type": "claude", "settings": {}}}
    if backend == "codex":
        return {"backend": {"type": "codex", "settings": {}}}
    if backend == "github_copilot":
        saved_model = ""
        if ((saved_config.get("backend") or {}).get("type") or "").strip() == "github_copilot":
            saved_model = str(saved_backend.get("model") or "").strip()
        return {"backend": {"type": "github_copilot", "settings": {"model": os.environ.get("SMOKE_COPILOT_MODEL") or saved_model or "gpt-4o", "auth_flow": "device_flow"}}}
    if backend == "openai":
        saved_base_url = ""
        saved_model = ""
        saved_api_key_env = ""
        if ((saved_config.get("backend") or {}).get("type") or "").strip() == "openai":
            saved_base_url = str(saved_backend.get("base_url") or "").strip()
            saved_model = str(saved_backend.get("model") or "").strip()
            saved_api_key_env = str(saved_backend.get("api_key_env") or "").strip()
        return {"backend": {"type": "openai", "settings": {"base_url": os.environ.get("SMOKE_OPENAI_BASE_URL") or saved_base_url, "model": os.environ.get("SMOKE_OPENAI_MODEL") or saved_model, "api_key_env": os.environ.get("SMOKE_OPENAI_API_KEY_ENV") or saved_api_key_env or "OPENAI_API_KEY"}}}
    raise ValueError(f"unsupported backend: {backend}")


def write_cron_config(runtime_root: Path, backend: str) -> None:
    cron, label = next_minute_schedule()
    config = load_base_config()
    config.update(backend_config_overlay(backend))
    config["telegram"] = {"enabled": False}
    config["schedule"] = {"cron": cron, "label": label}
    (runtime_root / ".data" / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def register_and_wait(backend: str, timeout: int) -> dict:
    ok, reason = backend_prereq(backend)
    if not ok:
        return {"backend": backend, "status": "skipped", "reason": reason}

    temp_ctx = tempfile.TemporaryDirectory(prefix=f"newsletter-cron-smoke-{backend}-")
    temp_root = Path(temp_ctx.name)
    try:
        runtime_root = render_common_runtime(temp_root)
        env = build_backend_env(temp_root, runtime_root, "terminal")
        env["NEWSLETTER_SMOKE_SKIP_COLLECTOR"] = "1"
        env["NEWSLETTER_SMOKE_SKIP_IMMEDIATE_COLLECT"] = "1"
        if backend == "codex":
            copy_codex_profile(temp_root)
        if backend == "claude":
            copy_claude_profile(temp_root)
        if backend == "github_copilot":
            copy_copilot_credentials(runtime_root)

        install_backend_runtime(runtime_root, backend, env)
        write_cron_config(runtime_root, backend)
        copy_fixture_seen_files(runtime_root)

        start = subprocess.run(["python3", str(runtime_root / "scripts" / "newsletter_dispatch.py"), "start"], env=env, capture_output=True, text=True, check=False)
        start_ok = start.returncode == 0
        status_text = subprocess.run(["python3", str(runtime_root / "scripts" / "newsletter_dispatch.py"), "status"], env=env, capture_output=True, text=True, check=False).stdout.strip()

        deadline = time.time() + timeout
        last_run = runtime_root / ".data" / "last_run.txt"
        delivery_log = runtime_root / ".data" / "delivery.log"
        summary = ""
        delivered_entries = 0
        while time.time() < deadline:
            delivered_entries = 0
            for seen_file in (runtime_root / ".data").glob("*_seen.jsonl"):
                for line in seen_file.read_text(encoding="utf-8").splitlines():
                    if line.strip() and json.loads(line).get("state") == "sent":
                        delivered_entries += 1
            if delivered_entries > 0:
                if last_run.exists() and last_run.read_text(encoding="utf-8").strip():
                    summary = last_run.read_text(encoding="utf-8").strip()
                elif delivery_log.exists() and delivery_log.read_text(encoding="utf-8").strip():
                    summary = delivery_log.read_text(encoding="utf-8").strip().splitlines()[-1]
                break
            time.sleep(5)

        stop = subprocess.run(["python3", str(runtime_root / "scripts" / "newsletter_dispatch.py"), "stop"], env=env, capture_output=True, text=True, check=False)
        after_stop = subprocess.run(["python3", str(runtime_root / "scripts" / "newsletter_dispatch.py"), "status"], env=env, capture_output=True, text=True, check=False).stdout.strip()

        cron_removed = "delivery:" not in after_stop and "collector:" not in after_stop
        passed = start_ok and delivered_entries > 0 and cron_removed

        return {
            "backend": backend,
            "status": "passed" if passed else "failed",
            "reason": "" if passed else "cron run did not complete cleanly",
            "summary": summary,
            "delivered_entries": delivered_entries,
            "start_stdout": start.stdout.strip(),
            "start_stderr": start.stderr.strip(),
            "status_stdout": status_text,
            "stop_stdout": stop.stdout.strip(),
            "after_stop": after_stop,
            "temp_root": str(temp_root),
            "_temp_ctx": temp_ctx,
        }
    except Exception as exc:  # pragma: no cover
        return {"backend": backend, "status": "failed", "reason": str(exc), "temp_root": str(temp_root), "_temp_ctx": temp_ctx}


def cleanup(results: list[dict], keep_temp: bool) -> None:
    for result in results:
        temp_ctx = result.pop("_temp_ctx", None)
        if temp_ctx is not None and not keep_temp:
            temp_ctx.cleanup()


def main() -> int:
    args = parse_args()
    results = []
    for backend in selected_backends(args.backend):
        result = register_and_wait(backend, args.timeout)
        if result["status"] == "skipped" and not args.skip_missing:
            results.append(result)
            print_report(results)
            cleanup(results, args.keep_temp)
            return 1
        results.append(result)

    print_report(results)
    for result in results:
        if result["status"] == "failed":
            cleanup(results, args.keep_temp)
            return 1
        if result["status"] == "skipped" and not args.skip_missing:
            cleanup(results, args.keep_temp)
            return 1
    cleanup(results, args.keep_temp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
