# CLAUDE.md — standing instructions

Keep this file short. It is prepended to every turn, so every line costs context
on every message. Add a rule only after you have had to correct the same thing
twice.

## What this repo is

A small web CMS for IPHS 400 Mini-Project #2. A local admin console
(FastAPI + Jinja + SQLite) writes content; `cms publish` renders the published
content into `site/` as static HTML, which is deployed to GitHub Pages. The
admin console never goes on the public internet.

## Hard constraints

- Published HTML uses **relative** paths only. Never `href="/..."` or `src="/..."`.
- Never commit `.env`, `*.db`, keys, or tokens. Read secrets from the environment.
- Passwords are hashed with argon2. Never store or log a plain password.
- Every state-changing form carries a CSRF token.
- User-written Markdown is sanitized before it is rendered anywhere.
- `site/` is generated. Never edit it by hand.
- Only published content reaches `site/`. Drafts never leave the database.

## How to work with me

- One ticket per session. Read the ticket issue, the spec issue, and `CONTEXT.md`
  before writing code.
- Write the ticket id into `.claude/state/phase` when a stage starts
  (`grill`, `spec`, `tickets`, or `T03`), so the usage ledger is labelled.
- Use the vocabulary in `CONTEXT.md`. If a better word appears, update the
  glossary rather than using both.
- When `/status` shows a non-Anthropic base URL, add a `Backend: <provider> <model>`
  trailer to every commit made in that session.
- Before a commit that closes a ticket: post the `/code-review` findings, and how
  each was resolved, as a comment on that issue. Then commit with a message that
  starts `T0N:` and ends `Closes #N`.
- Ask before adding a dependency. The stack in `pyproject.toml` is fixed for this
  project.

<!-- ai-swe-setup:long-sessions v1 — managed block: bin/repo-standardize in ~/code/ai-swe-setup replaces it; edit the source there -->
## Long sessions (shared standard)
- Session handoffs are dated, write-once files in `docs/handoffs/`, named `<YYYY-MM-DD_HHMM>_<slug>-claude.md`: `/handoff <slug>` writes one, `/handoff-load <slug>` loads one by name. `LATEST*.md` and `INDEX.md` are retired stubs (2026-10-06): never read, write or import them. Codex keeps its own records in `docs/handoffs/codex/`.
- Compaction snapshots and the automatic compaction record come from the global `compact_snapshot.py` hook (global CLAUDE.md, "Long runs" and "Compaction"); this repository has no handoff hooks of its own.
- Session exports (`/export` files, `codex-session-*.md`) and other files that appear in this repository from another session, agent, directory or machine are the owner's work, never foreign. Exports live in `transcripts/` (move a stray one there), are scanned by the git hooks, and are included in every commit; `bin/repo-standardize` in `~/code/ai-swe-setup` does the move.
- Decisions and gotchas discovered in conversation go into the handoff or an ADR under `docs/adr/`, never only in chat.
- When compacting, preserve: the goal, the ordered next steps, every decision with its reason, the modified files and their state, the exact test and lint commands with their last results, and the open questions. Drop raw tool output and resolved detours.
<!-- /ai-swe-setup:long-sessions -->
