"""T05: the Coach manages pages; pages build the navigation (issue #6).

Same two seams as T04. Over HTTP, an admin creates, edits, publishes,
unpublishes and deletes pages at /admin/pages and editors are refused every
one of those actions. Rendering tests call render_site() into a temporary
directory and read the navigation and home page it wrote.
"""
from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient
from test_t03_posts import new_post
from test_t04_publish import publish_new, site_text

from app.publish import render_site


def new_page(post_form, c: TestClient, title: str, body: str = "",
             action: str = "save") -> int:
    """Create a page through the console; return the id it redirects to."""
    response = post_form(c, "/admin/pages", title=title, body=body, action=action)
    assert response.status_code == 303, response.text
    match = re.fullmatch(r"/admin/pages/(\d+)", response.headers["location"])
    assert match, response.headers["location"]
    return int(match.group(1))


def page_slug(c: TestClient, page_id: int) -> str:
    match = re.search(rf'data-page-id="{page_id}" data-slug="([^"]*)"',
                      c.get("/admin/pages").text)
    assert match, f"No row for page {page_id}"
    return match.group(1)


def page_file(out, slug: str):
    return out / "pages" / f"{slug}.html"


def nav_of(html: str) -> str:
    match = re.search(r"<nav[^>]*>(.*?)</nav>", html, re.S)
    assert match, "No <nav> on the page"
    return match.group(1)


# --- the admin manages pages -------------------------------------------------

def test_admin_creates_a_draft_page_with_the_post_fields(client_as, post_form,
                                                          site_dir):
    admin = client_as("admin")
    page_id = new_page(post_form, admin, "Season Schedule", "- Oct 20, Denison")
    form = admin.get(f"/admin/pages/{page_id}").text
    assert "Season Schedule" in form and "Draft" in form
    assert 'class="created"' in form and 'class="updated"' in form
    assert 'name="slug"' in form
    assert page_slug(admin, page_id) == "season-schedule"
    assert not site_dir.exists()


def test_admin_publishes_a_page_and_it_reaches_the_site(client_as, post_form,
                                                         site_dir):
    admin = client_as("admin")
    page_id = new_page(post_form, admin, "Season Schedule",
                       "[Live scoring](https://golfstat.com)", action="publish")
    page = page_file(site_dir, "season-schedule").read_text()
    assert re.search(r'<a href="https://golfstat.com"[^>]*>Live scoring</a>', page)
    assert "Published" in admin.get(f"/admin/pages/{page_id}").text


def test_editing_a_published_page_updates_the_site(client_as, post_form, site_dir):
    admin = client_as("admin")
    page_id = new_page(post_form, admin, "Travel Lineup", "Sam, Alex",
                       action="publish")
    post_form(admin, f"/admin/pages/{page_id}", title="Travel Lineup",
              slug="travel-lineup", body="Sam, Jordan", action="save")
    text = page_file(site_dir, "travel-lineup").read_text()
    assert "Sam, Jordan" in text and "Alex" not in text


def test_unpublishing_a_page_removes_it_and_its_nav_link(client_as, post_form,
                                                          site_dir):
    admin = client_as("admin")
    publish_new(post_form, admin, "A post")
    page_id = new_page(post_form, admin, "Recruiting", action="publish")
    assert post_form(admin, f"/admin/pages/{page_id}/unpublish").status_code == 303
    assert "Draft" in admin.get(f"/admin/pages/{page_id}").text
    assert not page_file(site_dir, "recruiting").exists()
    assert "Recruiting" not in site_text(site_dir)


def test_deleting_a_published_page_removes_it(client_as, post_form, site_dir):
    admin = client_as("admin")
    page_id = new_page(post_form, admin, "Recruiting", action="publish")
    response = post_form(admin, f"/admin/pages/{page_id}/delete")
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/pages"
    assert not page_file(site_dir, "recruiting").exists()
    assert admin.get(f"/admin/pages/{page_id}").status_code == 404


