from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from common import load_json, load_yaml


def esc_table(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def paragraph_text(block: dict) -> str:
    if block.get("text") is not None:
        return str(block.get("text") or "")
    chunks = []
    for run in block.get("runs", []):
        text = run.get("text", "")
        if run.get("code"):
            text = f"`{text}`"
        if run.get("bold"):
            text = f"**{text}**"
        if run.get("italic"):
            text = f"*{text}*"
        if run.get("link"):
            text = f"[{text}]({run['link']})"
        chunks.append(text)
    return "".join(chunks)


def render(document: dict, style: dict) -> str:
    lines: list[str] = []
    features = style.get("features", {})

    if features.get("markdown_front_matter"):
        lines.append("---")
        lines.append(f"document_kind: {document.get('document_kind', '')}")
        lines.append(f"language: {document.get('language', '')}")
        pack_name = style.get("pack", {}).get("name", "")
        lines.append(f"style_pack: {pack_name}")
        for k, v in document.get("metadata", {}).items():
            if v is not None:
                clean = str(v).replace("\n", " ")
                lines.append(f"{k}: {json.dumps(clean, ensure_ascii=False)}")
        lines.append("---")
        lines.append("")

    if document.get("title"):
        lines.append(f"# {document['title']}")
        lines.append("")
    if document.get("subtitle"):
        lines.append(f"> {document['subtitle']}")
        lines.append("")

    if features.get("metadata_table") and document.get("metadata"):
        lines.extend(["| 项目 | 内容 |", "|---|---|"])
        for k, v in document["metadata"].items():
            if v is not None and str(v).strip():
                lines.append(f"| {esc_table(k)} | {esc_table(v)} |")
        lines.append("")

    for block in document.get("blocks", []):
        t = block.get("type")
        role = block.get("role", "body")

        if t == "heading":
            level = min(max(int(block.get("level", 1)), 1), 6)
            lines.append(f"{'#' * level} {block.get('text', '')}")
            lines.append("")
        elif t == "paragraph":
            lines.append(paragraph_text(block))
            lines.append("")
        elif t == "list":
            for i, item in enumerate(block.get("items", []), 1):
                prefix = f"{i}." if block.get("ordered") else "-"
                lines.append(f"{prefix} {item}")
            lines.append("")
        elif t == "quote":
            for ln in str(block.get("text", "")).splitlines() or [""]:
                lines.append(f"> {ln}")
            if block.get("source"):
                lines.append(f"> — {block['source']}")
            lines.append("")
        elif t == "callout":
            title = block.get("title") or role.replace("_", " ").title()
            lines.append(f"> **{title}**")
            for ln in str(block.get("text", "")).splitlines() or [""]:
                lines.append(f"> {ln}")
            meta = block.get("meta") or {}
            for k, v in meta.items():
                if v is not None and str(v).strip():
                    lines.append(f"> _{k}: {v}_")
            lines.append("")
        elif t == "table":
            headers = [esc_table(x) for x in block.get("headers", [])]
            rows = block.get("rows", [])
            width = len(headers) or max([len(r) for r in rows], default=1)
            if block.get("caption"):
                lines.append(f"**{block['caption']}**")
                lines.append("")
            if not headers:
                headers = [""] * width
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("|" + "|".join(["---"] * width) + "|")
            for row in rows:
                cells = [esc_table(x) for x in row] + [""] * max(0, width - len(row))
                lines.append("| " + " | ".join(cells[:width]) + " |")
            if block.get("note"):
                lines.append("")
                lines.append(f"_Note: {block['note']}_")
            lines.append("")
        elif t == "image":
            alt = block.get("alt") or block.get("caption") or "image"
            lines.append(f"![{alt}]({block.get('path', '')})")
            if block.get("caption"):
                lines.append(f"*{block['caption']}*")
            lines.append("")
        elif t == "equation":
            lines.append("$$")
            lines.append(str(block.get("text", "")))
            lines.append("$$")
            if block.get("label"):
                lines.append(f"*{block['label']}*")
            lines.append("")
        elif t == "page_break":
            lines.extend(["<!-- pagebreak -->", ""])
        elif t == "horizontal_rule":
            lines.extend(["---", ""])

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Render DocumentIR to Markdown.")
    ap.add_argument("--input", required=True)
    ap.add_argument("--style", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    document = load_json(args.input)
    style = load_yaml(args.style)
    out = render(document, style)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(out, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
