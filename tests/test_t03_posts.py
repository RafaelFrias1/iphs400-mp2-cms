"""T03: the Captain and the Coach write draft posts (issue #4)."""
from __future__ import annotations

import re

import pytest
from conftest import DEMO_ACCOUNTS
from fastapi.testclient import TestClient

EDITOR_EMAIL = DEMO_ACCOUNTS["editor"]["email"]
ADMIN_EMAIL = DEMO_ACCOUNTS["admin"]["email"]
TEAM_MANAGER = {"email": "manager@example.test", "password": "team-manager-pw"}


def new_post(post_form, c: TestClient, title: str, body: str = "", **fields) -> int:
    """Save a draft through the console; return the id it redirects to."""
    response = post_form(c, "/admin/posts", title=title, body=body,
                         action="save", **fields)
    assert response.status_code == 303, response.text
    match = re.fullmatch(r"/admin/posts/(\d+)", response.headers["location"])
    assert match, response.headers["location"]
    return int(match.group(1))


def slug_of(c: TestClient, post_id: int) -> str:
    match = re.search(rf'data-post-id="{post_id}" data-slug="([^"]*)"',
                      c.get("/admin/posts").text)
    assert match, f"No row for post {post_id}"
    return match.group(1)


def stamps(c: TestClient, post_id: int) -> dict[str, str]:
    page = c.get(f"/admin/posts/{post_id}").text
    return dict(re.findall(r'<time class="(created|updated)" datetime="([^"]+)"',
                           page))


@pytest.fixture
def team_manager(new_account, login_as) -> TestClient:
    """A second editor (the Team manager), created through the admin's route."""
    new_account(TEAM_MANAGER["email"], TEAM_MANAGER["password"])
    return login_as(TEAM_MANAGER["email"], TEAM_MANAGER["password"])


# --- writing drafts ----------------------------------------------------------

@pytest.mark.parametrize("role", ["editor", "admin"])
def test_any_account_writes_a_draft_post(client_as, post_form, role):
    c = client_as(role)
    post_id = new_post(post_form, c, "Practice schedule", "- Mon 3pm, range")
    page = c.get(f"/admin/posts/{post_id}")
    assert page.status_code == 200
    assert "Practice schedule" in page.text
    assert "- Mon 3pm, range" in page.text
    listing = c.get("/admin/posts").text
    assert "Practice schedule" in listing and "Draft" in listing


def test_new_post_form_has_save_draft_and_preview(client_as):
    page = client_as("editor").get("/admin/posts/new")
    assert page.status_code == 200
    assert 'value="save"' in page.text and 'value="preview"' in page.text


def test_a_post_needs_a_title_and_the_form_keeps_the_body(client_as, post_form):
    c = client_as("editor")
    response = post_form(c, "/admin/posts", title="  ", body="kept text",
                         action="save")
    assert response.status_code == 400
    assert "Enter a title" in response.text
    assert "kept text" in response.text
    assert "data-post-id" not in c.get("/admin/posts").text


def test_console_links_to_posts(client_as):
    assert 'href="admin/posts"' in client_as("editor").get("/admin").text


# --- slugs -------------------------------------------------------------------

def test_slug_is_generated_from_the_title_and_made_unique(client_as, post_form):
    c = client_as("editor")
    first = new_post(post_form, c, "Practice Schedule!")
    second = new_post(post_form, c, "Practice schedule")
    third = new_post(post_form, c, "practice   schedule")
    assert [slug_of(c, p) for p in (first, second, third)] == [
        "practice-schedule", "practice-schedule-2", "practice-schedule-3"]


def test_a_title_with_no_letters_still_gets_a_slug(client_as, post_form):
    c = client_as("editor")
    assert slug_of(c, new_post(post_form, c, "!!!")) == "post"


def test_editing_the_title_keeps_the_slug(client_as, post_form):
    c = client_as("editor")
    post_id = new_post(post_form, c, "Practice schedule")
    post_form(c, f"/admin/posts/{post_id}", title="Week 3 practice", body="",
              action="save")
    assert slug_of(c, post_id) == "practice-schedule"


def test_admin_edits_a_slug(client_as, post_form):
    admin = client_as("admin")
    post_id = new_post(post_form, admin, "Qualifying round 1")
    response = post_form(admin, f"/admin/posts/{post_id}",
                         title="Qualifying round 1", body="", slug="Q1 Results",
                         action="save")
    assert response.status_code == 303
    assert slug_of(admin, post_id) == "q1-results"


