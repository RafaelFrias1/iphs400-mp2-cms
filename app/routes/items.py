"""Posts and pages: one editor, two routers (/admin/posts and /admin/pages).

Any logged-in account writes posts; editors change only their own. Pages are
admin-only: every /admin/pages route refuses editors with 403, whether they
follow a link or type the URL.

The form's buttons are sent as `action`. Preview re-shows the form with the
sanitized, rendered Markdown and saves nothing. Save keeps the item's status:
a draft stays a draft, a published item stays published. Publish saves and
publishes in one click. Unpublish and Delete are separate small forms.

Any change to published content (publish, saving a published item, unpublish,
deleting a published item) runs as a site update; draft-only changes never do.
If the site update fails (no wifi), the change is not saved and the form
comes back with what was typed and an error, so the author can retry
(ADR-004). A new item published offline is kept as a draft instead, so the
text survives leaving the page.
Only admins may set a slug by hand; an editor's slug field, if sent anyway,
is ignored.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app import content, db, publish
from app.accounts import Account
from app.content import Item, Kind, Status
from app.markdown import render_markdown
from app.publish import OFFLINE
from app.routes.console import content_list
from app.web import current_account, require_admin, templates, verify_csrf


T = TypeVar("T")

OFFLINE_KEPT_AS_DRAFT = ("Website not updated, so this was saved as a draft. "
                         "Publish it again when you're online.")


def _change(request: Request, change: Callable[[db.Source], T],
            *statuses: Status) -> T:
    """Make `change`; as a site update when the item was or is now published.

    Raises publish.SiteUpdateFailed, with nothing saved, if the update fails.
    """
    state = request.app.state
    if Status.PUBLISHED in statuses:
        return publish.update_site(state.db_path, state.site_dir,
                                   state.deployer, change)
    return change(state.db_path)


def _saved_message(action: str, before: Status | None, after: Status) -> str:
    """What the item's page says after a successful save."""
    if after is Status.DRAFT:
        return "Saved as a draft."
    if action == "publish" and before is not Status.PUBLISHED:
        return "Published."
    return "Changes saved and published."


def _status_after(action: str, current: Status) -> Status:
    """Publish publishes; Save keeps the item's current status."""
    return Status.PUBLISHED if action == "publish" else current


