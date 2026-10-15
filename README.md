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

Models and Skills:
Opus 5.5 was used for almost all project work, including implementing the hook, grilling, spec, tickets, implementation, and reviews. I had originally planned to do planning and setup with opus and then proceed to sonnet for the implementation, however, the most recent opus 5.5 being more token efficient than the equivalent sonnet model led me to stick with Opus throughout. 

Backends used:

| Model | Provider | Sessions | Used for |
|---|---|---|---|
| Opus 5.5 | Anthropic (Claude Code) | 05–16 | everything from setup to T07 |
| Fable 5.1 | Anthropic (Claude Code) | 01–04 | early setup and housekeeping |
| Sonnet 5 | Anthropic (Claude Code) | 03 | one commit-and-cleanup session |

Skills Used:
/setup-matt-pocock-skills was used once at the start to setup the skills I would use for the project.
/research was used to compare how WordPress, Drupal, and static-site generators handle roles and publishing.
/grill-with-docs was used to take my field notes, client brief, and project details and reconcile the differences to ensure claude and I were on the same page with what to do. 
/to-spec and then /to-tickets was used to take the grill session and create actionable tickets with their own contexts so that they could be implemented one ticket at a time. 
/implement was ran to implement each ticket, using the /tdd approach where it fit and running /code-review on each ticket to ensure the tests were passing and catch bugs in the code.
/handoff was used twice to create a handoff document before ending a session that could be loaded when I open up a new session
/ask-matt was used 4 times to ensure I was on track with following the Matt Pocock development workflow.

Prompts Used:
1. "yes, I disagree with that choice since the users, like my non tech savvy coach, may be confused seeing 'Nothing published yet'"
Both code reviewers flagged the console's home page always saying "Nothing published yet," but the AI left it alone since it did not violate any Ticket or assignment requirement. I overrode this decision since it would cause confusion for the client in this situation, leading to commit 75dd168.

2. "/grill-with-docs I am building a small CMS for the Kenyon mens golf team. Here are my field notes: notes/cms-field-notes.md and my brief: notes/client-brief.md. The 7 required capabilities are in the manual; help me decide what they mean for this client."
Used to take the field notes, required capabilities, and client brief I drafted (with AI assistance) and reach a consensus on the features the site would need, and what should be included in the final iteration.

One Model Failure:
When originally testing if the admin and editor accounts worked, the AI falsely reported that the accounts existed under placeholder emails and a password it said it would not report, but was present in the .env. However, the accounts had never been created, and I was unable to login at that time. When I told it the password was incorrect, it first guessed the database had a different password, then found the database had no accounts at all. It then created the accounts, but also reported the password which is now commited in the transcript when it said it would not. This is not much of a concern though since the placeholder accounts would be replaced should this be used anyway.