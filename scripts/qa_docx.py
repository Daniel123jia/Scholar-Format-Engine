from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from validate_docx_structure import validate
from render_docx_preview import render_preview


def main() -> int:
    ap = argparse.ArgumentParser(description="Run Scholar-Format-Engine DOCX structural QA and optional page rendering.")
    ap.add_argument("docx")
    ap.add_argument("--preview-dir", default=None)
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()

    errors, warnings = validate(args.docx)
    for w in warnings:
        print("WARN:", w)
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    print("STRUCTURAL QA PASSED")
    if not args.no_render:
        out = Path(args.preview_dir) if args.preview_dir else Path(args.docx).with_suffix("").parent / (Path(args.docx).stem + "_preview")
        render_preview(args.docx, out)
        print(f"PREVIEW: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
