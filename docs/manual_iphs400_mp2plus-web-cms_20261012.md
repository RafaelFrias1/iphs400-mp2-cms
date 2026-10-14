# Mini-Project #2plus: Extend Your Web CMS
**Course:** IPHS 400: Frontiers in AI, Kenyon College
**Instructor:** Jon A. Chun · **Date:** 2026-10-12 (v3) · **Weeks 8–9** · **Extra credit**
**Changes:** v3: 15 exercises at 5–10 points, 15–60 min each, +30 cap; live deploy removed; assigned Oct 11.
**Format:** Self-guided lab manual. A menu of optional exercises: pick any, in any order, at your own pace.

---

## Front matter
### What this is
MP2plus is a **menu of 15 independent exercises** that extend the CMS you built in MP2. Pick any number, in any order, and stop whenever you like. Your points are **added to your MP2 score**, up to **+30**.

The menu has three groups:
- **Features** (F1–F9) come from MP2's stretch list, which MP2 introduced but did not score.
- **Process** (P1–P4) covers habits MP2 introduced but did not require, or scored only lightly.
- **Security** (S1–S2) extends two lines of `SECURITY-CHECKLIST.md` that MP2 scored only lightly.

### The menu
| Id | Exercise | Minutes | Pts |
|---|---|---|---|
| F1 | Media uploads with alt text | 45–60 | 9 |
| F2 | Categories and tags | 40–55 | 8 |
| F3 | Revision history with rollback | 40–55 | 8 |
| F4 | Scheduled publishing | 35–50 | 7 |
| F5 | Site search | 35–50 | 7 |
| F6 | Comments with moderation | 45–60 | 9 |
| F7 | Plugin or hook system | 45–60 | 9 |
| F8 | Switchable theme | 35–50 | 7 |
| F9 | Production configuration | 40–55 | 8 |
| P1 | Pull-request workflow | 30–45 | 6 |
| P2 | `/prototype` side session | 35–50 | 7 |
| P3 | Decision record | 30–45 | 6 |
| P4 | Budget re-forecast | 30–40 | 6 |
| S1 | Direct-URL access matrix | 30–45 | 6 |
| S2 | Login hardening | 40–55 | 8 |
| | **Menu total (up to 30 count)** | | **111** |

Pick what interests you, not everything. Reaching +30 takes three or four exercises, about three hours. One or two exercises is a solid MP2plus.

### Time and deadlines
| Milestone | What | When (Eastern, EDT) |
|---|---|---|
| **Assigned** | This manual and the rubric | **Sun Oct 11, 2026** |
| **Due** | Tag `mp2plus-final` pushed, report emailed | **Tue Oct 20, 2026, 2:40 pm** |
| **Grace** | No penalty | until **Wed Oct 21, 2026, 2:40 pm** |

Around the exercises you pick, two short parts are required and worth 0 points: Part 0, before you start (15 minutes), and Part 2, submit (20 minutes).

### Prerequisites
- **Your MP2 repo**, `iphs400-mp2-cms`, with `mp2-final` pushed. The MP2 resubmission is due Thu Oct 15, 2:40 pm (no-penalty grace until Fri Oct 16, 2:40 pm); Part 0 says how the two overlap.
- **Your MP2 setup still working:** `uv`, `gh` logged in, Claude Code with the mattpocock skills (`/implement`, `/tdd`, `/code-review`, `/prototype`, `/handoff`), the hooks, and the usage ledger.
- **These two files on GitHub.** Your repo was copied before they existed. Read them in the starter repo, `jon-chun/iphs400-mp2-cms-starter`: this manual and `docs/mp2plus-grading-rubric_20261012.md`.

> **Policy (set by the instructor).** MP2plus was assigned **Sun Oct 11, 2026**, after the first MP2 final submissions were graded, to give deeper hands-on practice and a way to close the gaps the MP2 rubric found. It is an optional menu of **15 independent exercises**. Each takes **15–60 minutes** and is worth **5–10 points** according to its time and difficulty: about 1 point per 6 minutes.
> **Points are added to the student's MP2 grade**, for every student, whatever the MP2 score. MP2 is graded as a numeric score out of 100. MP2plus points are added after the MP2 resubmission (due Thu Oct 15, 2026, 2:40 pm; no-penalty grace until Fri Oct 16, 2:40 pm) is graded. **Cap: +30 per student.** The sum may exceed 100 and is recorded as is: MP2 91 + MP2plus 24 = 115.
> **Due Tue Oct 20, 2026, 2:40 pm**; no-penalty grace until **Wed Oct 21, 2026, 2:40 pm**. One MP2plus resubmission within one week of feedback.
> **The gate.** An exercise earns points only if, at `mp2plus-final`, the MP2 checker (`check_submission.py --stage 2`) and `uv run pytest -q` show no failure that was absent at `mp2plus-base`. A failing test added for MP2plus costs only its own exercise's Tests point. Failures already present at `mp2plus-base` are reported, not scored, so MP2plus is not a repair pass. Solo work: every commit after `mp2plus-base` is authored by the student. No `mp2plus-base` tag, no points.

### Deliverables checklist
Tick every line that applies before you tag `mp2plus-final`.

- [ ] Tag `mp2plus-base` pushed before your first MP2plus commit
- [ ] `notes/mp2plus-plan.md` committed: the exercises you intend, minute estimates, the base check results
- [ ] Each exercise you did: everything its **Deliverables** line names
- [ ] `docs/iphs400_mp2plus-web-cms_report_{first}-{last}_{YYYYMMDD}.md` with each exercise's **Report row**, committed before the tag
- [ ] No checker or test failure that was not there at `mp2plus-base`; tag `mp2plus-final` pushed; email sent

---

## Part 0 — Before you start
**Time: 15 min. No points, but required: without `mp2plus-base`, no exercise earns points.**

### 0.1 Tag your baseline
`mp2plus-base` marks the commit graded for MP2. Everything after it is MP2plus, and the judge scores only that range. Run the two MP2 checks first:

```bash
cd ~/code/iphs400-mp2-cms
git switch main && git pull
uv run python scripts/check_submission.py --stage 2
uv run pytest -q
```

**Expected:** the checker ends with `N/N checks passed.` and pytest ends with `passed`. A `FAIL` line or a failing test here is a pre-existing failure. Copy it into your plan (0.2). It is reported, not scored, and you need not fix it for MP2plus. Then tag the commit graded for MP2:

```bash
git tag mp2plus-base mp2-final
git push origin mp2plus-base
```

**Expected:** `* [new tag] mp2plus-base -> mp2plus-base`.

- **Resubmitting MP2 by Oct 15?** The simplest order is to push your revised `mp2-final` first, then run the two commands above.
- **Starting MP2plus before you resubmit?** Tag now. Make the MP2 fixes on a branch from `mp2-final` (`git switch -c mp2-resubmit mp2-final`), move the tag there (`git tag -f mp2-final && git push -f origin mp2-final`), and `git switch main` to continue MP2plus. Before you tag `mp2plus-final`, run `git merge mp2-resubmit` on `main` and name the merge commit in your report. Those commits are MP2 work, and MP2plus does not score them.

### 0.2 Write your plan
Skim the menu and list what you intend to do, with minute estimates from the menu. The plan may change; your report says what you actually did. Create `notes/mp2plus-plan.md`, then commit it on `main` with the message `mp2plus: plan` and push:

```text
# MP2plus plan
Exercises: F2 about 50 min; S2 about 50 min; P4 about 35 min
At mp2plus-base: checker "<its last line>", FAIL lines: <names, or none>; pytest "<its last line>"
```

If you picked P4, its "before" run goes into this file now (see P4).

> **The gate.** At `mp2plus-final` the judge runs the same two checks. A check or a test that passed at `mp2plus-base` and fails at `mp2plus-final` sets every exercise to 0 until a resubmission fixes it. Test files that existed at `mp2plus-base` may change only by adding cases. If an exercise truly needs an existing assertion changed, say so in that exercise's findings comment and its report row; the judge then reviews `git diff mp2plus-base..mp2plus-final` for those files.

---

## Part 1 — The menu
- **Pick any.** The exercises are independent. P1 carries one other change, P2 needs code where its decision lands, and P4 measures one other exercise; each says so under **Prerequisites**.
- **New work only.** Only commits after `mp2plus-base` count. A feature already in your repo at `mp2plus-base` is not scored again.
- **Every point is a line** with a measure and a check, listed under each exercise's **Scoring**. One flaw costs points in one line only.

