"""The deployer: sends the rendered site/ to the web host (ADR-004).

A deployer is any callable that takes the site directory and raises if the
site did not reach the host. create_app() takes one; tests pass a fake. The
default is push_to_gh_pages() (which `cms deploy` also uses) when CMS_DEPLOY
is "on", and render_only() otherwise, so a fresh clone never pushes.

GitHub access comes from the environment, never from a committed file. When
CMS_GITHUB_TOKEN is set, git sends it as an HTTP header (through git's
GIT_CONFIG_* variables, so it never appears in a command line). Without it,
git uses whatever credentials the team laptop already has. The token is read
here at each deploy, not in settings.py at start-up, so one set later is used.
"""
from __future__ import annotations

import base64
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from app import settings

Deployer = Callable[[Path], None]

# Long enough for a slow hotel network, short enough that a request never hangs.
TIMEOUT_SECONDS = 120


class DeployFailed(Exception):
    """The site did not reach the host (no network, or GitHub said no)."""


def render_only(site: Path) -> None:
    """Send nothing: the site update stops at site/ (CMS_DEPLOY is not on)."""


def _git_env() -> dict[str, str]:
    env = os.environ | {"GIT_TERMINAL_PROMPT": "0"}
    token = os.environ.get("CMS_GITHUB_TOKEN", "")
    if token:
        basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        env |= {"GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
                "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: basic {basic}"}
    return env


def push_to_gh_pages(site: Path, message: str = "Site update") -> None:
    """Commit `site` to the gh-pages branch and push it to origin."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ghp_import", "-n", "-p", "-m", message,
             str(site)],
            cwd=settings.ROOT, env=_git_env(), capture_output=True, text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DeployFailed(str(exc)) from exc
    if result.returncode != 0:
        raise DeployFailed(result.stderr.strip() or "git push failed")