def test_an_edited_slug_must_still_be_unique(client_as, post_form):
    admin = client_as("admin")
    new_post(post_form, admin, "Practice schedule")
    post_id = new_post(post_form, admin, "Qualifying round 1")
    response = post_form(admin, f"/admin/posts/{post_id}",
                         title="Changed title", body="", slug="practice-schedule",
                         action="save")
    assert response.status_code == 400
    assert "already used" in response.text
    assert "Changed title" in response.text
    assert slug_of(admin, post_id) == "qualifying-round-1"


def test_admin_may_not_set_an_empty_slug(client_as, post_form):
    admin = client_as("admin")
    post_id = new_post(post_form, admin, "Qualifying round 1")
    response = post_form(admin, f"/admin/posts/{post_id}", title="Qualifying round 1",
                         body="", slug="!!!", action="save")
    assert response.status_code == 400
    assert slug_of(admin, post_id) == "qualifying-round-1"


def test_only_admins_see_or_set_the_slug_field(client_as, post_form):
    editor = client_as("editor")
    post_id = new_post(post_form, editor, "Practice schedule", slug="sneaky")
    assert slug_of(editor, post_id) == "practice-schedule"
    post_form(editor, f"/admin/posts/{post_id}", title="Practice schedule",
              body="", slug="sneaky", action="save")
    assert slug_of(editor, post_id) == "practice-schedule"
    assert 'name="slug"' not in editor.get(f"/admin/posts/{post_id}").text
    assert 'name="slug"' in client_as("admin").get(f"/admin/posts/{post_id}").text


# --- author and timestamps ---------------------------------------------------

def test_a_post_records_its_author_and_timestamps(client_as, post_form):
    c = client_as("editor")
    post_id = new_post(post_form, c, "Practice schedule", "v1")
    before = stamps(c, post_id)
    assert set(before) == {"created", "updated"}
    assert EDITOR_EMAIL in c.get(f"/admin/posts/{post_id}").text
    assert EDITOR_EMAIL in c.get("/admin/posts").text

    post_form(c, f"/admin/posts/{post_id}", title="Practice schedule", body="v2",
              action="save")
    after = stamps(c, post_id)
    assert after["created"] == before["created"]
    assert after["updated"] > before["updated"]


def test_admin_edit_keeps_the_original_author(client_as, post_form):
    editor = client_as("editor")
    post_id = new_post(post_form, editor, "Practice schedule")
    admin = client_as("admin")
    post_form(admin, f"/admin/posts/{post_id}", title="Practice schedule (fixed)",
              body="", slug="practice-schedule", action="save")
    page = editor.get(f"/admin/posts/{post_id}").text
    assert "Practice schedule (fixed)" in page and EDITOR_EMAIL in page


# --- own posts only ----------------------------------------------------------

def test_editor_edits_and_deletes_their_own_post(client_as, post_form):
    c = client_as("editor")
    post_id = new_post(post_form, c, "Practice schedule", "v1")
    response = post_form(c, f"/admin/posts/{post_id}", title="Practice schedule",
                         body="v2", action="save")
    assert response.status_code == 303
    assert "v2" in c.get(f"/admin/posts/{post_id}").text

    response = post_form(c, f"/admin/posts/{post_id}/delete")
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/posts"
    assert c.get(f"/admin/posts/{post_id}").status_code == 404


FOREIGN_POST_REQUESTS = [
    ("get", "/admin/posts/{id}", {}),
    ("post", "/admin/posts/{id}",
     {"title": "Hijacked", "body": "Hijacked", "action": "save"}),
    ("post", "/admin/posts/{id}",
     {"title": "Hijacked", "body": "Hijacked", "action": "preview"}),
    ("post", "/admin/posts/{id}/delete", {}),
]


@pytest.mark.parametrize("method, path, data", FOREIGN_POST_REQUESTS)
@pytest.mark.parametrize("author_role", ["editor", "admin"])
def test_editor_is_refused_someone_elses_post(client_as, post_form, team_manager,
                                              method, path, data, author_role):
    """The Team manager can't touch the Captain's schedule or the Coach's results,
    even with a direct request."""
    author = client_as(author_role)
    post_id = new_post(post_form, author, "Original title", "Original body")
    url = path.format(id=post_id)
    if method == "get":
        response = team_manager.get(url, follow_redirects=False)
    else:
        response = post_form(team_manager, url, **data)
    assert response.status_code == 403
    page = author.get(f"/admin/posts/{post_id}")
    assert page.status_code == 200
    assert "Original body" in page.text and "Hijacked" not in page.text


def test_editor_sees_no_edit_link_for_someone_elses_post(client_as, post_form,
                                                         team_manager):
    editor = client_as("editor")
    post_id = new_post(post_form, editor, "Practice schedule")
    listing = team_manager.get("/admin/posts").text
    assert "Practice schedule" in listing
    assert f'href="{post_id}"' not in listing and f'posts/{post_id}"' not in listing


