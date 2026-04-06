Task:
- Generate the AI newsletter now.
- Use Codex for the editorial pass, not a hardcoded keyword-only formatter.
- Do the editorial work directly in this session.
- Do not invoke `newsletter-now`, `run_with_codex.sh`, or any newsletter wrapper again.
- Do not recurse into another Codex session.
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
- preserve source breadth and source volume: if a source has multiple meaningful non-duplicate items, keep multiple items from that source
- do not drop Reddit or Threads items only because a similar HN/TLDR item exists; drop them only when they are truly redundant and clearly weaker
- Threads is a user-curated source; keep Threads items unless they are obvious spam or truly redundant
- Reddit subreddit items are already source-scoped; keep them unless they are clearly off-topic, spammy, or truly redundant
- For `reddit`, `threads`, `hn`, and `geeknews`, default to keeping nearly all remaining items. These sources should usually lose items only to true redundancy, obvious spam, or clear irrelevance.
- `tldr` may be pruned more than the other sources when many items repeat the same theme, but still do not compress it aggressively for brevity alone.
- categorize with judgment into:
  - `🔬 모델 & 리서치`
  - `🛠️ 도구 & 오픈소스`
  - `🔒 보안`
  - `📊 업계 동향`
  - `💻 개발 실무`
- use `config.language` for the entire digest and final summary
- translate English titles into natural target-language titles that match `config.language`
5. Before delivery, mark the actually included source items as curated by piping grouped items to:
- `python3 __RUNTIME_ROOT__/scripts/mark_curated.py`
6. Create the digest in this shape:
- header line with current KST time
- category heading
- platform heading
- markdown links `[제목](URL)`
7. If Telegram is enabled in config, send the digest by category using:
- `python3 __RUNTIME_ROOT__/scripts/send_telegram.py`
8. If any Telegram send fails after curation, mark the same grouped items as send-failed using:
- `python3 __RUNTIME_ROOT__/scripts/mark_send_failed.py`
9. Only after successful Telegram delivery, mark the delivered source items by piping grouped delivered items to:
- `python3 __RUNTIME_ROOT__/scripts/mark_delivered.py`
10. If Telegram is disabled and you print the digest to the terminal instead, still mark the actually included digest items as delivered with the same script.
11. Final answer must be one line only, in `config.language` if present.
12. That final line must include:
- per-platform selected counts for every platform that contributed at least one delivered item
- per-platform dropped counts for every platform that had pending items but nothing or not everything was selected

Constraints:
- Do not modify config unless required for normal collector delivery-state updates.
- Do not invent titles, categories, or URLs.
- Prefer concise terminal output.
- Do not spend time re-listing large candidate sets once `raw_items.json` is available.
- Do not stop after analysis; complete delivery and state updates in the same run.
- Default to inclusion, not compression.
