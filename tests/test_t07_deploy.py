"""T07: publishing deploys automatically; failure blocks the change (issue #8).

Seam 3, the deployer. Every test app gets the `deployer` fake from conftest:
it records what each deploy would have sent, or raises when `failing` is set,
as a push does with no wifi. Behaviour is read from responses, from the
console's own pages, and from the files in `site_dir`.
"""
from __future__ import annotations

import re
import subprocess

import pytest
from test_t03_posts import new_post, slug_of
from test_t04_publish import post_file, publish_new, site_text
from test_t05_pages import new_page, page_file

from app import deploy, settings
from app.cli import main
from app.main import create_app

OFFLINE = "website not updated"


# --- a site update deploys once ------------------------------------------------

def test_publishing_deploys_the_rebuilt_site_once(client_as, post_form, deployer):
    c = client_as("editor")
    publish_new(post_form, c, "Practice schedule", "- Mon 3pm, range")
    assert deployer.calls == 1
    assert "Practice schedule" in deployer.deployed[0]["index.html"]


@pytest.mark.parametrize("change", ["edit", "unpublish", "delete"])
def test_each_change_to_published_content_deploys_once(
        client_as, post_form, deployer, change):
    c = client_as("editor")
    post_id = publish_new(post_form, c, "Practice schedule", "Mon 3pm")
    path = {"edit": "", "unpublish": "/unpublish", "delete": "/delete"}[change]
    response = post_form(c, f"/admin/posts/{post_id}{path}",
                         title="Practice schedule", body="Tue 4pm", action="save")
    assert response.status_code == 303
    assert deployer.calls == 2


def test_publishing_a_page_deploys(client_as, post_form, deployer):
    new_page(post_form, client_as("admin"), "Season Schedule", action="publish")
    assert deployer.calls == 1
    assert any(path.startswith("pages") for path in deployer.deployed[0])


def test_draft_only_changes_never_deploy(client_as, post_form, deployer):
    c = client_as("editor")
    post_id = new_post(post_form, c, "Practice schedule")
    post_form(c, f"/admin/posts/{post_id}", title="v2", body="", action="save")
    post_form(c, f"/admin/posts/{post_id}", title="v3", body="", action="preview")
    post_form(c, "/admin/posts", title="Preview only", body="", action="preview")
    post_form(c, f"/admin/posts/{post_id}/unpublish")
    post_form(c, f"/admin/posts/{post_id}/delete")
    assert deployer.calls == 0


def test_account_changes_never_deploy(client_as, post_form, new_account,
                                      account_id, deployer):
    new_account("captain@example.com", "captain-pw-123")
    admin = client_as("admin")
    captain = account_id(admin, "captain@example.com")
    post_form(admin, f"/admin/accounts/{captain}/deactivate")
    assert deployer.calls == 0


# --- a failed deploy blocks the change ---------------------------------------

def test_publishing_a_draft_offline_keeps_it_a_draft(
        client_as, post_form, deployer, site_dir):
    c = client_as("editor")
    post_id = new_post(post_form, c, "Practice schedule", "draft text")
    deployer.failing = True
    response = post_form(c, f"/admin/posts/{post_id}", title="Practice schedule",
                         body="typed at the hotel", action="publish")
    assert response.status_code == 503
    assert OFFLINE in response.text.lower()
    assert "typed at the hotel" in response.text
    form = c.get(f"/admin/posts/{post_id}").text
    assert "Draft by" in form and "draft text" in form
    assert "typed at the hotel" not in form
    assert "Practice schedule" not in site_text(site_dir)


def test_a_new_post_published_offline_is_kept_as_a_draft(
        client_as, post_form, deployer, site_dir):
    c = client_as("editor")
    deployer.failing = True
    response = post_form(c, "/admin/posts", title="Practice schedule",
                         body="- Mon 3pm, range", action="publish")
    assert response.status_code == 503
    assert OFFLINE in response.text.lower()
    assert "saved as a draft" in response.text
    assert "Draft by" in response.text and "- Mon 3pm, range" in response.text
    post_id = int(re.search(r'action="[^"]*admin/posts/(\d+)"',
                            response.text).group(1))
    assert "Draft by" in c.get(f"/admin/posts/{post_id}").text
    assert "Practice schedule" not in site_text(site_dir)


def test_a_rendering_bug_is_not_reported_as_offline(
        client_as, post_form, deployer, monkeypatch):
    from app import publish

    def broken(*args, **kwargs):
        raise RuntimeError("template bug")

    c = client_as("editor")
    post_id = new_post(post_form, c, "Practice schedule")
    monkeypatch.setattr(publish, "home_html", broken)
    with pytest.raises(RuntimeError):
        post_form(c, f"/admin/posts/{post_id}", title="Practice schedule",
                  body="", action="publish")
    monkeypatch.undo()
    assert "Draft by" in c.get(f"/admin/posts/{post_id}").text
    assert deployer.calls == 0


