---
name: Scholar-Format-Engine
version: 1.4.0
description: Shared academic document formatting and delivery engine for Scholar AI. Converts structured research outputs into layered, semantically styled DOCX and Markdown with deterministic typography, restrained academic color, evidence appendices, and QA.
---

# Scholar-Format-Engine v1.4

Scholar-Format-Engine is the common presentation/export layer for Scholar AI research skills.

Upstream skills decide **what the research content means**. This skill decides **what the user sees first, what is visually emphasized, how detail is layered, and how the final document is exported and checked**.

```text
Upstream research skill
        ↓
structured domain JSON
        ↓
Adapter
        ↓
DocumentIR
        ↓
Style Pack + semantic roles
        ↓
Deterministic renderer
        ↓
DOCX / Markdown
        ↓
Structural validation + render QA
```

Do not move scientific reasoning into this skill.

---

## Core product principle

**The backend can be deep; the visible report must be easy to scan.**

For AI paper deep reading, the default report uses three layers:

1. **3-minute judgment** — what the user must know first.
2. **Deep reading** — the six-stage analytical report.
3. **Evidence appendix** — source snippets and traceability for verification.

For a typical 8–15 page method paper, aim for a **4–6 page main report**, excluding the evidence appendix. This is a presentation target, not a scientific truncation rule.

---

## Semantic styling system

Formatting is not decoration. It communicates meaning.

- **Bold communicates importance.**
- **Color communicates semantic type.**
- **Spacing communicates hierarchy.**

Use a restrained academic palette:

- primary indigo/purple: headings, key judgments, assumptions, research directions;
- evidence blue: claims/evidence;
- warm amber: weaknesses, risks, items requiring caution;
- neutral charcoal/gray: body text and secondary metadata.

Do not use a different color for every module. Do not render whole critique sections in bright red.

Named semantic Word styles should be available for roles such as:

- `SFE key_takeaway`
- `SFE judgment`
- `SFE claim`
- `SFE assumption`
- `SFE risk`
- `SFE evidence`
- `SFE research_direction`
- `SFE reading_path`
- `SFE secondary`

See `references/semantic-styling.md`.

---

## Inputs and outputs

Preferred canonical input: DocumentIR (`schemas/document-content.schema.json`).

Bundled adapter:

- `deep-reading` — supports AI Deep Reading v1.6 and practical fallbacks for recent earlier versions.

First-class outputs:

- `.docx` — editable, styled Word report;
- `.md` — clean structured Markdown.

Internal/QA outputs may include normalized IR, page PNG previews, and validation reports.

---

## AI Deep Reading presentation contract

Keep the six visible stages stable:

1. 论文速览
2. 研究问题与 Gap
3. 核心方法与真实创新
4. 实验与证据
5. 批判性评价
6. 开放问题与精读建议

### Layer 1 — 3-minute judgment

The first page should prioritize:

- one-sentence takeaway;
- research judgment card;
- core problem;
- core method;
- real paper-relative change;
- strongest evidence;
- biggest weakness/risk;
- why it is worth reading;
- most promising bounded follow-up direction;
- reading recommendation;
- compact material coverage.

Research-value score tables are secondary and hidden by default in the standard style.

### Layer 2 — deep reading

Prefer concise structured components:

- Gap judgment;
- Method Diff;
- compact module table;
- essential formula only when reliable;
- assumptions summarized in one table by default;
- experiment interpretation chains;
- compact Claim cards;
- 2–4 prominent core weakness cards;
- the most important open questions and research directions;
- 20-minute return-to-source route.

### Layer 3 — evidence appendix

The main body should normally show compact evidence labels/locations, not repeated full source excerpts.

Put source snippets, detailed evidence metadata, evidence roles, and backlinks in the Evidence Appendix.

This keeps traceability without forcing the user to read the evidence layer before understanding the paper.

---

## Default detail policy

The `ai-deep-reading` Style Pack uses:

- `report_profile: standard`
- `evidence_mode: index_only`
- compact claims;
- compact experiments;
- summary assumptions;
- compact material-coverage matrix;
- top 3 core weaknesses;
- top 3 open questions;
- top 3 bounded research directions;
- no separate TOC page by default;
- evidence appendix enabled.

A `complete` profile may expose full claim-audit fields, experiment protocol detail, reproduction risks, and more appendices.

---

## User-facing simplification rules

Do not expose raw backend jargon as the primary report language:

- `reported` → 作者明确说明
- `inferred` → 基于论文分析
- `E2_BODY_TEXT` → 已获取正文
- `paper_only` → 仅基于本文
- `cl-001` / `ev-003` → descriptive claim titles / compact E-labels
- `null` → hide the field or state the human-readable boundary

Do not turn every schema field into a visible paragraph.

---

## Deterministic DOCX rules

- Real Word named styles are mandatory.
- Latin/East Asian fonts are configured separately.
- Font size, bold, color, spacing, margins, tables, headers/footers, and page numbers are deterministic.
- Semantic callout titles are bold.
- Label prefixes such as `结论：`, `为什么重要：`, `如何验证：`, and `边界：` are bolded selectively; explanatory text remains normal weight.
- Callout fill/border color reflects semantic type.
- Keep semantic callout rows together when practical.
- Repeat table headers when useful.
- Avoid awkward claim-card page breaks.
- Evidence source text and AI interpretation remain visually distinct.

---

## Workflow

### 1. Normalize domain JSON

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

### 3. Render

DOCX or Markdown through `scripts/compile.py`.

### 4. Structural DOCX validation

```bash
python scripts/validate_docx_structure.py report.docx
```

### 5. Visual QA

```bash
python scripts/qa_docx.py report.docx --preview-dir preview
```

Inspect every rendered page. Fix clipping, crowding, awkward whitespace, orphan headings, broken tables, poor line wrapping, or excessive visual emphasis.

---

## Boundaries

Scholar-Format-Engine does not:

- decide whether a scientific claim is correct;
- invent missing weaknesses, evidence, equations, or research directions;
- perform novelty search;
- repair unsupported analysis;
- rewrite upstream scientific meaning to make the layout look complete.

If a structured field is missing, hide or flag the block; do not fabricate it.

---

## Shipping gate

For DOCX deliverables:

1. validate structure;
2. render to page images;
3. inspect every page;
4. iterate until clean;
5. deliver only the final requested artifact.
