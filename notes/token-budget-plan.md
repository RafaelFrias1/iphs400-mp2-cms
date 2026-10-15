# Token budget plan

Part 5.4 of the manual. Written 2026-10-14, before the first `/implement`.
Estimates are in percent of my own meters, not tokens (Pro publishes no token count).

## Models available

`/model` offers: Haiku 5.5, Sonnet 5.5, Opus 5.5 (and `opusplan`), Fable 5.1.
Fable 5.1 is the most expensive per turn and is not in the plan; I use it only if
Opus gets a hard design question wrong twice.

## Baseline from the ledger (setup sessions, before any ticket)

| Sessions | Model · effort | Turns | 5h spent | Weekly spent | 5h per turn |
|---|---|---|---|---|---|
| 623c67d3 … 4d76fb33 (hook setup) | Opus 5.5 · medium | ~30 | ~18% | ~3% | ~0.6–1% |
| 8ee601d3 (field trip, research) | Fable 5.1 · high | ~15 | ~14% | ~4% | ~1% |

Rule of thumb from these rows: **weekly ≈ 0.2 × 5h spend**.

## Plan

| Stage | Model | Effort | Estimate (% of a 5-hour window) |
|---|---|---|---|
| `/research`, quick lookups | Haiku 5.5 | low | 5% per lookup session |
| `/grill-with-docs` | `opusplan` | high | 30% (one session) |
| `/to-spec`, `/to-tickets` | `opusplan` | high | 25% (same window as spec) |
| `/implement` + `/tdd` (per ticket) | Sonnet 5.5 | medium | 15% |
| `/code-review` (per ticket) | Sonnet 5.5 | high | 5% |

## Forecast

- **Per ticket:** 15% + 5% = ~20% of a 5-hour window, ~4% of the weekly cap.
- **9 tickets:** 9 × 20% = 180% → about 1.8 windows.
- **Planning + research:** 30% + 25% + ~10% research = ~65% → about 0.7 windows.
- **Total:** ~245% of a 5-hour window → **3 five-hour windows**, allowing for slack.
- **Share of one week:** 245% × 0.2 ≈ **50% of the weekly cap**, leaving half for
  rework, the report, and other courses.

## If I am wrong

Cut first: **`/code-review` effort, high → medium.** It is the cheapest loss of
quality, because the review still runs on every ticket.
After that, the manual's order: Sonnet/Haiku for more stages → `/clear` more
often → split fat tickets → Plan B backend (declared).

## Re-forecast

Run after T01 and after T03 and record the actual numbers here:

    uv run python scripts/usage_report.py --remaining N

| Checkpoint | Avg weekly per ticket | Weekly remaining | Verdict |
|---|---|---|---|
| After T01 | | | |
| After T03 | | | |
