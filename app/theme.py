"""The public site's theme: one stylesheet, chosen on the Settings page.

Each theme is a folder under app/themes/ holding one style.css. The Coach's
choice is the 'theme' row of the settings table (key/value rows). Until one
is stored, CMS_THEME decides (default classic). Only a folder that exists is
ever used, so a typo or a path never reaches the published site.

A site update renders site/style.css from the theme its transaction sees, so
saving a theme goes through publish.update_site() like any published change.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from app import db, settings

THEMES = Path(__file__).resolve().parent / "themes"
DEFAULT = "classic"
SETTINGS_KEY = "theme"


class UnknownTheme(ValueError):
    """No folder under app/themes/ has that name."""


def available() -> list[str]:
    """Theme names, sorted: each folder under app/themes/ with a style.css."""
    return sorted(p.parent.name for p in THEMES.glob("*/style.css"))


def selected(source: db.Source) -> str:
    """The stored theme, else CMS_THEME, else classic; always one that exists."""
    for name in (_stored(source), settings.THEME):
        if name in available():
            return name
    return DEFAULT


def css(source: db.Source) -> str:
    """The selected theme's stylesheet, as site/style.css carries it."""
    return (THEMES / selected(source) / "style.css").read_text()


def set_theme(source: db.Source, name: str) -> None:
    """Store `name` as the theme; run it through update_site() (ADR-004)."""
    if name not in available():
        raise UnknownTheme(name)
    with db.connect(source) as conn:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT (key) DO UPDATE SET value = excluded.value",
            (SETTINGS_KEY, name))


def _stored(source: db.Source) -> str | None:
    """None for a fresh clone (no database) or one made before settings existed."""
    if isinstance(source, Path) and not source.exists():
        return None
    with db.connect(source) as conn:
        try:
            row = conn.execute("SELECT value FROM settings WHERE key = ?",
                               (SETTINGS_KEY,)).fetchone()
        except sqlite3.OperationalError:  # no settings table yet
            return None
    return row[0] if row else None
