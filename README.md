# Scholar-Format-Engine

A shared formatting and export engine for research products.

It converts structured outputs from AI paper deep reading, academic writing, literature review, peer review, reviewer response, thesis/proposal drafting, and research reports into consistent editable Word documents and clean Markdown.

## Architecture

```text
Domain result JSON
      ↓
Adapter
      ↓
DocumentIR
      ↓
Style Pack
      ↓
Deterministic renderer
      ↓
DOCX / Markdown
      ↓
Structural QA / visual QA
```

The upstream reasoning skill owns content. Scholar-Format-Engine owns presentation and delivery.

## What v1.1 improves

- Renamed from `scholar-document-delivery` to `Scholar-Format-Engine`.
- Real Word named styles are part of the delivery contract.
- Better bilingual typography and report spacing.
- Compact metadata block instead of a generic header table.
- Human-readable labels for deep-reading backend enums.
- Deep-reading v1.3 compatibility.
- Author limitations vs analysis limitations rendered separately.
- Paper-internal evidence support vs external verification rendered separately.
- Evidence de-duplication (`inline_first`) plus a single evidence index appendix.
- Open questions, reading guide, contradiction handling, and novelty-verification rendering.
- Improved table padding, light row striping, and callout spacing.
- DOCX structural validator and QA wrapper.

## Quick start

```bash
pip install -r requirements.txt
```

Deep-reading result → Word:

```bash
python scripts/compile.py \
  --input examples/deep-reading-result-v1.3.example.json \
  --adapter deep-reading \
  --style style-packs/ai-deep-reading.yaml \
  --format docx \
  --output /tmp/deep-reading.docx
```

Deep-reading result → Markdown:

```bash
python scripts/compile.py \
  --input examples/deep-reading-result-v1.3.example.json \
  --adapter deep-reading \
  --style style-packs/ai-deep-reading.yaml \
  --format md \
  --output /tmp/deep-reading.md
```

Structural QA:

```bash
python scripts/validate_docx_structure.py /tmp/deep-reading.docx
```

Render pages for visual QA:

```bash
python scripts/qa_docx.py /tmp/deep-reading.docx --preview-dir /tmp/deep-reading-preview
```

## Included Style Packs

- Scholar default
- AI deep reading
- Academic paper
- Literature review
- Peer-review report
- Reviewer response

## Scope

First-class:

- structured JSON → DOCX
- structured JSON → Markdown
- deep-reading adapter
- reusable YAML Style Packs
- named Word styles
- tables / callouts / captions / images / equation text
- static TOC
- headers / footers / PAGE fields
- structural validation
- optional visual QA

Deferred:

- arbitrary legacy Word reformatting
- Word-template reverse engineering
- advanced LaTeX → OMML conversion
- citation-style rewriting
- first-class PDF export
- poster/brochure/floating-layout authoring