def test_saving_a_draft_page_runs_no_site_update(client_as, post_form, site_dir):
    admin = client_as("admin")
    page_id = new_page(post_form, admin, "Recruiting")
    post_form(admin, f"/admin/pages/{page_id}", title="Recruiting v2",
              slug="recruiting", body="", action="save")
    post_form(admin, f"/admin/pages/{page_id}/delete")
    assert not site_dir.exists()


def test_pages_and_posts_share_one_slug_space(client_as, post_form):
    admin = client_as("admin")
    publish_new(post_form, admin, "Recruiting")
    assert page_slug(admin, new_page(post_form, admin, "Recruiting")) == "recruiting-2"


def test_a_post_id_is_not_a_page_and_a_page_id_is_not_a_post(client_as, post_form):
    admin = client_as("admin")
    post_id = new_post(post_form, admin, "A post")
    page_id = new_page(post_form, admin, "A page")
    assert admin.get(f"/admin/pages/{post_id}").status_code == 404
    assert admin.get(f"/admin/posts/{page_id}").status_code == 404


def test_console_links_admins_to_pages_but_not_editors(client_as):
    assert "admin/pages" in client_as("admin").get("/admin").text
    assert "admin/pages" not in client_as("editor").get("/admin").text


# --- editors are refused every page action -----------------------------------

@pytest.mark.parametrize("path", ["/admin/pages", "/admin/pages/new"])
def test_editor_is_refused_the_page_screens(client_as, path):
    assert client_as("editor").get(path).status_code == 403


@pytest.mark.parametrize("suffix", ["", "/unpublish", "/delete"])
def test_editor_is_refused_every_change_to_a_page(client_as, post_form, site_dir,
                                                  suffix):
    admin = client_as("admin")
    page_id = new_page(post_form, admin, "Travel Lineup", "Sam", action="publish")
    editor = client_as("editor")
    assert editor.get(f"/admin/pages/{page_id}").status_code == 403
    response = post_form(editor, f"/admin/pages/{page_id}{suffix}",
                         title="Hacked", body="", action="publish")
    assert response.status_code == 403
    assert "Hacked" not in site_text(site_dir)
    assert page_file(site_dir, "travel-lineup").exists()


def test_editor_cannot_create_a_page(client_as, post_form, site_dir, client):
    response = post_form(client_as("editor"), "/admin/pages", title="Fake lineup",
                         body="", action="publish")
    assert response.status_code == 403
    assert "Fake lineup" not in client.get("/").text


def test_an_editor_cannot_reach_a_page_through_the_post_routes(client_as,
                                                               post_form):
    page_id = new_page(post_form, client_as("admin"), "Travel Lineup")
    response = post_form(client_as("editor"), f"/admin/posts/{page_id}",
                         title="Hacked", body="", action="publish")
    assert response.status_code == 404


# --- navigation and the home page --------------------------------------------

def test_nav_lists_every_published_page_and_no_drafts_on_every_page(
        client_as, post_form, db_path, tmp_path):
    admin = client_as("admin")
    new_page(post_form, admin, "Season Schedule", action="publish")
    new_page(post_form, admin, "Recruiting", action="publish")
    new_page(post_form, admin, "Secret draft page")
    publish_new(post_form, admin, "Practice schedule")
    out = render_site(tmp_path / "out", db_path)
    files = list(out.rglob("*.html"))
    assert len(files) == 4  # home, two pages, one post
    for f in files:
        nav = nav_of(f.read_text())
        assert "Season Schedule" in nav and "Recruiting" in nav, f
        assert "Secret draft page" not in nav, f
    assert 'href="pages/season-schedule.html"' in nav_of(
        (out / "index.html").read_text())
    assert 'href="../pages/recruiting.html"' in nav_of(
        next((out / "posts").glob("*.html")).read_text())
    assert "Secret draft page" not in site_text(out)


