"""Posts: any logged-in account writes them; editors change only their own.

The form's buttons are sent as `action`. Preview re-shows the form with the
sanitized, rendered Markdown and saves nothing. Save keeps the post's status:
a draft stays a draft, a published post stays published. Publish saves and
publishes in one click. Unpublish and Delete are separate small forms.

Any change to published content (publish, saving a published post, unpublish,
deleting a published post) runs a site update; draft-only changes never do.
Editors get 403 on someone else's post, whether they follow a link or type
the URL. Only admins may set a slug by hand; an editor's slug field, if sent
anyway, is ignored.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app import content, publish
from app.accounts import Account
from app.content import Item, Kind, Status
from app.markdown import render_markdown
from app.web import current_account, templates, verify_csrf

router = APIRouter(prefix="/admin/posts", dependencies=[Depends(current_account)])


def _form(request: Request, me: Account, *, item: Item | None, title: str,
          body: str, slug: str, error: str = "", preview: bool = False,
          status_code: int = 200):
    return templates.TemplateResponse(
        request, "admin/post_form.html",
        {"title": item.title if item else "New post", "account": me,
         "item": item, "post_title": title, "body": body, "slug": slug,
         "error": error,
         "preview": render_markdown(body) if preview else None},
        status_code=status_code,
    )


def _editable(request: Request, me: Account, post_id: int) -> Item:
    item = content.get_item(request.app.state.db_path, post_id)
    if item is None or item.kind is not Kind.POST:
        raise HTTPException(status_code=404, detail="No such post.")
    if not content.can_change(me, item):
        raise HTTPException(status_code=403, detail="You can only change your own posts.")
    return item


def _update_site_if_published(request: Request, *statuses: Status) -> None:
    """Run a site update when the item was or is now published."""
    if Status.PUBLISHED in statuses:
        publish.update_site(request.app.state.db_path,
                            request.app.state.site_dir)


def _status_after(action: str, current: Status) -> Status:
    """Publish publishes; Save keeps the item's current status."""
    return Status.PUBLISHED if action == "publish" else current


def _to_post(item_id: int) -> RedirectResponse:
    return RedirectResponse(f"/admin/posts/{item_id}", status_code=303)


@router.get("")
def post_list(request: Request, me: Account = Depends(current_account)):
    return templates.TemplateResponse(
        request, "admin/posts.html",
        {"title": "Posts", "account": me, "can_change": content.can_change,
         "posts": content.list_items(request.app.state.db_path, Kind.POST)},
    )


@router.get("/new")
def new_post_form(request: Request, me: Account = Depends(current_account)):
    return _form(request, me, item=None, title="", body="", slug="")


@router.post("", dependencies=[Depends(verify_csrf)])
def create_post(request: Request, me: Account = Depends(current_account),
                title: str = Form(""), body: str = Form(""),
                action: str = Form("save")):
    if action == "preview":
        return _form(request, me, item=None, title=title, body=body, slug="",
                     preview=True)
    if not title.strip():
        return _form(request, me, item=None, title=title, body=body, slug="",
                     error="Enter a title.", status_code=400)
    status = _status_after(action, Status.DRAFT)
    item = content.create_item(request.app.state.db_path, Kind.POST,
                               title.strip(), body, me, status)
    _update_site_if_published(request, status)
    return _to_post(item.id)


@router.get("/{post_id}")
def edit_post_form(request: Request, post_id: int,
                   me: Account = Depends(current_account)):
    item = _editable(request, me, post_id)
    return _form(request, me, item=item, title=item.title, body=item.body,
                 slug=item.slug)


@router.post("/{post_id}", dependencies=[Depends(verify_csrf)])
def update_post(request: Request, post_id: int,
                me: Account = Depends(current_account), title: str = Form(""),
                body: str = Form(""), slug: str = Form(""),
                action: str = Form("save")):
    item = _editable(request, me, post_id)
    if not me.is_admin:
        slug = item.slug
    if action == "preview":
        return _form(request, me, item=item, title=title, body=body, slug=slug,
                     preview=True)
    error = ""
    status = _status_after(action, item.status)
    new_slug = content.slugify(slug) if me.is_admin else None
    if not title.strip():
        error = "Enter a title."
    elif new_slug == "":
        error = "Enter a slug with at least one letter or digit."
    else:
        try:
            content.update_item(request.app.state.db_path, item.id, title.strip(),
                                body, new_slug, status)
        except content.SlugTaken:
            error = f"The slug {new_slug} is already used by another item."
    if error:
        return _form(request, me, item=item, title=title, body=body, slug=slug,
                     error=error, status_code=400)
    _update_site_if_published(request, item.status, status)
    return _to_post(item.id)


@router.post("/{post_id}/unpublish", dependencies=[Depends(verify_csrf)])
def unpublish_post(request: Request, post_id: int,
                   me: Account = Depends(current_account)):
    item = _editable(request, me, post_id)
    if item.status is Status.PUBLISHED:
        content.set_status(request.app.state.db_path, item.id, Status.DRAFT)
        _update_site_if_published(request, item.status)
    return _to_post(item.id)


@router.post("/{post_id}/delete", dependencies=[Depends(verify_csrf)])
def delete_post(request: Request, post_id: int,
                me: Account = Depends(current_account)):
    item = _editable(request, me, post_id)
    content.delete_item(request.app.state.db_path, item.id)
    _update_site_if_published(request, item.status)
    return RedirectResponse("/admin/posts", status_code=303)
