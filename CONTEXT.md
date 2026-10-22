# Kenyon Men's Golf CMS

The team's own site: one place where players, parents, recruits and alumni find the schedule, the travel lineup, results and coach contact, instead of searching the group chat.

## People

**Account**:
One person's login, with one role. The Coach creates accounts for each season's Captain and Team manager and deactivates them when the person leaves.
_Avoid_: user (for the login), member

**Coach**:
The head coach. Holds the **admin** role, owns all pages and qualifying results, and manages accounts.
_Avoid_: owner, superuser

**Failed login**:
A login attempt with a wrong password, or for an email that has no account or a deactivated one. Every failed login counts against the email that was typed.
_Avoid_: bad login, invalid attempt

**Lockout**:
The 15 minutes during which an email that has had 5 failed logins is refused, even with the right password. A successful login before the lockout clears the count; the lockout ends on its own.
_Avoid_: ban, block, suspension

**Captain**:
The player who is team captain this season, with their own account. Holds the **editor** role and posts the weekly practice schedule.

**Team manager**:
The team manager this season, with their own account. Holds the **editor** role and writes tournament recaps after events.
_Avoid_: manager (alone), which could be confused with the admin role

**Webmaster**:
The person who built and maintains the CMS. Holds a backup **admin** account in case the Coach is locked out.
_Avoid_: developer, IT

**Admin**:
The role with full permissions: all pages, all posts, and managing accounts. An admin can't deactivate their own account or change their own role, so the site always keeps an admin.

**Deactivated**:
The state of an account whose person has left (e.g. a graduated Captain). It can no longer log in; it is never deleted.
_Avoid_: deleted, removed, banned

**Editor**:
The role for people who write posts and may change only their own. Editors never touch pages, other people's posts, or accounts.
_Avoid_: author, contributor

**Reader**:
Anyone viewing the public site: players, parents, recruits, alumni. Readers have no account.
_Avoid_: visitor, user

## Content

**Item**:
A post or a page. They share one shape: title, slug, Markdown body, status, author and timestamps.
_Avoid_: entry, content (as a count noun)

**Page**:
Long-lived content edited in place that appears in the public navigation, e.g. Season Schedule, Travel Lineup, Recruiting.

**Post**:
Dated content that accumulates over time, e.g. a weekly practice schedule, qualifying results or a tournament recap.
_Avoid_: article, update, announcement

**Season Schedule**:
The page that lists the season's tournaments, their locations and live-scoring links.

**Travel Lineup**:
The page naming the players who travel to the next tournament. Updated in place by the Coach.
_Avoid_: roster (the whole team), lineup post

**Recruiting page**:
The page aimed at recruits and their families, with coach contact details. Coach-only because it must follow NCAA rules.

**Practice schedule**:
A weekly post giving that week's practice times and places.

**Qualifying result**:
A dated post recording the results of a qualifying round. Part of the team's permanent record.
_Avoid_: scores, standings (as separate concepts)

**Tournament recap**:
A short post written after a tournament describing how the team did. Text only.

**Content list**:
The console's one list of every item, posts and pages together, with a single filter bar (status, kind, author). The dashboard's counts link into it.
_Avoid_: posts list, pages list (as separate screens)

## Publishing

**Draft**:
A page or post that exists only in the console and never reaches the public site.

**Published**:
The status of a page or post that is on the public site. Publishing triggers a site update, and if that fails the publish fails too.
_Avoid_: live, posted

**Site update**:
Rebuilding the public site from all published content and sending it to the web host. It happens automatically whenever published content changes; nobody presses a button for it.
_Avoid_: publish (for this step), sync, push

**Deployer**:
The part of a site update that sends the rebuilt site to the web host (GitHub Pages). If it fails (no wifi), the site update fails and the change is not saved.
_Avoid_: publisher, uploader

**Theme**:
The public site's look: one stylesheet, chosen by the Coach. There are two, **classic** (the original look, following the phone's light or dark setting) and **kenyon** (light, with Kenyon purple). Changing the theme is a site update.
_Avoid_: skin, template, style

**Settings page**:
The admin-only console screen where the Coach chooses the site-wide options, starting with the theme. Editors neither see its link nor can open it.
_Avoid_: preferences, config, options page

## Places

**Team laptop**:
The single machine the admin console runs on. All posting happens here; nobody posts from a phone.
_Avoid_: server, backend

## Decisions

| Question | Choice | Why |
|---|---|---|
| What does the login limiter count by? | The typed email, including emails with no account, not the IP address | All posting happens on one team laptop, so an IP limit would lock out the Coach whenever someone else on it mistyped; and counting unknown emails too means the 429 can't tell anyone which emails have accounts (checklist #2). |
| Where are failed logins remembered? | In the server's memory; a restart clears them | The console runs as one process on the one team laptop, so a single in-memory count sees every login attempt; a table would mean a schema change and an rm cms.db reseed on that laptop, and losing the count on restart only helps someone who can already restart the laptop. |
| When does a new theme reach the public site? | Immediately, as a site update; no wifi means the change is refused | The Coach doesn't want to learn new software mid-season; if he picks a theme and the public site doesn't change until someone next publishes a post, he'll think it's broken. Same rule as ADR-004: a change is live or it isn't saved. |
