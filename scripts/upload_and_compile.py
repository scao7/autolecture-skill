#!/usr/bin/env python3
"""Upload a generated work-dir to AutoLecture, compile, download mp4.

Run this as the LAST step of the autolecture-skill skill — it replaces
the old manual "drag zip to autolecture.ai → click Recompile" loop:

    AUTOLECTURE_API_KEY=al_live_... python upload_and_compile.py /path/to/workdir

What it does
------------
1. Resolves the main .tex (main.tex > index.tex > first root-level .tex).
2. Creates a fresh project on the server (uses workdir name as project name).
3. Uploads every other file as an asset (preserves relative paths, so
   `scenes/v1.py` stays at `scenes/v1.py` server-side).
4. PUTs the main .tex content via the tex endpoint (it's source, not
   an asset).
5. Triggers a compile and polls until terminal, printing block-level
   progress along the way.
6. Streams the final mp4 to `<workdir>/out.mp4`.
7. Prints the Studio URL so the user can open the project in the web
   UI for tweaking.

Why this exists
---------------
Before the SDK landed, the skill ended with "package_zip.py → upload
to autolecture.ai → click Recompile." Three manual steps. With the
SDK the whole tail is one command. `package_zip.py` is still useful
as a local backup but it's no longer required.

Exit codes
----------
0  — finished, mp4 written
1  — missing API key, missing workdir, missing main .tex, or compile
     failed. stderr carries the reason.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Files we never upload — work-dir noise from Whisper, OS, package_zip.
_SKIP_NAMES: set[str] = {
    ".DS_Store",
    "__pycache__",
    ".git",
    "project.zip",
    "beat_plan.md",   # planning artifact, not a runtime asset
    "out.mp4",        # previous run's output
}
_SKIP_SUFFIXES: set[str] = {".pyc"}

# Names we'll accept as "the main tex". First match wins (case-insensitive,
# shallowest first). If none of these match, we fall back to the first .tex
# at the work-dir root.
_MAIN_TEX_CANDIDATES: list[str] = [
    "main.tex",
    "index.tex",
    "paper_walkthrough.tex",   # historical skill default
    "video.tex",
    "script.tex",
]


def _is_skippable(path: Path) -> bool:
    if path.name in _SKIP_NAMES:
        return True
    if path.suffix in _SKIP_SUFFIXES:
        return True
    if any(part in _SKIP_NAMES for part in path.parts):
        return True
    return False


def _find_main_tex(workdir: Path) -> Path:
    """Pick the main .tex from the workdir. Raises SystemExit if none found."""
    # Pass 1: known names at root, in order.
    for name in _MAIN_TEX_CANDIDATES:
        cand = workdir / name
        if cand.is_file():
            return cand
    # Pass 2: any .tex at root.
    root_tex = sorted(p for p in workdir.glob("*.tex") if not _is_skippable(p))
    if root_tex:
        return root_tex[0]
    # Pass 3: any .tex anywhere (shallowest first).
    any_tex = sorted(
        (p for p in workdir.rglob("*.tex") if not _is_skippable(p)),
        key=lambda p: (len(p.relative_to(workdir).parts), str(p)),
    )
    if any_tex:
        return any_tex[0]
    raise SystemExit(f"no .tex file found under {workdir}")


def _iter_assets(workdir: Path, main_tex: Path):
    """Walk the workdir and yield (abs_path, rel_path_str) for every file
    that should be uploaded as an asset (everything except the main .tex
    and the skip-list)."""
    for path in workdir.rglob("*"):
        if not path.is_file():
            continue
        if path == main_tex:
            continue
        if _is_skippable(path):
            continue
        rel = path.relative_to(workdir).as_posix()
        yield path, rel


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workdir", type=Path, help="Generated project directory (must contain a .tex)")
    parser.add_argument("--name", default=None, help="Override project name (default: workdir basename)")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("AUTOLECTURE_BASE_URL", "https://autolecture.ai"),
        help="API base URL (default https://autolecture.ai or $AUTOLECTURE_BASE_URL)",
    )
    parser.add_argument(
        "--no-compile",
        action="store_true",
        help="Stop after upload — don't trigger compile.",
    )
    parser.add_argument(
        "--poll-interval",
        type=float, default=2.0,
        help="Seconds between compile-job polls. Default 2.0.",
    )
    args = parser.parse_args()

    workdir: Path = args.workdir.resolve()
    if not workdir.is_dir():
        print(f"workdir not found or not a directory: {workdir}", file=sys.stderr)
        return 1

    # Pre-flight: harness.check — refuse to upload+compile a non-compliant
    # project (would burn ✦ on a render that's going to fail). Same gate
    # as scripts/package_zip.py so zip-path and SDK-path agree.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    try:
        from harness.check import main as _harness_main
    except Exception as e:
        print(f"WARN: harness unavailable ({e}); skipping pre-flight",
              file=sys.stderr)
    else:
        rc = _harness_main([str(workdir)])
        if rc != 0:
            print("ERROR: harness.check failed — refusing to upload a "
                  "non-compliant project (would burn ✦ on a render that's "
                  "going to fail).", file=sys.stderr)
            print(f"Try: python -m harness.fix {workdir} --auto --apply",
                  file=sys.stderr)
            return rc

    # SDK presence — use require_pip for the standard "fail-loud + how to
    # fix" box (matches transcribe.py / extract_pdf_figures.py).
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _deps import require_pip  # noqa: E402
    require_pip(
        "autolecture",
        note="AutoLecture Python SDK — drives upload + compile + download",
    )
    from autolecture import (  # noqa: E402
        Client,
        CompileCancelledError,
        CompileFailedError,
        DeviceAuthError,
    )

    # Auth resolution: Client() walks (AUTOLECTURE_API_KEY env → local
    # cache at ~/.config/autolecture/auth.json) automatically. If neither
    # is set, drop into the OAuth device flow inline — prints a login
    # URL the user clicks, then resumes upload + compile with the
    # freshly-minted key. No more "go mint a key + paste into env"
    # ceremony for first-time users.
    try:
        al = Client(base_url=args.base_url)
    except ValueError:
        print(
            "[auth] No cached credentials. Starting OAuth device flow…",
            file=sys.stderr,
        )
        try:
            al = Client.login(
                base_url=args.base_url,
                client_name="autolecture-skill",
            )
        except DeviceAuthError as e:
            print(f"[auth] login failed: {e}", file=sys.stderr)
            return 1

    main_tex_path = _find_main_tex(workdir)
    main_tex_content = main_tex_path.read_text(encoding="utf-8")
    project_name = args.name or workdir.name

    print(f"== AutoLecture upload from {workdir}")
    print(f"   main tex: {main_tex_path.relative_to(workdir)} ({len(main_tex_content)} chars)")
    print(f"   project:  {project_name}")
    print(f"   server:   {args.base_url}")

    with al:
        # ── 1. create project ────────────────────────────────────────
        proj = al.create_project(project_name, template="blank")
        pid = proj["id"]
        print(f"   created project id={pid}")

        # ── 2. upload assets ─────────────────────────────────────────
        # main.tex name on server. If the workdir's main was at root,
        # use that filename; if nested, flatten to `main.tex` (the
        # server's auto-discovery prefers that name anyway).
        try:
            main_rel = main_tex_path.relative_to(workdir).as_posix()
        except ValueError:
            main_rel = "main.tex"

        uploaded = 0
        for abs_path, rel in _iter_assets(workdir, main_tex_path):
            try:
                al.upload_asset(pid, abs_path, rel_path=rel)
                uploaded += 1
                size_kb = abs_path.stat().st_size / 1024
                print(f"   uploaded  {rel}  ({size_kb:.1f} KB)")
            except Exception as e:
                print(f"   WARN      {rel}: {e}", file=sys.stderr)
        print(f"   {uploaded} asset(s) uploaded")

        # ── 3. write main.tex via the tex endpoint ───────────────────
        # The main tex is project SOURCE, not an asset — put it through
        # the tex endpoint so the parser sees it on the next compile.
        al.put_tex(pid, main_rel, main_tex_content)
        print(f"   wrote main tex → {main_rel}")

        if args.no_compile:
            print(f"\n[done — compile skipped per --no-compile]")
            print(f"  open: {args.base_url}/studio?id={pid}")
            return 0

        # ── 4. compile + poll ────────────────────────────────────────
        print(f"\n== compiling (polling every {args.poll_interval}s) ...")

        def _on_progress(job: dict) -> None:
            done   = job.get("blocks_done", 0)
            total  = job.get("blocks_total")
            status = job.get("status")
            cb     = job.get("current_block") or {}
            cur    = f"block#{cb.get('index')}" if cb else "—"
            tot    = total if total is not None else "?"
            print(f"   [{done}/{tot}] {status:9s} now: {cur}")

        try:
            job = al.compile(
                pid,
                tex_path=main_rel,
                on_progress=_on_progress,
                poll_interval=args.poll_interval,
            )
        except CompileFailedError as e:
            print(f"\n!! compile failed: {e.message}", file=sys.stderr)
            if e.error_log:
                print("--- error log tail ---", file=sys.stderr)
                print(e.error_log[-2000:], file=sys.stderr)
            print(f"\n  inspect at: {args.base_url}/studio?id={pid}", file=sys.stderr)
            return 1
        except CompileCancelledError:
            print(f"\n!! compile was cancelled", file=sys.stderr)
            return 1

        print(f"\n== compile succeeded — {job['actual_cost_credits']} ✦ spent in {(job.get('elapsed_ms') or 0)/1000:.1f}s")

        # ── 5. download final mp4 ────────────────────────────────────
        out_mp4 = workdir / "out.mp4"
        print(f"   downloading final mp4 → {out_mp4}")
        al.download_preview(pid, dest=out_mp4)
        size_mb = out_mp4.stat().st_size / (1024 * 1024)
        print(f"   wrote {out_mp4} ({size_mb:.1f} MB)")

        print(f"\n[done]")
        print(f"  open in Studio: {args.base_url}/studio?id={pid}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
