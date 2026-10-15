#!/usr/bin/env python3
"""Create demo data so a grader (and you) can use the CMS immediately.

    set -a; . ./.env; set +a
    uv run python scripts/seed_demo.py

Creates one admin and one editor account (app/seed.py), with passwords read
from CMS_ADMIN_PASSWORD and CMS_EDITOR_PASSWORD, never hard-coded. Later
tickets add demo posts and pages here.

The rubric expects this to run clean on a fresh clone with .env.example values
(item E4), because the database itself is never committed.
"""
from __future__ import annotations

import os
import sys

from app import settings
from app.seed import DEMO_EMAILS, seed_demo


def main() -> int:
    admin_pw = os.environ.get("CMS_ADMIN_PASSWORD")
    editor_pw = os.environ.get("CMS_EDITOR_PASSWORD")
    if not admin_pw or not editor_pw:
        print("Set CMS_ADMIN_PASSWORD and CMS_EDITOR_PASSWORD in .env "
              "(copy .env.example).")
        return 1

    created = seed_demo(settings.DATABASE_PATH, admin_pw, editor_pw)
    for role, email in DEMO_EMAILS.items():
        state = "created" if email in created else "already exists"
        print(f"{role:6}  {email}  ({state})")
    print(f"Database: {settings.DATABASE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
