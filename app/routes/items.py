"""Posts and pages: one editor, two routers (/admin/posts and /admin/pages).

Any logged-in account writes posts; editors change only their own. Pages are
admin-only: every /admin/pages route refuses editors with 403, whether they
follow a link or type the URL.

The form's buttons are sent as `action`. Preview re-shows the form with the
sanitized, rendered Markdown and saves nothing. Save keeps the item's status:
a draft stays a draft, a published item stays published. Publish saves and
publishes in one click. Unpublish and Delete are separate small forms.

Any change to published content (publish, saving a published item, unpublish,
deleting a published item) runs a site update; draft-only changes never do.
Only admins may set a slug by hand; an editor's slug field, if sent anyway,
is ignored.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app import content, publish
from app.accounts import Account
from app.content import Item, Kind, Status
from app.markdown import render_markdown
from app.routes.console import content_list
from app.web import current_account, require_admin, templates, verify_csrf


def _update_site_if_published(request: Request, *statuses: Status) -> None:
    """Run a site update when the item was or is now published."""
    if Status.PUBLISHED in statuses:
        publish.update_site(request.app.state.db_path,
                            request.app.state.site_dir)


def _status_after(action: str, current: Status) -> Status:
    """Publish publishes; Save keeps the item's current status."""
    return Status.PUBLISHED if action == "publish" else current


def item_router(kind: Kind) -> APIRouter:
    """The console routes for one kind of item, at /admin/<kind>s."""
    base = f"/admin/{kind}s"
    guard = require_admin if kind is Kind.PAGE else current_account
    router = APIRouter(prefix=base, dependencies=[Depends(guard)])

    def _form(request: Request, me: Account, *, item: Item | None, title: str,
              body: str, slug: str, error: str = "", preview: bool = False,
              status_code: int = 200):
        return templates.TemplateResponse(
            request, "admin/item_form.html",
            {"title": item.title if item else f"New {kind}", "account": me,
             "kind": kind, "item": item, "item_title": title, "body": body,
             "slug": slug, "error": error,
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

    def _to_item(item_id: int) -> RedirectResponse:
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
        item = content.create_item(request.app.state.db_path, kind,
                                   title.strip(), body, me, status)
        _update_site_if_published(request, status)
        return _to_item(item.id)

    @router.get("/{item_id}")
    def edit_item_form(request: Request, item_id: int,
                       me: Account = Depends(current_account)):
        item = _editable(request, me, item_id)
        return _form(request, me, item=item, title=item.title, body=item.body,
                     slug=item.slug)

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
        error = ""
        status = _status_after(action, item.status)
        new_slug = content.slugify(slug) if me.is_admin else None
        if not title.strip():
            error = "Enter a title."
        elif new_slug == "":
            error = "Enter a slug with at least one letter or digit."
        else:
            try:
                content.update_item(request.app.state.db_path, item.id,
                                    title.strip(), body, new_slug, status)
            except content.SlugTaken:
                error = f"The slug {new_slug} is already used by another item."
        if error:
            return _form(request, me, item=item, title=title, body=body,
                         slug=slug, error=error, status_code=400)
        _update_site_if_published(request, item.status, status)
        return _to_item(item.id)

    @router.post("/{item_id}/unpublish", dependencies=[Depends(verify_csrf)])
    def unpublish_item(request: Request, item_id: int,
                       me: Account = Depends(current_account)):
        item = _editable(request, me, item_id)
        if item.status is Status.PUBLISHED:
            content.set_status(request.app.state.db_path, item.id, Status.DRAFT)
            _update_site_if_published(request, item.status)
        return _to_item(item.id)

    @router.post("/{item_id}/delete", dependencies=[Depends(verify_csrf)])
    def delete_item(request: Request, item_id: int,
                    me: Account = Depends(current_account)):
        item = _editable(request, me, item_id)
        content.delete_item(request.app.state.db_path, item.id)
        _update_site_if_published(request, item.status)
        return RedirectResponse(base, status_code=303)

    return router


posts_router = item_router(Kind.POST)
pages_router = item_router(Kind.PAGE)