**How each exercise is laid out.** Every exercise has the same headings: Goal, Prerequisites, Roles, Steps, Prompt, Acceptance checklist, Out of scope, Deliverables, Report row, Scoring, If it goes wrong. The **Roles** line says which new routes are admin-only and which editors may use; S1 tests exactly those. The **Acceptance checklist** is the contract: the judge checks those steps and no others. Its **Checked by** column uses seven words. *walk*: the judge clicks through your app from a clean clone, at 1280 and 390 px. *publish*: the judge runs `uv run cms publish` and inspects `site/`. *test*: a named test for this step exists and passes. *read*: the judge reads the file or the code. *replay*: the judge sends the form's POST again without its CSRF token. *github*: the judge reads GitHub's own records and times (issues, pull requests, comments, pushes). *run*: the judge runs the command at the commit named.

> **How a feature scores.** A feature worth P points has four lines. **Screenshots, 1:** both `docs/screenshots/mp2plus-{slug}-1280.png` and `-390.png` are present. **Trail, 1:** the issue existed before your first commit for it reached GitHub, and your findings comment came before the issue closed. **Tests, 1:** every step marked *test* has a named test that passes. **Function, P − 3:** floor((P − 3) × steps passed ÷ steps in the table). Process and security exercises score one point per checklist row, as listed in their tables.

### The feature runbook
Every feature's **Steps** follow MP2 Part 6's per-ticket loop. The commands, once:

1. **The issue, before any code.** `gh issue create --label stretch --title "MP2plus F2: Categories and tags"`. When `gh` asks for the body, open the editor and paste the feature's acceptance table (the `| # | Step | Checked by |` rows) word for word, then a last line `Blocked by: none`. If `gh` says the label is not found, run `gh label create stretch` once and retry.
2. **The phase, before the session.** `echo T14 > .claude/state/phase`, with your issue number for 14. The usage ledger labels every turn with it, so set it before you start. Process and security exercises set their id instead, for example `echo S2 > .claude/state/phase`.
3. **The build.** `/clear`, then the feature's prompt with your issue number. `/implement` drives `/tdd`: a failing test first, then code.
4. **Your own walk.** Click through the acceptance checklist at 1280 and 390 px; fix what fails.
5. **Review, then close.** Send `/code-review`, then: `Post the code-review findings and how each was resolved as a comment on issue #14, then commit and push with a message that starts "T14:" and ends "Closes #14".`
6. **Check.** `gh issue view 14`. **Expected:** state CLOSED, with your findings comment above the close.
7. **Screenshots.** The feature working, at 1280 and 390 px, saved as named in its **Deliverables**.
8. **The two checks.** `uv run python scripts/check_submission.py --stage 2` and `uv run pytest -q`. Fix any failure that was not there at `mp2plus-base` before you start the next exercise.

Every feature prompt ends with the same rules; each one guards against a way to lose points. No `href="/` or `src="/` in any template, admin pages included: the MP2 checker greps every tracked `.html` file. A schema change needs a fresh database: `rm cms.db && uv run python scripts/seed_demo.py`. A new setting needs a line in `.env.example`, because the judge starts your app from it. Every new form needs a CSRF token.

| Symptom | Cause | Fix |
|---|---|---|
| Checker fails `no root-absolute paths in HTML` after a new admin page | a template has `href="/admin/..."` | use `url_for(...)` or a relative link; the checker reads admin templates too |
| `sqlite3.OperationalError: no such column` | the schema changed; your old `cms.db` did not | `rm cms.db && uv run python scripts/seed_demo.py` |
| An MP2 test fails after your change | the feature changed behaviour an old test pins | add cases, never weaken old ones; if one assertion truly must change, declare it (Part 0 gate box) |
| Issue did not close | the commit message or PR body lacked `Closes #N` | `gh issue close 14 --comment "closed by <sha>"`; use the exact phrase next time |
| Checker fails on a transcript name | a file in `docs/transcripts/` breaks MP2's pattern | set `CMS_STUDENT=first-last` in `.env`; rename to `iphs400_mp2-cms_chat-session_{NN}_{first}-{last}_{YYYYMMDD}.md` |
| Your exercise has no row in `usage_report.py` | the phase was set after the session started | set it first next time; the ledger cannot be relabelled |
### 1.1 Features (F1–F9)

#### F1 Media uploads with alt text (9 pts, about 45–60 min)
- **Goal.** Editors upload images to a media library and place them in posts. Every image carries alt text, so a screen reader can describe it.
- **Prerequisites.** MP2 done and Part 0 complete. Other exercises: none. Uses FastAPI's form uploads (`python-multipart` is already a dependency).
- **Roles.** Upload and media library: admin and editor.

**Steps.**
1. Create the issue (runbook 1), title `MP2plus F1: Media uploads with alt text`; then `echo T<issue#> > .claude/state/phase`.
2. `/clear`, then the prompt below with your issue number. Then walk the acceptance checklist yourself; fix what fails.
3. `/code-review`, then the close-out message (runbook 5). `gh issue view <issue#>` shows CLOSED, with your comment above the close.
4. Save `docs/screenshots/mp2plus-media-1280.png` and `mp2plus-media-390.png`: the library with one image. Then run the two checks (runbook 8).

**Prompt.**
```text
/implement #N Media uploads with alt text, for posts only. Follow the issue's acceptance checklist exactly. Store uploads under media/ and add media/ to .gitignore. Accept PNG and JPEG of 2 MB or less; check the type by extension and by the file's first bytes. The library shows a copyable Markdown snippet ![alt](media/<file>) for each item. cms publish copies media/ into site/media/ and makes every image src relative to the page that contains it. Rules: no href="/ or src="/ in any template, admin pages included; use url_for or relative links. Every new form carries a CSRF token and refuses a POST without it. Every new setting gets a line in .env.example. If you change the database schema, keep scripts/seed_demo.py running clean from .env.example and tell me to run rm cms.db && uv run python scripts/seed_demo.py. Tests that existed before may only gain cases; ask me before changing an existing assertion. Put the new tests in tests/test_media.py and name each one test_step<k>_<what> after the acceptance step it checks. Ask before adding any dependency.
```
**Acceptance checklist.**
| # | Step | Checked by |
|---|---|---|
| 1 | Upload a PNG or JPEG of 2 MB or less with alt text; it appears in the media library | walk, test |
| 2 | An upload with empty alt text is refused with a message | walk, test |
| 3 | A `.html` file, a `.html` file renamed to `.png`, and any file over 2 MB are refused: the type is checked by extension and by the file's first bytes | walk, test |
| 4 | Uploads are stored under `media/`, and `media/` is git-ignored | read |
| 5 | Each library item shows a copyable Markdown snippet, `![<alt text>](media/<file>)` | walk |
| 6 | The upload form carries a CSRF token; its POST replayed without the token is refused | replay, test |
| 7 | After `uv run cms publish`, the file is in `site/media/`, and the post's `<img>` has the alt text and a relative `src` that loads in the preview | publish, test |

**The judge runs:** upload an image; try an empty alt text, a `.html` file and a `.html` file renamed to `.png`; paste a snippet into a published post; publish; preview with `python3 -m http.server -d site 8001`; check that every `<img>` in `site/` has `alt=` and loads.
- **Out of scope.** Inserting images with a button, resizing, thumbnails, deleting media, video, drag-and-drop, images in pages.
- **Deliverables.** The closed issue; `tests/test_media.py`; `docs/screenshots/mp2plus-media-1280.png` and `-390.png`; your report row.
- **Report row.** `| F1 | issue #<n>; tests/test_media.py; mp2plus-media-1280.png, mp2plus-media-390.png |`
- **Scoring.** Screenshots 1 · Trail 1 · Tests 1 · Function 6 = floor(6 × steps passed ÷ 7). Total 9.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| Images load on the home page, broken on post pages | a post page needs `../media/x.png` | make `src` relative to each page's folder |
| A renamed `.html` file is accepted | only the extension is checked | compare the first bytes with the PNG and JPEG signatures |
#### F2 Categories and tags (8 pts, about 40–55 min)
- **Goal.** Readers browse by topic. Each post has one category and any number of tags, and the public site has one index page per category and per tag.
- **Prerequisites.** MP2 done and Part 0 complete. Other exercises: none. A schema change: rebuild `cms.db` afterwards.
- **Roles.** Category and tag fields in the post editor, and the category filter: admin and editor.

