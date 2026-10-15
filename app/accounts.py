"""Accounts: one person's login, with one role (see CONTEXT.md).

Passwords are stored only as argon2 hashes and are never logged. Accounts are
never deleted, only deactivated; a deactivated account cannot log in.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from enum import StrEnum
from functools import cache
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app import db

MIN_PASSWORD_LENGTH = 8

_hasher = PasswordHasher()


class Role(StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"


class EmailTaken(Exception):
    """Raised when creating an account whose email already has one."""


@dataclass(frozen=True)
class Account:
    id: int
    email: str
    role: Role
    active: bool

    @property
    def is_admin(self) -> bool:
        return self.role is Role.ADMIN


def _from_row(row) -> Account:
    return Account(id=row["id"], email=row["email"], role=Role(row["role"]),
                   active=bool(row["active"]))


def _normalize(email: str) -> str:
    return email.strip().lower()


def create_account(db_path: Path, email: str, password: str, role: Role) -> Account:
    try:
        with db.connect(db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO accounts (email, password_hash, role) VALUES (?, ?, ?)",
                (_normalize(email), _hasher.hash(password), role),
            )
    except sqlite3.IntegrityError as exc:
        raise EmailTaken(email) from exc
    return get_account(db_path, cursor.lastrowid)


def list_accounts(db_path: Path) -> list[Account]:
    with db.connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM accounts ORDER BY email").fetchall()
    return [_from_row(row) for row in rows]


def get_account(db_path: Path, account_id: int) -> Account | None:
    with db.connect(db_path) as conn:
        row = conn.execute("SELECT * FROM accounts WHERE id = ?",
                           (account_id,)).fetchone()
    return _from_row(row) if row else None


def _row_by_email(db_path: Path, email: str):
    with db.connect(db_path) as conn:
        return conn.execute("SELECT * FROM accounts WHERE email = ?",
                            (_normalize(email),)).fetchone()


def find_by_email(db_path: Path, email: str) -> Account | None:
    row = _row_by_email(db_path, email)
    return _from_row(row) if row else None


def set_role(db_path: Path, account_id: int, role: Role) -> None:
    with db.connect(db_path) as conn:
        conn.execute("UPDATE accounts SET role = ? WHERE id = ?",
                     (role, account_id))


def set_active(db_path: Path, account_id: int, active: bool) -> None:
    """Deactivate (False) or reactivate (True). Accounts are never deleted."""
    with db.connect(db_path) as conn:
        conn.execute("UPDATE accounts SET active = ? WHERE id = ?",
                     (int(active), account_id))


@cache
def _dummy_hash() -> str:
    return _hasher.hash("no account has this password")


def authenticate(db_path: Path, email: str, password: str) -> Account | None:
    """Return the account if the email and password match an active account.

    Unknown emails still pay for one argon2 verification, so response time
    does not reveal which emails have accounts.
    """
    row = _row_by_email(db_path, email)
    try:
        _hasher.verify(row["password_hash"] if row else _dummy_hash(), password)
    except (VerificationError, InvalidHashError):
        return None
    if row is None or not row["active"]:
        return None
    return _from_row(row)
