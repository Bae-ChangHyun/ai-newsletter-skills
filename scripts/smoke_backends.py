#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from common_install import (  # type: ignore
    CLAUDE_TEMPLATES,
    CODEX_TEMPLATES,
    COMMON_TEMPLATES,
    REPO_ROOT as INSTALL_REPO_ROOT,
    SHARED_ROOT,
    install_runtime,
    mergetree,
    render,
)


FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "smoke"
BACKENDS = ("claude", "codex", "github_copilot", "openai")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run fixture-based smoke tests against one or more newsletter AI backends."
    )
    parser.add_argument(
        "--backend",
        default="all",
        choices=("all",) + BACKENDS,
        help="backend to run (default: all)",
    )
    parser.add_argument(
        "--mode",
        default="terminal",
        choices=("terminal", "telegram"),
        help="delivery mode for the smoke run",
    )
    parser.add_argument(
        "--skip-missing",
        action="store_true",
        help="skip backends whose credentials/CLI prerequisites are missing",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="keep the temporary smoke runtime for debugging",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="per-backend newsletter-now timeout in seconds (default: 180)",
    )
    return parser.parse_args()


def selected_backends(name: str) -> list[str]:
    if name == "all":
        return list(BACKENDS)
    return [name]


def actual_home() -> Path:
    return Path(os.path.expanduser("~")).resolve()


def load_saved_runtime_config() -> dict:
    config_path = actual_home() / ".ai-newsletter" / "runtime" / ".data" / "config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def render_common_runtime(home_root: Path) -> Path:
    runtime_root = home_root / "runtime"
    install_runtime(SHARED_ROOT, runtime_root)
    (runtime_root / ".data").mkdir(parents=True, exist_ok=True)
    (runtime_root / "scripts").mkdir(parents=True, exist_ok=True)
    (runtime_root / "prompts").mkdir(parents=True, exist_ok=True)

    replacements = {
        "__REPO_ROOT__": str(INSTALL_REPO_ROOT),
        "__RUNTIME_ROOT__": str(runtime_root),
        "__HOME_ROOT__": str(home_root),
        "__DEFAULT_CODEX_BIN__": shutil.which("codex") or "codex",
        "__DEFAULT_CLAUDE_BIN__": shutil.which("claude") or "claude",
        "__DEFAULT_COPILOT_BIN__": shutil.which("copilot") or "copilot",
        "__DEFAULT_WORKDIR__": str(actual_home()),
    }

    for template_name, target_name in (
        ("newsletter_onboard.mjs.tpl", "newsletter_onboard.mjs"),
        ("newsletter_onboard_support.mjs.tpl", "newsletter_onboard_support.mjs"),
        ("newsletter_dispatch.py.tpl", "newsletter_dispatch.py"),
        ("newsletter_status.py.tpl", "newsletter_status.py"),
        ("run_with_openai.py.tpl", "run_with_openai.py"),
        ("run_with_copilot.py.tpl", "run_with_copilot.py"),
        ("install_codex_backend.py.tpl", "install_codex_backend.py"),
        ("install_claude_backend.py.tpl", "install_claude_backend.py"),
    ):
        render(COMMON_TEMPLATES / template_name, runtime_root / "scripts" / target_name, replacements)

    render(SHARED_ROOT / "prompts" / "generate_config.md.tpl", runtime_root / "prompts" / "generate_config.md", replacements)
    render(SHARED_ROOT / "prompts" / "normalize_schedule.md.tpl", runtime_root / "prompts" / "normalize_schedule.md", replacements)
    render(SHARED_ROOT / "prompts" / "run_newsletter_claude.md.tpl", runtime_root / "prompts" / "run_newsletter_claude.md", replacements)
    render(SHARED_ROOT / "prompts" / "run_newsletter_openai.md.tpl", runtime_root / "prompts" / "run_newsletter_openai.md", replacements)
    render(SHARED_ROOT / "prompts" / "run_newsletter_copilot.md.tpl", runtime_root / "prompts" / "run_newsletter_copilot.md", replacements)
    shutil.copy2(SHARED_ROOT / "prompts" / "run_newsletter_codex.md.tpl", runtime_root / "prompts" / "run_newsletter_codex.md.tpl")

    mergetree(CODEX_TEMPLATES, runtime_root / "integrations" / "codex")
    mergetree(CLAUDE_TEMPLATES, runtime_root / "integrations" / "claude")

    for script in (runtime_root / "scripts").glob("*"):
        if script.is_file():
            script.chmod(0o755)

    return runtime_root


