# ADR-006: The login limiter keeps failed logins in memory

**Status:** accepted (S2, commit 9aa5eef)
**Date:** 2026-10-21

## Context

Checklist #2 and MP2plus S2: after 5 failed logins for one email within 15
minutes, the next attempt is refused with 429, even with the right password.
The count has to live somewhere. The console runs as one process on the one
team laptop (`cms serve`), and the schema in `app/db.py` is only ever created,
never migrated: a new table means `rm cms.db` and a reseed on that laptop.
Options considered: a `failed_logins` table in `cms.db`, a limiter on
`app.state` (one per app), and one limiter object in its own module.

## Decision

One module-level limiter holds, per typed email (trimmed, lowercased), the
times of its recent failed logins. It reads the time through a `clock`
attribute (`time.monotonic` by default), so tests can freeze and advance it.
A successful login clears that email's failures. The autouse fixture
`reset_limiter` in `tests/conftest.py` clears it and restores the real clock
before every test.

Rejected: a `failed_logins` table, which survives restarts but costs a schema
change and a reseed, and is already reset by each test's fresh database;
and `app.state`, because the `login_as` fixture builds a new app per client,
so failures would not carry from one client to the next.

## Consequences

- No schema change and no reseed for S2.
- Restarting the console clears every lockout. Only someone who can already
  restart the team laptop gains from that; accepted.
- Running more than one server process would split the count. On one laptop
  there is one process; moving off it means revisiting this ADR.
- Tests share one limiter, so the autouse fixture is what keeps the 212
  existing tests from tripping a 429.
- The check, the password verify and the recording of a failure run under a
  per-email lock (one of 64, chosen by hashing the email), so simultaneous
  guesses cannot get past the 5-try limit. Unrelated emails that share a lock
  wait behind each other's argon2 verify; with the console never public and
  one team on the laptop, accepted.
- The lockout message gives the minutes left, rounded up. It reveals nothing,
  because unknown emails lock out the same way.
- Nothing lifts a lockout early: it ends on its own (`CONTEXT.md`, Lockout).