def test_admin_edits_and_deletes_any_post(client_as, post_form):
    editor = client_as("editor")
    post_id = new_post(post_form, editor, "Practice schedule", "v1")
    admin = client_as("admin")
    assert admin.get(f"/admin/posts/{post_id}").status_code == 200
    response = post_form(admin, f"/admin/posts/{post_id}", title="Practice schedule",
                         body="fixed by coach", slug="practice-schedule",
                         action="save")
    assert response.status_code == 303
    assert "fixed by coach" in editor.get(f"/admin/posts/{post_id}").text
    assert post_form(admin, f"/admin/posts/{post_id}/delete").status_code == 303
    assert editor.get(f"/admin/posts/{post_id}").status_code == 404


def test_unknown_post_is_404(client_as, post_form):
    admin = client_as("admin")
    assert admin.get("/admin/posts/999").status_code == 404
    assert post_form(admin, "/admin/posts/999", title="x", body="",
                     action="save").status_code == 404
    assert post_form(admin, "/admin/posts/999/delete").status_code == 404


# --- preview -----------------------------------------------------------------

MALICIOUS = ("## Times\n\n- **Mon** 3pm\n\n<script>alert('x')</script>\n\n"
             "[bad](javascript:alert(1)) <img src=x onerror=alert(1)>\n\n"
             "<a href=\"javascript:alert(2)\">raw</a>")


def test_preview_shows_sanitized_rendered_markdown_without_saving(client_as,
                                                                  post_form):
    c = client_as("editor")
    response = post_form(c, "/admin/posts", title="Practice schedule",
                         body=MALICIOUS, action="preview")
    assert response.status_code == 200
    preview = re.search(r'<section class="preview">(.*?)</section>',
                        response.text, re.S)
    assert preview, "No preview section"
    html = preview.group(1)
    assert "<h2>Times</h2>" in html and "<strong>Mon</strong>" in html
    assert "<script" not in html and "alert('x')" not in html
    assert 'href="javascript:' not in html
    assert "<img" not in html and "onerror" not in html
    # The textarea still holds what was typed, escaped.
    assert "&lt;script&gt;" in response.text
    assert "<script>" not in response.text
    assert "data-post-id" not in c.get("/admin/posts").text


def test_preview_of_an_existing_post_does_not_change_it(client_as, post_form):
    c = client_as("editor")
    post_id = new_post(post_form, c, "Practice schedule", "saved body")
    response = post_form(c, f"/admin/posts/{post_id}", title="Practice schedule",
                         body="*unsaved* body", action="preview")
    assert response.status_code == 200
    assert "<em>unsaved</em>" in response.text
    assert "saved body" in c.get(f"/admin/posts/{post_id}").text
    assert "unsaved" not in c.get(f"/admin/posts/{post_id}").text


# --- drafts stay private -----------------------------------------------------

def test_drafts_never_reach_the_public_site(client_as, post_form, client, db_path,
                                            tmp_path):
    """T04's test_drafts_never_reach_the_output adds a published post beside it."""
    from app.publish import render_site

    new_post(post_form, client_as("editor"), "Secret draft title", "secret body")
    assert "Secret draft title" not in client.get("/").text
    out = render_site(tmp_path / "site", db_path)
    for f in out.rglob("*"):
        if f.is_file():
            text = f.read_text()
            assert "Secret draft title" not in text and "secret body" not in text


# --- CSRF and login ----------------------------------------------------------

def test_post_forms_carry_a_csrf_token(client_as, post_form):
    c = client_as("admin")
    post_id = new_post(post_form, c, "Practice schedule")
    for url in ("/admin/posts/new", f"/admin/posts/{post_id}"):
        page = c.get(url).text
        assert page.count('method="post"') >= 1
        assert page.count('method="post"') == page.count('name="csrf_token"')


def test_post_forms_without_csrf_are_rejected(client_as, post_form):
    c = client_as("admin")
    post_id = new_post(post_form, c, "Practice schedule", "v1")
    for url in ("/admin/posts", f"/admin/posts/{post_id}",
                f"/admin/posts/{post_id}/delete"):
        response = c.post(url, data={"title": "x", "body": "x", "action": "save"},
                          follow_redirects=False)
        assert response.status_code == 403
    assert "v1" in c.get(f"/admin/posts/{post_id}").text


@pytest.mark.parametrize("method, url", [
    ("get", "/admin/posts"), ("get", "/admin/posts/new"), ("post", "/admin/posts"),
    ("get", "/admin/posts/1"), ("post", "/admin/posts/1"),
    ("post", "/admin/posts/1/delete"),
])
def test_anyone_not_logged_in_is_sent_to_login(client, method, url):
    response = getattr(client, method)(url, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
