---
name: scholar-document-delivery
description: Convert structured academic/research content into consistent, editable Word (.docx) and Markdown (.md) deliverables using reusable Style Packs, deterministic rendering, and QA. Use after upstream skills such as AI paper deep reading, academic writing, literature review, peer review, reviewer response, thesis/proposal drafting, or research reports have produced structured content.
---

# Scholar Document Delivery

Use this skill as the common document-delivery layer for a research platform. Upstream skills decide **what the content says**; this skill decides **how that content is structured, formatted, exported, and quality-checked**.

The default architecture is:

```text
Upstream research skill
        ↓
structured domain result
        ↓
Adapter (optional)
        ↓
DocumentIR (canonical document-content JSON)
        ↓
Style Pack
        ↓
Deterministic Renderer
        ↓
DOCX / Markdown
        ↓
Validation + optional visual QA
```

Do not put domain reasoning such as paper interpretation, novelty judgment, literature synthesis, reviewer criticism, or hypothesis generation into this skill. Those belong upstream.

---

## Primary goals

1. Produce editable `.docx` files with stable typography, heading hierarchy, page setup, tables, callouts, captions, headers/footers, page numbers, and optional TOC.
2. Produce clean `.md` files that preserve document structure without pretending Markdown controls fonts, margins, or page layout.
3. Reuse the same Style Pack across AI deep reading, academic writing, literature review, peer review, reviewer response, proposals, and general research reports.
4. Keep formatting deterministic: the model may map content into DocumentIR, but code applies the final formatting.
5. Make delivery auditable: validate the input contract, cross-check referenced assets, and visually inspect DOCX previews when the host environment supports rendering.

---

## Inputs

Preferred input is `schemas/document-content.schema.json` (DocumentIR).

Accepted upstream sources include:

- PaperScope AI Reader service/API result envelopes.
- AI deep-reading result JSON.
- Academic manuscript or review result JSON.
- Peer-review or reviewer-response result JSON.
- Structured report JSON produced by another skill.
- Manually authored DocumentIR.

If the input is a domain-specific JSON, use an adapter under `scripts/adapters/` or map it to DocumentIR before rendering. The bundled `deep_reading_to_document.py` supports PaperScope-style deep-reading results. The bundled `ai_reader_to_document.py` unwraps the local paper assistant AI Reader service/API envelope and then reuses the deep-reading adapter.

Do not silently infer missing scientific claims while adapting. Adapters are structural transforms, not reasoning passes.

---

## Outputs

Supported first-class outputs:

- `.docx` — editable, formatted delivery document.
- `.md` — clean structure-first Markdown.

Optional internal QA output:

- rendered page PNGs from a generated DOCX, for visual inspection only.

Do not expose internal QA images unless requested.

---

## Style Pack routing

Choose one Style Pack unless the caller explicitly provides another:

- `style-packs/scholar-default.yaml` — neutral academic/research report.
- `style-packs/ai-deep-reading.yaml` — AI paper deep-reading report with evidence callouts.
- `style-packs/academic-paper.yaml` — manuscript-like academic writing.
- `style-packs/literature-review.yaml` — literature review / state-of-the-art report.
- `style-packs/peer-review-report.yaml` — reviewer-style assessment.
- `style-packs/reviewer-response.yaml` — response-to-reviewers document.

A Style Pack may control page size, margins, fonts, heading levels, paragraph spacing, table style, callouts, metadata presentation, TOC, header/footer, and page numbering.

Formal school, journal, client, or institutional rules always override a generic Style Pack. When a caller supplies exact formatting rules, encode them in a new Style Pack rather than hard-coding one-off exceptions in the renderer.

---

## Workflow

### Step 1 — Identify document kind

Resolve `document_kind` from the input. If the content came from an upstream skill, preserve its semantic structure rather than flattening it into generic paragraphs.

### Step 2 — Normalize to DocumentIR

Create a valid object conforming to `schemas/document-content.schema.json`.

Use semantic roles such as:

- `body`
- `heading1`, `heading2`, `heading3`
- `evidence`
- `analysis`
- `warning`
- `limitation`
- `reviewer_comment`
- `author_response`
- `caption`
- `equation`

These roles are formatting hooks only. They must not alter the meaning of the content.

### Step 3 — Select Style Pack

