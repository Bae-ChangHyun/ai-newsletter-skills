#!/usr/bin/env python3
"""JSONL → PostgreSQL bridge.

Reads {platform}_seen.jsonl files produced by existing collectors
and upserts articles into the PostgreSQL database (Supabase).

Usage:
    python ingest_to_db.py                  # ingest all platforms
    python ingest_to_db.py hn reddit        # ingest specific platforms

DB connection is read from (in order):
    1. DATABASE_URL environment variable
    2. .data/config.json  →  database.url
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    sys.exit(
        "psycopg2 is required. Install with: pip install psycopg2-binary"
    )

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base_collector import (
    DATA_DIR,
    get_seen_file,
    load_seen,
    canonicalize_url,
)

# Platform name → source slug (must match seed.ts SEED_SOURCES)
PLATFORM_SOURCE_MAP = {
    "hn": "hn",
    "reddit": "reddit",
    "geeknews": "geeknews",
    "tldr": "tldr",
    "threads": None,  # no dedicated source slug yet
    "velopers": "velopers",
    "devday": "devday",
}

ALL_PLATFORMS = list(PLATFORM_SOURCE_MAP.keys())


def get_db_url():
    """Resolve database URL from env or config."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return url

    config_path = os.path.join(DATA_DIR, "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        url = config.get("database", {}).get("url")
        if url:
            return url
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    sys.exit(
        "No database URL found. Set DATABASE_URL env var or add "
        "database.url to .data/config.json"
    )


def connect(db_url):
    """Create and return a psycopg2 connection."""
    conn = psycopg2.connect(db_url)
    conn.autocommit = False
    return conn


def load_source_map(conn):
    """Load slug → id mapping from sources table."""
    with conn.cursor() as cur:
        cur.execute("SELECT slug, id FROM sources")
        return {row[0]: row[1] for row in cur.fetchall()}


def ts_to_datetime(ts):
    """Convert unix timestamp to datetime, or None."""
    if not ts or ts == 0:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def ingest_platform(conn, platform, source_map):
    """Ingest one platform's JSONL into the articles table.

    Returns (inserted, updated) counts.
    """
    source_slug = PLATFORM_SOURCE_MAP.get(platform)
    source_id = source_map.get(source_slug) if source_slug else None

    if source_id is None:
        print(
            f"  SKIP {platform}: no matching source in DB "
            f"(slug={source_slug!r})",
            file=sys.stderr,
        )
        return 0, 0

    seen_file = get_seen_file(platform)
    seen = load_seen(seen_file)

    if not seen:
        print(f"  SKIP {platform}: empty or missing JSONL", file=sys.stderr)
        return 0, 0

    inserted = 0
    updated = 0

    with conn.cursor() as cur:
        for canonical_url, entry in seen.items():
            if not canonical_url:
                continue

            title = entry.get("title", "").strip()
            if not title:
                continue

            url = entry.get("url", canonical_url)
            score = entry.get("score", 0) or 0
            comment_count = entry.get("comments", 0) or 0
            description = entry.get("description") or None
            external_source = entry.get("source") or None
            published_at = ts_to_datetime(entry.get("time"))
            first_seen_at = ts_to_datetime(entry.get("first_seen_at"))

            # UPSERT: insert or update score/comments on conflict
            cur.execute(
                """
                INSERT INTO articles (
                    source_id, title, url, canonical_url,
                    description, score, comment_count,
                    external_source, state, summary_status,
                    published_at, first_seen_at, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, 'ingested', 'pending',
                    %s, COALESCE(%s, NOW()), NOW(), NOW()
                )
                ON CONFLICT (canonical_url) DO UPDATE SET
                    score = GREATEST(articles.score, EXCLUDED.score),
                    comment_count = GREATEST(articles.comment_count, EXCLUDED.comment_count),
                    updated_at = NOW()
                RETURNING (xmax = 0) AS is_insert
                """,
                (
                    source_id,
                    title[:500],
                    url,
                    canonical_url,
                    description,
                    score,
                    comment_count,
                    external_source,
                    published_at,
                    first_seen_at,
                ),
            )

            result = cur.fetchone()
            if result and result[0]:
                inserted += 1
            else:
                updated += 1

    conn.commit()
    return inserted, updated


def main():
    platforms = sys.argv[1:] if len(sys.argv) > 1 else ALL_PLATFORMS

    # Validate platform names
    invalid = [p for p in platforms if p not in PLATFORM_SOURCE_MAP]
    if invalid:
        print(
            f"Unknown platforms: {', '.join(invalid)}. "
            f"Valid: {', '.join(ALL_PLATFORMS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    db_url = get_db_url()
    conn = connect(db_url)

    try:
        source_map = load_source_map(conn)
        print(
            f"Loaded {len(source_map)} sources from DB: "
            f"{', '.join(sorted(source_map.keys()))}",
            file=sys.stderr,
        )

        total_inserted = 0
        total_updated = 0

        for platform in platforms:
            print(f"Ingesting {platform}...", file=sys.stderr)
            ins, upd = ingest_platform(conn, platform, source_map)
            total_inserted += ins
            total_updated += upd
            print(
                f"  {platform}: {ins} inserted, {upd} updated",
                file=sys.stderr,
            )

        print(
            f"\nDone. Total: {total_inserted} inserted, "
            f"{total_updated} updated across {len(platforms)} platforms.",
            file=sys.stderr,
        )

    finally:
        conn.close()


if __name__ == "__main__":
    main()
