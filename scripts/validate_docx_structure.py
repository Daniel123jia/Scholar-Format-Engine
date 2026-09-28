from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _read_xml(zf: zipfile.ZipFile, name: str):
    return ET.fromstring(zf.read(name))


def validate(path: str | Path) -> tuple[list[str], list[str]]:
    path = Path(path)
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return [f"DOCX not found: {path}"], []
    if path.suffix.lower() != ".docx":
        warnings.append("File extension is not .docx")

    try:
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
            required = {"word/document.xml", "word/styles.xml", "word/settings.xml", "[Content_Types].xml"}
            for item in sorted(required):
                if item not in names:
                    errors.append(f"Missing required DOCX part: {item}")

            if "word/styles.xml" in names:
                styles = _read_xml(zf, "word/styles.xml")
                style_ids = {
                    el.attrib.get(f"{{{NS['w']}}}styleId")
                    for el in styles.findall("w:style", NS)
                }
                for sid in ("Normal", "Title", "Heading1", "Heading2", "Heading3"):
                    if sid not in style_ids:
                        errors.append(f"Missing named paragraph style: {sid}")
                sfe = [s for s in style_ids if s and s.startswith("SFE")]
                if not sfe:
                    warnings.append("No Scholar-Format-Engine custom styles found.")

            if "word/document.xml" in names:
                doc = _read_xml(zf, "word/document.xml")
                text = "".join(t.text or "" for t in doc.findall(".//w:t", NS))
                bad_tokens = ["[reported]", "[inferred]", "[unknown]"]
                for tok in bad_tokens:
                    if tok in text:
                        warnings.append(f"Raw backend status token visible in document: {tok}")
                if "E2_BODY_TEXT" in text or "E3_BODY_PLUS_ARTIFACTS" in text:
                    warnings.append("Raw Evidence Grade enum is visible in the human-facing document.")
                if "cl-00" in text:
                    warnings.append("Raw claim backend id is visible; prefer Claim 1/2/... in human-facing output.")
                if "ev-00" in text:
                    warnings.append("Raw evidence backend id is visible; prefer E1/E2/... in human-facing output.")

                fields = " ".join(x.text or "" for x in doc.findall(".//w:instrText", NS))
                has_page = "PAGE" in fields
                if not has_page:
                    # Page field may live in footer parts.
                    for name in names:
                        if name.startswith("word/footer") and name.endswith(".xml"):
                            root = _read_xml(zf, name)
                            ftxt = " ".join(x.text or "" for x in root.findall(".//w:instrText", NS))
                            if "PAGE" in ftxt:
                                has_page = True
                                break
                if not has_page:
                    warnings.append("No PAGE field found; page numbering may be absent.")

            if not any(n.startswith("word/header") and n.endswith(".xml") for n in names):
                warnings.append("No header part found.")
            if not any(n.startswith("word/footer") and n.endswith(".xml") for n in names):
                warnings.append("No footer part found.")

    except zipfile.BadZipFile:
        errors.append("File is not a valid DOCX/ZIP package.")
    except Exception as exc:
        errors.append(f"DOCX validation failed: {exc}")

    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate core DOCX structure produced by Scholar-Format-Engine.")
    ap.add_argument("docx")
    args = ap.parse_args()
    errors, warnings = validate(args.docx)
    for w in warnings:
        print("WARN:", w)
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print("DOCX STRUCTURE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
