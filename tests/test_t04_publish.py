"""T04: published posts appear on the public site (issue #5).

Two seams. Over HTTP, the console publishes, unpublishes, edits and deletes;
a site update writes into `site_dir` (the test app's site/). Rendering tests
call render_site() into a temporary directory and read the files it wrote.
"""
from __future__ import annotations

import re
import shutil

import pytest
from conftest import DEMO_ACCOUNTS
from fastapi.testclient import TestClient
from test_t03_posts import new_post, slug_of

from app.publish import render_site


def publish_new(post_form, c: TestClient, title: str, body: str = "") -> int:
    """Write and publish a post in one click; return its id."""
    response = post_form(c, "/admin/posts", title=title, body=body,
                         action="publish")
    assert response.status_code == 303, response.text
    return int(response.headers["location"].rsplit("/", 1)[1])


def site_text(out) -> str:
    """Every file under the site, concatenated."""
    return "\n".join(f.read_text() for f in sorted(out.rglob("*")) if f.is_file())


def post_file(out, slug: str):
    return out / "posts" / f"{slug}.html"


# --- the editor screen -------------------------------------------------------

def test_save_draft_and_publish_sit_side_by_side(client_as):
    page = client_as("editor").get("/admin/posts/new").text
    assert re.search(r'<button[^>]*value="save"[^>]*>Save draft</button>\s*'
                     r'<button[^>]*value="publish"[^>]*>Publish</button>', page)


def test_publish_takes_one_click_and_the_post_reaches_the_site(
        client_as, post_form, site_dir):
    c = client_as("editor")
    post_id = publish_new(post_form, c, "Practice schedule", "- Mon 3pm, range")
    assert "Published" in c.get(f"/admin/posts/{post_id}").text
    home = (site_dir / "index.html").read_text()
    assert "Practice schedule" in home
    page = post_file(site_dir, slug_of(c, post_id)).read_text()
    assert "<li>Mon 3pm, range</li>" in page


def test_publishing_an_existing_draft(client_as, post_form, site_dir):
    c = client_as("editor")
    post_id = new_post(post_form, c, "Practice schedule", "draft text")
    assert not site_dir.exists()
    response = post_form(c, f"/admin/posts/{post_id}", title="Practice schedule",
                         body="final text", action="publish")
    assert response.status_code == 303
    assert "final text" in post_file(site_dir, slug_of(c, post_id)).read_text()


def test_a_published_post_offers_unpublish_not_publish(client_as, post_form):
    c = client_as("editor")
    page = c.get(f"/admin/posts/{publish_new(post_form, c, 'Recap')}").text
    assert "Unpublish" in page
    assert 'value="publish"' not in page


def test_publish_without_a_title_is_refused_and_nothing_is_written(
        client_as, post_form, site_dir):
    c = client_as("editor")
    response = post_form(c, "/admin/posts", title=" ", body="kept",
                         action="publish")
    assert response.status_code == 400
    assert "kept" in response.text
    assert not site_dir.exists()


# --- which changes run a site update -----------------------------------------

def test_saving_a_draft_runs_no_site_update(client_as, post_form, site_dir):
    c = client_as("editor")
    post_id = new_post(post_form, c, "Practice schedule")
    post_form(c, f"/admin/posts/{post_id}", title="Practice schedule v2",
              body="", action="save")
    assert not site_dir.exists()


def test_deleting_a_draft_runs_no_site_update(client_as, post_form, site_dir):
    c = client_as("editor")
    publish_new(post_form, c, "Already published")
    shutil.rmtree(site_dir)
    draft_id = new_post(post_form, c, "Never published")
    post_form(c, f"/admin/posts/{draft_id}/delete")
    assert not site_dir.exists()


def test_editing_a_published_post_updates_the_site(client_as, post_form, site_dir):
    c = client_as("editor")
    post_id = publish_new(post_form, c, "Practice schedule", "Mon 3pm")
    response = post_form(c, f"/admin/posts/{post_id}", title="Practice schedule",
                         body="Tue 4pm", action="save")
    assert response.status_code == 303
    page = post_file(site_dir, slug_of(c, post_id)).read_text()
    assert "Tue 4pm" in page and "Mon 3pm" not in page
    assert "Published" in c.get(f"/admin/posts/{post_id}").text


def test_unpublishing_returns_the_post_to_draft_and_removes_it(
        client_as, post_form, site_dir):
    c = client_as("editor")
    post_id = publish_new(post_form, c, "Published by mistake", "oops")
    slug = slug_of(c, post_id)
    response = post_form(c, f"/admin/posts/{post_id}/unpublish")
    assert response.status_code == 303
    assert "Draft" in c.get(f"/admin/posts/{post_id}").text
    assert not post_file(site_dir, slug).exists()
    assert "Published by mistake" not in site_text(site_dir)


def test_deleting_a_published_post_removes_it_from_the_site(
        client_as, post_form, site_dir):
    c = client_as("editor")
    post_id = publish_new(post_form, c, "Old recap", "text")
    slug = slug_of(c, post_id)
    post_form(c, f"/admin/posts/{post_id}/delete")
    assert not post_file(site_dir, slug).exists()
    assert "Old recap" not in site_text(site_dir)


