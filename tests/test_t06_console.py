"""T06: the console dashboard and one content list (issue #7).

All through HTTP: the dashboard's counts (each carries data-count="kind-status"),
and which rows the content list's filter bar returns (rows carry
data-post-id or data-page-id, then the title cell).
"""
from __future__ import annotations

import re

import pytest
from conftest import DEMO_ACCOUNTS
from fastapi.testclient import TestClient
from test_t03_posts import new_post
from test_t04_publish import publish_new
from test_t05_pages import new_page

ROW = re.compile(r'<tr data-(post|page)-id="(\d+)"[^>]*>\s*<td>(.*?)</td>', re.S)


def titles(c: TestClient, query: str = "") -> list[str]:
    """The titles in the content list, top to bottom."""
    html = c.get(f"/admin/content{query}").text
    return [re.sub(r"<[^>]+>", "", cell).strip() for _, _, cell in ROW.findall(html)]


def count(html: str, kind: str, status: str) -> int:
    match = re.search(rf'data-count="{kind}-{status}">(\d+)<', html)
    assert match, f"No count for {kind}-{status}"
    return int(match.group(1))


@pytest.fixture
def team_content(client_as, post_form, new_account, login_as):
    """Two pages and four posts by three accounts, oldest first."""
    admin, editor = client_as("admin"), client_as("editor")
    new_account("manager@example.test", "manager-pw-123")
    manager = login_as("manager@example.test", "manager-pw-123")
    new_page(post_form, admin, "Season Schedule", action="publish")
    new_page(post_form, admin, "Recruiting draft")
    publish_new(post_form, admin, "Qualifying results")
    new_post(post_form, editor, "Captain draft")
    publish_new(post_form, editor, "Practice schedule")
    new_post(post_form, manager, "Recap draft")
    return admin, editor


# --- the dashboard -----------------------------------------------------------

def test_dashboard_counts_posts_and_pages_by_status(team_content):
    admin, _ = team_content
    html = admin.get("/admin").text
    assert count(html, "post", "draft") == 2
    assert count(html, "post", "published") == 2
    assert count(html, "page", "draft") == 1
    assert count(html, "page", "published") == 1


def test_dashboard_counts_start_at_zero(client_as):
    html = client_as("editor").get("/admin").text
    for kind in ("post", "page"):
        for status in ("draft", "published"):
            assert count(html, kind, status) == 0


def test_dashboard_counts_link_to_the_filtered_list(team_content):
    admin, _ = team_content
    html = admin.get("/admin").text
    assert 'href="admin/content?status=draft&amp;kind=post"' in html
    assert 'href="admin/content"' in html


# --- one content list --------------------------------------------------------

def test_one_list_shows_posts_and_pages_newest_updated_first(team_content,
                                                             post_form):
    admin, _ = team_content
    assert titles(admin) == ["Recap draft", "Practice schedule", "Captain draft",
                             "Qualifying results", "Recruiting draft",
                             "Season Schedule"]
    page_id = int(re.search(r'data-page-id="(\d+)"[^>]*>\s*<td>\s*<a[^>]*>'
                            r'Season Schedule', admin.get("/admin/content").text)
                  .group(1))
    post_form(admin, f"/admin/pages/{page_id}", title="Season Schedule",
              slug="season-schedule", body="updated", action="save")
    assert titles(admin)[0] == "Season Schedule"


def test_the_filter_bar_has_status_then_kind_then_author(client_as):
    html = client_as("editor").get("/admin/content").text
    bar = re.search(r'<form[^>]*class="filters".*?</form>', html, re.S).group(0)
    names = re.findall(r'<select name="(\w+)"', bar)
    assert names == ["status", "kind", "author"]
    assert 'method="get"' in bar


@pytest.mark.parametrize("query, expected", [
    ("?status=draft", {"Recap draft", "Captain draft", "Recruiting draft"}),
    ("?kind=page", {"Season Schedule", "Recruiting draft"}),
    ("?status=published&kind=post", {"Practice schedule", "Qualifying results"}),
    ("?status=&kind=&author=", {"Recap draft", "Practice schedule",
                                "Captain draft", "Qualifying results",
                                "Recruiting draft", "Season Schedule"}),
])
def test_filters_combine(team_content, query, expected):
    admin, _ = team_content
    assert set(titles(admin, query)) == expected


def test_filter_by_author_combines_with_status_and_kind(team_content,
                                                        account_id):
    admin, editor = team_content
    captain = account_id(admin, DEMO_ACCOUNTS["editor"]["email"])
    assert titles(editor, f"?status=draft&kind=post&author={captain}") == [
        "Captain draft"]
    assert titles(editor, f"?author={captain}") == ["Practice schedule",
                                                    "Captain draft"]


def test_the_filter_bar_keeps_the_chosen_filters(team_content):
    admin, _ = team_content
    html = admin.get("/admin/content?status=draft&kind=page").text
    assert '<option value="draft" selected>' in html
    assert '<option value="page" selected>' in html


def test_unknown_filter_values_show_nothing_rather_than_fail(team_content):
    admin, _ = team_content
    assert admin.get("/admin/content?author=%C2%B2").status_code == 200
    response = admin.get("/admin/content?status=live&kind=x&author=abc")
    assert response.status_code == 200
    assert titles(admin, "?status=live&kind=x&author=abc") == []


def test_posts_and_pages_urls_are_the_same_list_prefiltered(team_content):
    admin, _ = team_content
    assert set(titles(admin, "?kind=post")) == {
        t for t in titles(admin) if t not in ("Season Schedule",
                                              "Recruiting draft")}
    posts = admin.get("/admin/posts").text
    assert 'class="filters"' in posts
    assert '<option value="post" selected>' in posts


# --- who sees which controls -------------------------------------------------

def test_rows_link_to_the_editor_only_when_the_account_may_edit(team_content):
    admin, editor = team_content
    admin_html = admin.get("/admin/content").text
    assert len(re.findall(r'href="(?:\.\./)*admin/(?:posts|pages)/\d+"',
                          admin_html)) == 6
    editor_html = editor.get("/admin/content").text
    links = re.findall(r'href="(?:\.\./)*admin/(posts|pages)/\d+">([^<]+)<',
                       editor_html)
    assert sorted(t for _, t in links) == ["Captain draft", "Practice schedule"]


def test_editors_see_no_page_or_account_controls(team_content):
    _, editor = team_content
    for path in ("/admin", "/admin/content"):
        html = editor.get(path).text
        assert "admin/pages/new" not in html, path
        assert "admin/accounts" not in html, path
        assert "admin/posts/new" in html, path


def test_admins_see_page_and_account_controls(team_content):
    admin, _ = team_content
    html = admin.get("/admin").text
    assert "admin/pages/new" in html and "admin/accounts" in html
    assert "admin/pages/new" in admin.get("/admin/content").text


def test_content_list_needs_a_login(client):
    response = client.get("/admin/content", follow_redirects=False)
    assert response.headers["location"] == "/login"
