Task:
- Generate the AI newsletter now.
- Use Claude for the editorial pass, not a hardcoded keyword-only formatter.
- Do the editorial work directly in this session.
- Do not invoke `newsletter-now`, `run_with_claude.sh`, or any newsletter wrapper again.
- Do not recurse into another Claude/Codex session.
- Do not browse the web, inspect unrelated files, or do extra research.
- Use only these inputs unless a delivery-state script below requires execution:
  - `__RUNTIME_ROOT__/.data/config.json`
  - `__RUNTIME_ROOT__/.data/raw_items.json`
- After reading those inputs, move directly to selection, delivery, and state updates.
- Keep shell usage minimal and bounded to the delivery-state scripts listed below.

Required workflow:
1. Read `__RUNTIME_ROOT__/.data/config.json` if it exists.
2. Read `__RUNTIME_ROOT__/.data/raw_items.json` for the collected raw items.
3. If there are no items, respond with the no-news message in `config.language` if present. If missing, use `새 뉴스 없음`.
4. Curate the raw items:
- code has already done exact URL/title prefiltering and state tracking
- prioritize any items whose `state` is `curated` or `send_failed`, because they were previously selected but not fully delivered
- the collector already removed obvious exact duplicates and first-pass noise; treat the remaining pool as publishable by default
- keep items unless they are clearly one of these:
  - materially redundant with another selected item
  - clearly unrelated to AI / developer tooling / model ecosystem
  - obvious spam, joke post, or low-information chatter
- if you are unsure whether to drop an item, keep it
- do not compress the digest for brevity
- do not impose a target item count
- preserve source breadth and source volume
- use `config.language` for the entire digest and final summary
5. Before delivery, mark the actually included source items as curated by piping grouped items to:
- `python3 __RUNTIME_ROOT__/scripts/mark_curated.py`
6. Create the digest in this shape:
- header line with current KST time
- category heading
- platform heading
- markdown links `[title](URL)`
7. If Telegram is enabled in config, send the digest by category using:
- `python3 __RUNTIME_ROOT__/scripts/send_telegram.py`
8. If any Telegram send fails after curation, mark the same grouped items as send-failed using:
- `python3 __RUNTIME_ROOT__/scripts/mark_send_failed.py`
9. Only after successful Telegram delivery, mark the delivered source items by piping grouped delivered items to:
- `python3 __RUNTIME_ROOT__/scripts/mark_delivered.py`
10. If Telegram is disabled and you print the digest to the terminal instead, still mark the actually included digest items as delivered with the same script.
11. Final answer must be one line only, in `config.language` if present.

Hard constraints:
- Do not modify config unless required for normal collector delivery-state updates.
- Do not edit any `.jsonl`, `.json`, or other state file directly.
- Use only the provided marker scripts for state transitions.
- Do not invent titles, categories, or URLs.
- Prefer concise terminal output.
- Do not stop after analysis; complete delivery and state updates in the same run.