# --- who may publish and unpublish -------------------------------------------

def test_admin_can_unpublish_an_editors_post(client_as, post_form, site_dir):
    post_id = publish_new(post_form, client_as("editor"), "Captain's post")
    admin = client_as("admin")
    assert post_form(admin, f"/admin/posts/{post_id}/unpublish").status_code == 303
    assert "Captain's post" not in site_text(site_dir)


@pytest.mark.parametrize("path", ["/unpublish", ""])
def test_editor_cannot_publish_or_unpublish_someone_elses_post(
        client_as, post_form, site_dir, path):
    admin = client_as("admin")
    post_id = publish_new(post_form, admin, "Qualifying results", "1. Sam")
    response = post_form(client_as("editor"), f"/admin/posts/{post_id}{path}",
                         title="Hacked", body="", action="publish")
    assert response.status_code == 403
    assert "Qualifying results" in site_text(site_dir)
    assert "Hacked" not in site_text(site_dir)


def test_unpublish_needs_a_csrf_token(client_as, post_form, site_dir):
    c = client_as("editor")
    post_id = publish_new(post_form, c, "Practice schedule")
    response = c.post(f"/admin/posts/{post_id}/unpublish", data={},
                      follow_redirects=False)
    assert response.status_code == 403
    assert "Practice schedule" in site_text(site_dir)


# --- what the site update writes ---------------------------------------------

def test_home_lists_published_posts_newest_first_with_author_and_date(
        client_as, post_form, db_path, tmp_path):
    c = client_as("editor")
    publish_new(post_form, c, "Older recap")
    publish_new(post_form, c, "Newer practice schedule")
    home = (render_site(tmp_path / "out", db_path) / "index.html").read_text()
    assert home.index("Newer practice schedule") < home.index("Older recap")
    author = DEMO_ACCOUNTS["editor"]["email"].split("@")[0]
    assert home.count(author) >= 2
    assert home.count("<time datetime=") >= 2


def test_post_page_shows_author_and_created_and_updated_times(
        client_as, post_form, db_path, tmp_path):
    c = client_as("editor")
    post_id = publish_new(post_form, c, "Practice schedule")
    out = render_site(tmp_path / "out", db_path)
    page = post_file(out, slug_of(c, post_id)).read_text()
    assert DEMO_ACCOUNTS["editor"]["email"].split("@")[0] in page
    assert 'class="created"' in page and 'class="updated"' in page


def test_home_links_to_each_post_page(client_as, post_form, db_path, tmp_path):
    c = client_as("editor")
    slug = slug_of(c, publish_new(post_form, c, "Practice schedule"))
    out = render_site(tmp_path / "out", db_path)
    assert f'href="posts/{slug}.html"' in (out / "index.html").read_text()


def test_drafts_never_reach_the_output(client_as, post_form, db_path, tmp_path):
    c = client_as("editor")
    publish_new(post_form, c, "Published post", "public body")
    new_post(post_form, c, "Secret draft title", "secret body")
    text = site_text(render_site(tmp_path / "out", db_path))
    assert "Published post" in text
    assert "Secret draft title" not in text and "secret body" not in text
    assert len(list((tmp_path / "out" / "posts").iterdir())) == 1


def test_markdown_is_sanitized_before_it_is_written(
        client_as, post_form, db_path, tmp_path):
    c = client_as("editor")
    publish_new(post_form, c, "Pasted snippet <b>bold</b>",
                "<script>alert(1)</script>\n\n<a href=\"x\" onclick=\"evil()\">x</a>"
                "\n\n[link](javascript:alert(2))")
    text = site_text(render_site(tmp_path / "out", db_path)).lower()
    assert "<script" not in text
    assert "onclick" not in text
    assert not re.search(r'href="\s*javascript:', text)
    assert "<b>bold</b>" not in text


def test_every_href_and_src_is_relative(client_as, post_form, db_path, tmp_path):
    c = client_as("editor")
    publish_new(post_form, c, "Practice schedule", "[Golfstat](https://golfstat.com)")
    out = render_site(tmp_path / "out", db_path)
    for f in out.rglob("*.html"):
        html = f.read_text()
        assert not re.search(r'(?:href|src)="/', html), f
    page = next((out / "posts").glob("*.html")).read_text()
    assert 'href="../style.css"' in page and 'href="../index.html"' in page


def test_cms_publish_renders_through_the_same_module(client_as, post_form, db_path,
                                                tmp_path, monkeypatch):
    from app import settings
    from app.cli import main

    c = client_as("editor")
    slug = slug_of(c, publish_new(post_form, c, "Practice schedule"))
    monkeypatch.setattr(settings, "DATABASE_PATH", db_path)
    monkeypatch.setattr(settings, "SITE", tmp_path / "cli-site")
    assert main(["publish"]) == 0
    assert post_file(tmp_path / "cli-site", slug).exists()
