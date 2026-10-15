# ADR-003: The context Stop hook reads usage from the transcript

**Status:** accepted
**Date:** 2026-10-14

## Context

`ctx_guard.py` (Stop hook) warned from the percentage that `ctx_statusline.py`
saved in `.claude/state/ctx_<session>.json`. The status line refreshes about
0.3 s *after* the Stop hook runs (the file timestamps show this), so every
warning described the previous turn. On a short first turn the file did not
exist yet and the hook stayed silent, which made the Step 9 live test of the
setup exercise look broken.

## Decision

The status line also saves `context_window_size` as `window`, even before the
first reply when `used_percentage` is still null. The Stop hook takes the
`transcript_path` from its event, sums the input tokens (fresh + cache read +
cache write) of the last main-thread assistant message, and divides by
`window`. If the transcript gives no number (missing file, a compaction
boundary after the last message, no window size), it falls back to the status
line's saved percentage.

## Consequences

- Warnings and `notes/usage-ledger.csv` describe the turn that just ended.
- The hook depends on the transcript's JSONL shape (`type`, `isSidechain`,
  `message.usage`, `compact_boundary`). If Claude Code changes it, the hook
  falls back to the lagging status-line number rather than failing.
- The window size cannot be guessed: Opus 5.5 here reports about 1M tokens, so
  a hard-coded 200k default would overstate usage fivefold.

## Gotcha found on the way

The suite in `tests/test_ctx_guard.py` reads `CTX_WARN_PCT` and
`CTX_COMPACT_PCT` from the environment. Inside a session started with
`CTX_WARN_PCT=1 CTX_COMPACT_PCT=2 claude`, five tests fail even though the code
is correct. Run the suite in a normally started session, or unset both variables.
