"""T08: grader-readiness (issue #9).

The rubric's grading run copies .env.example to .env and runs the seed script
and the console with no other step, so settings must read .env themselves.
The console must also work on a phone: its own stylesheet, one nav on every
screen, and a message after a save.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

import pytest
from test_t03_posts import new_post
from test_t04_publish import publish_new

from app import settings


# --- .env is read without a manual step --------------------------------------

def test_env_file_values_are_loaded(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('# a comment\n\nCMS_T08_PLAIN=one\n'
                   'CMS_T08_QUOTED="Kenyon Men\'s Golf CMS"\n'
                   "export CMS_T08_EXPORTED='three'\nnot a setting\n")
    for key in ("CMS_T08_PLAIN", "CMS_T08_QUOTED", "CMS_T08_EXPORTED"):
        monkeypatch.delenv(key, raising=False)
    settings.load_env_file(env)
    assert os.environ["CMS_T08_PLAIN"] == "one"
    assert os.environ["CMS_T08_QUOTED"] == "Kenyon Men's Golf CMS"
    assert os.environ["CMS_T08_EXPORTED"] == "three"


def test_real_environment_variables_win_over_env_file(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("CMS_T08_PLAIN=from-file\n")
    monkeypatch.setenv("CMS_T08_PLAIN", "from-shell")
    settings.load_env_file(env)
    assert os.environ["CMS_T08_PLAIN"] == "from-shell"


def test_a_line_with_no_key_is_skipped(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("=orphan\nCMS_T08_PLAIN=kept\n")
    monkeypatch.delenv("CMS_T08_PLAIN", raising=False)
    settings.load_env_file(env)
    assert os.environ["CMS_T08_PLAIN"] == "kept"


def test_a_missing_env_file_is_fine(tmp_path):
    settings.load_env_file(tmp_path / "no-such.env")


def test_settings_read_env_with_no_sourcing_step(tmp_path):
    """What the grader does: cp .env.example .env, then run Python directly."""
    env = tmp_path / ".env"
    env.write_text("CMS_ADMIN_PASSWORD=change-me-admin\nCMS_DEPLOY=on\n")
    clean = {k: v for k, v in os.environ.items()
             if k not in ("CMS_ADMIN_PASSWORD", "CMS_DEPLOY")}
    out = subprocess.run(
        [sys.executable, "-c",
         "import os; from app import settings; "
         "print(os.environ['CMS_ADMIN_PASSWORD'], settings.DEPLOY)"],
        env=clean | {"CMS_ENV_FILE": str(env)}, cwd=settings.ROOT,
        capture_output=True, text=True, check=True)
    assert out.stdout.split() == ["change-me-admin", "True"]


def test_tests_never_read_the_developers_env_file():
    assert os.environ.get("CMS_ENV_FILE") == ""
    assert settings.DEPLOY is False


# --- the console on a phone --------------------------------------------------

def _nav(html: str) -> str:
    match = re.search(r'<nav aria-label="Console">(.*?)</nav>', html, re.S)
    return match.group(1) if match else ""


CONSOLE_PAGES = ["/admin", "/admin/content", "/admin/posts/new",
                 "/admin/pages/new", "/admin/pages", "/admin/accounts"]


def test_every_console_page_loads_the_stylesheet_relatively(client_as, post_form):
    admin = client_as("admin")
    post_id = new_post(post_form, admin, "Practice schedule")
    for path, css in [("/admin", "style.css"), ("/admin/content", "../style.css"),
                      ("/admin/posts/new", "../../style.css"),
                      (f"/admin/posts/{post_id}", "../../style.css")]:
        page = admin.get(path).text
        assert f'<link rel="stylesheet" href="{css}">' in page, path


def test_the_stylesheet_keeps_form_fields_inside_a_phone_screen(client):
    css = client.get("/style.css").text
    assert re.search(r"textarea[^{]*\{[^}]*max-width: 100%", css)


@pytest.mark.parametrize("path", CONSOLE_PAGES)
def test_every_console_page_has_the_same_nav(client_as, path):
    page = client_as("admin").get(path).text
    nav = _nav(page)
    for label in ("Dashboard", "Content", "New post", "Accounts", "Log out"):
        assert label in nav, (path, label)


def test_an_items_edit_page_has_the_nav(client_as, post_form):
    admin = client_as("admin")
    page = admin.get(f"/admin/posts/{new_post(post_form, admin, 'Recap')}").text
    assert '<nav aria-label="Console">' in page


def test_editors_get_the_nav_without_admin_links(client_as):
    page = client_as("editor").get("/admin").text
    nav = _nav(page)
    assert "New post" in nav and "Log out" in nav
    assert "Accounts" not in nav and "New page" not in nav


def test_the_login_page_and_public_preview_have_no_console_nav(client):
    assert 'aria-label="Console"' not in client.get("/login").text
    assert 'aria-label="Console"' not in client.get("/").text


# --- a save says it worked ---------------------------------------------------

def _status(html: str) -> str:
    match = re.search(r'<p role="status">(.*?)</p>', html, re.S)
    return match.group(1) if match else ""


def test_saving_a_draft_says_so(client_as, post_form):
    c = client_as("editor")
    response = post_form(c, "/admin/posts", title="Practice schedule", body="",
                         action="save")
    assert "Saved as a draft" in _status(c.get(response.headers["location"]).text)


def test_publishing_says_so_once(client_as, post_form):
    c = client_as("editor")
    post_id = publish_new(post_form, c, "Practice schedule")
    assert "Published" in _status(c.get(f"/admin/posts/{post_id}").text)
    assert _status(c.get(f"/admin/posts/{post_id}").text) == ""


def test_a_message_never_shows_on_another_items_page(client_as, post_form):
    c = client_as("editor")
    other = new_post(post_form, c, "Recap")
    publish_new(post_form, c, "Practice schedule")
    assert _status(c.get(f"/admin/posts/{other}").text) == ""


def test_saving_changes_and_unpublishing_say_so(client_as, post_form):
    c = client_as("editor")
    post_id = publish_new(post_form, c, "Practice schedule")
    c.get(f"/admin/posts/{post_id}")
    post_form(c, f"/admin/posts/{post_id}", title="Practice schedule v2",
              body="", action="save")
    assert "Changes saved" in _status(c.get(f"/admin/posts/{post_id}").text)
    post_form(c, f"/admin/posts/{post_id}/unpublish")
    assert "back to draft" in _status(c.get(f"/admin/posts/{post_id}").text)