def item_router(kind: Kind) -> APIRouter:
    """The console routes for one kind of item, at /admin/<kind>s."""
    base = f"/admin/{kind}s"
    guard = require_admin if kind is Kind.PAGE else current_account
    router = APIRouter(prefix=base, dependencies=[Depends(guard)])

    def _form(request: Request, me: Account, *, item: Item | None, title: str,
              body: str, slug: str, error: str = "", saved: str = "",
              preview: bool = False, status_code: int = 200):
        return templates.TemplateResponse(
            request, "admin/item_form.html",
            {"title": item.title if item else f"New {kind}", "account": me,
             "kind": kind, "item": item, "item_title": title, "body": body,
             "slug": slug, "error": error, "saved": saved,
             "preview": render_markdown(body) if preview else None},
            status_code=status_code,
        )

    def _editable(request: Request, me: Account, item_id: int) -> Item:
        item = content.get_item(request.app.state.db_path, item_id)
        if item is None or item.kind is not kind:
            raise HTTPException(status_code=404, detail=f"No such {kind}.")
        if not content.can_change(me, item):
            raise HTTPException(status_code=403,
                                detail=f"You can only change your own {kind}s.")
        return item

    def _offline(request: Request, me: Account, item: Item,
                 kept_as_draft: bool = False):
        """The item's form as saved, after a site update failed."""
        return _form(request, me, item=item, title=item.title, body=item.body,
                     slug=item.slug, status_code=503,
                     error=OFFLINE_KEPT_AS_DRAFT if kept_as_draft else OFFLINE)

    def _to_item(request: Request, item_id: int,
                 saved: str = "") -> RedirectResponse:
        """Back to the item's page, which shows `saved` once (if given)."""
        if saved:
            request.session["saved"] = [kind, item_id, saved]
        return RedirectResponse(f"{base}/{item_id}", status_code=303)

    @router.get("")
    def item_list(request: Request, me: Account = Depends(current_account),
                  status: str = "", author: str = ""):
        """The one content list, with this kind already chosen."""
        return content_list(request, me, status=status, kind=kind,
                            author=author)

    @router.get("/new")
    def new_item_form(request: Request, me: Account = Depends(current_account)):
        return _form(request, me, item=None, title="", body="", slug="")

    @router.post("", dependencies=[Depends(verify_csrf)])
    def create_item(request: Request, me: Account = Depends(current_account),
                    title: str = Form(""), body: str = Form(""),
                    action: str = Form("save")):
        if action == "preview":
            return _form(request, me, item=None, title=title, body=body,
                         slug="", preview=True)
        if not title.strip():
            return _form(request, me, item=None, title=title, body=body,
                         slug="", error="Enter a title.", status_code=400)
        status = _status_after(action, Status.DRAFT)
        try:
            item = _change(request, lambda source: content.create_item(
                source, kind, title.strip(), body, me, status), status)
        except publish.SiteUpdateFailed:
            item = content.create_item(request.app.state.db_path, kind,
                                       title.strip(), body, me)
            return _offline(request, me, item, kept_as_draft=True)
        return _to_item(request, item.id, _saved_message(action, None, status))

    @router.get("/{item_id}")
    def edit_item_form(request: Request, item_id: int,
                       me: Account = Depends(current_account)):
        item = _editable(request, me, item_id)
        # Only this item's own message, so another tab's never shows here.
        saved = ""
        if request.session.get("saved", [None, None])[:2] == [kind, item.id]:
            saved = request.session.pop("saved")[2]
        return _form(request, me, item=item, title=item.title, body=item.body,
                     slug=item.slug, saved=saved)

    @router.post("/{item_id}", dependencies=[Depends(verify_csrf)])
    def update_item(request: Request, item_id: int,
                    me: Account = Depends(current_account),
                    title: str = Form(""), body: str = Form(""),
                    slug: str = Form(""), action: str = Form("save")):
        item = _editable(request, me, item_id)
        if not me.is_admin:
            slug = item.slug
        if action == "preview":
            return _form(request, me, item=item, title=title, body=body,
                         slug=slug, preview=True)
        error, status_code = "", 400
        status = _status_after(action, item.status)
        new_slug = content.slugify(slug) if me.is_admin else None
        if not title.strip():
            error = "Enter a title."
        elif new_slug == "":
            error = "Enter a slug with at least one letter or digit."
        else:
            try:
                _change(request, lambda source: content.update_item(
                    source, item.id, title.strip(), body, new_slug, status),
                    item.status, status)
            except content.SlugTaken:
                error = f"The slug {new_slug} is already used by another item."
            except publish.SiteUpdateFailed:
                error, status_code = OFFLINE, 503
        if error:
            return _form(request, me, item=item, title=title, body=body,
                         slug=slug, error=error, status_code=status_code)
        return _to_item(request, item.id,
                        _saved_message(action, item.status, status))

    @router.post("/{item_id}/unpublish", dependencies=[Depends(verify_csrf)])
    def unpublish_item(request: Request, item_id: int,
                       me: Account = Depends(current_account)):
        item = _editable(request, me, item_id)
        if item.status is Status.PUBLISHED:
            try:
                _change(request, lambda source: content.set_status(
                    source, item.id, Status.DRAFT), item.status)
            except publish.SiteUpdateFailed:
                return _offline(request, me, item)
            return _to_item(request, item.id, "Unpublished: back to draft.")
        return _to_item(request, item.id)

    @router.post("/{item_id}/delete", dependencies=[Depends(verify_csrf)])
    def delete_item(request: Request, item_id: int,
                    me: Account = Depends(current_account)):
        item = _editable(request, me, item_id)
        try:
            _change(request, lambda source: content.delete_item(source, item.id),
                    item.status)
        except publish.SiteUpdateFailed:
            return _offline(request, me, item)
        return RedirectResponse(base, status_code=303)

    return router


posts_router = item_router(Kind.POST)
pages_router = item_router(Kind.PAGE)
