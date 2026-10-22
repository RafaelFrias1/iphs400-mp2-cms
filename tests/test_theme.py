"""F8 (#10): the Coach switches the public site's theme on the Settings page.

Each test is named after the acceptance step it checks:

  1. Two themes exist, each one CSS file in its own folder under app/themes/.
  2. The admin Settings page selects the theme, and the choice survives a
     server restart.
  3. Publishing writes the selected theme's CSS as site/style.css, so every
     page's relative stylesheet link still works.
  4. Switching back and publishing again restores the first theme's CSS.
  5. Both themes show no horizontal overflow at 390 px (walked by hand; here
     only the phone-first rules each stylesheet must carry).
  6. The Settings form carries a CSRF token; its POST without it is refused.
"""
from __future__ import annotations

import re

from fastapi.testclient import TestClient

from app import settings, theme
from app.main import create_app
from app.publish import render_site

THEMES_DIR = settings.ROOT / "app" / "themes"


def choose(post_form, c: TestClient, name: str):
    return post_form(c, "/admin/settings", theme=name)


def selected_on_page(c: TestClient) -> str:
    match = re.search(r'value="(\w+)" checked', c.get("/admin/settings").text)
    assert match, "No theme is checked on the Settings page"
    return match.group(1)


def theme_css(name: str) -> str:
    return (THEMES_DIR / name / "style.css").read_text()


# --- step 1: two themes, one CSS file each ------------------------------------

def test_step1_two_themes_each_one_css_file_in_its_own_folder():
    assert theme.available() == ["classic", "kenyon"]
    for name in theme.available():
        files = [f.name for f in (THEMES_DIR / name).iterdir()]
        assert files == ["style.css"], (name, files)


def test_step1_kenyon_is_light_with_purple_and_serif_headings():
    css = theme_css("kenyon")
    assert "color-scheme: light;" in css and "dark" not in css
    assert "--kenyon-purple" in css and "serif" in css


# --- step 2: the Settings page selects the theme, and it lasts ----------------

def test_step2_settings_page_defaults_to_classic(client_as):
    assert selected_on_page(client_as("admin")) == "classic"


def test_step2_admin_selects_a_theme_that_survives_a_restart(
        client_as, post_form, db_path, site_dir, deployer):
    admin = client_as("admin")
    response = choose(post_form, admin, "kenyon")
    assert response.status_code == 303
    assert selected_on_page(admin) == "kenyon"

    restarted = TestClient(create_app(db_path=db_path, site_dir=site_dir,
                                      deployer=deployer))
    assert restarted.get("/style.css").text == theme_css("kenyon")


def test_step2_the_console_preview_serves_the_selected_theme(
        client_as, post_form, client):
    assert client.get("/style.css").text == theme_css("classic")
    choose(post_form, client_as("admin"), "kenyon")
    response = client.get("/style.css")
    assert response.text == theme_css("kenyon")
    assert response.headers["content-type"].startswith("text/css")


def test_step2_only_an_existing_theme_folder_is_accepted(client_as, post_form):
    admin = client_as("admin")
    for name in ("nope", "../templates", "__pycache__", ""):
        response = choose(post_form, admin, name)
        assert response.status_code == 400, name
    assert selected_on_page(admin) == "classic"


def test_step2_editors_neither_see_nor_open_the_settings_page(
        client_as, post_form, client):
    editor = client_as("editor")
    assert "admin/settings" not in editor.get("/admin").text
    assert editor.get("/admin/settings").status_code == 403
    assert choose(post_form, editor, "kenyon").status_code == 403
    assert "admin/settings" in client_as("admin").get("/admin").text
    anonymous = client.get("/admin/settings", follow_redirects=False)
    assert anonymous.status_code == 303 and anonymous.headers["location"] == "/login"


def test_step2_saving_a_theme_is_a_site_update(client_as, post_form, deployer):
    choose(post_form, client_as("admin"), "kenyon")
    assert deployer.calls == 1
    assert deployer.deployed[-1]["style.css"] == theme_css("kenyon")


def test_step2_a_failed_site_update_refuses_the_change(
        client_as, post_form, deployer, site_dir):
    admin = client_as("admin")
    deployer.failing = True
    response = choose(post_form, admin, "kenyon")
    assert response.status_code == 503 and "not saved" in response.text
    assert selected_on_page(admin) == "classic"
    assert (site_dir / "style.css").read_text() == theme_css("classic")


def test_step2_cms_theme_is_used_when_no_theme_is_stored(
        db_path, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "THEME", "kenyon")
    out = render_site(tmp_path / "out", db_path)
    assert (out / "style.css").read_text() == theme_css("kenyon")


def test_step2_an_unknown_cms_theme_falls_back_to_classic(
        db_path, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "THEME", "nope")
    out = render_site(tmp_path / "out", db_path)
    assert (out / "style.css").read_text() == theme_css("classic")


# --- step 3: publish writes the selected theme as site/style.css -------------

def test_step3_publish_writes_the_selected_theme_as_style_css(
        client_as, post_form, db_path, tmp_path):
    admin = client_as("admin")
    post_form(admin, "/admin/posts/new", title="Practice schedule",
              body="Mon 3pm", action="publish")
    choose(post_form, admin, "kenyon")

    out = render_site(tmp_path / "out", db_path)
    assert (out / "style.css").read_text() == theme_css("kenyon")
    assert '<link rel="stylesheet" href="style.css">' in (
        out / "index.html").read_text()
    for page in (out / "posts").glob("*.html"):
        assert '<link rel="stylesheet" href="../style.css">' in page.read_text()


def test_step3_publishing_a_fresh_clone_writes_the_default_theme(tmp_path):
    out = render_site(tmp_path / "out", tmp_path / "missing.db")
    assert (out / "style.css").read_text() == theme_css("classic")


# --- step 4: switching back restores the first theme --------------------------

def test_step4_switching_back_restores_the_first_theme(
        client_as, post_form, db_path, tmp_path):
    admin = client_as("admin")
    choose(post_form, admin, "kenyon")
    render_site(tmp_path / "out", db_path)
    choose(post_form, admin, "classic")

    out = render_site(tmp_path / "out", db_path)
    assert (out / "style.css").read_text() == theme_css("classic")


# --- step 5: both themes fit a 390 px phone -----------------------------------

def test_step5_both_themes_carry_the_phone_first_rules():
    for name in theme.available():
        css = theme_css(name)
        assert "overflow-wrap: anywhere" in css, name
        assert "img, table, pre { max-width: 100%; }" in css, name
        assert "overflow-x: auto" in css, name
        assert re.search(r"textarea[^{]*\{[^}]*max-width: 100%", css), name


# --- step 6: the Settings form's CSRF token -----------------------------------

def test_step6_the_settings_form_carries_a_csrf_token(client_as):
    page = client_as("admin").get("/admin/settings").text
    form = page[page.index('action="../admin/settings"'):]
    assert re.search(r'name="csrf_token" value="[^"]+"', form)


def test_step6_a_settings_post_without_the_token_is_refused(client_as, deployer):
    admin = client_as("admin")
    for data in ({"theme": "kenyon"},
                 {"theme": "kenyon", "csrf_token": "forged"}):
        response = admin.post("/admin/settings", data=data,
                              follow_redirects=False)
        assert response.status_code == 403, data
    assert selected_on_page(admin) == "classic" and deployer.calls == 0
