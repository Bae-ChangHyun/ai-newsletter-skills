#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path


DEFAULT_OWNER = "Bae-ChangHyun"
DEFAULT_REPO = "ai-newsletter-skills"
DEFAULT_REF = "main"


def run_installer(repo_root: Path, target: str) -> None:
    scripts = {
        "codex": repo_root / "scripts" / "install_codex.py",
        "claude": repo_root / "scripts" / "install_claude.py",
    }
    targets = ("codex", "claude") if target == "all" else (target,)

    for name in targets:
        script = scripts[name]
        subprocess.run([sys.executable, str(script)], check=True)


def local_repo_root() -> Path | None:
    current = Path(__file__).resolve().parent
    if (current / "scripts" / "install_codex.py").exists():
        return current
    return None


def download_repo(owner: str, repo: str, ref: str) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    url = f"https://codeload.github.com/{owner}/{repo}/tar.gz/{ref}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = resp.read()

    temp_dir_ctx = tempfile.TemporaryDirectory(prefix="ai-newsletter-skills-")
    temp_dir = Path(temp_dir_ctx.name)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for member in tar.getmembers():
            member_path = temp_dir / member.name
            if not str(member_path.resolve()).startswith(str(temp_dir.resolve())):
                raise RuntimeError(f"Unsafe archive member: {member.name}")
        tar.extractall(temp_dir)

    matches = [path for path in temp_dir.iterdir() if path.is_dir()]
    if len(matches) != 1:
        raise RuntimeError(f"Unexpected archive layout for {owner}/{repo}@{ref}")
    return temp_dir_ctx, matches[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install AI Newsletter Skills for Codex, Claude Code, or both without cloning the repository."
    )
    parser.add_argument(
        "--target",
        choices=("codex", "claude", "all"),
        default="all",
        help="installation target",
    )
    parser.add_argument("--owner", default=DEFAULT_OWNER, help="GitHub owner")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub repository name")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Git ref or branch name")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    repo_root = local_repo_root()
    if repo_root is not None:
        run_installer(repo_root, args.target)
        return

    temp_dir_ctx, downloaded_root = download_repo(args.owner, args.repo, args.ref)
    try:
        run_installer(downloaded_root, args.target)
    finally:
        temp_dir_ctx.cleanup()


if __name__ == "__main__":
    main()
