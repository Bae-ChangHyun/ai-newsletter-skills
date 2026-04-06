#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from common_install import install_common_runtime


def ensure_clack(home_root: Path) -> None:
    node_modules = home_root / "node_modules" / "@clack" / "prompts"
    if node_modules.exists():
        return
    if shutil.which("node") is None:
        raise RuntimeError("node is required to run newsletter-onboard")
    if shutil.which("npm") is None:
        raise RuntimeError("npm is required to install @clack/prompts for newsletter-onboard")
    subprocess.run(
        [
            "npm",
            "install",
            "--prefix",
            str(home_root),
            "@clack/prompts@1.2.0",
        ],
        check=True,
    )


def main() -> None:
    common_home = Path(os.environ.get("AI_NEWSLETTER_HOME", Path.home() / ".ai-newsletter")).expanduser()
    ensure_clack(common_home)
    runtime_root, bin_root = install_common_runtime(common_home)
    print(f"Installed shared runtime: {runtime_root}")
    print(f"Installed unified commands: {bin_root}")
    print("Unified commands: newsletter-onboard, newsletter-doctor, newsletter-history, newsletter-now, newsletter-start, newsletter-stop, newsletter-status(alias)")


if __name__ == "__main__":
    main()
