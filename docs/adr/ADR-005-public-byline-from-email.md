# ADR-005: The public byline is the part of the email before @

**Status:** accepted
**Date:** 2026-10-15

## Context

T04 puts the author and date on every published post (spec #1, story 26:
"each post shows its author"). An account has only an email, a role and an
active flag; there is no name field. Publishing the full email on a public
site would hand every reader, and every scraper, the team's addresses.

Options considered: publish the full email; add a display-name field to
accounts (a schema change and a new T02 form field, mid-T04); show the part
of the email before `@`.

## Decision

The public site shows the part of the email before `@` (`publish.byline`).
The full email appears only in the console.

## Consequences

- The Coach should create accounts with readable local parts
  (`coach.smith@...`, `captain@...`), because that text is what readers see.
- If the team wants real names, a display-name field replaces `byline()`
  without touching the templates.
- Posts and their dates are ordered and shown by when the post was created,
  not when it was first published; there is no published-at field.
