#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
from pathlib import Path


RUNTIME_ROOT = Path("__RUNTIME_ROOT__")
TEMPLATES = RUNTIME_ROOT / "integrations" / "claude"
CLAUDE_HOME = Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude")).expanduser()
SKILLS_ROOT = CLAUDE_HOME / "skills"


def render(src: Path, dst: Path, replacements: dict[str, str]) -> None:
    text = src.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace(key, value)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")


def main() -> None:
    runtime_token = "__" + "RUNTIME_ROOT__"
    claude_bin_token = "__" + "DEFAULT_CLAUDE_BIN__"
    replacements = {
        runtime_token: str(RUNTIME_ROOT),
        claude_bin_token: shutil.which("claude") or "claude",
    }
    for name in ("newsletter-onboard", "newsletter-doctor", "newsletter-now", "newsletter-history", "newsletter-start", "newsletter-stop", "newsletter-status"):
        render(TEMPLATES / f"{name}.SKILL.md.tpl", SKILLS_ROOT / name / "SKILL.md", replacements)
    render(TEMPLATES / "news-collector.md.tpl", RUNTIME_ROOT / "agents" / "news-collector.md", replacements)
    render(TEMPLATES / "run_with_claude.sh.tpl", RUNTIME_ROOT / "scripts" / "run_with_claude.sh", replacements)
    (RUNTIME_ROOT / "scripts" / "run_with_claude.sh").chmod(0o755)
    print("Installed Claude backend integration.")


if __name__ == "__main__":
    main()
