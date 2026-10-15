"""The site update: render published content into site/ as plain HTML.

render_site() writes the home page (the Travel Lineup page if published, then
published posts newest first), one file per published post under posts/ and
one per published page under pages/. Every page carries a nav built from the
published pages. The console previews the same pages at / through home_html()
and item_html(), so it shows what readers will see. update_site() is what the console runs
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
from app.content import Item, Kind, Status
from app.markdown import render_markdown

CSS = """/* Phones first: one column, nothing wider than the screen. */
:root { color-scheme: light dark; }
body { font: 16px/1.6 system-ui, sans-serif; margin: 0 auto; max-width: 42rem;
       padding: 1rem; overflow-wrap: anywhere; }
header a { font-weight: 700; text-decoration: none; }
header .console { float: right; font-weight: 400; }
nav ul { display: flex; flex-wrap: wrap; gap: 0.25rem 1rem; list-style: none;
         margin: 0.5rem 0 0; padding: 0; }
main { margin-block: 2rem; }
img, table, pre { max-width: 100%; }
/* Wide tables and code scroll in their own box, not the page. */
table, pre { display: block; overflow-x: auto; }
.byline { color: GrayText; font-size: 0.9rem; }
.lineup { border-bottom: 1px solid GrayText; margin-bottom: 1.5rem; }
"""

TRAVEL_LINEUP = "travel-lineup"


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


def published(db_path: Path, kind: Kind) -> list[Item]:
    """Newest first. A database that doesn't exist yet (a fresh clone) has none."""
    if not db_path.exists():
        return []
    return content.list_items(db_path, kind, Status.PUBLISHED)


def _render(template: str, prefix: str, nav_pages: list[Item], preview: bool,
            **context) -> str:
    """Render a public page that sits `prefix` ("" or "../") below the root.

    Every link is built from `prefix`, so the paths stay relative. The nav
    lists pages oldest first, in the order the Coach created them.
    """
    nav_pages = sorted(nav_pages, key=lambda p: (p.created_at, p.id))
    return environment().get_template(template).render(
        title=settings.SITE_TITLE, prefix=prefix, nav_pages=nav_pages,
        css_path=f"{prefix}style.css", home_path=f"{prefix}index.html",
        console_path=f"{prefix}admin" if preview else None, **context,
    )


def home_html(pages: list[Item], posts: list[Item], preview: bool = False) -> str:
    """index.html: the Travel Lineup (if published), then posts newest first.

    A preview (the console's /) also links to the console; site/ never does.
    """
    lineup = next((p for p in pages if p.slug == TRAVEL_LINEUP), None)
    return _render(
        "public/home.html", "", pages, preview, posts=posts, lineup=lineup,
        lineup_body=render_markdown(lineup.body) if lineup else None,
    )


def item_html(item: Item, pages: list[Item], preview: bool = False) -> str:
    """posts/<slug>.html or pages/<slug>.html, its Markdown sanitized."""
    return _render("public/item.html", "../", pages, preview, item=item,
                   body=render_markdown(item.body))


def render_site(out: Path | None = None, db_path: Path | None = None) -> Path:
    """Rebuild `out` from scratch with every published item in `db_path`."""
    out = out or settings.SITE
    db_path = db_path or settings.DATABASE_PATH
    pages = published(db_path, Kind.PAGE)
    posts = published(db_path, Kind.POST)
    if out.exists():
        shutil.rmtree(out)
    for kind in Kind:
        (out / f"{kind}s").mkdir(parents=True)
    (out / "style.css").write_text(CSS)
    (out / "index.html").write_text(home_html(pages, posts))
    for item in pages + posts:
        (out / f"{item.kind}s" / f"{item.slug}.html").write_text(
            item_html(item, pages))
    return out


def update_site(db_path: Path, out: Path) -> Path:
    """Run a site update after a change to published content."""
    return render_site(out, db_path)
