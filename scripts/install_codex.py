#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
from pathlib import Path

from common_install import install_common_runtime, render

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = REPO_ROOT / "targets" / "codex" / "templates"


def main() -> None:
    common_home = Path(os.environ.get("AI_NEWSLETTER_HOME", Path.home() / ".ai-newsletter")).expanduser()
    runtime_root, bin_root = install_common_runtime(common_home)

    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    skills_root = codex_home / "skills"

    replacements = {
        "__RUNTIME_ROOT__": str(runtime_root),
        "__DEFAULT_CODEX_BIN__": shutil.which("codex") or "/home/bch/.nvm/versions/node/v20.20.1/bin/codex",
        "__DEFAULT_WORKDIR__": str(Path.home()),
    }

    for name in ("newsletter-now", "newsletter-start", "newsletter-stop", "newsletter-status"):
        render(TEMPLATES / f"{name}.SKILL.md.tpl", skills_root / name / "SKILL.md", replacements)

    render(TEMPLATES / "run_with_codex.sh.tpl", runtime_root / "scripts" / "run_with_codex.sh", replacements)
    (runtime_root / "scripts" / "run_with_codex.sh").chmod(0o755)
    render(REPO_ROOT / "shared" / "newsletter" / "prompts" / "run_newsletter_codex.md.tpl", runtime_root / "prompts" / "run_newsletter.md", replacements)

    print(f"Installed shared runtime: {runtime_root}")
    print(f"Installed unified commands: {bin_root}")
    print("Installed Codex skills: newsletter-now, newsletter-start, newsletter-stop, newsletter-status")


if __name__ == "__main__":
    main()
