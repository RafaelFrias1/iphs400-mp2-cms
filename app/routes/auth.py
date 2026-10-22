"""Logging in and out of the admin console."""
from __future__ import annotations

import math

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from app import accounts
from app.login_limiter import limiter
from app.web import templates, verify_csrf

router = APIRouter()

# The same message for a wrong password, an unknown email and a deactivated
# account, so the response never reveals which emails have accounts.
LOGIN_ERROR = "Incorrect email or password."


@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(request, "admin/login.html",
                                      {"title": "Log in", "email": ""})


@router.post("/login", dependencies=[Depends(verify_csrf)])
def login(request: Request, email: str = Form(""), password: str = Form("")):
    with limiter.lock(email):
        wait = limiter.seconds_locked(email)
        if wait > 0:
            return _login_page(request, email, _lockout_error(wait), status_code=429)
        account = accounts.authenticate(request.app.state.db_path, email, password)
        if account is None:
            limiter.record_failure(email)
            return _login_page(request, email, LOGIN_ERROR, status_code=401)
        limiter.clear(email)
    # A fresh session on login, so a session id or CSRF token planted before
    # login is worthless afterwards.
    request.session.clear()
    request.session["account_id"] = account.id
    return RedirectResponse("/admin", status_code=303)


def _lockout_error(seconds: float) -> str:
    minutes = math.ceil(seconds / 60)
    unit = "minute" if minutes == 1 else "minutes"
    return f"Too many failed logins. Try again in {minutes} {unit}."


def _login_page(request: Request, email: str, error: str, status_code: int):
    return templates.TemplateResponse(
        request, "admin/login.html",
        {"title": "Log in", "email": email, "error": error},
        status_code=status_code,
    )


@router.post("/logout", dependencies=[Depends(verify_csrf)])
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