def install_backend_runtime(runtime_root: Path, backend: str, env: dict[str, str]) -> None:
    if backend == "codex":
        subprocess.run(["python3", str(runtime_root / "scripts" / "install_codex_backend.py")], check=True, env=env)
    elif backend == "claude":
        subprocess.run(["python3", str(runtime_root / "scripts" / "install_claude_backend.py")], check=True, env=env)


def backend_prereq(backend: str) -> tuple[bool, str]:
    user_home = actual_home()
    if backend == "codex":
        return (shutil.which("codex") is not None, "codex CLI not found")
    if backend == "claude":
        return (shutil.which("claude") is not None, "claude CLI not found")
    if backend == "github_copilot":
        token_file = user_home / ".ai-newsletter" / "runtime" / ".data" / "credentials" / "github_copilot_github_token.json"
        return (token_file.exists(), f"missing GitHub Copilot token cache: {token_file}")
    if backend == "openai":
        base_url = os.environ.get("SMOKE_OPENAI_BASE_URL")
        model = os.environ.get("SMOKE_OPENAI_MODEL")
        api_key = os.environ.get(os.environ.get("SMOKE_OPENAI_API_KEY_ENV", "OPENAI_API_KEY"))
        if not base_url:
            return False, "SMOKE_OPENAI_BASE_URL is not set"
        if not model:
            return False, "SMOKE_OPENAI_MODEL is not set"
        if not api_key:
            return False, f"{os.environ.get('SMOKE_OPENAI_API_KEY_ENV', 'OPENAI_API_KEY')} is not set"
        return True, "ok"
    return False, f"unsupported backend: {backend}"


def backend_config_overlay(backend: str, saved_config: dict) -> dict:
    saved_backend = (saved_config.get("backend") or {}).get("settings") or {}
    if backend == "claude":
        return {"backend": {"type": "claude", "settings": {}}}
    if backend == "codex":
        return {"backend": {"type": "codex", "settings": {}}}
    if backend == "github_copilot":
        saved_model = ""
        if ((saved_config.get("backend") or {}).get("type") or "").strip() == "github_copilot":
            saved_model = str(saved_backend.get("model") or "").strip()
        return {
            "backend": {
                "type": "github_copilot",
                "settings": {
                    "model": os.environ.get("SMOKE_COPILOT_MODEL") or saved_model or "gpt-4o",
                    "auth_flow": "device_flow",
                },
            }
        }
    if backend == "openai":
        saved_base_url = ""
        saved_model = ""
        saved_api_key_env = ""
        if ((saved_config.get("backend") or {}).get("type") or "").strip() == "openai":
            saved_base_url = str(saved_backend.get("base_url") or "").strip()
            saved_model = str(saved_backend.get("model") or "").strip()
            saved_api_key_env = str(saved_backend.get("api_key_env") or "").strip()
        return {
            "backend": {
                "type": "openai",
                "settings": {
                    "base_url": os.environ.get("SMOKE_OPENAI_BASE_URL") or saved_base_url,
                    "model": os.environ.get("SMOKE_OPENAI_MODEL") or saved_model,
                    "api_key_env": os.environ.get("SMOKE_OPENAI_API_KEY_ENV") or saved_api_key_env or "OPENAI_API_KEY",
                },
            }
        }
    raise ValueError(f"unsupported backend: {backend}")


