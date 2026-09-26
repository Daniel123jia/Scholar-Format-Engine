from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def run(*args):
    result = subprocess.run([PY, *map(str, args)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {result.args}\nSTDOUT={result.stdout}\nSTDERR={result.stderr}")
    return result


def main():
    with tempfile.TemporaryDirectory(prefix="sdd-test-") as td:
        td = Path(td)
        example = ROOT / "examples/document.example.json"
        deep = ROOT / "examples/deep-reading-result.example.json"
        style = ROOT / "style-packs/ai-deep-reading.yaml"

        run(ROOT / "scripts/validate_document.py", "--input", example, "--style", style)

        md = td / "example.md"
        docx = td / "example.docx"
        run(ROOT / "scripts/compile.py", "--input", example, "--style", style, "--format", "md", "--output", md)
        run(ROOT / "scripts/compile.py", "--input", example, "--style", style, "--format", "docx", "--output", docx)
        assert md.exists() and md.stat().st_size > 100
        assert docx.exists() and docx.stat().st_size > 1000

        deep_docx = td / "deep.docx"
        ir = td / "deep.ir.json"
        run(ROOT / "scripts/compile.py", "--input", deep, "--adapter", "deep-reading", "--style", style, "--format", "docx", "--output", deep_docx, "--emit-ir", ir)
        assert deep_docx.exists() and deep_docx.stat().st_size > 1000
        data = json.loads(ir.read_text(encoding="utf-8"))
        assert data["document_kind"] == "ai_deep_reading"
        assert any(b.get("text") == "04 实验与证据" for b in data["blocks"] if b.get("type") == "heading")

        ai_reader_payload = td / "ai-reader-result.json"
        ai_reader_payload.write_text(
            json.dumps(
                {
                    "paper_key": "doi:10.0000/example",
                    "analysis_type": "deep",
                    "status": "ready",
                    "analysis": json.loads(deep.read_text(encoding="utf-8")),
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        ai_reader_md = td / "ai-reader.md"
        run(
            ROOT / "scripts/compile.py",
            "--input",
            ai_reader_payload,
            "--adapter",
            "ai-reader",
            "--style",
            style,
            "--format",
            "md",
            "--output",
            ai_reader_md,
        )
        assert "Example Evidence-Grounded Paper" in ai_reader_md.read_text(encoding="utf-8")

        print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