def test_editing_the_travel_lineup_offline_keeps_the_published_text(
        client_as, post_form, deployer, site_dir):
    admin = client_as("admin")
    page_id = new_page(post_form, admin, "Travel Lineup", "Sam, Alex",
                       action="publish")
    deployer.failing = True
    response = post_form(admin, f"/admin/pages/{page_id}", title="Travel Lineup",
                         body="Sam, Jordan", slug="travel-lineup", action="save")
    assert response.status_code == 503
    assert OFFLINE in response.text.lower()
    assert "Sam, Jordan" in response.text
    assert "Sam, Alex" in admin.get(f"/admin/pages/{page_id}").text
    assert "Sam, Alex" in page_file(site_dir, "travel-lineup").read_text()
    assert "Sam, Jordan" not in site_text(site_dir)

    deployer.failing = False
    response = post_form(admin, f"/admin/pages/{page_id}", title="Travel Lineup",
                         body="Sam, Jordan", slug="travel-lineup", action="save")
    assert response.status_code == 303
    assert "Sam, Jordan" in page_file(site_dir, "travel-lineup").read_text()


def test_deleting_a_published_post_offline_leaves_it_in_place(
        client_as, post_form, deployer, site_dir):
    c = client_as("editor")
    post_id = publish_new(post_form, c, "Old recap", "text")
    slug = slug_of(c, post_id)
    deployer.failing = True
    response = post_form(c, f"/admin/posts/{post_id}/delete")
    assert response.status_code == 503
    assert OFFLINE in response.text.lower()
    assert "Old recap" in response.text
    assert c.get(f"/admin/posts/{post_id}").status_code == 200
    assert post_file(site_dir, slug).exists()


def test_unpublishing_offline_keeps_the_post_published(
        client_as, post_form, deployer, site_dir):
    c = client_as("editor")
    post_id = publish_new(post_form, c, "Practice schedule")
    deployer.failing = True
    response = post_form(c, f"/admin/posts/{post_id}/unpublish")
    assert response.status_code == 503
    assert OFFLINE in response.text.lower()
    assert "Published by" in c.get(f"/admin/posts/{post_id}").text
    assert "Practice schedule" in site_text(site_dir)


# --- the default deployer and `cms deploy` -----------------------------------

class FakeRun:
    """Stands in for subprocess.run: records each command, never runs git."""

    def __init__(self, returncode: int = 0):
        self.returncode = returncode
        self.calls: list[tuple[list[str], dict]] = []

    def __call__(self, cmd, **kwargs):
        self.calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(cmd, self.returncode, "", "rejected")


def test_the_default_deployer_pushes_to_gh_pages(monkeypatch, tmp_path):
    assert create_app(db_path=tmp_path / "cms.db").state.deployer \
        is deploy.push_to_gh_pages
    run = FakeRun()
    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setenv("CMS_GITHUB_TOKEN", "fake-token-not-real")
    deploy.push_to_gh_pages(tmp_path)
    (cmd, kwargs), = run.calls
    assert "ghp_import" in cmd and "-p" in cmd and str(tmp_path) in cmd
    assert "fake-token-not-real" not in " ".join(cmd)
    assert kwargs["env"]["GIT_TERMINAL_PROMPT"] == "0"
    assert any(v.startswith("AUTHORIZATION: basic ")
               for v in kwargs["env"].values())


def test_the_default_deployer_raises_when_the_push_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(subprocess, "run", FakeRun(returncode=1))
    with pytest.raises(deploy.DeployFailed):
        deploy.push_to_gh_pages(tmp_path)


@pytest.mark.parametrize("returncode, exit_code", [(0, 0), (1, 1)])
def test_cms_deploy_still_works_by_hand(monkeypatch, tmp_path, returncode,
                                        exit_code):
    (tmp_path / "site").mkdir()
    monkeypatch.setattr(settings, "SITE", tmp_path / "site")
    run = FakeRun(returncode)
    monkeypatch.setattr(subprocess, "run", run)
    assert main(["deploy"]) == exit_code
    assert len(run.calls) == 1


def test_a_taken_slug_on_a_published_page_is_refused_without_a_deploy(
        client_as, post_form, deployer):
    admin = client_as("admin")
    new_page(post_form, admin, "Recruiting", action="publish")
    page_id = new_page(post_form, admin, "Season Schedule", action="publish")
    response = post_form(admin, f"/admin/pages/{page_id}", title="Season Schedule",
                         body="", slug="recruiting", action="save")
    assert response.status_code == 400
    assert "already used" in response.text
    assert deployer.calls == 2
    assert "season-schedule" in admin.get(f"/admin/pages/{page_id}").text
