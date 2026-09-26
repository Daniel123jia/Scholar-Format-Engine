from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def render_preview(docx_path: str | Path, output_dir: str | Path) -> list[Path]:
    docx_path = Path(docx_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    libreoffice = shutil.which("libreoffice") or shutil.which("soffice")
    pdftoppm = shutil.which("pdftoppm")
    if not libreoffice:
        raise RuntimeError("LibreOffice/soffice not found; cannot render DOCX preview.")
    if not pdftoppm:
        raise RuntimeError("pdftoppm not found; cannot convert PDF preview to PNG.")

    with tempfile.TemporaryDirectory(prefix="sdd-lo-") as tmp:
        tmp_path = Path(tmp)
        profile = tmp_path / "profile"
        home = tmp_path / "home"
        profile.mkdir()
        home.mkdir()
        env = os.environ.copy()
        env["HOME"] = str(home)
        cmd = [
            libreoffice,
            "--headless",
            f"-env:UserInstallation=file://{profile}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(docx_path),
        ]
        result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)
        pdf_path = output_dir / (docx_path.stem + ".pdf")
        if result.returncode != 0 or not pdf_path.exists():
            raise RuntimeError(f"LibreOffice render failed: {result.stderr.strip() or result.stdout.strip()}")

    prefix = output_dir / "page"
    result = subprocess.run(
        [pdftoppm, "-png", "-r", "144", str(pdf_path), str(prefix)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftoppm failed: {result.stderr.strip()}")
    pages = sorted(output_dir.glob("page-*.png"))
    if not pages:
        raise RuntimeError("No page PNGs were produced.")
    return pages


def main() -> int:
    ap = argparse.ArgumentParser(description="Render DOCX pages to PNGs for visual QA.")
    ap.add_argument("docx")
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    pages = render_preview(args.docx, args.output_dir)
    for p in pages:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
