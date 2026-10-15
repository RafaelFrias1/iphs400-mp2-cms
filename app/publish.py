"""The site update: render published content into site/ as plain HTML.

render_site() writes the home page (published posts, newest first) and one
file per published post under posts/. update_site() is what the console runs
after any change to published content. `cms publish` calls render_site() from
this module; T07 (ADR-004) adds the deploy to update_site() and decides how
the CLI reaches it.

Two rules the rubric checks:

  1. Only PUBLISHED content is written here. A draft that reaches site/ is a bug.
  2. Every href and src is RELATIVE ("style.css", "posts/x.html"), never
     root-absolute ("/style.css"), because Pages serves this from a subfolder.
"""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app import content, settings
from app.content import Kind, Status
from app.markdown import render_markdown

CSS = """/* Minimal starter styles — make them yours. */
:root { color-scheme: light dark; }
body { font: 16px/1.6 system-ui, sans-serif; margin: 0 auto; max-width: 42rem; padding: 1rem; }
header a { font-weight: 700; text-decoration: none; }
main { margin-block: 2rem; }
.byline { color: GrayText; font-size: 0.9rem; }
"""


def byline(email: str) -> str:
    """The author's name on the public site: the part of the email before @.

    The full email is never published, so readers can't harvest it (ADR-005).
    """
    return email.split("@", 1)[0]


def reader_date(timestamp: str) -> str:
    """An ISO UTC timestamp as readers see it, 'Oct 14, 2026', in the team
    laptop's time zone, so an evening post isn't dated tomorrow."""
    return datetime.fromisoformat(timestamp).astimezone().strftime("%b %d, %Y")


def environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(settings.TEMPLATES)),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["byline"] = byline
    env.filters["reader_date"] = reader_date
    return env


def render_site(out: Path | None = None, db_path: Path | None = None) -> Path:
    """Rebuild `out` from scratch with every published post in `db_path`.

    A database that doesn't exist yet (a fresh clone) renders an empty site.
    """
    out = out or settings.SITE
    db_path = db_path or settings.DATABASE_PATH
    posts = (content.list_items(db_path, Kind.POST, Status.PUBLISHED)
             if db_path.exists() else [])
    if out.exists():
        shutil.rmtree(out)
    (out / "posts").mkdir(parents=True)
    env = environment()
    (out / "style.css").write_text(CSS)
    (out / "index.html").write_text(
        env.get_template("public/home.html").render(
            title=settings.SITE_TITLE, posts=posts, css_path="style.css",
            home_path="index.html",
        )
    )
    post_page = env.get_template("public/post.html")
    for post in posts:
        (out / "posts" / f"{post.slug}.html").write_text(
            post_page.render(
                title=settings.SITE_TITLE, post=post,
                body=render_markdown(post.body),
                css_path="../style.css", home_path="../index.html",
            )
        )
    return out


def update_site(db_path: Path, out: Path) -> Path:
    """Run a site update after a change to published content."""
    return render_site(out, db_path)
