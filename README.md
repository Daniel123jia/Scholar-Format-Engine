# Scholar-Format-Engine v1.2

A shared deterministic formatting and export engine for research products.

It converts structured outputs from AI paper deep reading, academic writing, literature review, peer review, reviewer response, thesis/proposal drafting, and research reports into consistent editable Word documents and clean Markdown.

## Architecture

```text
Domain result JSON
      ↓
Adapter
      ↓
DocumentIR v1.1
      ↓
Style Pack
      ↓
Deterministic renderer
      ↓
DOCX / Markdown
      ↓
Structural QA / visual QA
```

## v1.2 highlights

- Full compatibility with AI Deep Reading v1.4.
- Compact front matter for research reports.
- Research judgment card and component-level material coverage.
- Gap / method / assumptions / experiment-evidence / claim-evidence / open-question rendering.
- Claim cards rendered as one-cell semantic callouts to reduce awkward cross-page splits.
- Evidence ids humanized (`E1`) and claim ids humanized (`Claim 1`).
- Evidence Index shows evidence role and supported claims.
- Structured 20-minute reading path rendering.
- Intentional table column widths via DocumentIR `column_widths_pct`.
- Neutral criticism typography; color reserved mainly for borders/fills.
- Real Word named styles, page fields, headers/footers, and structural QA.
- Block bookmarks prepared for traceable document navigation.

## Quick start

```bash
pip install -r requirements.txt
```

Deep reading → Word:

```bash
python scripts/compile.py \
  --input examples/deep-reading-result-v1.4.example.json \
  --adapter deep-reading \
  --style style-packs/ai-deep-reading.yaml \
  --format docx \
  --output /tmp/deep-reading.docx
```

Deep reading → Markdown:

```bash
python scripts/compile.py \
  --input examples/deep-reading-result-v1.4.example.json \
  --adapter deep-reading \
  --style style-packs/ai-deep-reading.yaml \
  --format md \
  --output /tmp/deep-reading.md
```

Structural QA:

```bash
python scripts/validate_docx_structure.py /tmp/deep-reading.docx
```

Visual QA:

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
- deep-reading v1.4 adapter
- reusable YAML Style Packs
- named Word styles
- semantic callouts/tables
- intentional table widths
- static TOC
- header/footer/PAGE fields
- structural validation
- render-and-inspect QA

Deferred:
- arbitrary legacy Word reformatting
- Word-template reverse engineering
- advanced LaTeX → native OMML conversion
- citation-style rewriting
- first-class PDF export
- complex poster/brochure/floating-layout authoring
