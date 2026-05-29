#!/usr/bin/env python3
"""Package a work directory into a deliverable zip for the user.

Validates that every `\\manimFile{...}` / `\\htmlFile{...}` / `\\remotionFile{...}`
/ `\\imageFile{...}` / `\\audio{...}` reference in the .tex actually exists,
then zips the whole directory.

Usage:
    python3 package_zip.py --work <workdir> --out <workdir>/autolecture_demo.zip

Exits non-zero if validation finds missing files (no silent fallback).
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path

REF_RE = re.compile(
    r"\\(manimFile|htmlFile|remotionFile|imageFile|audio)(?:\[[^\]]*\])?\{([^}]+)\}"
)


def find_referenced_assets(tex_path: Path) -> list[tuple[str, str]]:
    """Return list of (macro_name, relative_path) for every file reference."""
    text = tex_path.read_text(encoding="utf-8")
    return [(m.group(1), m.group(2).strip()) for m in REF_RE.finditer(text)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--work", required=True, help="work directory (contains the .tex + scenes/)")
    p.add_argument("--out", required=True, help="output zip path")
    p.add_argument("--tex", help="main tex filename (default: first .tex found)")
    args = p.parse_args()

    work = Path(args.work).resolve()
    if not work.is_dir():
        sys.exit(f"work dir not found: {work}")

    # Find the main tex
    if args.tex:
        tex_path = work / args.tex
    else:
        texs = sorted(work.glob("*.tex"))
        if not texs:
            sys.exit(f"no .tex file in {work}")
        tex_path = texs[0]
    if not tex_path.is_file():
        sys.exit(f"tex not found: {tex_path}")
    print(f"main tex: {tex_path.name}")

    # Pre-flight: full harness.check (asset references + all skill rules).
    # Reuses the same machinery upload_and_compile.py uses, so a project
    # that zip-passes will also SDK-upload-pass. Importable from the
    # repo root (harness/ sits next to scripts/).
    try:
        # Ensure repo root is on sys.path so `import harness` resolves
        # whether invoked from inside scripts/ or the repo root.
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from harness.check import main as _harness_main
    except Exception as e:
        print(f"WARN: harness unavailable ({e}); falling back to "
              f"asset-reference-only validation", file=sys.stderr)
        # Legacy path — at least catch missing files.
        refs = find_referenced_assets(tex_path)
        missing = [(m, r) for m, r in refs if not (work / r).is_file()]
        if missing:
            print("ERROR: missing assets:", file=sys.stderr)
            for m, r in missing:
                print(f"  \\{m}{{{r}}}", file=sys.stderr)
            sys.exit(1)
    else:
        rc = _harness_main([str(work)])
        if rc != 0:
            print("ERROR: harness.check failed — refusing to zip a "
                  "non-compliant project. Fix findings above (or run "
                  f"`python -m harness.fix {work} --auto --apply` for "
                  f"auto-fixable ones) and re-run.", file=sys.stderr)
            sys.exit(rc)

    # Zip the directory
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Don't include the zip itself if it lives inside `work`
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in work.rglob("*"):
            if f.is_file() and f.resolve() != out_path:
                arc = f.relative_to(work).as_posix()
                zf.write(f, arc)
                print(f"  + {arc}")

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"\nwrote {out_path}  ({size_mb:.1f} MB)")
    print(f"deliver to user: {out_path}")


if __name__ == "__main__":
    main()
