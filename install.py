#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import os
import stat
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import urllib.request
from pathlib import Path


DEFAULT_OWNER = "Bae-ChangHyun"
DEFAULT_REPO = "ai-newsletter-skills"
DEFAULT_REF = "main"


def bootstrap_script(home_root: Path, owner: str, repo: str, ref: str) -> str:
    return textwrap.dedent(
        f"""\
        #!/usr/bin/env python3
        from __future__ import annotations

        import io
        import os
        import subprocess
        import sys
        import tarfile
        import tempfile
        import urllib.request
        from pathlib import Path

        OWNER = {owner!r}
        REPO = {repo!r}
        REF = {ref!r}
        HOME_ROOT = Path({str(home_root)!r})


        def download_ref(target_ref: str) -> tuple[tempfile.TemporaryDirectory[str], Path]:
            url = f"https://codeload.github.com/{{OWNER}}/{{REPO}}/tar.gz/{{target_ref}}"
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = resp.read()

            temp_dir_ctx = tempfile.TemporaryDirectory(prefix="ai-newsletter-skills-bootstrap-")
            temp_dir = Path(temp_dir_ctx.name)
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
                for member in tar.getmembers():
                    member_path = temp_dir / member.name
                    if not str(member_path.resolve()).startswith(str(temp_dir.resolve())):
                        raise RuntimeError(f"Unsafe archive member: {{member.name}}")
                tar.extractall(temp_dir)

            matches = [path for path in temp_dir.iterdir() if path.is_dir()]
            if len(matches) != 1:
                raise RuntimeError(f"Unexpected archive layout for {{OWNER}}/{{REPO}}@{{target_ref}}")
            return temp_dir_ctx, matches[0]

        def main() -> None:
            env = os.environ.copy()
            env["AI_NEWSLETTER_HOME"] = str(HOME_ROOT)
            temp_dir_ctx, repo_root = download_ref(REF)
            try:
                installer = repo_root / "scripts" / "install_common.py"
                if not installer.exists():
                    raise RuntimeError(f"Bootstrap installer not found in {{OWNER}}/{{REPO}}@{{REF}}")
                subprocess.run([sys.executable, str(repo_root / "scripts" / "install_common.py")], check=True, env=env)
                onboarding_js = HOME_ROOT / "runtime" / "scripts" / "newsletter_onboard.mjs"
                onboarding_py = HOME_ROOT / "runtime" / "scripts" / "newsletter_onboard.py"
                if onboarding_js.exists():
                    subprocess.run(["node", str(onboarding_js)], check=True, env=env)
                else:
                    subprocess.run([sys.executable, str(onboarding_py)], check=True, env=env)
            finally:
                temp_dir_ctx.cleanup()


        if __name__ == "__main__":
            main()
        """
    )


def local_bootstrap_script(home_root: Path, repo_root: Path) -> str:
    return textwrap.dedent(
        f"""\
        #!/usr/bin/env python3
        from __future__ import annotations

        import os
        import subprocess
        import sys
        from pathlib import Path

        HOME_ROOT = Path({str(home_root)!r})
        REPO_ROOT = Path({str(repo_root)!r})


        def main() -> None:
            env = os.environ.copy()
            env["AI_NEWSLETTER_HOME"] = str(HOME_ROOT)
            subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "install_common.py")], check=True, env=env)
            onboarding_js = HOME_ROOT / "runtime" / "scripts" / "newsletter_onboard.mjs"
            onboarding_py = HOME_ROOT / "runtime" / "scripts" / "newsletter_onboard.py"
            if onboarding_js.exists():
                subprocess.run(["node", str(onboarding_js)], check=True, env=env)
            else:
                subprocess.run([sys.executable, str(onboarding_py)], check=True, env=env)


        if __name__ == "__main__":
            main()
        """
    )


