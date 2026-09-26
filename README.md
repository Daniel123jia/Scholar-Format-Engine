# Scholar Document Delivery

A reusable formatting and export skill for research products.

It sits **after** content-generation skills such as AI paper deep reading, academic writing, literature review, peer review, reviewer response, thesis/proposal drafting, and research reporting.

## Core idea

```text
Domain result JSON
      ↓
Adapter (optional)
      ↓
DocumentIR
      ↓
Style Pack
      ↓
Deterministic renderer
      ↓
DOCX / Markdown
      ↓
Validation / visual QA
```

The reasoning skill owns the content. This skill owns the final document.

## Why this exists

Without a shared delivery layer, every research feature ends up re-implementing fonts, headings, tables, evidence blocks, page setup, Word export, and Markdown export. This package centralizes those concerns.

## Included Style Packs

- `scholar-default.yaml`
- `ai-deep-reading.yaml`
- `academic-paper.yaml`
- `literature-review.yaml`
- `peer-review-report.yaml`
- `reviewer-response.yaml`

## Quick start

Requires Python 3.10 or newer.

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate Word from canonical DocumentIR:

```bash
python scripts/compile.py \
  --input examples/document.example.json \
  --style style-packs/ai-deep-reading.yaml \
  --format docx \
  --output /tmp/example.docx
```

Generate Markdown:

```bash
python scripts/compile.py \
  --input examples/document.example.json \
  --style style-packs/ai-deep-reading.yaml \
  --format md \
  --output /tmp/example.md
```

Generate a report directly from a PaperScope-style deep-reading result:

```bash
python scripts/compile.py \
  --input examples/deep-reading-result.example.json \
  --adapter deep-reading \
  --style style-packs/ai-deep-reading.yaml \
  --format docx \
  --output /tmp/deep-reading.docx
```

Generate a report from the PaperScope AI Reader service/API envelope used by the local paper assistant:

```bash
python scripts/compile.py \
  --input ai-reader-result.json \
  --adapter ai-reader \
  --style style-packs/ai-deep-reading.yaml \
  --format md \
  --output /tmp/ai-reader-report.md
```

Render DOCX pages for visual QA:

```bash
python scripts/render_docx_preview.py /tmp/deep-reading.docx --output-dir /tmp/deep-reading-preview
```

## Current scope

First-class:

- structured JSON → DOCX
- structured JSON → Markdown
- PaperScope deep-reading JSON adapter
- reusable YAML Style Packs
- typography / tables / callouts / captions / images / equations-as-text
- static TOC / headers / footers / page-number fields
- structural validation
- optional DOCX page preview through LibreOffice + `pdftoppm`

Deliberately deferred:

- arbitrary legacy Word reformatting
- uploaded Word-template style extraction
- true LaTeX-to-OMML equation conversion
- citation-style rewriting
- PDF as a first-class user export
- complex floating layouts / posters / brochures

## Design principle

The package uses original implementation code. It does not bundle code from the third-party formatting projects used as conceptual references. See `THIRD_PARTY_NOTICES.md`.
