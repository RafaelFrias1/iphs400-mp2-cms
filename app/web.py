"""What every console route shares: templates, CSRF, and who is logged in.

Two dependencies do the guarding:

  - `verify_csrf` goes on every state-changing (POST) route. It rejects the
    request with 403 unless the form's csrf_token matches the session's.
  - `current_account` goes on every console route (the console router in
    app/routes/console.py applies it to all of them). Someone who isn't
    logged in, or whose account was deactivated, is sent to /login.
"""
from __future__ import annotations

import hmac
import secrets

from fastapi import Form, HTTPException, Request
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


templates.env.globals["csrf_token"] = csrf_token


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
