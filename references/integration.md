# Integration patterns

## AI paper deep reading

```text
deep-reading-result.json
        ↓
deep_reading_to_document.py
        ↓
DocumentIR
        ↓
ai-deep-reading.yaml
        ↓
DOCX / Markdown
```

The v1.6 adapter should preserve:

- author-reported vs model-inferred status;
- evidence support strength;
- evidence locations;
- uncertainty and limitations;
- open-question provenance.

If an evidence record contains a verified verbatim `snippet`, it may be rendered as an evidence quotation. If it contains only a paraphrase or note, render it as a paraphrase / verification note, not as original paper text.

## Academic writing

The writing skill should output semantic sections, references, figures, and tables as DocumentIR or an adapter-friendly JSON. The delivery layer applies `academic-paper.yaml` or an institution/journal-specific replacement.

## Literature review

Use `literature-review.yaml`. Tables for study characteristics and evidence synthesis can be represented directly in DocumentIR.

## Peer review

Use `peer-review-report.yaml`. Reviewer concerns may use the `reviewer_comment`, `warning`, or `limitation` roles.

## Reviewer response

Use paired blocks:

- `reviewer_comment`
- `author_response`

This makes the final Word document visually scannable while keeping the wording unchanged.

## Custom institutional styles

Create a new Style Pack rather than modifying renderer code. Treat the renderer as infrastructure and the Style Pack as policy.


### Deep-reading presentation

The standard deep-reading pack uses a layered report: 3-minute judgment, six-stage deep reading, and an evidence appendix. Full source snippets belong in the appendix by default; the main narrative uses compact evidence labels and locations.
