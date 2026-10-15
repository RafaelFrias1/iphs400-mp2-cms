#!/usr/bin/env python3
"""SessionEnd hook: copy this session's transcript into docs/transcripts/.

Transcripts are required evidence (rubric H2). Saving them automatically means
you cannot forget — in MP1 nobody remembered. The name follows the required
pattern; set CMS_STUDENT=first-last in .env (or your shell) so it is right.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


def student_slug(project: Path) -> str:
    name = os.environ.get("CMS_STUDENT")
    if not name:
        env = project / ".env"
        if env.exists():
            match = re.search(r"^CMS_STUDENT=(.+)$", env.read_text(), re.M)
            name = match.group(1).strip() if match else None
    return re.sub(r"[^a-z-]", "", (name or "your-name").lower().replace(" ", "-"))


def main() -> None:
    event = json.load(sys.stdin)
    source = Path(event.get("transcript_path", ""))
    if not source.exists():
        return
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or ".")
    out = project / "docs" / "transcripts"
    out.mkdir(parents=True, exist_ok=True)
    # One more than the highest number so far, so moving a file out (such as
    # the template's own sessions) never makes two sessions share a number.
    taken = [int(m.group(1)) for p in out.glob("*.md")
             if (m := re.search(r"_chat-session_(\d+)_", p.name))]
    number = f"{max(taken, default=0) + 1:02d}"
    target = out / (f"iphs400_mp2-cms_chat-session_{number}_"
                    f"{student_slug(project)}_{datetime.now().strftime('%Y%m%d')}.md")
    if not target.exists():
        shutil.copy2(source, target)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
