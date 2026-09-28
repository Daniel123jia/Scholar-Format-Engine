---
name: Scholar-Format-Engine
version: 1.2.0
description: Shared academic document formatting and export engine. Convert structured outputs from paper deep reading, academic writing, literature review, peer review, reviewer response, thesis/proposal, and research reports into consistent editable DOCX and clean Markdown using reusable Style Packs, deterministic rendering, traceability-aware layouts, and QA.
---

# Scholar-Format-Engine v1.2

Scholar-Format-Engine is the common **document formatting and delivery layer** for Scholar AI / research products.

Upstream skills decide **what the research content means**. Scholar-Format-Engine decides **how that structured content is presented, formatted, navigated, exported, and checked**.

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

Do not move domain reasoning into this skill.

---

## Core principles

1. **Content and formatting are separate.** Formatting must not silently rewrite scientific meaning.
2. **Model maps; code executes.** Fonts, sizes, spacing, margins, tables, headers/footers, page-number fields, and layout rules are deterministic.
3. **Named Word styles are mandatory.** DOCX output contains real Word styles, not only run-level formatting.
4. **Human-facing reports hide backend jargon.** Raw values such as `reported`, `E2_BODY_TEXT`, `cl-001`, `ev-003`, and `null` should not appear unless the caller explicitly requests technical output.
5. **Traceability must survive export.** Important judgments retain evidence labels, source locations, evidence roles, and an evidence index.
6. **Evidence is de-duplicated.** Long source snippets appear once by default; later references use compact evidence labels.
7. **Semantic cards should stay visually coherent.** Claim cards, assumptions, evidence callouts, and open questions should not be casually split across pages when they fit on one page.
8. **Color is semantic, not decorative.** Body text remains neutral; color is mainly used for borders, fills, and small status accents.
9. **DOCX is not done until QA passes.** Render every page and visually inspect before delivery.
10. **Markdown is structure-first.** Do not claim Markdown preserves Word pagination or exact typography.

---

## First-class inputs

Preferred canonical input: `DocumentIR` conforming to `schemas/document-content.schema.json` v1.1.

Bundled adapter:

- `deep-reading` — supports PaperScope / Scholar AI Deep Reading v1.4, with compatibility fallbacks for earlier v1.2/v1.3 fields where practical.

Future domain skills should add adapters under `scripts/adapters/` rather than hard-code domain semantics in the renderer.

Adapters may reorganize presentation structure, but must not invent scientific claims or evidence.

---

## Outputs

First-class:
- `.docx` — editable, styled Word deliverable.
- `.md` — clean structural Markdown.

QA/internal:
- normalized DocumentIR JSON;
- rendered page PNGs;
- structural validation output.

Deliver only requested final artifacts unless debug outputs are requested.

---

## Style Packs

Bundled packs:
- `scholar-default.yaml`
- `ai-deep-reading.yaml`
- `academic-paper.yaml`
- `literature-review.yaml`
- `peer-review-report.yaml`
- `reviewer-response.yaml`

A Style Pack controls:
- page size/orientation/margins;
- Latin and East Asian fonts;
- font size, weight, and color;
- heading hierarchy;
- line/paragraph spacing;
- table geometry and column proportions;
- callout fills/borders;
- metadata and front matter;
- TOC/header/footer/page numbering;
- evidence display policy.

Official school/journal/client rules override generic packs. Encode exact requirements in a new Style Pack instead of adding one-off renderer branches.

---

## AI deep-reading presentation contract

The default Word/Markdown report keeps the stable six-stage structure:

1. 论文速览
2. 研究问题与 Gap
3. 核心方法与真实创新
4. 实验与证据
5. 批判性评价
6. 开放问题与精读建议

### v1.2 rendering behavior

- Compact front matter: avoid spending two nearly empty pages on cover + TOC by default.
- Show a **科研判断卡** in the overview.
- Render component-level material coverage instead of only “部分/充分”.
- Render Gap as author framing + actual bottleneck + Gap judgment.
- Render Method Diff and module decomposition with intentional column widths.
- Render assumptions with why-needed, failure mode, and stress test.
- Render experiment-evidence chains before Claim–Evidence.
- Render each Claim as a **single semantic callout/card** instead of a long multi-row table; this reduces awkward page splitting.
- Hide backend ids (`cl-001`, `ev-001`) and display user labels such as `Claim 1`, `E1`.
- Keep paper-internal evidence support separate from external verification.
- Keep author limitations separate from PaperScope analysis limitations.
- Render Open Questions as question → why it matters → how to validate.
- Render a source-aware reading guide and structured 20-minute path.
- Render Evidence Index entries with source location, evidence role, and supported claims.
- Use neutral body text for criticism; reserve warm colors for warning borders/fills.

See `references/deep-reading-layout.md`.

---

## Workflow

### 1. Normalize domain JSON

Deep reading:

```bash
python scripts/compile.py \
  --input deep-reading-result.json \
  --adapter deep-reading \
  --style style-packs/ai-deep-reading.yaml \
  --format docx \
  --output report.docx \
  --emit-ir normalized.json
```

### 2. Validate contracts

```bash
python scripts/validate_document.py \
  --input normalized.json \
  --style style-packs/ai-deep-reading.yaml
```

Schema errors are blockers.

### 3. Render deterministically

DOCX:

```bash
python scripts/compile.py \
  --input deep-reading-result.json \
  --adapter deep-reading \
  --style style-packs/ai-deep-reading.yaml \
  --format docx \
  --output report.docx
```

Markdown:

```bash
python scripts/compile.py \
  --input deep-reading-result.json \
  --adapter deep-reading \
  --style style-packs/ai-deep-reading.yaml \
  --format md \
  --output report.md
```

### 4. Structural DOCX validation

```bash
python scripts/validate_docx_structure.py report.docx
```

### 5. Render and visually inspect

```bash
python scripts/qa_docx.py report.docx --preview-dir preview
```

Inspect every rendered page. Fix and repeat if there is clipping, excessive whitespace, awkward table splitting, orphan headings, poor column widths, missing glyphs, or header/footer defects.

### 6. Deliver final artifacts only

Do not deliver QA page images unless requested.

---

## DOCX requirements

- Real Word named styles for Normal, Title, Heading 1/2/3 and semantic Scholar-Format-Engine roles.
- Latin + East Asian font mappings.
- PAGE fields in footer when page numbers are enabled.
- Repeat table headers where useful.
- `cantSplit` for table rows and one-cell semantic callouts.
- Optional `column_widths_pct` for intentional table proportions.
- Evidence/claim/open-question cards should stay together when practical.
- Evidence appendix entries may carry bookmarks for future internal navigation.
- Source snippets and AI interpretation must remain visually distinct.
- Do not expose raw backend ids/statuses by default.

---

## Markdown requirements

Markdown preserves semantic structure, not exact layout.

Use headings, lists, tables, blockquotes/callouts, images, equations, and optional front matter. When blocks contain stable ids, render anchors so evidence appendices remain addressable.

---

## Boundaries

Scholar-Format-Engine does not:
- decide whether scientific claims are correct;
- perform literature search or novelty verification;
- repair unsupported evidence;
- invent figures/equations/references/metadata;
- act as a PDF layout-restoration engine;
- reverse-engineer arbitrary Word templates in v1.2;
- automatically reformat arbitrary legacy Word documents in v1.2.
