#!/usr/bin/env python3
"""Build the claude.ai-uploadable zip of THIS skill.

claude.ai (Settings → Capabilities → Skills → Upload) validates:
  - the zip contains ONE top-level folder whose name equals the
    frontmatter `name:` (GitHub's "Download ZIP" fails this — its top
    folder is `autolecture-skill-main`)
  - SKILL.md with name + description sits at that folder's root

This script zips the repo into `dist/autolecture-skill.zip` with the
correct top folder and without dev junk (git, caches, tests/fixtures —
agents never need them at runtime; they exist for the pre-push harness).

Usage:  python3 scripts/make_skill_zip.py
"""
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_NAME = "autolecture-skill"

EXCLUDE_DIRS = {".git", "__pycache__", "dist",
                "harness/tests", "harness/fixtures"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}
EXCLUDE_NAMES = {".DS_Store"}


def _excluded(rel: Path) -> bool:
    posix = rel.as_posix()
    for d in EXCLUDE_DIRS:
        if posix == d or posix.startswith(d + "/"):
            return True
    return rel.suffix in EXCLUDE_SUFFIXES or rel.name in EXCLUDE_NAMES


def main() -> int:
    fm = (REPO / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^name:\s*(\S+)", fm, re.M)
    if not m or m.group(1) != SKILL_NAME:
        sys.exit(f"frontmatter name {m and m.group(1)!r} != {SKILL_NAME!r} "
                 "— claude.ai requires the top folder to match it")

    out = REPO / "dist" / f"{SKILL_NAME}.zip"
    out.parent.mkdir(exist_ok=True)
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for fp in sorted(REPO.rglob("*")):
            if not fp.is_file():
                continue
            rel = fp.relative_to(REPO)
            if _excluded(rel):
                continue
            z.write(fp, f"{SKILL_NAME}/{rel.as_posix()}")
            n += 1
    print(f"{out}  ({n} files, {out.stat().st_size/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
