"""Demo data: one admin and one editor, plus the three pages and a few posts.

scripts/seed_demo.py calls this with passwords from the environment; the tests
call it with fixed ones. Running it again leaves existing accounts alone.
"""
from __future__ import annotations

from pathlib import Path

from app import accounts, content, db
from app.accounts import Role
from app.content import Kind, Status

DEMO_EMAILS = {
    Role.ADMIN: "admin@example.test",
    Role.EDITOR: "editor@example.test",
}


def seed_demo(db_path: Path, admin_password: str, editor_password: str) -> list[str]:
    """Create the demo accounts that do not exist yet; return the emails created."""
    db.init(db_path)
    created = []
    for role, password in ((Role.ADMIN, admin_password), (Role.EDITOR, editor_password)):
        email = DEMO_EMAILS[role]
        if accounts.find_by_email(db_path, email) is None:
            accounts.create_account(db_path, email, password, role)
            created.append(email)
    return created


# The admin (the Coach) owns the pages; posts come from both roles. One post
# stays a draft so the console shows both statuses.
DEMO_PAGES = [
    ("Season Schedule", """\
| Dates | Tournament | Location | Live scoring |
| --- | --- | --- | --- |
| Oct 19–20 | Fall Invitational | Granville, OH | [Golfstat](https://golfstat.com) |
| Mar 28–29 | Spring Opener | Wooster, OH | [Golfstat](https://golfstat.com) |
"""),
    ("Travel Lineup", """\
**Fall Invitational, Oct 19–20.** Vans leave the athletic center at 7:00 am.

1. Sam
2. Alex
3. Jordan
4. Chris
5. Taylor
"""),
    ("Recruiting", """\
Interested in playing golf at Kenyon? Fill out the recruiting questionnaire on
the athletics site, then email the coach with your schedule and scores.

- Coach: coach@example.test
"""),
]

DEMO_POSTS = [
    (Role.EDITOR, Status.PUBLISHED, "Practice schedule, week of Oct 12", """\
- Mon 3:30 pm, range
- Wed 3:30 pm, nine holes
- Fri 7:00 am, qualifying round
"""),
    (Role.ADMIN, Status.PUBLISHED, "Qualifying results, Oct 9", """\
1. Sam, 72
2. Alex, 74
3. Jordan, 75
"""),
    (Role.EDITOR, Status.DRAFT, "Fall Invitational recap", "Draft: finish after the event."),
]


def seed_demo_content(db_path: Path) -> int:
    """Add the demo pages and posts once; return how many items were created.

    Needs the demo accounts (seed_demo) first. Content with the same title
    already in the database is left alone, so running it again adds nothing.
    """
    authors = {role: accounts.find_by_email(db_path, email)
               for role, email in DEMO_EMAILS.items()}
    wanted = ([(Kind.PAGE, Role.ADMIN, Status.PUBLISHED, title, body)
               for title, body in DEMO_PAGES]
              + [(Kind.POST, role, status, title, body)
                 for role, status, title, body in DEMO_POSTS])
    existing = {(i.kind, i.title) for kind in Kind
                for i in content.list_items(db_path, kind)}
    created = 0
    for kind, role, status, title, body in wanted:
        if (kind, title) not in existing:
            content.create_item(db_path, kind, title, body, authors[role], status)
            created += 1
    return created
