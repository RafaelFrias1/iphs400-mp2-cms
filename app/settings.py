"""Configuration, read from the environment (never hard-code secrets).

`.env` at the repo root is read first, so `cp .env.example .env` followed by
`uv run cms serve` works with no sourcing step. Variables already set in the
environment win over the file. CMS_ENV_FILE names a different file, or ""
for none (the tests use that, so a developer's .env never reaches them).
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env_file(path: Path) -> None:
    """Copy KEY=value lines from `path` into os.environ, unless already set.

    Understands blank lines, # comments, an `export ` prefix and values in
    single or double quotes, which is all .env.example uses.
    """
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.removeprefix("export ").strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


_env_file = os.environ.get("CMS_ENV_FILE", str(ROOT / ".env"))
if _env_file:
    load_env_file(Path(_env_file))

TEMPLATES = ROOT / "templates"
SITE = ROOT / "site"

SECRET_KEY = os.environ.get("CMS_SECRET_KEY", "dev-only-not-for-production")
DATABASE_PATH = Path(os.environ.get("CMS_DATABASE", ROOT / "cms.db"))
SITE_TITLE = os.environ.get("CMS_SITE_TITLE", "Kenyon Men's Golf CMS")
# "on" only on the team laptop: every site update then pushes to gh-pages, and
# a failed push blocks the change (ADR-004). A fresh clone leaves it unset, so
# publishing there only renders site/ and never pushes to someone else's repo.
DEPLOY = os.environ.get("CMS_DEPLOY", "").lower() == "on"
# Set this to your Pages URL once you deploy, e.g.
# https://yourname.github.io/iphs400-mp2-cms/
BASE_PATH = os.environ.get("CMS_BASE_PATH", "")
# The public site's theme until the Coach picks one on the Settings page
# (a folder under app/themes/; app/theme.py).
THEME = os.environ.get("CMS_THEME", "classic")
