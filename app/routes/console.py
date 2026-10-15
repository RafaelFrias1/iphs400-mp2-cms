"""The admin console's home: a dashboard, and one content list for everything.

Every route on this router requires a logged-in account. The dashboard counts
posts and pages by status. The content list shows posts and pages together,
newest updated first, with one filter bar (status, then kind, then author);
the filters combine. /admin/posts and /admin/pages show the same list with
the kind already chosen (app/routes/items.py).
"""
from __future__ import annotations

from enum import StrEnum

from fastapi import APIRouter, Depends, Request

from app import accounts, content
from app.accounts import Account
from app.content import Kind, Status
from app.web import current_account, templates

router = APIRouter(prefix="/admin", dependencies=[Depends(current_account)])


class NoMatch(Exception):
    """A filter value that matches no item, e.g. ?status=archived."""


def _choice[E: StrEnum](enum: type[E], value: str) -> E | None:
    """'' means any; an unknown value matches nothing rather than failing."""
    if not value:
        return None
    try:
        return enum(value)
    except ValueError:
        raise NoMatch(value) from None


def _author(value: str) -> int | None:
    if not value:
        return None
    if not (value.isascii() and value.isdecimal()):
        raise NoMatch(value)
    return int(value)


def content_list(request: Request, me: Account, *, status: str = "",
                 kind: str = "", author: str = ""):
    """The content list, filtered by whatever the filter bar sent."""
    db_path = request.app.state.db_path
    try:
        items = content.find_items(db_path, _choice(Kind, kind),
                                   _choice(Status, status), _author(author))
    except NoMatch:
        items = []
    return templates.TemplateResponse(
        request, "admin/content.html",
        {"title": "Content", "account": me, "items": items,
         "can_change": content.can_change,
         "statuses": list(Status), "kinds": list(Kind),
         "authors": accounts.list_accounts(db_path),
         "chosen": {"status": status, "kind": kind, "author": author}},
    )


@router.get("")
def dashboard(request: Request, account: Account = Depends(current_account)):
    return templates.TemplateResponse(
        request, "admin/dashboard.html",
        {"title": "Dashboard", "account": account, "kinds": list(Kind),
         "statuses": list(Status),
         "counts": content.count_items(request.app.state.db_path)},
    )


@router.get("/content")
def all_content(request: Request, me: Account = Depends(current_account),
                status: str = "", kind: str = "", author: str = ""):
    return content_list(request, me, status=status, kind=kind, author=author)
