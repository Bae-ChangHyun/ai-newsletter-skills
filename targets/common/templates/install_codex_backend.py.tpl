#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path


RUNTIME_ROOT = Path("__RUNTIME_ROOT__")
TEMPLATES = RUNTIME_ROOT / "integrations" / "codex"
PROMPT_TEMPLATE = RUNTIME_ROOT / "prompts" / "run_newsletter_codex.md.tpl"
CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
SKILLS_ROOT = CODEX_HOME / "skills"


def render(src: Path, dst: Path, replacements: dict[str, str]) -> None:
    text = src.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace(key, value)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")


def main() -> None:
    replacements = {
        "__RUNTIME_ROOT__": str(RUNTIME_ROOT),
        "__DEFAULT_CODEX_BIN__": "__DEFAULT_CODEX_BIN__",
        "__DEFAULT_WORKDIR__": "__DEFAULT_WORKDIR__",
    }
    for name in ("newsletter-now", "newsletter-start", "newsletter-stop", "newsletter-status"):
        render(TEMPLATES / f"{name}.SKILL.md.tpl", SKILLS_ROOT / name / "SKILL.md", replacements)
    render(TEMPLATES / "run_with_codex.sh.tpl", RUNTIME_ROOT / "scripts" / "run_with_codex.sh", replacements)
    (RUNTIME_ROOT / "scripts" / "run_with_codex.sh").chmod(0o755)
    render(PROMPT_TEMPLATE, RUNTIME_ROOT / "prompts" / "run_newsletter.md", replacements)
    print("Installed Codex backend integration.")


if __name__ == "__main__":
    main()
