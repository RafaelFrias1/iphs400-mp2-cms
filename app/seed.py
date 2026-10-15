"""Demo data: one admin and one editor, so the console is usable straight away.

scripts/seed_demo.py calls this with passwords from the environment; the tests
call it with fixed ones. Running it again leaves existing accounts alone.
"""
from __future__ import annotations

from pathlib import Path

from app import accounts, db
from app.accounts import Role

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
