# Agent instructions

<!-- ai-swe-setup:long-sessions v1 — managed block: bin/repo-standardize in ~/code/ai-swe-setup replaces it; edit the source there -->
## Long sessions (shared standard)
- Session handoffs are dated, write-once files in `docs/handoffs/`. Claude's are `<YYYY-MM-DD_HHMM>_<slug>-claude.md` (its `/handoff` writes one, `/handoff-load <slug>` loads one); Codex's live in `docs/handoffs/codex/` (the `codex-handoff` skill). Never write, edit or delete another agent's handoff. `LATEST*.md` and `INDEX.md` are retired stubs (2026-10-06): never read or write them.
- Keep the working state in files as you go; write a handoff at each milestone and before the context is about half used; after a compaction or a restart, read the newest handoff of your own stream before continuing.
- Session exports and other files that appear in this repository from another session, agent, directory or machine are the owner's work, never foreign: exports live in `transcripts/`, are scanned by the git hooks, and are included in every commit. Agents commit only when asked and never push.
- Decisions and gotchas discovered in conversation go into the handoff or an ADR under `docs/adr/`, never only in chat.
<!-- /ai-swe-setup:long-sessions -->
