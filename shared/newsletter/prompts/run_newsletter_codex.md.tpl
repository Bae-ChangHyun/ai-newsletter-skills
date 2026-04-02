Use the `newsletter-now` skill behavior.

Task:
- Generate the AI newsletter now.
- Use Codex for the editorial pass, not a hardcoded keyword-only formatter.

Required workflow:
1. Read `__RUNTIME_ROOT__/.data/config.json` if it exists.
2. Run `python3 __RUNTIME_ROOT__/scripts/run_all.py` to collect raw items.
3. If there are no items, respond with the no-news message in `config.language` if present. If missing, use `새 뉴스 없음`.
4. Curate the raw items:
- code has already done exact URL/title prefiltering and state tracking
- prioritize any items whose `state` is `curated` or `send_failed`, because they were previously selected but not fully delivered
- keep only meaningful AI news
- remove semantic duplicates and near-duplicates across sources
- drop weak or noisy items
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

Constraints:
- Do not modify config unless required for normal collector delivery-state updates.
- Do not invent titles, categories, or URLs.
- Prefer concise terminal output.
