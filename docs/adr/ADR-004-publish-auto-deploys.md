# ADR-004: Publishing automatically rebuilds and deploys the public site

**Status:** accepted
**Date:** 2026-10-14

## Context

ADR-001 makes the public site a static export, so a change is invisible to
readers until `site/` is rebuilt and pushed to GitHub Pages. The posters (coach,
captain, team manager) are not technical and post mid-season; the whole point of
the site is that players stop asking "when is practice?" in the group chat. A
practice schedule that is "published" but not on the website fails that goal.

Options considered: an admin-only "Update public site" button (editors' posts
wait for the coach); a button any account can press (posters must remember a
second step); the webmaster running `cms publish` and `cms deploy` by hand
(readers wait hours); rebuilding and deploying automatically on every change to
published content.

## Decision

Any change to published content (publish, edit, unpublish, delete) triggers a
site update: rebuild `site/` and deploy it to the `gh-pages` branch. If the
deploy fails, the publish fails too. The content returns to its previous
state and the poster is told to try again later, so "Published" in the console
always means "on the website".

## Consequences

- The team laptop must hold GitHub push access (read from the environment, never
  committed) and be online to publish.
- No wifi means no publishing. The posters accept this in exchange for never
  seeing a "published but not live" state.
- ADR-001's consequence "content changes are not live until `cms publish` runs"
  no longer describes what posters experience; the step still exists, but the
  console runs it for them.
