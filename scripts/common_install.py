#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_ROOT = REPO_ROOT / "shared" / "newsletter"
COMMON_TEMPLATES = REPO_ROOT / "targets" / "common" / "templates"
CODEX_TEMPLATES = REPO_ROOT / "targets" / "codex" / "templates"
CLAUDE_TEMPLATES = REPO_ROOT / "targets" / "claude" / "templates"


def copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def mergetree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for child in src.iterdir():
        if child.name == "__pycache__" or child.suffix == ".pyc":
            continue
        target = dst / child.name
        if child.is_dir():
            mergetree(child, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(child, target)


def install_runtime(src: Path, dst: Path) -> None:
    preserved_data_dir: Path | None = None

    if dst.exists():
        data_dir = dst / ".data"
        if data_dir.exists():
            temp_root = Path(tempfile.mkdtemp(prefix="newsletter-runtime-"))
            preserved_data_dir = temp_root / ".data"
            shutil.copytree(data_dir, preserved_data_dir)

    copytree(src, dst)

    if preserved_data_dir is not None:
        target_data_dir = dst / ".data"
        target_data_dir.mkdir(parents=True, exist_ok=True)
        for child in preserved_data_dir.iterdir():
            target_path = target_data_dir / child.name
            if target_path.exists():
                if target_path.is_dir():
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
            shutil.move(str(child), str(target_path))
        shutil.rmtree(preserved_data_dir.parent)


def render(src: Path, dst: Path, replacements: dict[str, str]) -> None:
    text = src.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace(key, value)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")


def install_common_runtime(home_root: Path) -> tuple[Path, Path]:
    runtime_root = home_root / "runtime"
    bin_root = home_root / "bin"
    local_bin_root = Path.home() / ".local" / "bin"
    install_runtime(SHARED_ROOT, runtime_root)
    (runtime_root / ".data").mkdir(parents=True, exist_ok=True)
    bin_root.mkdir(parents=True, exist_ok=True)
    local_bin_root.mkdir(parents=True, exist_ok=True)

    replacements = {
        "__REPO_ROOT__": str(REPO_ROOT),
        "__RUNTIME_ROOT__": str(runtime_root),
        "__HOME_ROOT__": str(home_root),
        "__DEFAULT_CODEX_BIN__": shutil.which("codex") or "codex",
        "__DEFAULT_CLAUDE_BIN__": shutil.which("claude") or "claude",
        "__DEFAULT_COPILOT_BIN__": shutil.which("copilot") or "copilot",
        "__DEFAULT_WORKDIR__": str(Path.home()),
    }

    render(COMMON_TEMPLATES / "newsletter_onboard.mjs.tpl", runtime_root / "scripts" / "newsletter_onboard.mjs", replacements)
    render(COMMON_TEMPLATES / "newsletter_dispatch.py.tpl", runtime_root / "scripts" / "newsletter_dispatch.py", replacements)
    render(COMMON_TEMPLATES / "newsletter_status.py.tpl", runtime_root / "scripts" / "newsletter_status.py", replacements)
    render(COMMON_TEMPLATES / "run_with_openai.py.tpl", runtime_root / "scripts" / "run_with_openai.py", replacements)
    render(COMMON_TEMPLATES / "run_with_copilot.py.tpl", runtime_root / "scripts" / "run_with_copilot.py", replacements)
    render(COMMON_TEMPLATES / "install_codex_backend.py.tpl", runtime_root / "scripts" / "install_codex_backend.py", replacements)
    render(COMMON_TEMPLATES / "install_claude_backend.py.tpl", runtime_root / "scripts" / "install_claude_backend.py", replacements)
    render(SHARED_ROOT / "prompts" / "generate_config.md.tpl", runtime_root / "prompts" / "generate_config.md", replacements)
    render(SHARED_ROOT / "prompts" / "run_newsletter_openai.md.tpl", runtime_root / "prompts" / "run_newsletter_openai.md", replacements)
    render(SHARED_ROOT / "prompts" / "run_newsletter_copilot.md.tpl", runtime_root / "prompts" / "run_newsletter_copilot.md", replacements)
    shutil.copy2(SHARED_ROOT / "prompts" / "run_newsletter_codex.md.tpl", runtime_root / "prompts" / "run_newsletter_codex.md.tpl")
    mergetree(CODEX_TEMPLATES, runtime_root / "integrations" / "codex")
    mergetree(CLAUDE_TEMPLATES, runtime_root / "integrations" / "claude")

    for name in (
        "newsletter-onboard",
        "newsletter-now",
        "newsletter-start",
        "newsletter-stop",
        "newsletter-status",
    ):
        command_path = bin_root / name
        render(COMMON_TEMPLATES / f"{name}.sh.tpl", command_path, replacements)
        command_path.chmod(0o755)
        link_path = local_bin_root / name
        if link_path.exists() or link_path.is_symlink():
            if link_path.is_symlink() or link_path.samefile(command_path):
                link_path.unlink()
            else:
                link_path.unlink()
        link_path.symlink_to(command_path)

    for script_name in (
        "newsletter_onboard.mjs",
        "newsletter_dispatch.py",
        "newsletter_status.py",
        "run_with_openai.py",
        "run_with_copilot.py",
        "install_codex_backend.py",
        "install_claude_backend.py",
    ):
        (runtime_root / "scripts" / script_name).chmod(0o755)

    return runtime_root, bin_root
