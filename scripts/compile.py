from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SKILL_ROOT))

from common import (
    collect_validation_warnings,
    dump_json,
    load_json,
    load_yaml,
    validate_document_ir,
    validate_style_pack,
)
from render_docx import render as render_docx
from render_markdown import render as render_markdown


def adapt_input(data: dict, adapter: str | None) -> dict:
    if not adapter:
        return data
    if adapter == "ai-reader":
        from adapters.ai_reader_to_document import adapt
        return adapt(data)
    if adapter == "deep-reading":
        from adapters.deep_reading_to_document import adapt
        return adapt(data)
    raise ValueError(f"Unknown adapter: {adapter}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile research content into DOCX or Markdown.")
    ap.add_argument("--input", required=True)
    ap.add_argument("--adapter", choices=["deep-reading", "ai-reader"], default=None)
    ap.add_argument("--style", required=True)
    ap.add_argument("--format", required=True, choices=["docx", "md"])
    ap.add_argument("--output", required=True)
    ap.add_argument("--emit-ir", default=None)
    ap.add_argument("--qa", action="store_true", help="Render DOCX pages after generation when supported.")
    args = ap.parse_args()

    raw = load_json(args.input)
    document = adapt_input(raw, args.adapter)
    style = load_yaml(args.style)

    errors = [f"DocumentIR: {e}" for e in validate_document_ir(document)]
    errors += [f"StylePack: {e}" for e in validate_style_pack(style)]
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    for w in collect_validation_warnings(document, style, Path(args.input).resolve().parent):
        print("WARN:", w, file=sys.stderr)

    if args.emit_ir:
        dump_json(document, args.emit_ir)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "docx":
        render_docx(document, style, out, Path(args.input).resolve().parent)
        if args.qa:
            from render_docx_preview import render_preview
            preview_dir = out.with_suffix("")
            preview_dir = preview_dir.parent / (preview_dir.name + "_preview")
            render_preview(out, preview_dir)
            print(f"QA preview: {preview_dir}")
    else:
        out.write_text(render_markdown(document, style), encoding="utf-8")

    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
