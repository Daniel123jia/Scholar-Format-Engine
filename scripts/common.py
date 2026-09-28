from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict

import yaml
from jsonschema import Draft202012Validator, RefResolver

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = SKILL_ROOT / "schemas"


def load_json(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(data: Dict[str, Any], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_yaml(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return data


def validate_against_schema(instance: Any, schema_path: str | Path) -> list[str]:
    schema = load_json(schema_path)
    resolver = RefResolver("#", schema, store={"#": schema, schema.get("$id", ""): schema})
    validator = Draft202012Validator(schema, resolver=resolver)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    out = []
    for err in errors:
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        out.append(f"{path}: {err.message}")
    return out


def validate_document_ir(data: Dict[str, Any]) -> list[str]:
    return validate_against_schema(data, SCHEMA_DIR / "document-content.schema.json")


def validate_style_pack(data: Dict[str, Any]) -> list[str]:
    return validate_against_schema(data, SCHEMA_DIR / "style-pack.schema.json")


def safe_filename(text: str, fallback: str = "document") -> str:
    text = (text or "").strip()
    text = re.sub(r"[\\/:*?\"<>|]+", "_", text)
    text = re.sub(r"\s+", "_", text)
    text = text.strip("._")
    return text[:120] or fallback


def format_template(text: str | None, context: Dict[str, Any]) -> str | None:
    if text is None:
        return None
    out = text
    for key, value in context.items():
        out = out.replace("{" + key + "}", "" if value is None else str(value))
    return out


def normalize_hex(value: str | None, default: str = "000000") -> str:
    if not value:
        return default
    value = value.lstrip("#").upper()
    if re.fullmatch(r"[0-9A-F]{6}", value):
        return value
    return default


def cm_from_mm(mm: float) -> float:
    return mm / 10.0


def collect_validation_warnings(document: Dict[str, Any], style: Dict[str, Any], base_dir: str | Path | None = None) -> list[str]:
    warnings: list[str] = []
    known_roles = set(style.get("roles", {}).keys())
    base = Path(base_dir) if base_dir else Path.cwd()
    if not document.get("title"):
        warnings.append("Document has no title.")

    for idx, block in enumerate(document.get("blocks", [])):
        role = block.get("role", "body")
        if role not in known_roles:
            warnings.append(f"Block {idx}: unknown role '{role}', renderer will fall back to 'body'.")
        if block.get("type") == "image":
            p = Path(block.get("path", ""))
            if not p.is_absolute():
                p = base / p
            if not p.exists():
                required = block.get("required", True)
                warnings.append(
                    f"Block {idx}: {'required' if required else 'optional'} image not found: {p}"
                )
        if block.get("type") == "table":
            headers = block.get("headers", [])
            for r_i, row in enumerate(block.get("rows", [])):
                if headers and len(row) > len(headers):
                    warnings.append(
                        f"Block {idx}, row {r_i}: row has {len(row)} cells but only {len(headers)} headers."
                    )
    return warnings