**Steps.**
1. Create the issue (runbook 1), title `MP2plus F2: Categories and tags`; then `echo T<issue#> > .claude/state/phase`.
2. `/clear`, then the prompt below with your issue number. Then `rm cms.db && uv run python scripts/seed_demo.py`, then walk the acceptance checklist yourself; fix what fails.
3. `/code-review`, then the close-out message (runbook 5). `gh issue view <issue#>` shows CLOSED, with your comment above the close.
4. Save `docs/screenshots/mp2plus-categories-1280.png` and `mp2plus-categories-390.png`: a published category page. Then run the two checks (runbook 8).

**Prompt.**
```text
/implement #N Categories and tags, for posts only. Follow the issue's acceptance checklist exactly. One category per post as a single field; tags as one comma-separated field. The admin content list filters by category only. cms publish writes site/category/<slug>.html and site/tag/<slug>.html with published posts only, and every link between them is relative. Add the new terms to CONTEXT.md. Rules: no href="/ or src="/ in any template, admin pages included; use url_for or relative links. Every new form carries a CSRF token and refuses a POST without it. Every new setting gets a line in .env.example. If you change the database schema, keep scripts/seed_demo.py running clean from .env.example and tell me to run rm cms.db && uv run python scripts/seed_demo.py. Tests that existed before may only gain cases; ask me before changing an existing assertion. Put the new tests in tests/test_taxonomy.py and name each one test_step<k>_<what> after the acceptance step it checks. Ask before adding any dependency.
```
**Acceptance checklist.**
| # | Step | Checked by |
|---|---|---|
| 1 | A post has one category (a single field) and tags (one comma-separated field); both persist after save | walk, test |
| 2 | The admin content list filters by category | walk, test |
| 3 | `uv run cms publish` writes `site/category/<slug>.html` and `site/tag/<slug>.html`, each listing its published posts | publish, test |
| 4 | Each published post links to its category page and its tag pages with relative paths | publish |
| 5 | A draft with the same category and tag is absent from both index pages | publish, test |

**The judge runs:** give two posts a category and tags; filter the admin list by category; publish; open a category page and a tag page from a post's links; add a draft with the same category and tag, publish again, and check it is absent.
- **Out of scope.** Nested categories, tag clouds, a tag filter in the admin list, categories on pages, renaming a tag across posts.
- **Deliverables.** The closed issue; `tests/test_taxonomy.py`; `docs/screenshots/mp2plus-categories-1280.png` and `-390.png`; your report row.
- **Report row.** `| F2 | issue #<n>; tests/test_taxonomy.py; mp2plus-categories-1280.png, mp2plus-categories-390.png |`
- **Scoring.** Screenshots 1 · Trail 1 · Tests 1 · Function 5 = floor(5 × steps passed ÷ 5). Total 8.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| Category links break from a post page | a post page needs `../category/x.html` | make links relative to each page's folder |
| A tag with a space makes a broken file name | no slug was generated | slugify tag and category names for file names |
#### F3 Revision history with rollback (8 pts, about 40–55 min)
- **Goal.** Nobody loses work to a bad edit. Every save of a post stores a revision, and rolling back copies an old revision forward as a new one, so the history only grows.
- **Prerequisites.** MP2 done and Part 0 complete. Other exercises: none. A schema change: rebuild `cms.db` afterwards.
- **Roles.** Revision list, revision view and rollback: admin and editor.

**Steps.**
1. Create the issue (runbook 1), title `MP2plus F3: Revision history with rollback`; then `echo T<issue#> > .claude/state/phase`.
2. `/clear`, then the prompt below with your issue number. Then `rm cms.db && uv run python scripts/seed_demo.py`, then walk the acceptance checklist yourself; fix what fails.
3. `/code-review`, then the close-out message (runbook 5). `gh issue view <issue#>` shows CLOSED, with your comment above the close.
4. Save `docs/screenshots/mp2plus-revisions-1280.png` and `mp2plus-revisions-390.png`: a post's revision list. Then run the two checks (runbook 8).

**Prompt.**
```text
/implement #N Revision history with rollback, for posts only. Follow the issue's acceptance checklist exactly. Store revisions in their own table, with who, when, title and body, written on every save including the first create. Rollback is a POST that creates a new revision; it never deletes or rewrites an old one. Rules: no href="/ or src="/ in any template, admin pages included; use url_for or relative links. Every new form carries a CSRF token and refuses a POST without it. Every new setting gets a line in .env.example. If you change the database schema, keep scripts/seed_demo.py running clean from .env.example and tell me to run rm cms.db && uv run python scripts/seed_demo.py. Tests that existed before may only gain cases; ask me before changing an existing assertion. Put the new tests in tests/test_revisions.py and name each one test_step<k>_<what> after the acceptance step it checks. Ask before adding any dependency.
```
**Acceptance checklist.**
| # | Step | Checked by |
|---|---|---|
| 1 | Every save of a post, the first create included, stores a revision with who, when, title and body | test |
| 2 | The admin lists a post's revisions, newest first, and shows any one of them | walk |
| 3 | Creating a post and saving it twice more lists three revisions | walk, test |
| 4 | Rolling back to revision 1 adds revision 4, whose title and body equal revision 1's; nothing is deleted | walk, test |
| 5 | The rollback form carries a CSRF token; its POST replayed without the token is refused | replay, test |
| 6 | Revisions survive a server restart | walk |

