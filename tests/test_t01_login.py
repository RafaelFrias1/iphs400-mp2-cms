"""T01: the Coach and editors log in and out (issue #2)."""
from __future__ import annotations

import os
import sqlite3
import subprocess
import sys

from fastapi.testclient import TestClient

from app import settings
from app.main import create_app
from conftest import DEMO_ACCOUNTS

from app.routes.auth import LOGIN_ERROR as GENERIC_ERROR


def login(c: TestClient, csrf, email: str, password: str):
    return c.post("/login", data={"email": email, "password": password,
                                  "csrf_token": csrf(c, "/login")},
                  follow_redirects=False)


def test_correct_email_and_password_logs_in(client, csrf):
    response = login(client, csrf, DEMO_ACCOUNTS["editor"]["email"],
                     DEMO_ACCOUNTS["editor"]["password"])
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    assert client.get("/admin").status_code == 200


def test_email_is_not_case_sensitive(client, csrf):
    response = login(client, csrf, DEMO_ACCOUNTS["admin"]["email"].upper(),
                     DEMO_ACCOUNTS["admin"]["password"])
    assert response.status_code == 303


def test_wrong_password_and_unknown_email_give_the_same_error(client, csrf):
    wrong_pw = login(client, csrf, DEMO_ACCOUNTS["admin"]["email"], "nope")
    unknown = login(client, csrf, "nobody@example.test", "nope")
    assert wrong_pw.status_code == unknown.status_code == 401
    assert GENERIC_ERROR in wrong_pw.text and GENERIC_ERROR in unknown.text
    assert client.get("/admin", follow_redirects=False).status_code == 303


def test_failed_login_keeps_the_email_but_not_the_password(client, csrf):
    response = login(client, csrf, DEMO_ACCOUNTS["admin"]["email"], "secret-guess")
    assert DEMO_ACCOUNTS["admin"]["email"] in response.text
    assert "secret-guess" not in response.text


def test_deactivated_account_is_refused_with_the_right_password(
        client, client_as, csrf, account_id, new_account, post_form):
    new_account("old-captain@example.test", "right-password")
    admin = client_as("admin")
    target = account_id(admin, "old-captain@example.test")
    post_form(admin, f"/admin/accounts/{target}/active", active="0")
    response = login(client, csrf, "old-captain@example.test", "right-password")
    assert response.status_code == 401
    assert GENERIC_ERROR in response.text


def test_deactivating_a_logged_in_account_ends_its_session(client_as, post_form,
                                                          account_id):
    c = client_as("editor")
    admin = client_as("admin")
    target = account_id(admin, DEMO_ACCOUNTS["editor"]["email"])
    post_form(admin, f"/admin/accounts/{target}/active", active="0")
    response = c.get("/admin", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_logout_ends_the_session(client_as, csrf):
    c = client_as("admin")
    response = c.post("/logout", data={"csrf_token": csrf(c, "/admin")},
                      follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    assert c.get("/admin", follow_redirects=False).headers["location"] == "/login"


def test_console_redirects_anyone_not_logged_in_to_login(client):
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_login_page_is_reachable_without_logging_in(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert 'name="csrf_token"' in response.text


def test_login_without_a_csrf_token_is_rejected(client):
    response = client.post("/login", data={
        "email": DEMO_ACCOUNTS["admin"]["email"],
        "password": DEMO_ACCOUNTS["admin"]["password"]}, follow_redirects=False)
    assert response.status_code == 403
    assert client.get("/admin", follow_redirects=False).status_code == 303


def test_login_with_a_forged_csrf_token_is_rejected(client):
    client.get("/login")
    response = client.post("/login", data={
        "email": DEMO_ACCOUNTS["admin"]["email"],
        "password": DEMO_ACCOUNTS["admin"]["password"],
        "csrf_token": "forged"}, follow_redirects=False)
    assert response.status_code == 403


def test_logout_without_a_csrf_token_is_rejected(client_as):
    c = client_as("admin")
    assert c.post("/logout", follow_redirects=False).status_code == 403
    assert c.get("/admin").status_code == 200


def test_passwords_are_stored_only_as_argon2_hashes(db_path):
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT password_hash FROM accounts").fetchall()
    assert len(rows) == 2
    for (stored,) in rows:
        assert stored.startswith("$argon2")
        assert "test-admin-pw" not in stored and "test-editor-pw" not in stored


def _run_seed(db: os.PathLike, **extra_env: str):
    env = {k: v for k, v in os.environ.items()
           if k not in ("CMS_ADMIN_PASSWORD", "CMS_EDITOR_PASSWORD")}
    env.update(CMS_DATABASE=str(db), **extra_env)
    return subprocess.run([sys.executable, str(settings.ROOT / "scripts/seed_demo.py")],
                          env=env, capture_output=True, text=True)


def test_demo_seed_runs_clean_twice_and_its_accounts_can_log_in(tmp_path, csrf):
    db = tmp_path / "fresh.db"
    pws = {"CMS_ADMIN_PASSWORD": "seed-admin", "CMS_EDITOR_PASSWORD": "seed-editor"}
    first, second = _run_seed(db, **pws), _run_seed(db, **pws)
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert "seed-admin" not in first.stdout + second.stdout

    c = TestClient(create_app(db_path=db))
    assert login(c, csrf, DEMO_ACCOUNTS["admin"]["email"], "seed-admin").status_code == 303
    c = TestClient(create_app(db_path=db))
    assert login(c, csrf, DEMO_ACCOUNTS["editor"]["email"], "seed-editor").status_code == 303


def test_demo_seed_refuses_to_run_without_passwords(tmp_path):
    db = tmp_path / "fresh.db"
    result = _run_seed(db)
    assert result.returncode == 1
    assert not db.exists()
