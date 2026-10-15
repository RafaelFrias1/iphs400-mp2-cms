"""What every console route shares: templates, CSRF, and who is logged in.

Three dependencies do the guarding:

  - `verify_csrf` goes on every state-changing (POST) route. It rejects the
    request with 403 unless the form's csrf_token matches the session's.
  - `current_account` goes on every console route (the console router in
    app/routes/console.py applies it to all of them). Someone who isn't
    logged in, or whose account was deactivated, is sent to /login.
  - `require_admin` goes on admin-only routes. It does what `current_account`
    does, then refuses editors with 403, so a typed URL is denied, not just
    a hidden link.
"""
from __future__ import annotations

import hmac
import secrets

from fastapi import Depends, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app import accounts, settings
from app.accounts import Account

templates = Jinja2Templates(directory=str(settings.TEMPLATES))


class LoginRequired(Exception):
    """Raised by `current_account`; create_app() turns it into a redirect."""


def csrf_token(request: Request) -> str:
    """The session's CSRF token, created on first use. Put it in every form."""
    if "csrf" not in request.session:
        request.session["csrf"] = secrets.token_urlsafe(32)
    return request.session["csrf"]


def root(request: Request) -> str:
    """The relative path from this page back to the site root ("", "../", ...).

    Console links are written as {{ root(request) }}admin/accounts, so they stay
    relative yet still work when a form re-renders a page at a deeper URL such
    as /admin/accounts/5/role.
    """
    return "../" * (request.url.path.count("/") - 1)


def when(timestamp: str) -> str:
    """An ISO UTC timestamp as the console shows it: '2026-10-14 18:05 UTC'."""
    return f"{timestamp[:16].replace('T', ' ')} UTC"


templates.env.globals["csrf_token"] = csrf_token
templates.env.globals["root"] = root
templates.env.filters["when"] = when


def verify_csrf(request: Request, csrf_token: str = Form("")) -> None:
    expected = request.session.get("csrf", "")
    if not (expected and hmac.compare_digest(expected, csrf_token)):
        raise HTTPException(status_code=403, detail="Invalid or missing CSRF token.")


def current_account(request: Request) -> Account:
    account_id = request.session.get("account_id")
    account = (accounts.get_account(request.app.state.db_path, account_id)
               if account_id is not None else None)
    if account is None or not account.active:
        request.session.clear()
        raise LoginRequired
    return account


def require_admin(account: Account = Depends(current_account)) -> Account:
    if not account.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can do that.")
    return account
