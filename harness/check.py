"""Harness check entry point.

Usage:
    python -m harness.check <workdir>                # human output
    python -m harness.check <workdir> --json          # machine-readable
    python -m harness.check <workdir> --strict        # treat warns as fails

Exit codes:
    0  — clean (or only warnings, unless --strict)
    1  — at least one `fail` finding
    2  — harness itself blew up (missing yaml, malformed .tex, etc.)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .checks import ALL_CHECKS
from .checks._common import Finding


def _color(code: int, text: str) -> str:
    if not sys.stderr.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def _emit_human(findings: list[Finding], workdir: Path) -> None:
    by_sev = {"fail": [], "warn": [], "info": []}
    for f in findings:
        by_sev.setdefault(f.severity, []).append(f)

    n_fail = len(by_sev["fail"])
    n_warn = len(by_sev["warn"])
    n_info = len(by_sev.get("info", []))

    if not findings:
        print(_color(32, f"✓ harness.check passed — no findings in {workdir}"))
        return

    print(_color(1, f"harness.check on {workdir}"))
    print(_color(1, f"  {n_fail} fail, {n_warn} warn, {n_info} info"))
    print()
    for sev in ("fail", "warn", "info"):
        items = by_sev.get(sev, [])
        if not items:
            continue
        color = {"fail": 31, "warn": 33, "info": 36}[sev]
        for f in items:
            loc = f"{f.file}:{f.line}" if f.line is not None else f.file
            tag = _color(color, f"[{sev.upper()} {f.check}]")
            print(f"  {tag}  {loc}")
            for line in f.message.splitlines():
                print(f"    {line}")
            if f.fixer:
                print(_color(36, f"    → auto-fixable: python -m harness.fix {workdir} --only {f.fixer} --apply"))
            print()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("workdir", type=Path)
    p.add_argument("--json", action="store_true",
                   help="emit findings as JSON to stdout")
    p.add_argument("--strict", action="store_true",
                   help="treat warn findings as fails")
    p.add_argument("--only", action="append", default=[],
                   help="run only this check (repeatable); names without "
                        ".py — e.g. --only tts_length --only manimfile_retime")
    args = p.parse_args(argv)

    workdir: Path = args.workdir.resolve()
    if not workdir.is_dir():
        print(f"workdir not found: {workdir}", file=sys.stderr)
        return 2

    checks = ALL_CHECKS
    if args.only:
        wanted = set(args.only)
        checks = [c for c in ALL_CHECKS if c.CHECK_NAME in wanted]
        missing = wanted - {c.CHECK_NAME for c in checks}
        if missing:
            print(f"unknown checks: {sorted(missing)}", file=sys.stderr)
            print(f"available: {sorted(c.CHECK_NAME for c in ALL_CHECKS)}",
                  file=sys.stderr)
            return 2

    all_findings: list[Finding] = []
    for mod in checks:
        try:
            all_findings.extend(mod.run(workdir))
        except FileNotFoundError as e:
            print(f"[harness] check {mod.CHECK_NAME} skipped: {e}",
                  file=sys.stderr)
        except Exception as e:
            print(f"[harness] check {mod.CHECK_NAME} crashed: {e!r}",
                  file=sys.stderr)
            return 2

    if args.json:
        print(json.dumps([f.to_dict() for f in all_findings], indent=2,
                         ensure_ascii=False))
    else:
        _emit_human(all_findings, workdir)

    has_fail = any(f.severity == "fail" for f in all_findings)
    has_warn = any(f.severity == "warn" for f in all_findings)
    if has_fail:
        return 1
    if args.strict and has_warn:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
