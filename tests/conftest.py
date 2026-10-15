"""Shared test fixtures.

`client` gives you the app. `client_as(role)` gives you a client that is logged
in as a seeded account of that role, so access-control tests stay one line:

    def test_editor_cannot_manage_accounts(client_as):
        assert client_as("editor").get("/admin/accounts").status_code in (302, 403)

Every test that uses these fixtures gets its own fresh database with the demo
accounts seeded, so tests never touch your real cms.db.
"""
from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.seed import DEMO_EMAILS, seed_demo

# Emails come from app/seed.py (what scripts/seed_demo.py creates). Passwords
# come from the environment there; in tests they are fixed and meaningless.
DEMO_ACCOUNTS = {
    "admin": {"email": DEMO_EMAILS["admin"], "password": "test-admin-pw"},
    "editor": {"email": DEMO_EMAILS["editor"], "password": "test-editor-pw"},
}

CSRF_FIELD = re.compile(r'name="csrf_token" value="([^"]+)"')


@pytest.fixture
def db_path(tmp_path):
    """A fresh database with the demo accounts seeded."""
    path = tmp_path / "cms.db"
    seed_demo(path, DEMO_ACCOUNTS["admin"]["password"],
              DEMO_ACCOUNTS["editor"]["password"])
    return path


@pytest.fixture
def csrf():
    """Return a helper: csrf(client, "/login") -> the CSRF token on that page."""

    def _token(c: TestClient, path: str) -> str:
        match = CSRF_FIELD.search(c.get(path).text)
        assert match, f"No CSRF token on {path}"
        return match.group(1)

    return _token


@pytest.fixture
def client(db_path) -> TestClient:
    return TestClient(create_app(db_path=db_path))


@pytest.fixture
def client_as(db_path, csrf):
    """Return a factory: client_as("editor") -> a logged-in TestClient."""

    def _login(role: str) -> TestClient:
        account = DEMO_ACCOUNTS[role]
        c = TestClient(create_app(db_path=db_path))
        response = c.post("/login", data={"email": account["email"],
                                          "password": account["password"],
                                          "csrf_token": csrf(c, "/login")},
                          follow_redirects=False)
        assert response.status_code in (302, 303), (
            f"Login as {role} failed with {response.status_code}")
        return c

    return _login
