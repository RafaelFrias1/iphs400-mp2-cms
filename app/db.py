"""The SQLite database: one file, opened per operation.

The database is never committed (it is gitignored); scripts/seed_demo.py
rebuilds it on a fresh clone.
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
"""


@contextmanager
def connect(path: Path) -> Iterator[sqlite3.Connection]:
    """Open the database, commit on success, roll back on error, always close."""
    conn = sqlite3.connect(path)
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
