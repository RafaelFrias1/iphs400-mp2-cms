"""User-written Markdown -> safe HTML.

Every place that shows a post or page body (console preview, public site)
goes through render_markdown(), so nothing user-written reaches a browser
unsanitized. Scripts, event handlers and javascript: links are stripped, and
images are not allowed at all (recaps are text only).
"""
from __future__ import annotations

import nh3
from markdown_it import MarkdownIt

_md = MarkdownIt("commonmark").enable("table").enable("strikethrough")

ALLOWED_TAGS = nh3.ALLOWED_TAGS - {"img", "area", "map"}


def render_markdown(text: str) -> str:
    return nh3.clean(_md.render(text), tags=ALLOWED_TAGS)
