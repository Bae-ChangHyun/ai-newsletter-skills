#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
from pathlib import Path

from common_install import install_common_runtime, render


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = REPO_ROOT / "targets" / "claude" / "templates"


def main() -> None:
    common_home = Path(os.environ.get("AI_NEWSLETTER_HOME", Path.home() / ".ai-newsletter")).expanduser()
    runtime_root, bin_root = install_common_runtime(common_home)

    claude_home = Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude")).expanduser()
    skills_root = claude_home / "skills"

    replacements = {
        "__RUNTIME_ROOT__": str(runtime_root),
        "__DEFAULT_CLAUDE_BIN__": shutil.which("claude") or "claude",
    }

    for name in ("newsletter-onboard", "newsletter-doctor", "newsletter-now", "newsletter-history", "newsletter-start", "newsletter-stop", "newsletter-status"):
        render(TEMPLATES / f"{name}.SKILL.md.tpl", skills_root / name / "SKILL.md", replacements)

    render(TEMPLATES / "news-collector.md.tpl", runtime_root / "agents" / "news-collector.md", replacements)
    render(TEMPLATES / "run_with_claude.sh.tpl", runtime_root / "scripts" / "run_with_claude.sh", replacements)
    (runtime_root / "scripts" / "run_with_claude.sh").chmod(0o755)

    print(f"Installed shared runtime: {runtime_root}")
    print(f"Installed unified commands: {bin_root}")
    print("Installed Claude skills: newsletter-onboard, newsletter-doctor, newsletter-now, newsletter-history, newsletter-start, newsletter-stop, newsletter-status(alias)")


if __name__ == "__main__":
    main()
