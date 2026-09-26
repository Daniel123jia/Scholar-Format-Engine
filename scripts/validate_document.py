from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from common import (
    collect_validation_warnings,
    load_json,
    load_yaml,
    validate_document_ir,
    validate_style_pack,
)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate Scholar DocumentIR and a Style Pack.")
    ap.add_argument("--input", required=True, help="DocumentIR JSON path")
    ap.add_argument("--style", required=True, help="Style Pack YAML path")
    args = ap.parse_args()

    document = load_json(args.input)
    style = load_yaml(args.style)

    errors = []
    errors.extend([f"DocumentIR: {e}" for e in validate_document_ir(document)])
    errors.extend([f"StylePack: {e}" for e in validate_style_pack(style)])

    warnings = collect_validation_warnings(document, style, Path(args.input).resolve().parent)

    if errors:
        print("VALIDATION FAILED", file=sys.stderr)
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        for w in warnings:
            print(f"WARN: {w}", file=sys.stderr)
        return 2

    print("VALIDATION PASSED")
    for w in warnings:
        print(f"WARN: {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
