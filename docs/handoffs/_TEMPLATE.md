# Handoff: <slug>
- **Written:** <YYYY-MM-DD HH:MM local>  **Session:** <session name or id if known>
- **Agent:** claude  **Stream:** <main | stream name>  **Continues:** <dated handoff file this session started from | none>
- **Status:** <one line: where the work stands and what comes next>
- **Branch:** <branch>  **HEAD:** <short sha> <subject>  **Working tree:** clean | N uncommitted (listed below)
- **Model/effort used:** <e.g. Opus 5, high>  **Context at handoff:** <NN% if known>

## Goal (1–3 sentences)
What this work stream is trying to achieve and how we will know it is done.

## Done (this session)
- <verifiable outcome, with file/commit/test reference>

## In progress (state on disk right now)
- <what is half-finished, which files, whether it compiles/tests pass>

## Next steps (ordered, concrete, each startable in <1 min)
1. <verb> <object> in <path> — <expected result / how to verify>
2. …

## Decisions and why (things a fresh session must not re-litigate)
- <decision> — because <reason>. Alternatives rejected: <x, y>.

## Gotchas / traps discovered
- <non-obvious thing that cost time; how to avoid or detect it>

## Verification state
- Tests: <command> → <pass/fail counts>   Lint/type: <status>   Benchmarks: <status>

## Pointers (read these before anything else)
- <path> — why it matters
- ADR/issue/backlog links

## Open questions / risks
- <question> — who decides / what would settle it

## How to recover detail if needed
- Previous session: `claude --resume <session-id-or-name>`
- Ask it without loading it: `claude -p --resume <id> --fork-session --output-format json "<question>"`
- Compaction snapshots: `~/.claude/handoffs/<project-slug>/auto/*_precompact.md` (written by the `compact_snapshot.py` hook before each compaction)
