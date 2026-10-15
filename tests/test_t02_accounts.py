"""T02: the Coach manages accounts (issue #3)."""
from __future__ import annotations

import re
from urllib.parse import urljoin

import pytest
from conftest import DEMO_ACCOUNTS
from fastapi.testclient import TestClient

ADMIN_EMAIL = DEMO_ACCOUNTS["admin"]["email"]
EDITOR_EMAIL = DEMO_ACCOUNTS["editor"]["email"]


def can_log_in(client: TestClient, csrf, email: str, password: str) -> bool:
    response = client.post("/login", data={"email": email, "password": password,
                                           "csrf_token": csrf(client, "/login")},
                           follow_redirects=False)
    return response.status_code == 303


# --- creating accounts -------------------------------------------------------

def test_admin_creates_an_editor_who_can_then_log_in(
        client_as, post_form, client, csrf):
    admin = client_as("admin")
    response = post_form(admin, "/admin/accounts", email="manager@example.test",
                       password="team-manager-pw", role="editor")
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/accounts"
    listing = admin.get("/admin/accounts").text
    assert "manager@example.test" in listing
    assert can_log_in(client, csrf, "manager@example.test", "team-manager-pw")


def test_admin_creates_another_admin(client_as, client, csrf, post_form):
    admin = client_as("admin")
    post_form(admin, "/admin/accounts", email="webmaster@example.test",
            password="webmaster-pw", role="admin")
    assert can_log_in(client, csrf, "webmaster@example.test", "webmaster-pw")
    assert client.get("/admin/accounts").status_code == 200


def test_creating_an_account_with_a_taken_email_is_refused(client_as, post_form):
    admin = client_as("admin")
    response = post_form(admin, "/admin/accounts", email=EDITOR_EMAIL.upper(),
                       password="another-password", role="editor")
    assert response.status_code == 400
    assert "already has an account" in response.text


@pytest.mark.parametrize("fields, message", [
    ({"email": "x@example.test", "password": "short", "role": "editor"},
     "at least 8 characters"),
    ({"email": "", "password": "long-enough-pw", "role": "editor"},
     "Enter an email"),
    ({"email": "x@example.test", "password": "long-enough-pw", "role": "owner"},
     "Choose a role"),
])
def test_invalid_new_account_is_refused_and_the_form_keeps_the_email(
        client_as, post_form, fields, message):
    admin = client_as("admin")
    response = post_form(admin, "/admin/accounts", **fields)
    assert response.status_code == 400
    assert message in response.text
    if fields["email"]:
        assert fields["email"] in response.text
    assert fields["password"] not in response.text


# --- changing roles ----------------------------------------------------------

def test_admin_changes_an_editors_role_to_admin(client_as, post_form, account_id):
    admin = client_as("admin")
    target = account_id(admin, EDITOR_EMAIL)
    response = post_form(admin, f"/admin/accounts/{target}/role", role="admin")
    assert response.status_code == 303
    assert client_as("editor").get("/admin/accounts").status_code == 200


def test_admin_cannot_change_their_own_role(client_as, post_form, account_id):
    admin = client_as("admin")
    me = account_id(admin, ADMIN_EMAIL)
    response = post_form(admin, f"/admin/accounts/{me}/role", role="editor")
    assert response.status_code == 400
    assert admin.get("/admin/accounts").status_code == 200


def test_changing_to_an_unknown_role_is_refused(client_as, post_form, account_id):
    admin = client_as("admin")
    target = account_id(admin, EDITOR_EMAIL)
    response = post_form(admin, f"/admin/accounts/{target}/role", role="owner")
    assert response.status_code == 400


# --- deactivating and reactivating -------------------------------------------

def test_deactivate_then_reactivate(client_as, post_form, client, csrf, account_id):
    admin = client_as("admin")
    target = account_id(admin, EDITOR_EMAIL)
    password = DEMO_ACCOUNTS["editor"]["password"]

    assert post_form(admin, f"/admin/accounts/{target}/active",
                   active="0").status_code == 303
    assert not can_log_in(client, csrf, EDITOR_EMAIL, password)
    assert "Deactivated" in admin.get("/admin/accounts").text

    assert post_form(admin, f"/admin/accounts/{target}/active",
                   active="1").status_code == 303
    assert can_log_in(client, csrf, EDITOR_EMAIL, password)


