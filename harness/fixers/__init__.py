"""Fixer registry. Each fixer is a module with `FIXER_NAME` and
`apply(workdir: Path, dry_run: bool) -> list[dict]`.

Findings carry an optional `fixer=<name>` field that points here; fix.py
dispatches based on the name."""
from __future__ import annotations

from . import add_voice_clone, split_long_say

FIXERS = {
    add_voice_clone.FIXER_NAME: add_voice_clone,
    split_long_say.FIXER_NAME:  split_long_say,
}
