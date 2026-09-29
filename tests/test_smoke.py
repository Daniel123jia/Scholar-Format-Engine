from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def run(*args):
    result = subprocess.run([PY, *map(str, args)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {result.args}\nSTDOUT={result.stdout}\nSTDERR={result.stderr}")
    return result


def main():
    with tempfile.TemporaryDirectory(prefix="sfe-test-") as td:
        td = Path(td)
        example = ROOT / "examples/document.example.json"
        deep = ROOT / "examples/deep-reading-result-v1.5.example.json"
        style = ROOT / "style-packs/ai-deep-reading.yaml"

        run(ROOT / "scripts/validate_document.py", "--input", example, "--style", style)

        md = td / "example.md"
        docx = td / "example.docx"
        run(ROOT / "scripts/compile.py", "--input", example, "--style", style, "--format", "md", "--output", md)
        run(ROOT / "scripts/compile.py", "--input", example, "--style", style, "--format", "docx", "--output", docx)
        assert md.exists() and md.stat().st_size > 100
        assert docx.exists() and docx.stat().st_size > 1000
        run(ROOT / "scripts/validate_docx_structure.py", docx)

        deep_docx = td / "deep.docx"
        deep_md = td / "deep.md"
        ir = td / "deep.ir.json"
        run(ROOT / "scripts/compile.py", "--input", deep, "--adapter", "deep-reading", "--style", style, "--format", "docx", "--output", deep_docx, "--emit-ir", ir)
        run(ROOT / "scripts/compile.py", "--input", deep, "--adapter", "deep-reading", "--style", style, "--format", "md", "--output", deep_md)
        run(ROOT / "scripts/validate_docx_structure.py", deep_docx)

        data = json.loads(ir.read_text(encoding="utf-8"))
        assert data["document_kind"] == "ai_deep_reading"
        assert data["title"] == "AI 论文精读报告"
        assert any(b.get("text") == "04 实验与证据" for b in data["blocks"] if b.get("type") == "heading")
        assert any(b.get("text") == "附录：证据索引" for b in data["blocks"] if b.get("type") == "heading")

        md_text = deep_md.read_text(encoding="utf-8")
        assert "[reported]" not in md_text
        assert "[inferred]" not in md_text
        assert "E2_BODY_TEXT" not in md_text
        assert "论文内部支持" in md_text
        assert "Open Question" in md_text
        assert "20 分钟" in md_text
        assert "科研判断卡" in md_text
        assert "核心缺陷" in md_text
        assert "后续研究方向" in md_text
        assert "Core method change" in md_text

        with zipfile.ZipFile(deep_docx) as zf:
            names = set(zf.namelist())
            assert "word/styles.xml" in names
            styles = zf.read("word/styles.xml").decode("utf-8", errors="ignore")
            assert 'w:styleId="Heading1"' in styles
            assert "SFE" in styles

        print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
