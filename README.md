# IPHS 400 — Mini-Project #2 starter (Web CMS)

Click **Use this template** → name your repo **`iphs400-mp2-cms`** → make it **Public**.
Do not fork: a fork arrives without an Issues tab, and your tickets live in Issues.

## Start here

1. `docs/manual_iphs400_mp2-web-cms_20260922.md` — the manual. Read Part 0 and Part 1 first.
2. `docs/mp2-grading-rubric_20260922.md` — how you are graded. Read it **before** you build or revise.
3. `docs/mp2-setup_context-threshold-hook_20260922.md` — Exercise A, in Part 4 of the manual.

## Run it

```bash
uv sync
cp .env.example .env
uv run cms serve        # then open http://localhost:8000/admin  -> "T00: hello admin"
```

## What is here

```text
.claude/hooks/     the context meter and usage ledger (Exercise A lives in ctx_guard.py)
scripts/           usage_report.py (Exercise B lives in spend()), check_submission.py, seed_demo.py
tests/             the exercise tests, plus helpers such as client_as("editor")
app/, templates/   the T00 skeleton — every CMS feature is yours to build
docs/adr/          two example decision records
```

Two functions are deliberately unfinished and their tests fail until you write them:
`decide()` in `.claude/hooks/ctx_guard.py` and `spend()` in `scripts/usage_report.py`.
Both are graded in Stage 2. Use `/tdd`, as the manual says.

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
