"""Configuration, read from the environment (never hard-code secrets)."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
