#!/usr/bin/env python3
r"""Agent debug loop for AutoLecture — Path B (API key) ONLY.

The zip path (Path A in workflows/_delivery.md) is untouched: users who don't
use an API key still download the zip and drag it to autolecture.ai. This
script is for when Claude HAS a key and wants to compile + autonomously DEBUG
the project in the cloud (the user's machine has no manim / Playwright /
Remotion / ffmpeg).

It leans on the agent-first error contract:
  • compile failures come back as STRUCTURED per-block envelopes
    (`CompileFailedError.block_errors`: code / category / actions /
    failing_source / hint), not a prose blob.
  • category gates the next move:
      provider_unreachable      → transient: auto-retry (≤2) here
      code_error                → Claude must FIX the source file, then `rerender`
      render_timeout            → Claude lowers duration= / splits the view
      engine_capability         → Claude swaps the engine
      missing_asset / quota /
        toolchain_missing       → ESCALATE to the user (needs a human)
  • multimodal: for any block that produced a (partial) mp4 we also pull a
    FRAME PNG to ./.debug/ so Claude can SEE the output.

Failure isolation = block: a fix re-pushes ONE source file; the content hash
changes for that block only, so every other block is a cache hit on rerender.

Usage (Claude drives the loop; cap retries at ~3 per block, then escalate):
  AUTOLECTURE_API_KEY=al_live_... python debug_loop.py run \
      --project-id PID --workdir DIR [--tex main.tex]
  # Claude reads the evidence, edits DIR/<failing file>, then:
  AUTOLECTURE_API_KEY=al_live_... python debug_loop.py rerender \
      --project-id PID --workdir DIR --file scenes/scene_03.tsx [--tex main.tex]

Exit codes: 0 = compiled (preview downloaded); 2 = Claude-fixable (fix + rerender);
3 = escalate to the user; 1 = usage / setup error.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import uuid
from pathlib import Path

# Category → what the agent should do next. Drives both the printed guidance
# and the exit code (so a wrapper script / Claude can branch without parsing).
_CLAUDE_FIXABLE = {"code_error", "render_timeout", "engine_capability"}
_ESCALATE = {"missing_asset", "quota", "toolchain_missing"}
_AUTO_RETRY = {"provider_unreachable"}          # transient — retry here
_MAX_PROVIDER_RETRIES = 2


def _action_guidance(be, workdir: Path) -> str:
    """One concrete next-step line for a BlockError, in Claude's voice."""
    fs = be.failing_source or {}
    where = ""
    if fs.get("path"):
        # The envelope path is the server's; the editable copy is the same
        # relpath under the workdir. Show both so Claude opens the right file.
        rel = fs["path"].split("/assets/")[-1] if "/assets/" in fs["path"] else fs["path"]
        local = workdir / rel
        where = f" → edit {local} (around line {fs.get('line')})"
    cat = be.category
    if cat == "code_error":
        return f"FIX_CODE{where}, then: rerender --file {rel if fs.get('path') else '<file>'}"
    if cat == "render_timeout":
        return "SET_DURATION/SPLIT: lower duration= on the view or split it into two, then rerender main.tex"
    if cat == "engine_capability":
        return f"SWAP_ENGINE: this engine can't do it{where}; switch \\manimFile↔\\htmlFile↔\\remotionFile"
    if cat in _ESCALATE:
        return "ESCALATE_USER: needs the user/operator (register voice / add credits / install a tool). Do not retry."
    if cat in _AUTO_RETRY:
        return "RETRY: transient provider issue — auto-retried; if still failing, escalate."
    return "ESCALATE_USER: unclassified failure — show the user raw_stderr."


def _print_evidence(be, workdir: Path, al, project_id: str) -> None:
    """Print one block's structured evidence + save a frame PNG if any."""
    print("─" * 72, file=sys.stderr)
    print(f"BLOCK #{be.order_index}  [{be.category} · {be.code} · {be.severity}]",
          file=sys.stderr)
    print(f"  {be.message}", file=sys.stderr)
    fs = be.failing_source or {}
    if fs.get("path"):
        print(f"  source: {fs['path']}:{fs.get('line')}", file=sys.stderr)
        if fs.get("snippet"):
            print(fs["snippet"], file=sys.stderr)
    if be.hint:
        print(f"  hint: {be.hint}", file=sys.stderr)
    # Multimodal: if the block produced any (partial) frame, pull it for Claude.
    if be.block_hash:
        try:
            png = al.fetch_frame(project_id, be.block_hash, t=0.0)
            out = workdir / ".debug" / f"{be.block_hash}.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(png)
            print(f"  frame: {out}  (open it to SEE the render)", file=sys.stderr)
        except Exception:
            pass  # failed blocks usually have no mp4 — the snippet is the evidence
    print(f"  NEXT: {_action_guidance(be, workdir)}", file=sys.stderr)


