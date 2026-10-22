# MP2plus grill: decisions and session checklist (2026-10-21)

Glossary terms and the P3 Decisions table are in `CONTEXT.md`; the hardest-to-reverse
decision is drafted in `docs/adr/ADR-006-login-limiter-in-memory.md`.

## Decisions

**S2 Login hardening**
- Ordinary failed logins stay 401 + `LOGIN_ERROR` (pinned by `tests/test_t01_login.py`).
- A locked-out attempt: status 429, the login page re-rendered with its own lockout message.
- Lockout: 5 failed logins for one email within 15 minutes; refused even with the right password.
- Keyed on the typed email (trimmed, lowercased), unknown and deactivated emails included.
- A successful login (before lockout) clears that email's failures.
- One module-level limiter in memory; `clock` attribute, `time.monotonic` by default.
- Fixture: `reset_limiter` in `tests/conftest.py`, autouse; clears failures, restores the real clock.

**F8 Switchable theme**
- Themes: `app/themes/classic/style.css` (today's `publish.CSS`, moved) and
  `app/themes/kenyon/style.css` (light only, Kenyon purple header bar and links, serif headings,
  same layout rules: no horizontal overflow at 390 px).
- `settings` table of key/value rows: `key TEXT PRIMARY KEY, value TEXT NOT NULL`; theme is `('theme', '<name>')`.
  Only a folder that exists under `app/themes/` is accepted.
- Fallback when no row: `CMS_THEME`, default `classic`; `.env.example` gets `CMS_THEME=classic`.
- Saving a theme is a site update (`update_site`): no wifi means the change is refused.
- The console preview's `/style.css` serves the selected theme too.
- Settings link in `templates/admin/_nav.html`: inside the `account.is_admin` block. `/admin/settings` guarded by `require_admin`.

**S1 Access matrix**
- Routes: `create_app().routes` whose dependency tree contains `require_admin`.
- Path parameters: real ids. The test seeds demo content; `{item_id}` = a real page's id,
  `{account_id}` = the editor's id.
- Anonymous: `follow_redirects=False`, status in (302, 303, 307), Location path `/login`.
- Editor: 403 or a redirect. POSTs carry a valid session CSRF token, so a 403 can only come from `require_admin`.

## Session checklist

Before each: `git switch main && git pull`, then the two checks at the end (runbook 8):
`uv run python scripts/check_submission.py --stage 2` (22/22) and `uv run pytest -q` (212 + new, all passed).

### 1. S2 Login hardening
- Phase: `echo S2 > .claude/state/phase`
- Issue/branch: none; on `main`.
- Prompt 1 (`/clear` first):
  `/tdd Make a wrong password and an unknown email produce the same login error message and status code. Add tests/test_login_hardening.py with a test that asserts both responses match.`
- Prompt 2 (`/clear` first):
  `/tdd Rate-limit login, keyed on the account: after 5 failed attempts for one email within 15 minutes, refuse further attempts for that email with 429 and the login page showing a lockout message, even with the right password. Count failures by the typed email, trimmed and lowercased, including emails with no account or a deactivated one. A successful login clears that email's failures. Keep failures in one module-level limiter in memory with a clock attribute (time.monotonic by default) so tests can freeze and advance it. Ordinary failures stay 401 with LOGIN_ERROR. In tests/test_login_hardening.py, test that attempt 6 is refused, that a login works again once 15 minutes have passed, and that another email can still log in from the same client. Add an autouse fixture reset_limiter to tests/conftest.py that clears the limiter and restores the real clock; change nothing else in conftest. No new dependencies. See docs/adr/ADR-006-login-limiter-in-memory.md.`
- Review: `/code-review`; fix findings.
- Commit: `S2: ...`, push. Stage only S2 files (leave CONTEXT.md and ADR-006 for P3).
- Report row: `| S2 | tests/test_login_hardening.py; fixture reset_limiter in tests/conftest.py |`

### 2. F8 Switchable theme, through P1
- Issue first: `gh issue create --label stretch --title "MP2plus F8: Switchable theme"`; body = F8's
  acceptance table word for word, then `Blocked by: none` (`gh label create stretch` if missing).
- Phase: `echo T<N> > .claude/state/phase`
- Branch: `git switch main && git pull && git switch -c mp2plus-theme`
- Prompt (`/clear` first): the manual's F8 prompt with `#N`, plus:
  `The two themes are classic (today's CSS, moved unchanged) and kenyon (light only: Kenyon purple header bar and links, serif headings, no horizontal overflow at 390 px). Store settings as key/value rows (key TEXT PRIMARY KEY, value TEXT NOT NULL); accept only a theme folder that exists. When no theme is stored, use CMS_THEME (default classic) and add CMS_THEME=classic to .env.example. Saving the theme is a site update through update_site, so a failed deploy refuses the change. The console preview's /style.css serves the selected theme. Guard /admin/settings with require_admin and show the Settings link only inside the admin block of templates/admin/_nav.html.`
- Then `rm cms.db && uv run python scripts/seed_demo.py`; walk the checklist at 1280 and 390 px.
- Push + PR: `git push -u origin mp2plus-theme`, `gh pr create --title "MP2plus P1: Switchable theme" --body "Closes #N"`.
- Review: `/code-review`, then `Post the code-review findings and how each was resolved as a comment on pull request #<pr>, then commit and push the fixes to this branch.` At least one commit pushed after the comment.
- Commit prefix: `T<N>:`
- Merge: `gh pr merge <pr> --merge --delete-branch`; `git switch main && git pull`; `gh issue view N` shows CLOSED by the PR.
- Screenshots: home page in kenyon, `docs/screenshots/mp2plus-theme-1280.png` and `-390.png`.
- Report rows: `| F8 | issue #N; tests/test_theme.py; mp2plus-theme-1280.png, mp2plus-theme-390.png |` and
  `| P1 | PR #<pr> closing issue #N; carries F8 |`

### 3. P3 Decision record
- Phase: `echo P3 > .claude/state/phase`
- Issue/branch: none; on `main`.
- Prompt: none needed; the table and ADR-006 draft exist. Reword the "why"s in your own voice if you like,
  check ADR-006 against the S2 code, and set its status to accepted.
- Review: read both against the code (P3 row 6).
- Commit: `P3: ...` with CONTEXT.md, ADR-006 and this file; push.
- Report row: `| P3 | CONTEXT.md Decisions table; docs/adr/ADR-006-login-limiter-in-memory.md |`

### 4. S1 Access matrix
- Phase: `echo S1 > .claude/state/phase`
- Issue/branch: none; on `main`.
- Prompt (`/clear` first): the manual's S1 prompt, plus:
  `Seed demo content in the test and fill {item_id} with a real page's id and {account_id} with the editor's id. For the anonymous client use follow_redirects=False and assert a 302, 303 or 307 whose Location path is /login. Send a valid session CSRF token on every POST, so the editor's 403 can only come from require_admin.`
- Check: add a throwaway `require_admin` route, rerun `uv run pytest -q tests/test_access_matrix.py`, see it covered, delete it.
- Review: `/code-review`; fix findings.
- Commit: `S1: ...`, push.
- Report row: `| S1 | tests/test_access_matrix.py |`

### Then Part 2
Report `docs/iphs400_mp2plus-web-cms_report_rafael-frias_<YYYYMMDD>.md` with the rows above, the two checks,
`git tag mp2plus-final && git push origin mp2plus-final`, email.
