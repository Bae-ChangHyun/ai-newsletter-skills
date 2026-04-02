#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_ROOT = REPO_ROOT / "shared" / "newsletter"
TEMPLATES = REPO_ROOT / "targets" / "claude" / "templates"


def copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


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


def main() -> None:
    claude_home = Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude")).expanduser()
    skills_root = claude_home / "skills"
    runtime_root = skills_root / "newsletter-runtime"
    install_runtime(SHARED_ROOT, runtime_root)
    (runtime_root / ".data").mkdir(parents=True, exist_ok=True)

    replacements = {
        "__RUNTIME_ROOT__": str(runtime_root),
        "__DEFAULT_CLAUDE_BIN__": shutil.which("claude") or "claude",
    }

    for name in ("newsletter-onboard", "newsletter-now", "newsletter-start", "newsletter-stop", "newsletter-status"):
        render(TEMPLATES / f"{name}.SKILL.md.tpl", skills_root / name / "SKILL.md", replacements)

    render(TEMPLATES / "news-collector.md.tpl", runtime_root / "agents" / "news-collector.md", replacements)
    render(TEMPLATES / "run_with_claude.sh.tpl", runtime_root / "scripts" / "run_with_claude.sh", replacements)
    (runtime_root / "scripts" / "run_with_claude.sh").chmod(0o755)

    print(f"Installed Claude runtime: {runtime_root}")
    print("Installed skills: newsletter-onboard, newsletter-now, newsletter-start, newsletter-stop, newsletter-status")


if __name__ == "__main__":
    main()
