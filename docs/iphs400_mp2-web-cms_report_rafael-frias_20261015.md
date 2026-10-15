# IPHS 400 Mini-Project #2: Kenyon Men's Golf CMS

Rafael Frias · Oct 15, 2026
Repo: https://github.com/RafaelFrias1/iphs400-mp2-cms · Site: https://rafaelfrias1.github.io/iphs400-mp2-cms/ · Tag: `mp2-final`

## 1. What I built, and which grill decisions were mine

I built a WordPress style CMS for the Kenyon Men's golf team as a hypothetical client. The admin and the editors would be the coach and the captain and team manager, respectively where they have different permissions (the captain and team manager can just make posts and edit their own while the coach can add/edit pages and also users). They all would access from a team laptop, and every change to the published content would update the GitHub Pages site to be viewed by readers within minutes. This was done with 7 tickets and 191 tests.

The grill decisions that were mine (went against the AI's recommendation) was adjusting the delete permissions to where only the admin could delete, going against what the client brief suggested (no one can delete past results). This allows for the coach to have final say/veto power over what is posted. Additionally, the AI suggested adding features that prevented the captain from posting qualifying scores (as was indicated in the client brief) however I overrode it since the small team and prospective audience made that unnecessary, as there is a significant level of trust between the captain and the coach that they will not overstep. I also ruled out features that were unnecessarily complicated for a first pass, like photo posting, search feature, and phone posting (even though the client brief said they post from a phone half the time).

## 2. Where the AI drifted, and how the workflow caught it

Ticket 07 was built exactly to the ticket spec, and was passed by the reviewers without noticing the grader's copy would try to push to my repo, fail, and be blocked. This was caught when the run steps were checked against a fresh clone when running locally, so writing the README essentially forced us to look at it from a stranger's view. This catch resulted in commit fa985d3, which added a CMS_DEPLOY setting so only my laptop pushes to the site (recorded in ADR-004).

## 3. Skills, prompts and resources, and why

I first logged into WordPress to get a handle of what I was working on, and took note of what I found clunky, redundant, or what could maybe be improved upon. This was then used in the grill with docs session to generate actionable tickets.

The AI use statement in the README.md file shows the skills and prompts used. In addition, the final session used screenshots taken with Playwright for the submission requirements. This allowed me to ensure the screenshots were much more consistent to the project requirements rather than doing them by hand, which could leave room for mistakes.

The Matt Pocock skills came in super useful to catch inconsistencies and mistakes that I may not be as adept in catching as a novice developer. The AI questioning me on the documents provided allowed it to catch inconsistencies between the documents that would have presented problems when trying to implement the changes, and the code review caught mistakes I was able to question and change before committing, like the homepage saying "Nothing published yet" that the AI waved through.

Additionally, I went to bed after implementing tickets T01-T03 on the night of Oct 14, and used /handoff to ensure I could pick up where we left off the next morning and save tokens rather than having it reread the entire session again.

## 4. Token budget: plan vs. actual

Plan:
Sonnet 5.5 for /implement, and about 20% of a 5-hour window per ticket with 9 total tickets. Eventually taking up 2 and a half 5 hour windows.

Actual:
8 tickets. T01-T06 used about 41% of a 5 hour window, and T07 about 13%. The T07 row in the ledger shows 40%, but that is because the phase label stayed on T07 while I did the screenshots, README, report and a mock grade afterwards. When taking into account grill (3%), setup (10%), and unlabelled sessions (9%), about 103% of a 5-hour window was used in the project spread across two main days (Oct 14 and 15), and about 1.8% of the weekly cap per ticket. This came in well under the forecast despite using Opus 5.5 instead. Likely came in under plan since opus remained efficient.

My first numbers were higher (116%) because the template's own sessions had been mixed into my ledger. The mock grade caught it, and I moved those rows out.

## 5. Future improvements

The 403 page for editors is still a raw JSON instead of a friendly page, posts should be dated when they are published, not created, and the slug field only appears after first save, which could be tedious for an unfamiliar admin like a coach. These should all be improved before actual use of the site.

Additionally, the site still runs on placeholders for admin and editor, so real accounts should be created for the coach and captain, which would also solve the issue of the passwords being committed in the transcript.
