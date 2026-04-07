#!/usr/bin/env python3
"""GitHub Releases collector — fetches latest releases from configured repositories."""

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime as _dt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_collector import fetch_json, run_collector, format_output, load_runtime_config

DEFAULT_GITHUB_REPOS = [
    "pytorch/pytorch",
    "huggingface/transformers",
    "langchain-ai/langchain",
    "ollama/ollama",
    "openai/openai-python",
    "anthropics/anthropic-sdk-python",
]

MAX_WORKERS = 6
MAX_RELEASES_PER_REPO = 5
GITHUB_API_BASE = "https://api.github.com"


def _get_auth_headers():
    """Build auth headers from GITHUB_TOKEN env var or gh CLI."""
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return {"Authorization": f"Bearer {token}"}

    # Try gh CLI credential store
    try:
        import subprocess
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return {"Authorization": f"Bearer {result.stdout.strip()}"}
    except Exception:
        pass

    return {}


def _fetch_repo_releases(repo):
    """Fetch latest releases for a single repo."""
    import urllib.request
    import json

    url = f"{GITHUB_API_BASE}/repos/{repo}/releases?per_page={MAX_RELEASES_PER_REPO}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-newsletter-github/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    headers.update(_get_auth_headers())

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            releases = json.loads(resp.read())
    except Exception as e:
        print(f"WARN github_releases repo={repo} error={e}", file=sys.stderr)
        return []

    items = []
    for release in releases:
        if not isinstance(release, dict):
            continue
        # Skip drafts
        if release.get("draft", False):
            continue

        tag = release.get("tag_name", "")
        name = release.get("name", "") or tag
        html_url = release.get("html_url", "")
        body = (release.get("body") or "")[:300]
        prerelease = release.get("prerelease", False)
        published_at = release.get("published_at", "")

        ts = 0
        if published_at:
            try:
                text = published_at.strip()
                if text.endswith("Z"):
                    text = text[:-1] + "+00:00"
                dt = _dt.fromisoformat(text)
                ts = dt.timestamp()
            except Exception:
                pass

        if not html_url or not name:
            continue

        title = f"{repo} {name}"
        if prerelease:
            title += " (pre-release)"

        items.append({
            "title": title,
            "url": html_url,
            "source": repo,
            "time": ts,
            "score": 0,
            "description": body,
        })

    return items


def fetch_items(repos=None):
    """Fetch releases from all configured repos in parallel."""
    if repos is None:
        repos = DEFAULT_GITHUB_REPOS

    all_items = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(_fetch_repo_releases, repo): repo
            for repo in repos
        }
        for future in as_completed(futures):
            repo = futures[future]
            try:
                items = future.result()
                all_items.extend(items)
                print(
                    f"GITHUB_RELEASES repo={repo} items={len(items)}",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"GITHUB_RELEASES repo={repo} error={e}",
                    file=sys.stderr,
                )
    return all_items


def collect(repos=None):
    if repos is None:
        config = load_runtime_config()
        repos = config.get("github_repos", DEFAULT_GITHUB_REPOS)
    return run_collector("github_releases", lambda: fetch_items(repos))


if __name__ == "__main__":
    output = format_output(collect())
    if output:
        print(output)
    else:
        print("NO_NEW_GITHUB_RELEASES", file=sys.stderr)
