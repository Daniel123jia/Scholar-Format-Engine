---
name: Scholar-Format-Engine
description: Shared formatting and export engine for academic/research products. Convert structured outputs from paper deep reading, academic writing, literature review, peer review, reviewer response, thesis/proposal, and research reports into consistent editable DOCX and clean Markdown using reusable Style Packs, deterministic rendering, and QA.
---

# Scholar-Format-Engine

Scholar-Format-Engine is the common **document formatting and delivery layer** for a research platform.

Upstream skills decide **what the content says**. Scholar-Format-Engine decides **how the content is presented, formatted, exported, and checked**.

```text
Upstream research skill
        ↓
structured domain JSON
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
Structural validation + visual QA
```

Do not move domain reasoning into this skill. Paper interpretation, novelty judgment, literature synthesis, reviewer criticism, hypothesis generation, and scientific conclusions belong to the upstream skill.

---

## Core principles

1. **Content and formatting are separate.** Formatting must not silently rewrite scientific meaning.
2. **Model maps; code executes.** Deterministic code applies fonts, sizes, spacing, margins, tables, headers/footers, and page-number fields.
3. **Named Word styles are mandatory.** DOCX output must contain real `styles.xml` definitions for Normal, Title, Heading 1/2/3, plus Scholar-Format-Engine semantic styles.
4. **Human-facing reports hide backend enums by default.** Raw values such as `[reported]`, `moderate`, `E2_BODY_TEXT`, and `structure_grounded` should be translated into readable labels or omitted.
5. **Evidence is source-grounded.** Verbatim evidence snippets and AI paraphrases must remain visually and semantically distinct.
6. **Do not repeat the same evidence everywhere.** Deep-reading reports default to `inline_first` evidence plus a single evidence index appendix.
7. **DOCX is not done until QA passes.** Structural checks must pass and, when rendering is available, every page should be visually inspected.
8. **Markdown is structure-first.** Do not claim Markdown preserves Word fonts, page margins, pagination, or exact line spacing.

---

## First-class inputs

Preferred input is canonical `DocumentIR` conforming to:

`schemas/document-content.schema.json`

Bundled adapter support:

- `deep-reading` — PaperScope / Scholar AI deep-reading result JSON, including v1.2 and v1.3-style fields.

Additional upstream skills should add their own adapter under `scripts/adapters/` instead of embedding one-off formatting rules in the renderer.

Adapters are structural transformations only. They must not invent missing scientific claims.

---

## Outputs

First-class:

- `.docx` — editable research deliverable with named styles.
- `.md` — clean structural Markdown.

Internal QA:

- rendered page PNGs for visual inspection.
- structural DOCX validation report printed by CLI.

Do not expose QA previews or intermediate JSON unless requested.

---

## Style Packs

Bundled packs:

- `style-packs/scholar-default.yaml`
- `style-packs/ai-deep-reading.yaml`
- `style-packs/academic-paper.yaml`
- `style-packs/literature-review.yaml`
- `style-packs/peer-review-report.yaml`
- `style-packs/reviewer-response.yaml`

A Style Pack controls:

- page size/orientation/margins;
- Latin and East Asian fonts;
- font sizes and colors;
- line spacing and paragraph spacing;
- heading hierarchy;
- table style and cell padding;
- callout presentation;
- metadata presentation;
- TOC, header, footer, page-number fields;
- deep-reading presentation policy such as enum humanization and evidence display mode.

Official school, journal, funder, court, client, or institutional rules override generic packs. Encode exact rules in a new Style Pack rather than hard-coding special cases.

---

## Deep-reading presentation rules

The `ai-deep-reading` adapter and Style Pack are designed for Scholar AI deep-reading results.

Default user-facing behavior:

- Report title: `AI 论文精读报告`.
- Paper title becomes the subtitle.
- Six primary report sections remain stable.
- Backend enums are translated into natural language.
- `reported` / `inferred` / `unknown` are not printed as raw bracket tags.
- Paper-internal evidence strength and external verification status remain separate.
- Evidence snippets appear once by default; subsequent references point to evidence IDs.
- A single `附录：证据索引` collects the evidence actually used.
- Author-acknowledged limitations and analysis-derived limitations are rendered separately.
- Open questions and reading-guide output are supported.
- Novelty verification distinguishes paper-relative delta from externally verified field novelty.

See `references/deep-reading-layout.md` and `references/user-facing-labels.md`.

---

## Workflow

### 1. Resolve document kind

Preserve the semantic structure produced by the upstream skill. Do not flatten structured claims, evidence, limitations, or reviewer responses into generic paragraphs.

### 2. Normalize to DocumentIR

For domain-specific JSON, run an adapter. For deep reading:

```bash
python scripts/compile.py \
  --input deep-reading-result.json \
  --adapter deep-reading \
  --style style-packs/ai-deep-reading.yaml \
  --format docx \
  --output paper-report.docx
```

Use `--emit-ir normalized.json` to inspect the normalized structure.

### 3. Validate contracts

```bash
python scripts/validate_document.py \
  --input normalized.json \
  --style style-packs/ai-deep-reading.yaml
```

Schema errors are blockers.

### 4. Render deterministically

DOCX:

```bash
python scripts/compile.py \
  --input normalized.json \
  --style style-packs/ai-deep-reading.yaml \
  --format docx \
  --output report.docx
```

Markdown:

```bash
python scripts/compile.py \
  --input normalized.json \
  --style style-packs/ai-deep-reading.yaml \
  --format md \
  --output report.md
```

### 5. Validate DOCX structure

```bash
python scripts/validate_docx_structure.py report.docx
```

The validator checks for core OOXML parts, named styles, Scholar-Format-Engine styles, PAGE fields, and accidental leakage of raw backend tokens.

### 6. Render and visually inspect DOCX

```bash
python scripts/qa_docx.py report.docx --preview-dir preview
```

Inspect every rendered page. Fix and re-render if there is clipping, broken tables, poor spacing, orphan headings, missing glyphs, or header/footer defects.

### 7. Deliver only final artifacts

Return only the requested `.docx` and/or `.md` unless the user asks for debug outputs.

---

## DOCX requirements

- Use actual Word named styles, not only run-level formatting.
- Set both Latin and East Asian fonts.
- Keep headings with following content when practical.
- Apply widow/orphan control where supported.
- Use real PAGE fields for page numbers.
- Repeat table header rows when configured.
- Prevent table rows and callout blocks from splitting when practical.
- Use readable table cell padding.
- Keep evidence snippets distinct from AI analysis.
- Do not fabricate captions, page numbers, references, evidence text, or figures.
- Do not overwrite source files unless explicitly requested by the caller.

---

## Markdown requirements

Markdown preserves semantic structure, not page layout.

Use:

- headings;
- paragraphs;
- ordered/unordered lists;
- blockquotes/callouts;
- tables;
- images;
- fenced/code or math blocks when applicable;
- optional YAML front matter.

Do not claim Markdown itself controls fonts, point sizes, page margins, page numbers, or print pagination.

---

## Boundaries

Scholar-Format-Engine does **not**:

- decide whether a scientific claim is correct;
- perform literature search or novelty verification;
- rewrite citations into a new style unless an upstream citation tool does so;
- repair unsupported evidence;
- invent missing figures, equations, references, or metadata;
- serve as a PDF-layout restoration engine;
- automatically reformat arbitrary legacy Word documents in this version;
- parse arbitrary uploaded Word templates into new Style Packs in this version.

Those can be added as separate capabilities later.