def test_admin_cannot_deactivate_their_own_account(client_as, post_form, account_id):
    admin = client_as("admin")
    me = account_id(admin, ADMIN_EMAIL)
    response = post_form(admin, f"/admin/accounts/{me}/active", active="0")
    assert response.status_code == 400
    assert "your own account" in response.text
    assert admin.get("/admin").status_code == 200


def test_unknown_account_is_404(client_as, post_form):
    admin = client_as("admin")
    assert post_form(admin, "/admin/accounts/999/active",
                   active="0").status_code == 404
    assert post_form(admin, "/admin/accounts/999/role",
                   role="editor").status_code == 404


def test_accounts_cannot_be_deleted(client_as, post_form, account_id):
    admin = client_as("admin")
    target = account_id(admin, EDITOR_EMAIL)
    response = post_form(admin, f"/admin/accounts/{target}/delete")
    assert response.status_code in (404, 405)
    assert EDITOR_EMAIL in admin.get("/admin/accounts").text


# --- the permission matrix ---------------------------------------------------

ACCOUNT_ROUTES = [
    ("get", "/admin/accounts", {}),
    ("post", "/admin/accounts",
     {"email": "sneaky@example.test", "password": "sneaky-pw", "role": "admin"}),
    ("post", "/admin/accounts/{admin_id}/role", {"role": "editor"}),
    ("post", "/admin/accounts/{admin_id}/active", {"active": "0"}),
]


@pytest.mark.parametrize("method, path, data", ACCOUNT_ROUTES)
def test_editor_is_refused_every_account_route(
        client_as, post_form, client, csrf, account_id, method, path, data):
    admin_id = account_id(client_as("admin"), ADMIN_EMAIL)
    editor = client_as("editor")
    url = path.format(admin_id=admin_id)
    if method == "get":
        response = editor.get(url, follow_redirects=False)
    else:
        response = post_form(editor, url, **data)
    assert response.status_code == 403
    # Nothing changed: the admin can still log in and manage accounts, and the
    # sneaky account was not created.
    assert can_log_in(client, csrf, ADMIN_EMAIL, DEMO_ACCOUNTS["admin"]["password"])
    assert client.get("/admin/accounts").status_code == 200
    assert "sneaky@example.test" not in client.get("/admin/accounts").text


@pytest.mark.parametrize("method, path, data", ACCOUNT_ROUTES)
def test_anyone_not_logged_in_is_sent_to_login(client, method, path, data):
    url = path.format(admin_id=1)
    response = getattr(client, method)(url, follow_redirects=False,
                                       **({"data": data} if data else {}))
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


@pytest.mark.parametrize("path", ["/admin/accounts", "/admin/accounts/1/role",
                                  "/admin/accounts/1/active"])
def test_account_forms_without_csrf_are_rejected(client_as, path):
    admin = client_as("admin")
    response = admin.post(path, data={"email": "x@example.test", "password":
                                      "long-enough-pw", "role": "editor",
                                      "active": "0"}, follow_redirects=False)
    assert response.status_code == 403


def test_account_forms_carry_a_csrf_token(client_as):
    page = client_as("admin").get("/admin/accounts").text
    assert page.count('method="post"') >= 3
    assert page.count('method="post"') == page.count('name="csrf_token"')


# --- the console link --------------------------------------------------------

def test_accounts_link_appears_only_for_admins(client_as):
    assert 'href="admin/accounts"' in client_as("admin").get("/admin").text
    assert "admin/accounts" not in client_as("editor").get("/admin").text


def test_links_still_work_on_a_refusal_page_at_a_deeper_url(client_as, post_form,
                                                           account_id):
    """A refusal re-renders the list at /admin/accounts/N/active; every link and
    form on it must still point at a real console route."""
    admin = client_as("admin")
    me = account_id(admin, ADMIN_EMAIL)
    url = f"/admin/accounts/{me}/active"
    page = post_form(admin, url, active="0")
    assert page.status_code == 400
    targets = re.findall(r'(?:href|action)="([^"]+)"', page.text)
    resolved = {urljoin(f"http://testserver{url}", t) for t in targets}
    paths = {r.removeprefix("http://testserver") for r in resolved}
    assert "/admin" in paths and "/admin/accounts" in paths
    editor_id = account_id(admin, EDITOR_EMAIL)
    assert f"/admin/accounts/{editor_id}/role" in paths
    assert f"/admin/accounts/{editor_id}/active" in paths
