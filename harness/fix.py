"""Harness fix entry point.

Usage:
    python -m harness.fix <workdir>                       # dry-run (default)
    python -m harness.fix <workdir> --apply               # write files
    python -m harness.fix <workdir> --only split_long_say --apply
    python -m harness.fix <workdir> --auto                # run all suggested
                                                            fixers based on
                                                            current check output

Exit codes:
    0  — fixers ran clean (with or without edits)
    1  — at least one fixer reported a "skipped" (can't auto-fix)
    2  — harness itself blew up
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .checks import ALL_CHECKS
from .fixers import FIXERS


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("workdir", type=Path)
    p.add_argument("--apply", action="store_true",
                   help="actually write changes (default is dry-run)")
    p.add_argument("--only", action="append", default=[],
                   help=f"fixer name (repeatable). Available: "
                        f"{sorted(FIXERS.keys())}")
    p.add_argument("--auto", action="store_true",
                   help="run all fixers suggested by the current "
                        "harness.check findings")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    workdir: Path = args.workdir.resolve()
    if not workdir.is_dir():
        print(f"workdir not found: {workdir}", file=sys.stderr)
        return 2

    selected: list[str]
    if args.auto:
        # Inspect current findings, take their .fixer values.
        suggested: set[str] = set()
        for mod in ALL_CHECKS:
            try:
                for f in mod.run(workdir):
                    if f.fixer:
                        suggested.add(f.fixer)
            except Exception as e:
                print(f"[harness] {mod.CHECK_NAME} crashed: {e!r}",
                      file=sys.stderr)
        selected = sorted(suggested)
    elif args.only:
        unknown = [n for n in args.only if n not in FIXERS]
        if unknown:
            print(f"unknown fixers: {unknown}", file=sys.stderr)
            print(f"available: {sorted(FIXERS.keys())}", file=sys.stderr)
            return 2
        selected = list(args.only)
    else:
        selected = list(FIXERS.keys())

    all_edits: dict[str, list[dict]] = {}
    for name in selected:
        mod = FIXERS[name]
        try:
            edits = mod.apply(workdir, dry_run=not args.apply)
        except Exception as e:
            print(f"[harness] fixer {name} crashed: {e!r}", file=sys.stderr)
            return 2
        all_edits[name] = edits

    if args.json:
        print(json.dumps({"applied": args.apply, "edits": all_edits},
                         indent=2, ensure_ascii=False))
    else:
        n_edits = sum(len([e for e in v if not e.get("skipped")])
                      for v in all_edits.values())
        n_skipped = sum(len([e for e in v if e.get("skipped")])
                        for v in all_edits.values())
        verb = "would edit" if not args.apply else "edited"
        print(f"harness.fix on {workdir}")
        print(f"  {n_edits} call(s) {verb}, {n_skipped} could not auto-fix")
        if not args.apply and n_edits:
            print(f"  (dry-run — pass --apply to write changes)")
        print()
        for fixer_name, edits in all_edits.items():
            if not edits:
                continue
            print(f"  {fixer_name}:")
            for e in edits:
                if e.get("skipped"):
                    print(f"    [skipped] {e['file']}:{e.get('line', '?')}: "
                          f"{e.get('reason', 'unknown reason')}")
                else:
                    summary = ""
                    if "before" in e and "after" in e:
                        summary = f"  {e['before']!r}  →  {e['after']!r}"
                    elif "split_into" in e:
                        summary = (f"  {e.get('before_chars', '?')}c → "
                                   f"{e['split_into']} chunks "
                                   f"{e.get('chunk_sizes', [])}")
                    print(f"    {e['file']}:{e.get('line', '?')}{summary}")
            print()

    has_skipped = any(
        e.get("skipped") for v in all_edits.values() for e in v
    )
    return 1 if has_skipped else 0


if __name__ == "__main__":
    sys.exit(main())
