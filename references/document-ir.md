# DocumentIR guidance

`DocumentIR` is the stable contract between research reasoning and final delivery.

## Core principle

Represent meaning and document structure, not pixel coordinates.

Good:

```json
{
  "type": "callout",
  "role": "evidence",
  "title": "原文依据",
  "text": "..."
}
```

Avoid:

```json
{
  "x": 138,
  "y": 442,
  "font_size": 10.37
}
```

The Style Pack decides visual details.

## Semantic roles

Recommended roles:

- `body`
- `lead`
- `heading1`
- `heading2`
- `heading3`
- `evidence`
- `analysis`
- `note`
- `warning`
- `limitation`
- `reviewer_comment`
- `author_response`
- `caption`
- `equation`
- `code`

Custom roles are allowed. Unknown roles fall back to body formatting.

## Block types

### paragraph
Normal prose or short labeled text.

### heading
Semantic section title. Use `level` 1–6.

### list
Ordered or unordered list.

### table
Header + rows. Prefer concise cells.

### quote
Verbatim quotation supplied by the upstream system. The exporter does not verify whether it is truly verbatim.

### callout
Structured visual emphasis for evidence, analysis, warning, reviewer comments, author responses, and similar blocks.

### image
Local image asset. Missing assets should fail validation or produce a visible warning.

### equation
Equation source text, usually LaTeX-like text. The first version preserves equation content but does not promise editable native OMML conversion.

### page_break
Explicit page break.

### horizontal_rule
Logical separator.

## Integrity

DocumentIR should preserve uncertainty labels from upstream systems.

If the source says `inferred`, `unverified`, or `insufficient evidence`, do not silently convert the wording into a definitive claim during export.