def test_nav_lists_pages_in_the_order_they_were_created(client_as, post_form,
                                                         db_path, tmp_path):
    admin = client_as("admin")
    for title in ("Season Schedule", "Travel Lineup", "Recruiting"):
        new_page(post_form, admin, title, action="publish")
    nav = nav_of((render_site(tmp_path / "out", db_path) / "index.html").read_text())
    assert nav.index("Season Schedule") < nav.index("Travel Lineup") < nav.index(
        "Recruiting")


def test_home_shows_the_travel_lineup_first_then_newest_posts(
        client_as, post_form, db_path, tmp_path):
    admin = client_as("admin")
    publish_new(post_form, admin, "Older recap")
    new_page(post_form, admin, "Travel Lineup", "Sam, Alex, Jordan",
             action="publish")
    publish_new(post_form, admin, "Newer practice schedule")
    main = re.search(r"<main>(.*)</main>",
                     (render_site(tmp_path / "out", db_path) / "index.html")
                     .read_text(), re.S).group(1)
    assert main.index("Sam, Alex, Jordan") < main.index("Newer practice schedule")
    assert main.index("Newer practice schedule") < main.index("Older recap")


def test_a_draft_travel_lineup_is_not_on_the_home_page(client_as, post_form,
                                                       db_path, tmp_path):
    admin = client_as("admin")
    new_page(post_form, admin, "Travel Lineup", "secret lineup")
    publish_new(post_form, admin, "Practice schedule")
    assert "secret lineup" not in site_text(render_site(tmp_path / "out", db_path))


def test_page_markdown_is_sanitized_and_paths_stay_relative(
        client_as, post_form, db_path, tmp_path):
    admin = client_as("admin")
    new_page(post_form, admin, "Recruiting",
             "<script>alert(1)</script>\n\n[x](javascript:alert(2))",
             action="publish")
    out = render_site(tmp_path / "out", db_path)
    text = site_text(out).lower()
    assert "<script" not in text and not re.search(r'href="\s*javascript:', text)
    for f in out.rglob("*.html"):
        assert not re.search(r'(?:href|src)="/', f.read_text()), f
    page = page_file(out, "recruiting").read_text()
    assert 'href="../style.css"' in page and 'href="../index.html"' in page


def test_public_pages_fit_a_phone(db_path, tmp_path):
    out = render_site(tmp_path / "out", db_path)
    assert 'name="viewport" content="width=device-width' in (
        out / "index.html").read_text()
    css = (out / "style.css").read_text()
    assert "overflow-wrap" in css and "max-width: 100%" in css


# --- the console's public preview --------------------------------------------

def test_console_preview_serves_published_pages_with_the_nav(client_as,
                                                             post_form, client):
    admin = client_as("admin")
    new_page(post_form, admin, "Season Schedule", "Denison", action="publish")
    new_page(post_form, admin, "Secret draft page")
    assert 'href="pages/season-schedule.html"' in nav_of(client.get("/").text)
    page = client.get("/pages/season-schedule.html")
    assert page.status_code == 200 and "Denison" in page.text
    assert 'href="../admin"' in page.text
    assert client.get("/pages/secret-draft-page.html").status_code == 404


# --- demo seed ---------------------------------------------------------------

def test_demo_seed_adds_the_three_pages_and_some_posts(tmp_path):
    from app.content import Kind, Status, list_items
    from app.seed import seed_demo, seed_demo_content

    db = tmp_path / "demo.db"
    seed_demo(db, "admin-pw", "editor-pw")
    seed_demo_content(db)
    seed_demo_content(db)  # running it again adds nothing
    pages = list_items(db, Kind.PAGE)
    assert sorted(p.slug for p in pages) == [
        "recruiting", "season-schedule", "travel-lineup"]
    posts = list_items(db, Kind.POST)
    assert {p.status for p in posts} == {Status.DRAFT, Status.PUBLISHED}
    assert len(posts) >= 3
