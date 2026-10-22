"""The SQLite database: one file, opened per operation.

The database is never committed (it is gitignored); scripts/seed_demo.py
rebuilds it on a fresh clone.

Functions that read or write take a `Source`: usually the database's path,
but a site update passes an open connection instead, so a change and the
site rendered from it share one transaction (see publish.update_site()).
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id            INTEGER PRIMARY KEY,
    email         TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK (role IN ('admin', 'editor')),
    active        INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);

-- Posts and pages share one table; kind drives navigation and permissions.
-- Timestamps are ISO 8601 UTC strings, so they sort as text.
CREATE TABLE IF NOT EXISTS items (
    id         INTEGER PRIMARY KEY,
    kind       TEXT    NOT NULL CHECK (kind IN ('post', 'page')),
    title      TEXT    NOT NULL,
    slug       TEXT    NOT NULL UNIQUE,
    body       TEXT    NOT NULL DEFAULT '',
    status     TEXT    NOT NULL DEFAULT 'draft'
                       CHECK (status IN ('draft', 'published')),
    author_id  INTEGER NOT NULL REFERENCES accounts (id),
    created_at TEXT    NOT NULL,
    updated_at TEXT    NOT NULL
);

-- Site-wide options the Coach sets on the Settings page, e.g. ('theme', 'kenyon').
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


Source = Path | sqlite3.Connection


@contextmanager
def connect(source: Source) -> Iterator[sqlite3.Connection]:
    """Open the database, commit on success, roll back on error, always close.

    Given an open connection, use it as is: whoever opened it commits or
    rolls back, so the changes made here stay staged until then.
    """
    if isinstance(source, sqlite3.Connection):
        yield source
        return
    conn = sqlite3.connect(source)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init(path: Path) -> None:
    """Create the tables if they do not exist yet."""
    with connect(path) as conn:
        conn.executescript(SCHEMA)
