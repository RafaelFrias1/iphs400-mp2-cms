"""Accounts: one person's login, with one role (see CONTEXT.md).

Passwords are stored only as argon2 hashes and are never logged. Accounts are
never deleted, only deactivated; a deactivated account cannot log in.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app import db

ROLES = ("admin", "editor")

_hasher = PasswordHasher()


@dataclass(frozen=True)
class Account:
    id: int
    email: str
    role: str
    active: bool


def _from_row(row) -> Account:
    return Account(id=row["id"], email=row["email"], role=row["role"],
                   active=bool(row["active"]))


def _normalize(email: str) -> str:
    return email.strip().lower()


def create_account(db_path: Path, email: str, password: str, role: str) -> Account:
    if role not in ROLES:
        raise ValueError(f"Unknown role: {role!r}")
    with db.connect(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO accounts (email, password_hash, role) VALUES (?, ?, ?)",
            (_normalize(email), _hasher.hash(password), role),
        )
    return get_account(db_path, cursor.lastrowid)


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


def set_active(db_path: Path, account_id: int, active: bool) -> None:
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
