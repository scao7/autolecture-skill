#!/usr/bin/env python3
"""Runtime-mode detector CLI — workflows call this at step 0 to decide
whether to use SDK introspection (dynamic) or fall back to user prompts
+ conservative defaults (static).

Usage:
    python -m scripts.runtime_mode               # prints "dynamic" or "static"
    python -m scripts.runtime_mode --verbose      # prints mode + base_url + source
    python -m scripts.runtime_mode --json         # machine-readable

Exit codes:
    0  — detection succeeded (mode printed to stdout)
    2  — bad CLI args
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure the harness package is importable regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harness.runtime import detect  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--verbose", action="store_true",
                   help="print mode + base_url + source + email (if known)")
    p.add_argument("--json", action="store_true",
                   help="emit a JSON object instead of a single word")
    args = p.parse_args(argv)

    m = detect()
    if args.json:
        print(json.dumps({
            "mode": m.mode,
            "base_url": m.base_url,
            "source": m.source,
            "email": m.email,
        }))
    elif args.verbose:
        print(f"mode:     {m.mode}")
        print(f"source:   {m.source}")
        if m.base_url:
            print(f"base_url: {m.base_url}")
        if m.email:
            print(f"email:    {m.email}")
    else:
        # Single word: the most common workflow consumer pattern
        # (`mode=$(python -m scripts.runtime_mode)` then bash branch).
        print(m.mode)
    return 0


if __name__ == "__main__":
    sys.exit(main())