def _run_compile(al, project_id: str, tex_path: str, workdir: Path,
                 *, idem: str | None = None) -> int:
    """Compile once; auto-retry transient provider errors; surface evidence."""
    from autolecture import CompileFailedError, CompileCancelledError

    provider_retries = 0
    while True:
        try:
            al.compile(project_id, tex_path=tex_path, idempotency_key=idem,
                       on_progress=lambda j: None)
        except CompileFailedError as e:
            blocks = e.block_errors
            if not blocks:
                # No structured detail (shouldn't happen post-P0) — fall back.
                print(f"compile failed: {e.error_log or e.message}", file=sys.stderr)
                return 3
            print(f"\n✗ compile failed — {len(blocks)} block(s) failed "
                  f"(others are isolated/cached):", file=sys.stderr)
            for be in blocks:
                _print_evidence(be, workdir, al, project_id)

            cats = {be.category for be in blocks}
            # Transient-only failure → auto-retry here (cap), no Claude needed.
            if cats <= _AUTO_RETRY and provider_retries < _MAX_PROVIDER_RETRIES:
                provider_retries += 1
                wait = 3 * provider_retries
                print(f"\n… transient provider error; auto-retry "
                      f"{provider_retries}/{_MAX_PROVIDER_RETRIES} in {wait}s",
                      file=sys.stderr)
                time.sleep(wait)
                idem = None   # fresh attempt
                continue
            if cats & _CLAUDE_FIXABLE:
                print("\n→ Claude: fix the file(s) above, then run "
                      "`debug_loop.py rerender --file <relpath>`.", file=sys.stderr)
                return 2
            print("\n→ Escalate to the user (see evidence above).", file=sys.stderr)
            return 3
        except CompileCancelledError:
            print("compile cancelled", file=sys.stderr)
            return 1
        else:
            # Success — pull the final mp4 next to the project.
            out = workdir / "out.mp4"
            al.download_preview(project_id, out)
            print(f"\n✓ compiled — {out}", file=sys.stderr)
            print(f"  Studio: {al._http._base_url}/studio?id={project_id}",  # noqa: SLF001
                  file=sys.stderr)
            return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("run", "rerender"):
        sp = sub.add_parser(name)
        sp.add_argument("--project-id", required=True)
        sp.add_argument("--workdir", type=Path, required=True,
                        help="local project dir (holds the editable scene sources)")
        sp.add_argument("--tex", default="main.tex")
        sp.add_argument("--base-url",
                        default=os.environ.get("AUTOLECTURE_BASE_URL",
                                               "https://autolecture.ai"))
        if name == "rerender":
            sp.add_argument("--file", required=True,
                            help="relpath (under workdir) of the source you just fixed")
    args = p.parse_args()

    api_key = os.environ.get("AUTOLECTURE_API_KEY")
    if not api_key:
        print("AUTOLECTURE_API_KEY not set. Mint one at /account.", file=sys.stderr)
        return 1
    try:
        from autolecture import Client
    except ImportError:
        print("pip install autolecture", file=sys.stderr)
        return 1

    with Client(api_key=api_key, base_url=args.base_url) as al:
        if args.cmd == "rerender":
            local = args.workdir / args.file
            if not local.is_file():
                print(f"no such file: {local}", file=sys.stderr)
                return 1
            # Push the fixed source — its block's hash changes, so ONLY that
            # block re-renders; every other block is a cache hit.
            al.put_tex(args.project_id, args.file, local.read_text(encoding="utf-8"))
            print(f"pushed {args.file}; recompiling…", file=sys.stderr)
        return _run_compile(al, args.project_id, args.tex, args.workdir,
                            idem=str(uuid.uuid4()))


if __name__ == "__main__":
    raise SystemExit(main())