Load and validate the chosen YAML against `schemas/style-pack.schema.json`.

If a role is not defined by the selected pack, fall back to `body` rather than inventing formatting.

### Step 4 — Validate before rendering

Run:

```bash
python scripts/validate_document.py \
  --input document.json \
  --style style-packs/ai-deep-reading.yaml
```

Validation failures are blockers. Warnings may proceed if they do not threaten content integrity.

### Step 5 — Render

Recommended entry point:

```bash
python scripts/compile.py \
  --input document.json \
  --style style-packs/ai-deep-reading.yaml \
  --format docx \
  --output report.docx
```

For Markdown:

```bash
python scripts/compile.py \
  --input document.json \
  --style style-packs/ai-deep-reading.yaml \
  --format md \
  --output report.md
```

For PaperScope deep-reading JSON:

```bash
python scripts/compile.py \
  --input deep-reading-result.json \
  --adapter deep-reading \
  --style style-packs/ai-deep-reading.yaml \
  --format docx \
  --output paper_deep_reading.docx
```

For the local paper assistant AI Reader result envelope:

```bash
python scripts/compile.py \
  --input ai-reader-result.json \
  --adapter ai-reader \
  --style style-packs/ai-deep-reading.yaml \
  --format md \
  --output paper_deep_reading.md
```

Use `--emit-ir path.json` when the normalized DocumentIR should be saved for debugging or reuse.

### Step 6 — QA

For DOCX, run structural validation and, when available, render pages for visual review:

```bash
python scripts/render_docx_preview.py report.docx --output-dir preview
```

Then inspect every generated page image before final delivery. Fix clipping, broken tables, missing glyphs, bad spacing, orphan headings, or header/footer defects and re-render.

### Step 7 — Deliver only final artifacts

Return the requested `.docx` and/or `.md`. Do not return intermediate JSON, previews, or logs unless the user asks.

---

## Markdown rules

Markdown is a structural export, not a page-layout format.

Do not claim that Markdown itself preserves:

- fonts or exact point sizes;
- page margins;
- page numbers;
- exact line spacing;
- Word-style TOC fields;
- print pagination.

Use headings, lists, tables, blockquotes, images, code fences, math fences, and optional YAML front matter to preserve structure.

---

## DOCX rules

- Use named semantic styles where practical.
- Set both Latin and East Asian font names for bilingual documents.
- Prefer paragraph styles over scattered run-level overrides.
- Keep text content unchanged during formatting unless an upstream skill explicitly requested editing.
- Use real Word fields for page numbers. Version 1.0 uses a deterministic static TOC so previews remain stable across Word and LibreOffice.
- Keep evidence snippets visually distinct from AI analysis.
- Do not label paraphrases as verbatim quotations.
- Do not fabricate images, captions, references, equations, or source locations during export.
- Do not overwrite source documents by default.

---

## Content-integrity rules

1. Rendering must be content-preserving.
2. Adapters must not add new domain conclusions.
3. If an upstream result marks content as uncertain, inferred, unsupported, or unverified, preserve that status in the exported document.
4. Evidence snippets supplied as verified verbatim text may be rendered as quotations; paraphrases must be labeled as paraphrases or analysis.
5. Missing images or assets must produce a visible warning or validation error, never a fabricated replacement.
6. If a style rule conflicts with content integrity, content integrity wins.

---

## Boundaries

This skill is not:

- a paper reader;
- a literature search engine;
- a reviewer;
- a citation verifier;
- a novelty checker;
- a thesis-writing agent;
- a PDF layout-reconstruction tool;
- a poster/brochure/resume design system.

It is a **document delivery and formatting layer**.

For complex journal/school templates, create a dedicated Style Pack or a separate adapter rather than bloating the core renderer.

---

## Quality bar

A successful DOCX export should satisfy all of the following:

- opens without repair warnings;
- contains all source text expected from DocumentIR;
- heading hierarchy is visible and consistent;
- Chinese/English mixed text uses configured font families;
- tables fit the printable width and remain readable;
- evidence/analysis/reviewer-response blocks remain visually distinguishable;
- page number/footer/header placement is correct;
- no clipped or overlapping content appears in visual preview;
- Markdown export preserves the same logical section order.

Read `references/qa-rules.md` for detailed checks.
