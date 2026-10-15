#!/usr/bin/env python3
"""Stop hook: warn when the context window crosses 50% / 60% / 80%.

Claude Code runs this after every Claude turn (the Stop event) and pipes the
event JSON to stdin. It computes the current percentage from the last
assistant message's token usage in the transcript, divided by the window size
the status line recorded. (The status line's own percentage lags one turn: it
refreshes just after this hook runs.) It prints {"systemMessage": "..."} the
first time usage crosses a threshold.
The message is shown to YOU, not to Claude. The hook never blocks and never
runs /compact itself: slash commands are yours to type.

Thresholds (override when launching:  CTX_WARN_PCT=1 claude  to test):
  CTX_WARN_PCT     default 50  -> "plan a /compact"
  CTX_COMPACT_PCT  default 60  -> "/compact at the next green test"
  urgent = CTX_COMPACT_PCT + 20 -> "compact or /handoff now; consider splitting"
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

NONE, WARN, COMPACT, URGENT = 0, 1, 2, 3


def thresholds() -> tuple[float, float, float]:
    warn = float(os.environ.get("CTX_WARN_PCT", 50))
    compact = float(os.environ.get("CTX_COMPACT_PCT", 60))
    return warn, compact, compact + 20


def band_for(pct: float, warn: float, compact: float, urgent: float) -> int:
    if pct >= urgent:
        return URGENT
    if pct >= compact:
        return COMPACT
    if pct >= warn:
        return WARN
    return NONE


def message_for(band: int, pct: float) -> str:
    p = f"{pct:.0f}%"
    return {
        WARN: (
            f"Context {p}: finish the current red-green cycle, then plan a "
            "/compact at the next green test."
        ),
        COMPACT: (
            f"Context {p}: at the next green test run  /compact keep: ticket #N "
            "acceptance criteria, what is left, files touched"
        ),
        URGENT: (
            f"Context {p}: compact now (or /handoff and start fresh). If this "
            "ticket keeps overflowing, split it with /to-tickets."
        ),
    }[band]


def decide(pct: float, last_band: int) -> tuple[str | None, int]:
    """Pure function (unit-tested): return (message or None, band to store).

    Warn once per upward crossing. When usage drops (after /compact or
    /clear), store the lower band so the next crossing warns again.
    """
    band = band_for(pct, *thresholds())
    if band > last_band:
        return message_for(band, pct), band
    return None, band  # same band: stay quiet; lower band: re-arm


def pct_from_transcript(transcript: Path, window: float) -> float | None:
    """Context % of the last main-thread assistant message, or None.

    Counts input tokens only (fresh + cache read + cache write), the same
    quantity the status line's used_percentage measures. Stops at a compaction
    boundary: usage from before /compact no longer describes the context.
    """
    if not window:
        return None
    try:
        lines = transcript.read_text().splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("type") == "system" and entry.get("subtype") == "compact_boundary":
            return None
        if entry.get("type") != "assistant" or entry.get("isSidechain"):
            continue
        message = entry.get("message") or {}
        usage = message.get("usage") or {}
        tokens = sum(
            int(usage.get(k) or 0)
            for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
        )
        if tokens and message.get("model") != "<synthetic>":
            return tokens / float(window) * 100
    return None


LEDGER_COLUMNS = [
    "ts", "session", "phase", "provider", "model", "effort",
    "ctx_pct", "five_h_pct", "weekly_pct",
]


def log_usage(project: Path, session: str, state: dict, pct: float) -> None:
    """Append one row per turn to notes/usage-ledger.csv (rubric item B7)."""
    ledger = project / "notes" / "usage-ledger.csv"
    phase_file = project / ".claude" / "state" / "phase"
    try:
        phase = phase_file.read_text().strip() or "unlabelled"
    except OSError:
        phase = "unlabelled"

    def cell(value: object) -> str:
        return "" if value is None else str(value)

    row = [
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        session[:8], phase, cell(state.get("provider")), cell(state.get("model")),
        cell(state.get("effort")), f"{pct:.1f}",
        cell(state.get("five_h")), cell(state.get("weekly")),
    ]
    try:
        ledger.parent.mkdir(parents=True, exist_ok=True)
        new = not ledger.exists()
        with ledger.open("a", newline="") as f:
            writer = csv.writer(f)
            if new:
                writer.writerow(LEDGER_COLUMNS)
            writer.writerow(row)
    except OSError:
        pass


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd())
    session = event.get("session_id") or "default"
    state_dir = project / ".claude" / "state"
    ctx_file = state_dir / f"ctx_{session}.json"
    band_file = state_dir / f"ctx_{session}_band.json"

    try:
        state = json.loads(ctx_file.read_text())
    except (OSError, ValueError):
        return  # no status-line data yet: stay silent
    pct = None
    if event.get("transcript_path"):
        pct = pct_from_transcript(Path(event["transcript_path"]), state.get("window"))
    if pct is None:
        try:
            pct = float(state["pct"])  # fallback: last status-line reading
        except (KeyError, TypeError, ValueError):
            return
    try:
        last_band = int(json.loads(band_file.read_text())["band"])
    except (OSError, ValueError, KeyError):
        last_band = NONE

    log_usage(project, session, state, pct)

    msg, band = decide(pct, last_band)
    try:
        band_file.write_text(json.dumps({"band": band}))
    except OSError:
        pass
    if msg:
        print(json.dumps({"systemMessage": msg}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # a warning hook must never break the session
    sys.exit(0)