def write_bootstrap(home_root: Path, script_text: str, *, download_on_first_run: bool) -> None:
    bin_root = home_root / "bin"
    bin_root.mkdir(parents=True, exist_ok=True)

    bootstrap_py = home_root / "bootstrap_onboard.py"
    bootstrap_py.write_text(script_text, encoding="utf-8")
    bootstrap_py.chmod(bootstrap_py.stat().st_mode | stat.S_IXUSR)

    launcher = bin_root / "newsletter-onboard"
    launcher.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f'exec python3 "{bootstrap_py}"\n',
        encoding="utf-8",
    )
    launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR)

    local_bin = Path.home() / ".local" / "bin"
    path_entries = os.environ.get("PATH", "").split(os.pathsep)
    exposed = local_bin / "newsletter-onboard"
    linked = False
    local_bin.mkdir(parents=True, exist_ok=True)
    try:
        if exposed.exists() or exposed.is_symlink():
            exposed.unlink()
        exposed.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            f'exec "{launcher}" "$@"\n',
            encoding="utf-8",
        )
        exposed.chmod(exposed.stat().st_mode | stat.S_IXUSR)
        linked = True
    except OSError:
        linked = False

    print(f"Installed bootstrap onboarding launcher: {launcher}")
    print("Run this next:")
    if linked and str(local_bin) in path_entries:
        print("  newsletter-onboard")
    elif linked:
        print(f"  {exposed}")
    else:
        print(f"  {launcher}")
    if download_on_first_run:
        print("The first onboarding run will download and install the shared runtime automatically.")
    else:
        print("The first onboarding run will install the shared runtime from the current checkout automatically.")


def install_bootstrap(home_root: Path, owner: str, repo: str, ref: str) -> None:
    write_bootstrap(home_root, bootstrap_script(home_root, owner, repo, ref), download_on_first_run=True)


def install_local_bootstrap(home_root: Path, repo_root: Path) -> None:
    write_bootstrap(home_root, local_bootstrap_script(home_root, repo_root), download_on_first_run=False)


def run_installer(repo_root: Path, target: str) -> None:
    scripts = {
        "common": repo_root / "scripts" / "install_common.py",
        "codex": repo_root / "scripts" / "install_codex.py",
        "claude": repo_root / "scripts" / "install_claude.py",
    }
    targets = ("codex", "claude") if target == "all" else (target,)
    for name in targets:
        subprocess.run([sys.executable, str(scripts[name])], check=True)


def local_repo_root() -> Path | None:
    current = Path(__file__).resolve().parent
    if (current / "scripts" / "install_common.py").exists():
        return current
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install the AI Newsletter onboarding bootstrap or the full shared runtime."
    )
    parser.add_argument(
        "--target",
        choices=("bootstrap", "common", "codex", "claude", "all"),
        default="bootstrap",
        help="installation target",
    )
    parser.add_argument("--owner", default=DEFAULT_OWNER, help="GitHub owner")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub repository name")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Git ref or branch name")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    home_root = Path(os.environ.get("AI_NEWSLETTER_HOME", Path.home() / ".ai-newsletter")).expanduser()
    repo_root = local_repo_root()

    if args.target == "bootstrap":
        if repo_root is not None:
            install_local_bootstrap(home_root, repo_root)
        else:
            install_bootstrap(home_root, args.owner, args.repo, args.ref)
        return

    if repo_root is not None:
        run_installer(repo_root, args.target)
        return

    url = f"https://codeload.github.com/{args.owner}/{args.repo}/tar.gz/{args.ref}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = resp.read()

    temp_dir_ctx = tempfile.TemporaryDirectory(prefix="ai-newsletter-skills-")
    temp_dir = Path(temp_dir_ctx.name)
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            for member in tar.getmembers():
                member_path = temp_dir / member.name
                if not str(member_path.resolve()).startswith(str(temp_dir.resolve())):
                    raise RuntimeError(f"Unsafe archive member: {member.name}")
            tar.extractall(temp_dir)
        matches = [path for path in temp_dir.iterdir() if path.is_dir()]
        if len(matches) != 1:
            raise RuntimeError(f"Unexpected archive layout for {args.owner}/{args.repo}@{args.ref}")
        run_installer(matches[0], args.target)
    finally:
        temp_dir_ctx.cleanup()


if __name__ == "__main__":
    main()