def load_base_config() -> dict:
    with open(FIXTURE_DIR / "base_config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def configure_delivery(config: dict, mode: str) -> dict:
    if mode == "terminal":
        config["telegram"] = {"enabled": False}
        return config

    token = os.environ.get("SMOKE_TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("SMOKE_TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("telegram mode requires SMOKE_TELEGRAM_BOT_TOKEN (or TELEGRAM_BOT_TOKEN) and SMOKE_TELEGRAM_CHAT_ID")
    config["telegram"] = {
        "enabled": True,
        "bot_token": token,
        "chat_id": chat_id,
    }
    return config


def write_runtime_config(runtime_root: Path, backend: str, mode: str) -> Path:
    config = load_base_config()
    config.update(backend_config_overlay(backend, load_saved_runtime_config()))
    configure_delivery(config, mode)
    config_path = runtime_root / ".data" / "config.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return config_path


def copy_fixture_seen_files(runtime_root: Path) -> None:
    data_dir = runtime_root / ".data"
    for seen_file in FIXTURE_DIR.glob("*_seen.jsonl"):
        shutil.copy2(seen_file, data_dir / seen_file.name)


def copy_copilot_credentials(runtime_root: Path) -> None:
    source_dir = actual_home() / ".ai-newsletter" / "runtime" / ".data" / "credentials"
    target_dir = runtime_root / ".data" / "credentials"
    if not source_dir.exists():
        return
    target_dir.mkdir(parents=True, exist_ok=True)
    for name in ("github_copilot_github_token.json", "github_copilot_api_token.json"):
        source = source_dir / name
        if source.exists():
            shutil.copy2(source, target_dir / name)


def copy_codex_profile(temp_root: Path) -> None:
    source_root = actual_home() / ".codex"
    target_root = temp_root / ".codex"
    target_root.mkdir(parents=True, exist_ok=True)
    for name in ("auth.json", "config.toml", "version.json", "models_cache.json"):
        source = source_root / name
        if source.exists():
            shutil.copy2(source, target_root / name)


def copy_claude_profile(temp_root: Path) -> None:
    source_root = actual_home() / ".claude"
    target_root = temp_root / ".claude"
    target_root.mkdir(parents=True, exist_ok=True)
    for name in (".credentials.json", "settings.json", "settings.local.json", "CLAUDE.md", "RTK.md"):
        source = source_root / name
        if source.exists():
            shutil.copy2(source, target_root / name)


def build_backend_env(temp_root: Path, runtime_root: Path, mode: str) -> dict[str, str]:
    env = os.environ.copy()
    env["AI_NEWSLETTER_HOME"] = str(temp_root)
    env["CODEX_HOME"] = str(temp_root / ".codex")
    env["CLAUDE_HOME"] = str(temp_root / ".claude")
    env["NEWSLETTER_DELIVERY_MODE"] = "deliver-only"
    env["PYTHONPATH"] = os.pathsep.join(
        [str(runtime_root / "scripts"), env.get("PYTHONPATH", "")]
    ).strip(os.pathsep)
    if mode == "telegram":
        token = os.environ.get("SMOKE_TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
        if token:
            env["TELEGRAM_BOT_TOKEN"] = token
    return env


def run_command(command: list[str], env: dict[str, str], timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, env=env, check=False, timeout=timeout)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def run_smoke_for_backend(backend: str, mode: str, timeout: int) -> dict:
    ok, reason = backend_prereq(backend)
    if not ok:
        return {"backend": backend, "status": "skipped", "reason": reason}

    temp_ctx = tempfile.TemporaryDirectory(prefix=f"newsletter-smoke-{backend}-")
    temp_root = Path(temp_ctx.name)
    try:
        runtime_root = render_common_runtime(temp_root)
        env = build_backend_env(temp_root, runtime_root, mode)
        if backend == "codex":
            copy_codex_profile(temp_root)
        if backend == "claude":
            copy_claude_profile(temp_root)
        if backend == "github_copilot":
            copy_copilot_credentials(runtime_root)
        install_backend_runtime(runtime_root, backend, env)
        write_runtime_config(runtime_root, backend, mode)
        copy_fixture_seen_files(runtime_root)

        now_result = run_command(["python3", str(runtime_root / "scripts" / "newsletter_dispatch.py"), "now"], env, timeout=timeout)
        doctor_result = run_command(["python3", str(runtime_root / "scripts" / "newsletter_doctor.py")], env)
        history_result = run_command(["python3", str(runtime_root / "scripts" / "newsletter_history.py"), "--limit", "5", "--summary-limit", "3"], env)

        summary = read_text(runtime_root / ".data" / "last_run.txt")
        delivered_entries = 0
        for seen_file in (runtime_root / ".data").glob("*_seen.jsonl"):
            delivered_entries += sum(
                1
                for line in seen_file.read_text(encoding="utf-8").splitlines()
                if line.strip() and json.loads(line).get("state") == "sent"
            )

        status = "passed" if now_result.returncode == 0 and summary and delivered_entries > 0 else "failed"
        return {
            "backend": backend,
            "status": status,
            "reason": "" if status == "passed" else ("newsletter-now completed without delivered state updates" if now_result.returncode == 0 and summary else "newsletter-now failed"),
            "summary": summary,
            "delivered_entries": delivered_entries,
            "now_stdout": now_result.stdout.strip(),
            "now_stderr": now_result.stderr.strip(),
            "doctor_stdout": doctor_result.stdout.strip(),
            "history_stdout": history_result.stdout.strip(),
            "temp_root": str(temp_root),
            "_temp_ctx": temp_ctx,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "backend": backend,
            "status": "failed",
            "reason": f"newsletter-now timed out after {timeout}s",
            "now_stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "now_stderr": (exc.stderr or "").strip() if isinstance(exc.stderr, str) else "",
            "temp_root": str(temp_root),
            "_temp_ctx": temp_ctx,
        }
    except Exception as exc:  # pragma: no cover - smoke harness defensive fallback
        return {
            "backend": backend,
            "status": "failed",
            "reason": str(exc),
            "temp_root": str(temp_root),
            "_temp_ctx": temp_ctx,
        }


def print_report(results: list[dict]) -> None:
    print("Backend smoke results")
    print("=====================")
    for result in results:
        print(f"- {result['backend']}: {result['status']}")
        if result.get("reason"):
            print(f"  reason: {result['reason']}")
        if result.get("summary"):
            print(f"  summary: {result['summary']}")
        if "delivered_entries" in result:
            print(f"  delivered_entries: {result['delivered_entries']}")
        if result.get("doctor_stdout"):
            print("  doctor:")
            for line in result["doctor_stdout"].splitlines()[:8]:
                print(f"    {line}")
        if result.get("history_stdout"):
            print("  history:")
            for line in result["history_stdout"].splitlines()[:8]:
                print(f"    {line}")
        if result["status"] == "failed":
            if result.get("temp_root"):
                print(f"  temp_root: {result['temp_root']}")
            if result.get("now_stdout"):
                print("  now stdout:")
                for line in result["now_stdout"].splitlines()[:12]:
                    print(f"    {line}")
            if result.get("now_stderr"):
                print("  now stderr:")
                for line in result["now_stderr"].splitlines()[:12]:
                    print(f"    {line}")


def cleanup_results(results: list[dict], keep_temp: bool) -> None:
    for result in results:
        temp_ctx = result.pop("_temp_ctx", None)
        if temp_ctx is None:
            continue
        if keep_temp:
            continue
        temp_ctx.cleanup()


def main() -> int:
    args = parse_args()
    results: list[dict] = []
    for backend in selected_backends(args.backend):
        result = run_smoke_for_backend(backend, args.mode, args.timeout)
        if result["status"] == "skipped" and not args.skip_missing:
            results.append(result)
            print_report(results)
            cleanup_results(results, args.keep_temp)
            return 1
        results.append(result)

    print_report(results)
    exit_code = 0
    for result in results:
        if result["status"] == "failed":
            exit_code = 1
            break
        if result["status"] == "skipped" and not args.skip_missing:
            exit_code = 1
            break

    cleanup_results(results, args.keep_temp)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