**The judge runs:** create a post and save it twice more (three revisions); roll back to revision 1 (four revisions, revision 1's body); replay the rollback POST without its token; restart the server and check the list again.
- **Out of scope.** Revisions of pages, users or settings; side-by-side diffs; pruning; autosave.
- **Deliverables.** The closed issue; `tests/test_revisions.py`; `docs/screenshots/mp2plus-revisions-1280.png` and `-390.png`; your report row.
- **Report row.** `| F3 | issue #<n>; tests/test_revisions.py; mp2plus-revisions-1280.png, mp2plus-revisions-390.png |`
- **Scoring.** Screenshots 1 · Trail 1 · Tests 1 · Function 5 = floor(5 × steps passed ÷ 6). Total 8.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| Two revisions per save | both the create and the update path write one | write the revision in one shared save function |
| Rollback is a link, not a form | a GET changes state | make it a POST form with a CSRF token |
#### F4 Scheduled publishing (7 pts, about 35–50 min)
- **Goal.** An author finishes a post on Sunday and wants it public on Tuesday. The post gets a `publish_at` time and the status `scheduled`, and goes public the next time you publish after that time.
- **Prerequisites.** MP2 done and Part 0 complete. Other exercises: none. A new setting, `CMS_TIMEZONE` (default `America/New_York`), read with Python's `zoneinfo`; a schema change.
- **Roles.** Scheduling in the post editor: admin and editor.

**Steps.**
1. Create the issue (runbook 1), title `MP2plus F4: Scheduled publishing`; then `echo T<issue#> > .claude/state/phase`.
2. `/clear`, then the prompt below with your issue number. Then `rm cms.db && uv run python scripts/seed_demo.py`, then walk the acceptance checklist yourself; fix what fails.
3. `/code-review`, then the close-out message (runbook 5). `gh issue view <issue#>` shows CLOSED, with your comment above the close.
4. Save `docs/screenshots/mp2plus-scheduled-1280.png` and `mp2plus-scheduled-390.png`: the admin list with a scheduled post. Then run the two checks (runbook 8).

**Prompt.**
```text
/implement #N Scheduled publishing, for posts only. Follow the issue's acceptance checklist exactly. Add the status scheduled and a publish_at time. Read CMS_TIMEZONE with zoneinfo, default America/New_York, and add CMS_TIMEZONE=America/New_York to .env.example. Pass the current time into the publish filter instead of reading the clock inside it, so tests can freeze it. Rules: no href="/ or src="/ in any template, admin pages included; use url_for or relative links. Every new form carries a CSRF token and refuses a POST without it. Every new setting gets a line in .env.example. If you change the database schema, keep scripts/seed_demo.py running clean from .env.example and tell me to run rm cms.db && uv run python scripts/seed_demo.py. Tests that existed before may only gain cases; ask me before changing an existing assertion. Put the new tests in tests/test_scheduled.py and name each one test_step<k>_<what> after the acceptance step it checks. Ask before adding any dependency.
```
**Acceptance checklist.**
| # | Step | Checked by |
|---|---|---|
| 1 | A post can be saved with the status `scheduled` and a `publish_at` date and time | walk, test |
| 2 | The admin content list shows scheduled posts with their `publish_at` time | walk |
| 3 | `uv run cms publish` exports a scheduled post whose `publish_at` is now or earlier in `CMS_TIMEZONE` | publish, test |
| 4 | A scheduled post whose `publish_at` is in the future is not exported | publish, test |
| 5 | The tests freeze the clock: the current time is passed in, so they pass on any day | read, test |
| 6 | `.env.example` has the line `CMS_TIMEZONE=America/New_York`, and `America/New_York` is the default when the variable is unset | read, test |

**The judge runs:** schedule one post an hour in the past and one a day ahead, both in `America/New_York` time; publish; check that only the first is in `site/` and that the admin list shows both with their times.
- **Out of scope.** A background scheduler, flipping the status to `published`, recurring posts, an unpublish time, scheduled pages.
- **Deliverables.** The closed issue; `tests/test_scheduled.py`; `docs/screenshots/mp2plus-scheduled-1280.png` and `-390.png`; your report row.
- **Report row.** `| F4 | issue #<n>; tests/test_scheduled.py; mp2plus-scheduled-1280.png, mp2plus-scheduled-390.png |`
- **Scoring.** Screenshots 1 · Trail 1 · Tests 1 · Function 4 = floor(4 × steps passed ÷ 6). Total 7.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| The test passes today, fails tomorrow | the code reads the real clock | pass `now` into the filter; tests pass a fixed time |
| A post goes public hours early or late | naive times compared with UTC | store aware times; compare in `CMS_TIMEZONE` |
#### F5 Site search (7 pts, about 35–50 min)
- **Goal.** Readers find a post without scrolling. `cms publish` writes a small search index and a `search.html` page that queries it with one short script. ADR-002 rejected a JavaScript application stack, not one script on the public site; if you also do P3, that exception makes a good ADR.
- **Prerequisites.** MP2 done and Part 0 complete. Other exercises: none.
- **Roles.** No new admin routes.

**Steps.**
1. Create the issue (runbook 1), title `MP2plus F5: Site search`; then `echo T<issue#> > .claude/state/phase`.
2. `/clear`, then the prompt below with your issue number. Then publish, preview with `python3 -m http.server -d site 8001`, and walk the acceptance checklist yourself; fix what fails.
3. `/code-review`, then the close-out message (runbook 5). `gh issue view <issue#>` shows CLOSED, with your comment above the close.
4. Save `docs/screenshots/mp2plus-search-1280.png` and `mp2plus-search-390.png`: a search with one result. Then run the two checks (runbook 8).

**Prompt.**
```text
/implement #N Site search on the public site. Follow the issue's acceptance checklist exactly. cms publish writes site/search-index.json from published posts and pages only: title, relative URL, short excerpt. site/search.html loads one plain JavaScript file of at most 60 lines, with relative paths and no library, and the home page links to it. Rules: no href="/ or src="/ in any template, admin pages included; use url_for or relative links. Every new form carries a CSRF token and refuses a POST without it. Every new setting gets a line in .env.example. If you change the database schema, keep scripts/seed_demo.py running clean from .env.example and tell me to run rm cms.db && uv run python scripts/seed_demo.py. Tests that existed before may only gain cases; ask me before changing an existing assertion. Put the new tests in tests/test_search.py and name each one test_step<k>_<what> after the acceptance step it checks. Ask before adding any dependency.
```
**Acceptance checklist.**
| # | Step | Checked by |
|---|---|---|
| 1 | `uv run cms publish` writes `site/search-index.json` with the title, relative URL and a short excerpt of each published post and page | publish, test |
| 2 | Drafts are absent from the index | publish, test |
| 3 | `site/search.html` loads one plain JavaScript file of 60 lines or fewer, with no external dependency and relative paths only | read |
| 4 | Typing a word from a published post's title into `search.html` lists a link to that post, and the link opens it | walk |
| 5 | The published home page links to `search.html` with a relative path | publish, test |

**The judge runs:** publish with a draft present and read the index; preview with `python3 -m http.server -d site 8001` (opening the file directly blocks the index fetch); follow the home page's search link; search for a word from one post's title and open the result.
- **Out of scope.** A search box in the admin, fuzzy matching, ranking, a search server, searching drafts.
- **Deliverables.** The closed issue; `tests/test_search.py`; `docs/screenshots/mp2plus-search-1280.png` and `-390.png`; your report row.
- **Report row.** `| F5 | issue #<n>; tests/test_search.py; mp2plus-search-1280.png, mp2plus-search-390.png |`
- **Scoring.** Screenshots 1 · Trail 1 · Tests 1 · Function 4 = floor(4 × steps passed ÷ 5). Total 7.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| Search finds nothing; the console shows a fetch error | the file was opened directly | preview with `python3 -m http.server -d site 8001` |
| Works locally, fails on Pages | `fetch("/search-index.json")` | fetch `search-index.json`, relative |
#### F6 Comments with moderation (9 pts, about 45–60 min)
- **Goal.** Readers send comments, and only the ones you approve are published. A static site cannot accept posts, so comments enter through an admin form; how readers reach you is out of scope. Approved comments are exported under their post and sanitized like Markdown.
- **Prerequisites.** MP2 done and Part 0 complete. Other exercises: none. A schema change; MP2's sanitizer.
- **Roles.** The Moderation queue and its forms: admin only.

**Steps.**
1. Create the issue (runbook 1), title `MP2plus F6: Comments with moderation`; then `echo T<issue#> > .claude/state/phase`.
2. `/clear`, then the prompt below with your issue number. Then `rm cms.db && uv run python scripts/seed_demo.py`, then walk the acceptance checklist yourself; fix what fails.
3. `/code-review`, then the close-out message (runbook 5). `gh issue view <issue#>` shows CLOSED, with your comment above the close.
4. Save `docs/screenshots/mp2plus-comments-1280.png` and `mp2plus-comments-390.png`: the Moderation queue with one pending comment. Then run the two checks (runbook 8).

**Prompt.**
```text
/implement #N Comments with moderation, for posts only. Follow the issue's acceptance checklist exactly. One admin-only Moderation queue page: a form that adds a pending comment to a post, and approve and reject buttons on each pending comment; no editing. Sanitize comment bodies with the same sanitizer as post Markdown, and export approved comments only. Rules: no href="/ or src="/ in any template, admin pages included; use url_for or relative links. Every new form carries a CSRF token and refuses a POST without it. Every new setting gets a line in .env.example. If you change the database schema, keep scripts/seed_demo.py running clean from .env.example and tell me to run rm cms.db && uv run python scripts/seed_demo.py. Tests that existed before may only gain cases; ask me before changing an existing assertion. Put the new tests in tests/test_comments.py and name each one test_step<k>_<what> after the acceptance step it checks. Ask before adding any dependency.
```
**Acceptance checklist.**
| # | Step | Checked by |
|---|---|---|
| 1 | A comments table stores reader name, body, status (pending, approved or rejected), post and time | read, test |
| 2 | The Moderation queue (admin only) has a form that adds a pending comment to a post, and approve and reject buttons on each pending comment | walk, test |
| 3 | A pending comment is absent from the export; after approval and a new publish it appears under its post | publish, test |
| 4 | A rejected comment is absent from the export | publish, test |
| 5 | A comment carrying MP2's D4 payload (`<script>` and an `onerror=` attribute) does not execute in the queue or the export | walk, test |
| 6 | The queue's forms carry a CSRF token; each POST replayed without the token is refused | replay, test |
| 7 | An editor who requests the Moderation queue URL gets 403 or a redirect | test |

**The judge runs:** add a pending comment and publish (absent); approve it and publish (present); reject another (absent); run the D4 payload through a comment; replay each queue POST without its token; request the queue as the editor.
- **Out of scope.** A public comment form, reader accounts, editing comments, spam filtering, threaded replies, email notifications.
- **Deliverables.** The closed issue; `tests/test_comments.py`; `docs/screenshots/mp2plus-comments-1280.png` and `-390.png`; your report row.
- **Report row.** `| F6 | issue #<n>; tests/test_comments.py; mp2plus-comments-1280.png, mp2plus-comments-390.png |`
- **Scoring.** Screenshots 1 · Trail 1 · Tests 1 · Function 6 = floor(6 × steps passed ÷ 7). Total 9.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| The payload runs in the queue but not the export | the queue template marks the raw body safe | render the sanitized body only |
| An editor can open the queue | the route lacks the admin-only check | add the same dependency your MP2 admin routes use |
#### F7 Plugin or hook system (9 pts, about 45–60 min)
- **Goal.** New behaviour arrives without editing the publisher. A small registry offers two hooks; plugins are Python files in `app/plugins/`, switched on and off on an admin Settings page. You ship one plugin: reading time.
- **Prerequisites.** MP2 done and Part 0 complete. F7 and F8 share one admin Settings page (`/admin/settings`, stored in a `settings` table). Whichever of the two you build first builds the page; the other adds a field to it.
- **Roles.** The Settings page: admin only.

**Steps.**
1. Create the issue (runbook 1), title `MP2plus F7: Plugin or hook system`; then `echo T<issue#> > .claude/state/phase`.
2. `/clear`, then the prompt below with your issue number. Then `rm cms.db && uv run python scripts/seed_demo.py`, then walk the acceptance checklist yourself; fix what fails.
3. `/code-review`, then the close-out message (runbook 5). `gh issue view <issue#>` shows CLOSED, with your comment above the close.
4. Save `docs/screenshots/mp2plus-plugins-1280.png` and `mp2plus-plugins-390.png`: the Settings page with the plugin switch. Then run the two checks (runbook 8).

**Prompt.**
```text
/implement #N Plugin or hook system. Follow the issue's acceptance checklist exactly. Two hooks only: before_publish(item) and render_body(html, item). Discover plugins from app/plugins/ in alphabetical order of file name. Ship one plugin, reading time, which adds "N min read" to each exported post. Plugins are switched on and off on an admin-only Settings page at /admin/settings, stored in a settings table; build that page if it does not exist yet. Rules: no href="/ or src="/ in any template, admin pages included; use url_for or relative links. Every new form carries a CSRF token and refuses a POST without it. Every new setting gets a line in .env.example. If you change the database schema, keep scripts/seed_demo.py running clean from .env.example and tell me to run rm cms.db && uv run python scripts/seed_demo.py. Tests that existed before may only gain cases; ask me before changing an existing assertion. Put the new tests in tests/test_plugins.py and name each one test_step<k>_<what> after the acceptance step it checks. Ask before adding any dependency.
```
**Acceptance checklist.**
| # | Step | Checked by |
|---|---|---|
| 1 | A registry offers two hooks, `before_publish(item)` and `render_body(html, item)` | read, test |
| 2 | Plugins are discovered from `app/plugins/` without editing the publisher | test |
| 3 | The shipped reading-time plugin, when enabled, adds a `N min read` line to every exported post | publish, test |
| 4 | Disabling the plugin on the admin Settings page and publishing again removes that line | walk, publish |
| 5 | Hooks run in alphabetical order of plugin file name: a test plugin whose name sorts later runs later | test |
| 6 | The Settings form carries a CSRF token; its POST replayed without the token is refused | replay, test |

**The judge runs:** enable the plugin and publish (line present); disable it on the Settings page and publish (line absent); replay the Settings POST without its token; run your ordering test.
- **Out of scope.** A table-of-contents plugin, installing plugins from the internet, plugin dependencies, editing plugin code in the browser.
- **Deliverables.** The closed issue; `tests/test_plugins.py`; `docs/screenshots/mp2plus-plugins-1280.png` and `-390.png`; your report row.
- **Report row.** `| F7 | issue #<n>; tests/test_plugins.py; mp2plus-plugins-1280.png, mp2plus-plugins-390.png |`
- **Scoring.** Screenshots 1 · Trail 1 · Tests 1 · Function 6 = floor(6 × steps passed ÷ 6). Total 9.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| The ordering test passes on your machine only | discovery uses directory order | sort the file names |
| The plugin stays on after you switch it off | publish reads a cached setting | read the setting when `cms publish` runs |
#### F8 Switchable theme (7 pts, about 35–50 min)
- **Goal.** Your client changes the site's look without a developer. Two themes, each one CSS file, are selectable on the admin Settings page, and `cms publish` exports the selected one.
- **Prerequisites.** MP2 done and Part 0 complete. Shares the Settings page with F7 (see F7). The template keeps its CSS as a string in `app/publish.py`; this exercise moves it into a theme file.
- **Roles.** The Settings page: admin only.

**Steps.**
1. Create the issue (runbook 1), title `MP2plus F8: Switchable theme`; then `echo T<issue#> > .claude/state/phase`.
2. `/clear`, then the prompt below with your issue number. Then `rm cms.db && uv run python scripts/seed_demo.py`, then walk the acceptance checklist yourself; fix what fails.
3. `/code-review`, then the close-out message (runbook 5). `gh issue view <issue#>` shows CLOSED, with your comment above the close.
4. Save `docs/screenshots/mp2plus-theme-1280.png` and `mp2plus-theme-390.png`: the home page in the second theme. Then run the two checks (runbook 8).

**Prompt.**
```text
/implement #N Switchable theme, CSS only. Follow the issue's acceptance checklist exactly. Move the CSS out of app/publish.py into app/themes/<name>/style.css and add a second theme. The theme is chosen on an admin-only Settings page at /admin/settings, stored in a settings table; build that page if it does not exist yet. cms publish writes the selected theme's CSS as site/style.css. Check both themes at 390 px wide. Rules: no href="/ or src="/ in any template, admin pages included; use url_for or relative links. Every new form carries a CSRF token and refuses a POST without it. Every new setting gets a line in .env.example. If you change the database schema, keep scripts/seed_demo.py running clean from .env.example and tell me to run rm cms.db && uv run python scripts/seed_demo.py. Tests that existed before may only gain cases; ask me before changing an existing assertion. Put the new tests in tests/test_theme.py and name each one test_step<k>_<what> after the acceptance step it checks. Ask before adding any dependency.
```
**Acceptance checklist.**
| # | Step | Checked by |
|---|---|---|
| 1 | Two themes exist, each one CSS file in its own folder under `app/themes/` | read |
| 2 | The admin Settings page selects the theme, and the choice survives a server restart | walk, test |
| 3 | `uv run cms publish` writes the selected theme's CSS as `site/style.css`, so every page's relative stylesheet link still works | publish, test |
| 4 | Switching back and publishing again restores the first theme's CSS | publish, test |
| 5 | Both themes show no horizontal overflow at 390 px on the home page and one post | walk |
| 6 | The Settings form carries a CSRF token; its POST replayed without the token is refused | replay, test |

**The judge runs:** switch the theme; restart the server; publish and compare `site/style.css` with the theme's file; switch back and publish again; check both themes at 390 px; replay the Settings POST without its token.
- **Out of scope.** Template overrides, theme upload, per-post themes, a visual theme editor.
- **Deliverables.** The closed issue; `tests/test_theme.py`; `docs/screenshots/mp2plus-theme-1280.png` and `-390.png`; your report row.
- **Report row.** `| F8 | issue #<n>; tests/test_theme.py; mp2plus-theme-1280.png, mp2plus-theme-390.png |`
- **Scoring.** Screenshots 1 · Trail 1 · Tests 1 · Function 4 = floor(4 × steps passed ÷ 6). Total 7.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| Post pages lose their styles | they link `style.css` instead of `../style.css` | keep MP2's relative links; only the file's contents change |
| `test_t00.py` fails | `render_site` no longer writes `style.css` | always write `site/style.css` |
#### F9 Production configuration (8 pts, about 40–55 min)
- **Goal.** Your app refuses to run in production with unsafe settings. With `CMS_ENV=production` it needs a real secret key and an admin account from the environment, never creates demo users, and the README says how to start it. Everything runs on your machine: a live deploy is not part of MP2plus.
- **Prerequisites.** MP2 done and Part 0 complete. Other exercises: none. New settings `CMS_ENV` (default `development`) and `CMS_ADMIN_EMAIL`.
- **Roles.** No new routes.

**Steps.**
1. Create the issue (runbook 1), title `MP2plus F9: Production configuration`; then `echo T<issue#> > .claude/state/phase`.
2. `/clear`, then the prompt below with your issue number. Then walk the acceptance checklist yourself with the commands under **The judge runs**; fix what fails.
3. `/code-review`, then the close-out message (runbook 5). `gh issue view <issue#>` shows CLOSED, with your comment above the close.
4. Save `docs/screenshots/mp2plus-production-1280.png` and `mp2plus-production-390.png`: the admin dashboard after logging in as the production admin. Then run the two checks (runbook 8).

**Prompt.**
```text
/implement #N Production configuration, local only. Follow the issue's acceptance checklist exactly. Put the checks in one function that takes the environment as a dict, so tests pass a dict instead of changing the real environment. Call it in create_app() and at the start of cms serve, so a bad configuration stops the server with a message naming the variable. In production, scripts/seed_demo.py refuses to run, and startup creates the admin from CMS_ADMIN_EMAIL and CMS_ADMIN_PASSWORD if no admin exists. Variables set on the command line win over .env. Add CMS_ENV=development and CMS_ADMIN_EMAIL to .env.example and a Production section to README.md. Development behaviour does not change. Rules: no href="/ or src="/ in any template, admin pages included; use url_for or relative links. Every new form carries a CSRF token and refuses a POST without it. Every new setting gets a line in .env.example. If you change the database schema, keep scripts/seed_demo.py running clean from .env.example and tell me to run rm cms.db && uv run python scripts/seed_demo.py. Tests that existed before may only gain cases; ask me before changing an existing assertion. Put the new tests in tests/test_production.py and name each one test_step<k>_<what> after the acceptance step it checks. Ask before adding any dependency.
```
**Acceptance checklist.**
| # | Step | Checked by |
|---|---|---|
| 1 | With `CMS_ENV=production`, `uv run cms serve` refuses to start when `CMS_SECRET_KEY` is unset, equals the development default in `app/settings.py`, or equals the `.env.example` value; the message names the variable | walk, test |
| 2 | With `CMS_ENV=production`, it also refuses to start when `CMS_ADMIN_EMAIL` or `CMS_ADMIN_PASSWORD` is unset, or the password equals the `.env.example` value | test |
| 3 | With `CMS_ENV=production`, `scripts/seed_demo.py` exits non-zero with a message and creates nothing | walk, test |
| 4 | Started in production on an empty database, the app creates one admin from `CMS_ADMIN_EMAIL` and `CMS_ADMIN_PASSWORD`; that login works, and the demo logins from `tests/conftest.py` are refused | walk, test |
| 5 | `.env.example` lists `CMS_ENV=development` and `CMS_ADMIN_EMAIL`, and the README has a *Production* section naming every variable production needs and the start command | read |

**The judge runs:** `CMS_ENV=production uv run cms serve --port 8001` with the `.env.example` values (refused); the same with fresh values for `CMS_SECRET_KEY`, `CMS_ADMIN_EMAIL` and `CMS_ADMIN_PASSWORD` and `CMS_DATABASE=prod-check.db` (starts); logs in as that admin and tries the demo logins; runs the seed script with `CMS_ENV=production`.
- **Out of scope.** Hosting, HTTPS, a live URL, a rate limiter (S2 covers it), email.
- **Deliverables.** The closed issue; `tests/test_production.py`; `docs/screenshots/mp2plus-production-1280.png` and `-390.png`; the README *Production* section; your report row.
- **Report row.** `| F9 | issue #<n>; tests/test_production.py; mp2plus-production-1280.png, mp2plus-production-390.png |`
- **Scoring.** Screenshots 1 · Trail 1 · Tests 1 · Function 5 = floor(5 × steps passed ÷ 5). Total 8.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| Tests pass alone, fail together | a test changed `os.environ` | pass a dict to the check function; never set the real environment |
| Production mode starts with the `.env` secret | `.env` overrides the command line | load `.env` without overriding variables already set |
### 1.2 Process (P1–P4)

#### P1 Pull-request workflow (6 pts, about 30–45 min)
- **Goal.** Ship one change through a branch, a pull request and a review before the merge, the way most teams work.
- **Prerequisites.** Part 0 complete. P1 carries one change: a feature from this menu (scored as that feature too), or one item from your MP2 feedback's repair list, written as a small issue. A repair earns P1's points only, not MP2 points.
- **Roles.** No new routes of its own; a carried feature keeps its own Roles line.

**Steps.**
1. Create the issue first. For a feature, that feature's step 1. For a repair: `gh issue create --label stretch --title "MP2plus P1: <the repair>"`, body = two to four acceptance steps, then `Blocked by: none`. Set the phase: `echo T<issue#> > .claude/state/phase` for a feature, `echo P1 > .claude/state/phase` for a repair.
2. Branch: `git switch main && git pull && git switch -c mp2plus-<slug>`.
3. `/clear`, then the feature's prompt or the prompt below; let it commit on the branch.
4. `git push -u origin mp2plus-<slug>`, then `gh pr create --title "MP2plus P1: <the change>" --body "Closes #<issue#>"`.
5. `/code-review`, then: `Post the code-review findings and how each was resolved as a comment on pull request #<pr#>, then commit and push the fixes to this branch.`
6. `gh pr merge <pr#> --merge --delete-branch`, then `git switch main && git pull` and `gh issue view <issue#>`. **Expected:** CLOSED, closed by your pull request, with the review comment on the PR dated before the merge.

**Prompt.** For a repair (a feature uses its own prompt):
```text
/implement #N <the repair, in one sentence>. Follow the issue's acceptance steps exactly. Rules: no href="/ or src="/ in any template, admin pages included; use url_for or relative links. Every new form carries a CSRF token and refuses a POST without it. Every new setting gets a line in .env.example. If you change the database schema, keep scripts/seed_demo.py running clean from .env.example and tell me to run rm cms.db && uv run python scripts/seed_demo.py. Tests that existed before may only gain cases; ask me before changing an existing assertion. Ask before adding any dependency.
```
**Acceptance checklist.**
| # | Step | Checked by | Pts |
|---|---|---|---|
| 1 | The issue's `createdAt` is before the branch's first push | github | 1 |
| 2 | The PR comes from a branch off `main`, and its body contains `Closes #<issue#>` | github | 1 |
| 3 | A `/code-review` findings comment on the PR, listing each finding and how it was resolved, is dated before `mergedAt` | github | 2 |
| 4 | At least one commit was pushed to the branch after that comment | github | 1 |
| 5 | The PR is merged, and the merge closed the issue | github | 1 |

- **Out of scope.** Reviews by another person, protected branches, CI.
- **Deliverables.** The closed issue; the merged PR; your report row.
- **Report row.** `| P1 | PR #<n> closing issue #<n>; carries <F-id, or "MP2 repair: <what>"> |`
- **Scoring.** One point per row as listed. Total 6. When P1 carries a feature, row 3's comment is also that feature's findings comment (its Trail line); a missing or late comment costs both.
  - ✅ *"Findings: (1) upload accepted a renamed `.html` file; fixed by checking the first bytes, test added. (2) suggested Pillow for resizing; rejected, resizing is out of scope."* Posted before the merge.
  - ❌ *"LGTM"*, or any comment posted after the merge.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| The PR shows unrelated commits | you branched from another branch | ask Claude to explain a rebase onto `main` before running it |
| The review found nothing to fix | a small change | ask `/code-review` for the weakest test in the diff and strengthen it; that is your fix commit |
#### P2 `/prototype` side session (7 pts, about 35–50 min)
- **Goal.** Settle one design question with throwaway code instead of guessing, then carry the answer back into your real code.
- **Prerequisites.** Part 0 complete. Code where the decision lands: a feature you build in MP2plus, or a small commit on `main`.
- **Roles.** No new routes.

**Steps.**
1. `echo P2 > .claude/state/phase`. Pick a question that fits one of `/prototype`'s two modes. Logic: *"Can a rejected comment be approved later, and what does the export show?"* Look: *"Which of three media-library layouts works at 390 px?"*
2. `git switch -c prototype-<topic>`, then `/clear` and `/prototype <your question, in one sentence>`.
3. When you have an answer, commit the prototype on that branch, `git push -u origin prototype-<topic>`, then `git switch main`. Carry the decision into the code on `main`, and add a `CONTEXT.md` entry naming it.
4. `/handoff Record this prototype in four parts: the question, what was tried (branch prototype-<topic>), the finding, and what was carried back (the file path on main).`
5. `/handoff` tells you the path of the file it wrote; copy it to `docs/handoff/{NN}_prototype-{topic}_{YYYYMMDD}.md`, `{NN}` continuing the folder's numbering. Commit with a message that starts `P2:` and push.

**Prompt.** The `/prototype` and `/handoff` lines in steps 2 and 4.

**Acceptance checklist.**
| # | Step | Checked by | Pts |
|---|---|---|---|
| 1 | `docs/handoff/<NN>_prototype-<topic>_<YYYYMMDD>.md` exists, with `<NN>` continuing that folder's numbering | read | 1 |
| 2 | It states the design question in one sentence | read | 1 |
| 3 | It says what was tried and names the prototype branch, which exists on GitHub | read, github | 1 |
| 4 | It states the finding with one concrete observation: a number, a state the model reached, or the variant chosen | read | 1 |
| 5 | It says what was carried back, with the file path on `main` where the decision lands | read | 1 |
| 6 | The code at that path implements the decision | read | 1 |
| 7 | `CONTEXT.md` has an entry naming the decision | read | 1 |

- **Out of scope.** Polishing the prototype, tests for it, merging its branch.
- **Deliverables.** `docs/handoff/{NN}_prototype-{topic}_{YYYYMMDD}.md`; the pushed `prototype-<topic>` branch; the `CONTEXT.md` entry; your report row.
- **Report row.** `| P2 | docs/handoff/<file>; branch prototype-<topic>; decision in <file path> |`
- **Scoring.** One point per row as listed. Total 7.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| Your `/prototype` offers neither mode | a different skill version | ask Claude for a throwaway script on the branch; the handoff parts are the same |
| You cannot find the handoff file | the skill saves outside the repo | ask `where did you save the handoff?` |
#### P3 Decision record (6 pts, about 30–45 min)
- **Goal.** Write down why your CMS is the way it is, so the next developer, or you in a month, does not undo a choice by accident.
- **Prerequisites.** Part 0 complete. Decisions you made in MP2 or MP2plus, already in the code.
- **Roles.** No new routes.

**Steps.**
1. `echo P3 > .claude/state/phase`, then `ls docs/adr/` and take the next free number. The template ships ADR-001 and ADR-002.
2. Add a **Decisions** table to `CONTEXT.md` with at least three rows: question, choice, why. Write the "why" yourself.
3. `/clear`, then the prompt below for the decision that is hardest to reverse. Edit the draft until it says what you mean.
4. Commit with a message that starts `P3:` and push.

**Prompt.**
```text
Write docs/adr/ADR-<NNN>-<slug>.md in the format of docs/adr/ADR-002-stack.md. Decision: <what I decided>. Context: <what forced it>. Name the options I rejected and why. Keep it under 30 lines.
```

- ✅ `| Where do uploads live? | media/ at the repo root, git-ignored | Photos are 1–3 MB each; I did not want them in git history, same reason as cms.db |`
- ❌ `| Storage | Local filesystem | Simple, efficient, and follows best practices |` (it restates the choice)

**Acceptance checklist.**
| # | Step | Checked by | Pts |
|---|---|---|---|
| 1 | `CONTEXT.md` has a **Decisions** table with at least three rows: question, choice, why | read | 1 |
| 2 | Row 1's "why" gives a real reason in your own words (a client fact, a measurement or a constraint), not a restatement of the choice | read | 1 |
| 3 | Row 2's "why" passes the same test | read | 1 |
| 4 | Row 3's "why" passes the same test | read | 1 |
| 5 | `docs/adr/ADR-<NNN>-<slug>.md`, numbered with the next free number, records the hardest-to-reverse decision in ADR-002's format (status, date, context, decision, consequences) and names at least one rejected option | read | 1 |
| 6 | The ADR's decision matches the code | read | 1 |

- **Out of scope.** Rewriting ADR-001 or ADR-002; ADRs for easy-to-reverse choices.
- **Deliverables.** The Decisions table in `CONTEXT.md`; `docs/adr/ADR-<NNN>-<slug>.md`; your report row.
- **Report row.** `| P3 | CONTEXT.md Decisions table; docs/adr/ADR-<NNN>-<slug>.md |`
- **Scoring.** One point per row as listed. Total 6.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| The ADR describes a decision the code does not show | it was planned, not built | pick a decision that is in the code |
#### P4 Budget re-forecast (6 pts, about 30–40 min)
- **Goal.** Forecast what your next exercises will cost in usage, then measure what they did cost and explain the gap.
- **Prerequisites.** Part 0 complete. MP2 Exercise B done: `spend()` in `scripts/usage_report.py` works and `tests/test_usage_report.py` passes. One other exercise to measure, with its phase set (runbook 2).
- **Roles.** No new routes.

**Steps.**
1. Before your next exercise, in your terminal and not inside Claude (so the ledger does not change between the run and the commit): `uv run python scripts/usage_report.py --remaining 3`, where 3 stands for the number of exercises still in your plan. **Expected:** the phase table, then `Tickets done: ...` and `Forecast: 3 tickets need ~X% of the weekly cap; Y% remains → FITS` (or `TIGHT`, or `OVER BUDGET`).
2. Paste those two lines into `notes/mp2plus-plan.md` under `## P4 before`, name the exercise you do next, and commit the plan with `notes/usage-ledger.csv` (message `P4: before`). Push. If the verdict is not `FITS`, apply MP2's fixes in order (MP2 manual Part 5.6) or pick a smaller exercise.
3. After at least one other exercise is done, run the same command in your terminal with the number of exercises you have left.
4. In your report, under `## P4`: paste the two lines, a cost table (one row per MP2plus phase, copied from the phase table: phase, turns, 5h spent, weekly), and two or three sentences on the largest gap between forecast and actual. Commit the report with `notes/usage-ledger.csv` (message `P4: after`) and push.

**Prompt.** None: P4 is your own work.

**Acceptance checklist.**
| # | Step | Checked by | Pts |
|---|---|---|---|
| 1 | The "before" lines (`Tickets done` and `Forecast`) are in `notes/mp2plus-plan.md`, committed together with `notes/usage-ledger.csv` before the first commit of the exercise the plan names next | read | 1 |
| 2 | The "after" lines are in the report, committed together with `notes/usage-ledger.csv` after at least one other exercise is done | read | 1 |
| 3 | Re-running the same `usage_report.py` command at each of those two commits prints the same lines | run | 1 |
| 4 | The report's cost table has one row per MP2plus phase, copied from the phase table of the "after" run | read, run | 1 |
| 5 | Every exercise in your report has its own phase row in the "after" run (`T<issue#>` for a feature, its id otherwise) | run | 1 |
| 6 | Two or three sentences explain the largest gap between the forecast cost per ticket and one exercise's actual cost, quoting both numbers and giving a cause | read | 1 |

- **Out of scope.** Changing `usage_report.py`; dollar costs.
- **Deliverables.** The `## P4 before` section in `notes/mp2plus-plan.md`; the `## P4` section in your report; both commits; your report row.
- **Report row.** `| P4 | before: commit <sha>; after: commit <sha>; see the P4 section |`
- **Scoring.** One point per row as listed. Total 6.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| `NotImplementedError: MP2 Exercise B` | `spend()` was never written | finish MP2 Exercise B first (MP2 manual Part 5.6) |
| Your exercise has no phase row | the phase was not set before the session | set it first next time; explain the gap in your sentences |
### 1.3 Security (S1–S2)

#### S1 Direct-URL access matrix (6 pts, about 30–45 min)
- **Goal.** Checklist #10: access control lives in code, not in hidden links. One test asks every admin-only route, read from the app's router, whether the editor and an anonymous visitor are kept out. It extends MP2 rubric item D3.
- **Prerequisites.** Part 0 complete. MP2's login and roles; `client_as` in `tests/conftest.py`. Do it after your features, so their admin-only routes are covered.
- **Roles.** No new routes. The test covers every admin-only route, including those your features' Roles lines name.

**Steps.**
1. `echo S1 > .claude/state/phase`, then `/clear` and the prompt below.
2. `uv run pytest -q tests/test_access_matrix.py`. **Expected:** `passed`.
3. Check it yourself: add a throwaway admin-only route, marked the way your other admin routes are, and run the test again. It must cover the new route with no edit to the test. Delete the throwaway route.
4. Commit with a message that starts `S1:` and push.

**Prompt.**
```text
/tdd Write tests/test_access_matrix.py. Build the app with create_app() and collect every admin-only route from app.routes, using a marker in code (for example the admin-only dependency), not a hand-written list. For each route and its method, assert client_as("editor") gets 403 or a redirect, and an anonymous client is redirected to login. Fill path parameters with the id of a seeded item. Do not change existing tests.
```
**Acceptance checklist.**
| # | Step | Checked by | Pts |
|---|---|---|---|
| 1 | `tests/test_access_matrix.py` exists and passes | test | 1 |
| 2 | Its route list is built from the app's router (`create_app().routes`) through a marker in code, such as the admin-only dependency, not typed by hand | read | 1 |
| 3 | A new admin-only route, marked the same way, is tested without editing the test (the judge adds one in a scratch copy) | test | 1 |
| 4 | Every admin-only route, feature routes included, is in the generated list | read, test | 1 |
| 5 | For each route, the editor gets 403 or a redirect | test | 1 |
| 6 | For each route, an anonymous client is redirected to login | test | 1 |

- **Out of scope.** Testing editor routes, rate limits, CSRF.
- **Deliverables.** `tests/test_access_matrix.py`; your report row.
- **Report row.** `| S1 | tests/test_access_matrix.py |`
- **Scoring.** One point per row as listed. Total 6. Rows 2 and 3 together are the "generated from the router" tier.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| The test finds no routes | admin routes carry no marker the test can see | mark them all the same way, for example one shared dependency |
| A route returns 422, not 403 | the path parameter is not a real id | fill it with a seeded item's id |
#### S2 Login hardening (8 pts, about 40–55 min)
- **Goal.** Two attacks, two fixes. Checklist #2: a wrong password and an unknown email give the same answer, so an attacker cannot learn which emails have accounts. And guessing is slowed: after five failed logins within 15 minutes, the next attempt is refused.
- **Prerequisites.** Part 0 complete. MP2's login. Adding a fixture to `tests/conftest.py` counts as adding a case and does not break the gate.
- **Roles.** No new routes.

**Steps.**
1. `echo S2 > .claude/state/phase`, then `/clear` and the first prompt below.
2. `/clear`, then the second prompt below.
3. `uv run pytest -q`. **Expected:** `passed`, with no MP2 test failing. Commit with a message that starts `S2:` and push.

**Prompt.**
```text
/tdd Make a wrong password and an unknown email produce the same login error message and status code. Add tests/test_login_hardening.py with a test that asserts both responses match.
```
```text
/tdd Rate-limit login, keyed on the account: after 5 failed attempts for one email within 15 minutes, refuse further attempts for that email with 429 or a lockout message, even with the right password. Pass the clock in so tests can freeze it. In tests/test_login_hardening.py, test that attempt 6 is refused, that a login works again once 15 minutes have passed, and that another email can still log in. Reset the limiter in a fixture in tests/conftest.py. No new dependencies.
```
**Acceptance checklist.**
| # | Step | Checked by | Pts |
|---|---|---|---|
| 1 | A wrong password and an unknown email give the same message and the same status code | walk | 1 |
| 2 | A test asserts that both responses match | test | 1 |
| 3 | After 5 failed logins within 15 minutes, the 6th attempt is refused with 429 or a lockout message, even with the right password | walk | 2 |
| 4 | A test with a frozen clock asserts that attempt 6 is refused | test | 1 |
| 5 | A test with a frozen clock asserts that a login works again once 15 minutes have passed | test | 1 |
| 6 | The limiter is keyed on the account: 5 failures for one email do not block another email's correct login from the same client | test | 1 |
| 7 | A fixture in `tests/conftest.py` resets the limiter between tests, so the full suite stays green | read, test | 1 |

- **Out of scope.** CAPTCHAs, email alerts, password rules, limiting by IP address alone.
- **Deliverables.** `tests/test_login_hardening.py`; the fixture in `tests/conftest.py`; your report row.
- **Report row.** `| S2 | tests/test_login_hardening.py; fixture <name> in tests/conftest.py |`
- **Scoring.** One point per row as listed. Total 8.

**If it goes wrong.**
| Symptom | Cause | Fix |
|---|---|---|
| Other tests start failing with 429 | the limiter's state is shared across tests | reset it in the conftest fixture |
| An MP2 login test fails | it asserted the old message text | declare the change (Part 0 gate box) and assert the new shared message |

---

## Part 2 — Submit
**Time: 20 min. No points, but required: no tag and email, no points.**

**Before you tag.** Every exercise you did has its report row. Then run:

```bash
uv run python scripts/check_submission.py --stage 2
uv run pytest -q
```

**Expected:** no `FAIL` line that was not in your plan's base results, and pytest ends in `passed`. A failing test you wrote for MP2plus costs that exercise's Tests point only; a failing test that existed at `mp2plus-base` costs everything.

**Tag.**

```bash
git tag mp2plus-final
git push origin mp2plus-final
```

**Expected:** `* [new tag] mp2plus-final -> mp2plus-final`.

**Report.** `docs/iphs400_mp2plus-web-cms_report_{first}-{last}_{YYYYMMDD}.md`, committed before the tag: one table row per exercise (copy each exercise's "Report row"), then one sentence per exercise on anything left broken. P4 adds its second forecast and comparison here. An exercise without a row is not scored.

```text
| Id | Evidence |
|----|----------|
| F2 | issue #14; tests/test_taxonomy.py; mp2plus-categories-1280.png, mp2plus-categories-390.png |
| P1 | PR #15 closing issue #14; carries F2 |
| S2 | tests/test_login_hardening.py; fixture reset_limiter in tests/conftest.py |
```

**Email** the instructor by Tue Oct 20, 2026, 2:40 pm (no-penalty grace until Wed Oct 21, 2026, 2:40 pm). The due date is the expected date; the grace period carries no penalty.
- **Subject:** `IPHS400 MP2plus - First Last` (any dash counts; the words must match)
- **Body:** repo URL; Pages URL; tag `mp2plus-final`.
- **Attach:** your report file.

---

## Appendix A — How you are graded (summary)
Part 0 and Part 2 are required and worth 0 points. Each exercise carries its own points, 111 in all. Your points are summed, capped at +30, and added to your MP2 score; the sum may exceed 100. The gate applies to every exercise. Every point is a line under an exercise's **Scoring**, and every lost point comes back with a specific fix. One flaw costs points in one line only. The full rubric is `docs/mp2plus-grading-rubric_20261012.md` in the starter repo.

## Appendix B — Where this content comes from
Everything in MP2plus was introduced in MP2 but not required, or scored only lightly. "MP2 rubric" is `docs/mp2-grading-rubric_20260922.md`; "MP2 manual" is `docs/manual_iphs400_mp2-web-cms_20260922.md`. A live deploy of the admin console, the last row of MP2's stretch list, is not part of MP2plus; F9 keeps its local half.

| MP2plus exercise | Introduced in | Line |
|---|---|---|
| F1–F8, the eight features | MP2 rubric, section 5 stretch list, one row each in order | 238–245 |
| F9, production configuration | MP2 rubric, section 5, last stretch row (env-var admin password, no default accounts); `docs/adr/ADR-001-local-admin-static-public.md` | 247; 23 |
| Issue, review and timing per feature | MP2 rubric B4 and B5; MP2 manual Part 6.3 | 128, 129; 469 |
| P1, pull-request workflow | MP2 rubric, section 5 stretch list, "Last two tickets done as branch + pull request" | 246 |
| P2, `/prototype` with `/handoff` | `/prototype` is one of the mattpocock skills set up in MP2 manual Part 1.4; the handoff copy step is in MP2 manual Part 6.4 | 178; 510 |
| P3, decision record and ADR | MP2 manual Part 6.1, "Expect few or no ADRs"; MP2 rubric artifacts, "Glossary and decisions"; format in `docs/adr/ADR-002-stack.md` | 440; 36 |
| P4, re-forecast with `--remaining` | MP2 manual Part 5.6; MP2 rubric B7 (c), 1 point | 392; 131 |
| S1, access matrix | `SECURITY-CHECKLIST.md` #10; MP2 rubric D3 | 17; 164 |
| S2, login hardening | `SECURITY-CHECKLIST.md` #2; MP2 rubric C1; the rate-limited login in the last stretch row | 9; 143; 247 |
| "Review, revise, and extend" | Course page, Week 8 | n/a |
