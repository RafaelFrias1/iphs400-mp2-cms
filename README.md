# Kenyon Men's Golf CMS (IPHS 400 Mini-Project #2)

A small CMS for the Kenyon men's golf team. The Coach, Captain and Team manager
write posts and pages in a local admin console (FastAPI, Jinja, SQLite). Every
change to published content rebuilds the static public site and pushes it to
GitHub Pages (ADR-004). Vocabulary is in `CONTEXT.md`; decisions are in `docs/adr/`.

## Live URL

https://rafaelfrias1.github.io/iphs400-mp2-cms/

## Run locally

Needs Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env                       # then change the passwords if you like
set -a; . ./.env; set +a                   # load .env (it is not read automatically)
uv run python scripts/seed_demo.py         # demo accounts, 3 pages, a few posts
uv run cms serve                           # http://localhost:8000
```

Open http://localhost:8000/login and log in with a demo account. The password
is the one in `.env`.

| Account | Email | Role | Password from |
|---|---|---|---|
| Coach | `admin@example.test` | admin | `CMS_ADMIN_PASSWORD` |
| Captain | `editor@example.test` | editor | `CMS_EDITOR_PASSWORD` |

`http://localhost:8000/` previews the public site; `/admin` is the console.

**Publishing.** Clicking Publish (or editing, unpublishing or deleting
something published) rebuilds `site/`. Only where `.env` has `CMS_DEPLOY=on`
does it also push `site/` to the `gh-pages` branch. If that push fails (no
wifi), the change is not saved. A fresh clone leaves `CMS_DEPLOY` unset, so
publishing there only writes `site/`. Preview it with
`python3 -m http.server -d site 8001`.

The Webmaster can still run each step by hand:

```bash
uv run cms publish    # render site/ from published content
uv run cms deploy     # push site/ to gh-pages (uses CMS_GITHUB_TOKEN if set)
```

**Tests.** `uv run pytest -q`. The tests use a fake deployer and never touch
the network.

## What is here

```text
app/               the CMS: routes/, publish.py (site update), deploy.py (push to gh-pages)
templates/         admin/ (the console) and public/ (the static site)
tests/             one file per ticket (test_t01_login.py ... test_t07_deploy.py)
scripts/           seed_demo.py, check_submission.py, usage_report.py
.claude/hooks/     the context meter and usage ledger
docs/adr/          decision records; docs/handoff/ session handoffs
notes/             client brief, field notes, research, token budget, usage ledger
```

## Deadlines

Stage 1 (`mp2-mvp` tag): Tue Sep 29, 2:40 pm Eastern. A preliminary checkpoint, past and ungraded; its 15 points are credited for the tag.
Stage 2 (`mp2-final` tag): the final, graded submission, due Thu Oct 15, 2:40 pm Eastern, grace until Fri Oct 16, 2:40 pm. The first round (due Oct 6) was graded and returned on Oct 8; the deadline was extended so you can revise after feedback, and one revised `mp2-final` by Oct 15 replaces the earlier grade.
MP2plus (optional extra credit): assigned Sun Oct 11, due Tue Oct 20, 2:40 pm Eastern, grace until Wed Oct 21, 2:40 pm. Each exercise is worth 5–10 points, added to your MP2 grade, up to +30.
MP2 is graded as a score out of 100, scaled to 5% of the course grade.

Run `uv run python scripts/check_submission.py --stage 2` before you submit.

## Generative AI Use Statement

*(Required. Replace this section: name the models and skills you used, quote two
prompts you really sent, describe one real model failure, and include a
"Backends used" table if you ever switched providers.)*
