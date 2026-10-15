"""Content items: posts and pages share one shape (see CONTEXT.md).

An item has a kind (post or page), a title, a unique slug, a Markdown body, a
status (draft or published), an author account and created/updated
timestamps. The slug is generated from the title and de-duplicated
("practice-schedule", "practice-schedule-2", ...); only admins set one by hand.
"""
from __future__ import annotations

import re
import sqlite3
import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from app import db
from app.accounts import Account


class Kind(StrEnum):
    POST = "post"
    PAGE = "page"


class Status(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class SlugTaken(Exception):
    """Raised when an admin sets a slug another item already uses."""


@dataclass(frozen=True)
class Item:
    id: int
    kind: Kind
    title: str
    slug: str
    body: str
    status: Status
    author_id: int
    author_email: str
    created_at: str
    updated_at: str


def can_change(account: Account, item: Item) -> bool:
    """Admins change anything; editors change only posts they wrote."""
    return account.is_admin or (item.kind is Kind.POST
                                and item.author_id == account.id)


def slugify(text: str) -> str:
    """'Practice Schedule!' -> 'practice-schedule'; '' when nothing is left."""
    ascii_text = (unicodedata.normalize("NFKD", text)
                  .encode("ascii", "ignore").decode())
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds")


_SELECT = """
SELECT items.*, accounts.email AS author_email
FROM items JOIN accounts ON accounts.id = items.author_id
"""


def _from_row(row) -> Item:
    return Item(id=row["id"], kind=Kind(row["kind"]), title=row["title"],
                slug=row["slug"], body=row["body"], status=Status(row["status"]),
                author_id=row["author_id"], author_email=row["author_email"],
                created_at=row["created_at"], updated_at=row["updated_at"])


def _unique_slug(conn: sqlite3.Connection, title: str, kind: Kind) -> str:
    base = slugify(title) or kind.value
    taken = {row["slug"] for row in conn.execute(
        "SELECT slug FROM items WHERE slug = ? OR slug LIKE ?",
        (base, f"{base}-%"))}
    slug, n = base, 2
    while slug in taken:
        slug, n = f"{base}-{n}", n + 1
    return slug


def create_item(db_path: Path, kind: Kind, title: str, body: str,
                author: Account) -> Item:
    now = _now()
    with db.connect(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO items (kind, title, slug, body, author_id, created_at,"
            " updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (kind, title, _unique_slug(conn, title, kind), body, author.id, now,
             now),
        )
    return get_item(db_path, cursor.lastrowid)


def get_item(db_path: Path, item_id: int) -> Item | None:
    with db.connect(db_path) as conn:
        row = conn.execute(_SELECT + "WHERE items.id = ?", (item_id,)).fetchone()
    return _from_row(row) if row else None


def list_items(db_path: Path, kind: Kind) -> list[Item]:
    """Newest first."""
    with db.connect(db_path) as conn:
        rows = conn.execute(_SELECT + "WHERE kind = ? ORDER BY created_at DESC,"
                            " items.id DESC", (kind,)).fetchall()
    return [_from_row(row) for row in rows]


def update_item(db_path: Path, item_id: int, title: str, body: str,
                slug: str | None = None) -> None:
    """Change title and body; change the slug too when one is given.

    Raises SlugTaken if the new slug belongs to another item.
    """
    try:
        with db.connect(db_path) as conn:
            conn.execute(
                "UPDATE items SET title = ?, body = ?, slug = COALESCE(?, slug),"
                " updated_at = ? WHERE id = ?",
                (title, body, slug, _now(), item_id),
            )
    except sqlite3.IntegrityError as exc:
        raise SlugTaken(slug) from exc


def delete_item(db_path: Path, item_id: int) -> None:
    with db.connect(db_path) as conn:
        conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
